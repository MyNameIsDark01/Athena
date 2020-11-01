import json
import logging
import os
from math import ceil
from sys import exit
from time import sleep

import coloredlogs
import twitter
from PIL import Image, ImageDraw

import googletrans
from googletrans import Translator
from util import ImageUtil, Utility

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")


class Athena:
    """Fortnite Item Shop Generator."""

    def main(self):

        initialized = Athena.LoadConfiguration(self)

        if initialized is True:
            if self.delay > 0:
                log.info(f"Delaying process start for {self.delay}s...")
                sleep(self.delay)

            itemShop = Utility.GET(
                self,
                "https://fortnite-api.com/v2/shop/br/combined",
                {"language": self.language},
            )

            if itemShop is not None:
                itemShop = json.loads(itemShop)["data"]

                # Strip time from the timestamp, we only need the date + translate in every language from googletrans
                date = Translator().translate(Utility.ISOtoHuman(
                    self, itemShop["date"].split("T")[0], self.language
                ), str = 'en', dest= self.date_language).text

                log.info(f"Retrieved Item Shop for {date}")

                shopImage = Athena.GenerateImage(self, date, itemShop)

                if shopImage is True:
                    if self.twitterEnabled is True:
                        Athena.Tweet(self, date)

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json

        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            self.delay = configuration["delayStart"]
            self.apiKey = configuration["fortniteAPI"]["apiKey"]
            self.language = configuration["language"]
            self.date_language = configuration["date_language"]
            self.style = configuration["style"]
            if os.path.exists('assets/images/' + self.style) == False:
                log.critical(f"Icon Style not found.")
                return False
            self.supportACreator = configuration["supportACreator"]
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]

            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")

    def GenerateImage(self, date: str, itemShop: dict):
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        if itemShop["featured"] != None:
            featured = itemShop["featured"]["entries"]
        else:
            featured = []

        if itemShop["daily"] != None:
            daily = itemShop["daily"]["entries"]
        else:
            daily = []

        # Determine the max amount of rows required for the current
        # Item Shop when there are 3 columns for both Featured and Daily.
        # This allows us to determine the image height.

        rows = max(ceil(len(featured) / 3), ceil(len(daily) / 3))

        shopImage = Image.new("RGBA", (1920, ((545 * rows) + 340)))

        try:
            background = ImageUtil.Open(self, "background.png")
            background = ImageUtil.RatioResize(
                self, background, shopImage.width, shopImage.height
            )
            shopImage.paste(
                background, ImageUtil.CenterX(self, background.width, shopImage.width)
            )
        except FileNotFoundError:
            log.warn("Failed to open background.png, defaulting to dark gray")
            shopImage.paste((18, 18, 18), [0, 0, shopImage.size[0], shopImage.size[1]])

        logo = ImageUtil.Open(self, "logo.png")
        logo = ImageUtil.RatioResize(self, logo, 0, 210)
        shopImage.paste(
            logo, ImageUtil.CenterX(self, logo.width, shopImage.width, 20), logo
        )

        canvas = ImageDraw.Draw(shopImage)

        font = ImageUtil.Font(self, 48)
        textWidth, _ = font.getsize(date)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, shopImage.width, 255),
            date,
            (255, 255, 255),
            font=font,
        )
        f = Translator().translate("Featured", str = 'en', dest= self.language).text
        d = Translator().translate("Daily", str = 'en', dest= self.language).text
        
        canvas.text((20, 255), f, (255, 255, 255), font=font)
        textWidth, _ = font.getsize(d)
        canvas.text(
            (shopImage.width - (textWidth + 20), 255),
            d,
            (255, 255, 255),
            font=font,
        )

        # Track grid position
        i = 0

        for item in featured:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (20 + ((i % 3) * (card.width + 5))),
                        (315 + ((i // 3) * (card.height + 5))),
                    ),
                    card,
                )

                i += 1

        # Reset grid position
        i = 0

        for item in daily:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (990 + ((i % 3) * (card.width + 5))),
                        (315 + ((i // 3) * (card.height + 5))),
                    ),
                    card,
                )

                i += 1

        try:
            shopImage.save("itemshop.png")
            log.info("Generated Item Shop image")

            return True
        except Exception as e:
            log.critical(f"Failed to save Item Shop image, {e}")

    def GenerateCard(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""

        try:
            name = item["items"][0]["name"]
            rarity = item["items"][0]["rarity"]["value"]
            category = item["items"][0]["type"]["value"]
            price = item["finalPrice"]

            if item["items"][0]["images"]["featured"] != None:
                icon = item["items"][0]["images"]["featured"]
            else:
                icon = item["items"][0]["images"]["icon"]

            # Select bundle image and name
            if item["bundle"] != None:
                name = item["bundle"]["name"]
                icon = item["bundle"]["image"]

        except Exception as e:
            log.error(f"Failed to parse item {name}, {e}")

            return

        # Should be outdated

        if rarity == "frozen":
            blendColor = (148, 223, 255)
        elif rarity == "lava":
            blendColor = (234, 141, 35)
        elif rarity == "legendary":
            blendColor = (211, 120, 65)
        elif rarity == "dark":
            blendColor = (251, 34, 223)
        elif rarity == "starwars":
            blendColor = (231, 196, 19)
        elif rarity == "marvel":
            blendColor = (197, 51, 52)
        elif rarity == "dc":
            blendColor = (84, 117, 199)
        elif rarity == "icon":
            blendColor = (54, 183, 183)
        elif rarity == "shadow":
            blendColor = (113, 113, 113)
        elif rarity == "epic":
            blendColor = (177, 91, 226)
        elif rarity == "rare":
            blendColor = (73, 172, 242)
        elif rarity == "uncommon":
            blendColor = (96, 170, 58)
        elif rarity == "common":
            blendColor = (190, 190, 190)
        else:
            blendColor = (255, 255, 255)

        card = Image.new("RGBA", (300, 545))

        try:
            layer = ImageUtil.Open(self, self.style + f"/card_top_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open card_top_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, self.style + f"/card_top_common.png")

        card.paste(layer)

        icon = ImageUtil.Download(self, icon).convert("RGBA")
        if (category == "outfit") or (category == "emote"):
            icon = ImageUtil.RatioResize(self, icon, 285, 365)
        elif category == "wrap":
            icon = ImageUtil.RatioResize(self, icon, 230, 310)
        else:
            icon = ImageUtil.RatioResize(self, icon, 310, 390)
        if (category == "outfit") or (category == "emote"):
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width), icon)
        else:
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width, 15), icon)

        if len(item["items"]) > 1:
            # Track grid position
            i = 0

            # Start at position 1 in items array
            for extra in item["items"][1:]:
                try:
                    extraRarity = extra["rarity"]['value']
                    extraIcon = extra["images"]["smallIcon"]
                except Exception as e:
                    log.error(f"Failed to parse item {name}, {e}")

                    return

                try:
                    layer = ImageUtil.Open(self, self.style + f"/box_bottom_{extraRarity}.png")
                except FileNotFoundError:
                    log.warn(
                        f"Failed to open box_bottom_{extraRarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil.Open(self, self.style + f"/box_bottom_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (layer.height))),
                    ),
                )

                extraIcon = ImageUtil.Download(self, extraIcon)
                extraIcon = ImageUtil.RatioResize(self, extraIcon, 75, 75)

                card.paste(
                    extraIcon,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (extraIcon.height))),
                    ),
                    extraIcon,
                )

                try:
                    layer = ImageUtil.Open(self, self.style + f"/box_faceplate_{extraRarity}.png")
                except FileNotFoundError:
                    log.warn(
                        f"Failed to open box_faceplate_{extraRarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil.Open(self, self.style + f"/box_faceplate_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (layer.height))),
                    ),
                    layer,
                )

                i += 1

        if self.style == 'old':
            try:
                layer = ImageUtil.Open(self, self.style + f"/card_faceplate_{rarity}.png")
            except FileNotFoundError:
                log.warn(f"Failed to open card_faceplate_{rarity}.png, defaulted to Common")
                layer = ImageUtil.Open(self, self.style + f"/card_faceplate_common.png")

            card.paste(layer, layer)
        
        try:
            layer = ImageUtil.Open(self, self.style + f"/card_bottom_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open card_bottom_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, self.style + f"/card_bottom_common.png")

        card.paste(layer, layer)

        canvas = ImageDraw.Draw(card)
        
        if self.style == 'old':
            font = ImageUtil.Font(self, 30)
            textWidth, _ = font.getsize(f"{rarity.capitalize()} {category.capitalize()}")
            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, 385),
                f"{rarity.capitalize()} {category.capitalize()}",
                blendColor,
                font=font,
            )

            vbucks = ImageUtil.Open(self, "vbucks.png")
            vbucks = ImageUtil.RatioResize(self, vbucks, 25, 25)

            price = str(f"{price:,}")
            textWidth, _ = font.getsize(price)
            canvas.text(
                ImageUtil.CenterX(self, ((textWidth + 15) - vbucks.width), card.width, 495),
                price,
                blendColor,
                font=font,
            )

            card.paste(
                vbucks,
                ImageUtil.CenterX(self, (vbucks.width + (textWidth + 5)), card.width, 495),
                vbucks,
            )

            font = ImageUtil.Font(self, 56)
            textWidth, _ = font.getsize(name)
            change = 0
            if textWidth >= 270:
                # Ensure that the item name does not overflow
                font, textWidth, change = ImageUtil.FitTextX(self, name, 56, 260)
            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, (425 + (change / 2))),
                name,
                (255, 255, 255),
                font=font,
            )
        elif self.style == 'new':
            font = ImageUtil.Font(self, 33)

            vbucks = ImageUtil.Open(self, "vbucks_card.png")
            vbucks = ImageUtil.RatioResize(self, vbucks, 49, 49)

            price = str(f"{price:,}")
            textWidth, _ = font.getsize(price)
            canvas.text(
                ImageUtil.CenterX(self, ((textWidth + 15) - vbucks.width), card.width, 450),
                price,
                blendColor,
                font=font,
            )

            card.paste(
                vbucks,
                ImageUtil.CenterX(self, (vbucks.width + (textWidth - 290)), card.width, 436),
                vbucks,
            )

            font = ImageUtil.Font(self, 56)
            textWidth, _ = font.getsize(name)
            change = 0
            if textWidth >= 270:
                # Ensure that the item name does not overflow
                font, textWidth, change = ImageUtil.FitTextX(self, name, 56, 260)
            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, (380 + (change / 2))),
                name,
                (255, 255, 255),
                font=font,
            )

        return card

    def Tweet(self, date: str):
        """
        Tweet the current `itemshop.png` local file to Twitter using the credentials provided
        in `configuration.json`.
        """

        try:
            twitterAPI = twitter.Api(
                consumer_key=self.twitterAPIKey,
                consumer_secret=self.twitterAPISecret,
                access_token_key=self.twitterAccessToken,
                access_token_secret=self.twitterAccessSecret,
            )

            twitterAPI.VerifyCredentials()
        except Exception as e:
            log.critical(f"Failed to authenticate with Twitter, {e}")

            return

        body = f"#Fortnite Item Shop for {date}"

        if self.supportACreator is not None:
            body = f"{body}\n\nSupport-a-Creator Code: {self.supportACreator}"

        try:
            with open("itemshop.png", "rb") as shopImage:
                twitterAPI.PostUpdate(body, media=shopImage)

            log.info("Tweeted Item Shop")
        except Exception as e:
            log.critical(f"Failed to Tweet Item Shop, {e}")


if __name__ == "__main__":
    try:
        Athena.main(Athena)
    except KeyboardInterrupt:
        log.info("Exiting...")
        exit()
