"""
Generate itemshop image
"""
import logging
import os
import sys
from math import ceil
from time import sleep

import coloredlogs
import twitter
from PIL import Image, ImageDraw
from googletrans import Translator

from util import ImageUtil, Utility
from configuration import Config, TwitterConfig

log = logging.getLogger(__name__)
coloredlogs.install(
    level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")


class Athena:
    """Fortnite Item Shop Generator."""

    def __init__(self) -> None:
        """
        Set the configuration values specified in configuration.json

        Return True if configuration sucessfully loaded.
        """
        self.delay = Config.DELAY_START
        self.fortnite_api_key = Config.FORTINTE_API_KEY
        self.language = Config.LANGUAGE
        self.date_language = Config.DATE_LANGUAGE
        self.style = Config.STYLE
        self.creator_code = Config.CREATOR_CODE
        self.twitter_enabled = TwitterConfig.ENABLED
        self.twitter_api_key = TwitterConfig.API_KEY
        self.twitter_api_secret = TwitterConfig.API_SECRET
        self.twitter_access_token = TwitterConfig.ACCESS_TOKEN
        self.twitter_access_secret = TwitterConfig.ACCESS_SECRET

        if not os.path.exists(f'assets/images/{self.style}'):
            log.critical("Icon Style not found.")
            sys.exit()

        log.info("Loaded configuration")

    def start(self) -> None:
        """Start generating and tweet the itemshop"""
        if self.delay > 0:
            log.info(f"Delaying process start for {self.delay}s...")
            sleep(self.delay)

        item_shop = Utility().get_url(
            "https://fortnite-api.com/v2/shop/br/combined",
            {"language": self.language},
        )

        if item_shop is not None:
            item_shop = item_shop["data"]

            # Strip time from the timestamp, we only need the date + translate
            # in every language from googletrans
            date = Translator().translate(
                Utility().iso_to_human(item_shop["date"].split("T")[0]),
                str='en',
                dest=self.date_language
            ).text

            log.info(f"Retrieved Item Shop for {date}")

            shop_image = self.generate_image(date, item_shop)

            if shop_image is True:
                if self.twitter_enabled is True:
                    self.tweet(date)

    def generate_image(self, date: str, item_shop: dict) -> bool:
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        if item_shop["featured"] is not None:
            featured = item_shop["featured"]["entries"]
        else:
            featured = []

        if item_shop["daily"] is not None:
            daily = item_shop["daily"]["entries"]
        else:
            daily = []

        # Determine the max amount of rows required for the current
        # Item Shop when there are 3 columns for both Featured and Daily.
        # This allows us to determine the image height.

        rows = max(ceil(len(featured) / 3), ceil(len(daily) / 3))

        shop_image = Image.new("RGBA", (1920, ((545 * rows) + 340)))

        try:
            background = ImageUtil().open_image("background.png")
            background = ImageUtil().resize_ratio(
                background, shop_image.width, shop_image.height
            )
            shop_image.paste(
                background, ImageUtil().align_center(
                    shop_image.width, background.width)
            )
        except FileNotFoundError:
            log.warning(
                "Failed to open background.png, defaulting to dark gray")
            shop_image.paste(
                (18, 18, 18), [0, 0, shop_image.size[0], shop_image.size[1]])

        logo = ImageUtil().open_image("logo.png")
        logo = ImageUtil().resize_ratio(logo, 0, 210)
        shop_image.paste(
            logo, ImageUtil().align_center(
                shop_image.width, logo.width, 20), logo
        )

        canvas = ImageDraw.Draw(shop_image)

        font = ImageUtil().get_font(48)
        text_width, _ = font.getsize(date)
        canvas.text(
            ImageUtil().align_center(shop_image.width, text_width, 255),
            date,
            (255, 255, 255),
            font=font,
        )
        featured_title = Translator().translate(
            "Featured", str='en', dest=self.language).text
        daily_title = Translator().translate("Daily", str='en', dest=self.language).text

        canvas.text((20, 255), featured_title, (255, 255, 255), font=font)
        text_width, _ = font.getsize(daily_title)
        canvas.text(
            (shop_image.width - (text_width + 20), 255),
            daily_title,
            (255, 255, 255),
            font=font,
        )

        # Track grid position
        i = 0

        for item in featured:
            card = self.generate_card(item)

            if card is not None:
                shop_image.paste(
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
            card = self.generate_card(item)

            if card is not None:
                shop_image.paste(
                    card,
                    (
                        (990 + ((i % 3) * (card.width + 5))),
                        (315 + ((i // 3) * (card.height + 5))),
                    ),
                    card,
                )

                i += 1

        try:
            shop_image.save("itemshop.png")
            log.info("Generated Item Shop image")
            return True
        except Exception as error:
            log.critical(f"Failed to save Item Shop image, {error}")
        return False

    def generate_card(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""

        try:
            name = item["items"][0]["name"]
            rarity = item["items"][0]["rarity"]["value"]
            category = item["items"][0]["type"]["value"]
            price = item["finalPrice"]

            if item["items"][0]["images"]["featured"] is not None:
                icon = item["items"][0]["images"]["featured"]
            else:
                icon = item["items"][0]["images"]["icon"]

            # Select bundle image and name
            if item["bundle"] is not None:
                name = item["bundle"]["name"]
                icon = item["bundle"]["image"]

        except Exception as error:
            log.error(f"Failed to parse item, {error}")
            return

        # Should be outdated

        if rarity == "frozen":
            blend_color = (148, 223, 255)
        elif rarity == "lava":
            blend_color = (234, 141, 35)
        elif rarity == "legendary":
            blend_color = (211, 120, 65)
        elif rarity == "dark":
            blend_color = (251, 34, 223)
        elif rarity == "starwars":
            blend_color = (231, 196, 19)
        elif rarity == "marvel":
            blend_color = (197, 51, 52)
        elif rarity == "dc":
            blend_color = (84, 117, 199)
        elif rarity == "icon":
            blend_color = (54, 183, 183)
        elif rarity == "shadow":
            blend_color = (113, 113, 113)
        elif rarity == "epic":
            blend_color = (177, 91, 226)
        elif rarity == "rare":
            blend_color = (73, 172, 242)
        elif rarity == "uncommon":
            blend_color = (96, 170, 58)
        elif rarity == "common":
            blend_color = (190, 190, 190)
        else:
            blend_color = (255, 255, 255)

        card = Image.new("RGBA", (300, 545))

        try:
            layer = ImageUtil().open_image(
                self.style + f"/card_top_{rarity}.png")
        except FileNotFoundError:
            log.warning(
                f"Failed to open card_top_{rarity}.png, defaulted to Common")
            layer = ImageUtil().open_image(f"{self.style}/card_top_common.png")

        card.paste(layer)

        icon = ImageUtil().download_image(icon).convert("RGBA")
        if category in ["outfit", "emote"]:
            icon = ImageUtil().resize_ratio(icon, 285, 365)
        elif category == "wrap":
            icon = ImageUtil().resize_ratio(icon, 230, 310)
        else:
            icon = ImageUtil().resize_ratio(icon, 310, 390)
        if category in ["outfit", "emote"]:
            card.paste(icon, ImageUtil().align_center(
                card.width, icon.width), icon)
        else:
            card.paste(icon, ImageUtil().align_center(
                card.width, icon.width, 15), icon)

        if len(item["items"]) > 1:
            # Track grid position
            i = 0

            # Start at position 1 in items array
            for extra in item["items"][1:]:
                try:
                    extra_rarity = extra["rarity"]['value']
                    extra_icon = extra["images"]["smallIcon"]
                except Exception as error:
                    log.error(f"Failed to parse item {name}, {error}")

                    return

                try:
                    layer = ImageUtil().open_image(
                        self.style + f"/box_bottom_{extra_rarity}.png")
                except FileNotFoundError:
                    log.warning(
                        f"Failed to open box_bottom_{extra_rarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil().open_image(
                        f"{self.style}/box_bottom_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * layer.height)),
                    ),
                )

                extra_icon = ImageUtil().download_image(extra_icon)
                extra_icon = ImageUtil().resize_ratio(extra_icon, 75, 75)

                card.paste(
                    extra_icon,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * extra_icon.height)),
                    ),
                    extra_icon,
                )

                try:
                    layer = ImageUtil().open_image(
                        self.style + f"/box_faceplate_{extra_rarity}.png")
                except FileNotFoundError:
                    log.warning(
                        f"Failed to open box_faceplate_{extra_rarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil().open_image(
                        f"{self.style}/box_faceplate_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * layer.height)),
                    ),
                    layer,
                )

                i += 1

        if self.style == 'old':
            try:
                layer = ImageUtil().open_image(
                    self.style + f"/card_faceplate_{rarity}.png")
            except FileNotFoundError:
                log.warning(
                    f"Failed to open card_faceplate_{rarity}.png, defaulted to Common")
                layer = ImageUtil().open_image(
                    f"{self.style}/card_faceplate_common.png")

            card.paste(layer, layer)

        try:
            layer = ImageUtil().open_image(
                self.style + f"/card_bottom_{rarity}.png")
        except FileNotFoundError:
            log.warning(
                f"Failed to open card_bottom_{rarity}.png, defaulted to Common")
            layer = ImageUtil().open_image(
                f"{self.style}/card_bottom_common.png")

        card.paste(layer, layer)

        canvas = ImageDraw.Draw(card)

        if self.style == 'old':
            font = ImageUtil().get_font(30)
            text_width, _ = font.getsize(
                f"{rarity.capitalize()} {category.capitalize()}")
            canvas.text(
                ImageUtil().align_center(card.width, text_width, 385),
                f"{rarity.capitalize()} {category.capitalize()}",
                blend_color,
                font=font,
            )

            vbucks = ImageUtil().open_image("vbucks.png")
            vbucks = ImageUtil().resize_ratio(vbucks, 25, 25)

            price = str(f"{price:,}")
            text_width, _ = font.getsize(price)
            canvas.text(
                ImageUtil().align_center(
                    card.width, (text_width - vbucks.width), 495),
                price,
                blend_color,
                font=font,
            )

            card.paste(
                vbucks,
                ImageUtil().align_center(
                    card.width, (vbucks.width + (text_width + 5)), 495),
                vbucks,
            )

            font = ImageUtil().get_font(56)
            text_width, _ = font.getsize(name)
            change = 0
            if text_width >= 270:
                # Ensure that the item name does not overflow
                font, text_width, change = ImageUtil().fit_text(
                    name, 56, 260)
            canvas.text(
                ImageUtil().align_center(card.width, text_width,
                                         (425 + (change // 2))),
                name,
                (255, 255, 255),
                font=font,
            )
        elif self.style == 'new':
            font = ImageUtil().get_font(33)

            vbucks = ImageUtil().open_image("vbucks_card.png")
            vbucks = ImageUtil().resize_ratio(vbucks, 49, 49)

            price = str(f"{price:,}")
            text_width, _ = font.getsize(price)
            canvas.text(
                ImageUtil().align_center(
                    card.width, ((text_width + 15) - vbucks.width), 450),
                price,
                blend_color,
                font=font,
            )

            card.paste(
                vbucks,
                ImageUtil().align_center(
                    card.width, (vbucks.width + (text_width - 290)), 436),
                vbucks,
            )

            font = ImageUtil().get_font(56)
            text_width, _ = font.getsize(name)
            change = 0
            if text_width >= 270:
                # Ensure that the item name does not overflow
                font, text_width, change = ImageUtil().fit_text(
                    name, 56, 260)
            canvas.text(
                ImageUtil().align_center(card.width, text_width,
                                         (380 + (change // 2))),
                name,
                (255, 255, 255),
                font=font,
            )

        return card

    def tweet(self, date: str):
        """
        Tweet the current `itemshop.png` local file to Twitter using the credentials provided
        in `configuration.json`.
        """

        try:
            twitter_api = twitter.Api(
                consumer_key=self.twitter_api_key,
                consumer_secret=self.twitter_api_secret,
                access_token_key=self.twitter_access_token,
                access_token_secret=self.twitter_access_secret,
            )

            twitter_api.VerifyCredentials()
        except Exception as twtter_error:
            log.critical(
                "Failed to authenticate with Twitter, {}".format(twtter_error))
            return

        body = f"#Fortnite Item Shop for {date}"

        if self.creator_code is not None:
            body = f"{body}\n\nSupport-a-Creator Code: {self.creator_code}"

        try:
            with open("itemshop.png", "rb") as shop_image:
                twitter_api.PostUpdate(body, media=shop_image)

            log.info("Tweeted Item Shop")
        except Exception as error:
            log.critical("Failed to Tweet Item Shop, {}".format(error))


if __name__ == "__main__":
    try:
        Athena().start()
    except KeyboardInterrupt:
        log.info("Exiting...")
        sys.exit()
