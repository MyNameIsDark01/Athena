import logging
from datetime import datetime

import requests
from PIL import Image, ImageFont

log = logging.getLogger(__name__)


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate code."""

    @staticmethod
    def get_url(url: str, parameters=None):
        """
        Return the response of a successful HTTP GET request to the specified
        URL with the optionally provided header values.
        """

        if parameters is None:
            parameters = {"language": "en"}
        res = requests.get(url, params=parameters)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return res.json()
        else:
            log.critical(f"Failed to GET {url} (HTTP {res.status_code})")

    @staticmethod
    def iso_to_human(date: str):
        """Return the provided ISO8601 timestamp in human-readable format."""

        try:
            # Unix-supported zero padding removal
            return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %-d, %Y")
        except ValueError:
            try:
                # Windows-supported zero padding removal
                return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %#d, %Y")
            except Exception as e:
                log.error(
                    f"Failed to convert to human-readable time, {e}")


class ImageUtil:
    """Class containing utilitarian image-based functions intended to reduce duplicate code."""

    @staticmethod
    def open_image(filename: str):
        """Return the specified image file."""
        return Image.open(f"assets/images/{filename}")

    @staticmethod
    def download_image(url: str):
        """Download and return the raw file from the specified url as an image object."""
        res = requests.get(url, stream=True)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return Image.open(res.raw)
        else:
            log.critical(f"Failed to GET {url} (HTTP {res.status_code})")

    @staticmethod
    def resize_ratio(image: Image.Image, max_width: int, max_height: int):
        """Resize and return the provided image while maintaining aspect ratio."""
        ratio = max(max_width / image.width, max_height / image.height)
        return image.resize(
            (int(image.width * ratio), int(image.height * ratio)),
            Image.ANTIALIAS
        )

    @staticmethod
    def align_center(background_width: int, foreground_width: int, distance_top: int = 0):
        """Return the tuple necessary for horizontal centering and an optional vertical distance."""
        return background_width // 2 - foreground_width // 2, distance_top

    @staticmethod
    def get_font(size: int):
        """
        :size -> font size of text
        :return -> A font object with the specified font file and size.
        """
        return ImageFont.truetype(f"assets/fonts/BurbankBigCondensed-Black.otf", size)

    def fit_text(self, text: str, size: int, max_size: int):
        """
        Return the font and width which fits the provided text within the
        specified maxiumum width.

        :text -> string text that we want to fit it
        :size -> main font size of text
        :max_size -> max width size per pixel
        :return -> font object + new text width + change int to align the text
        """
        font = self.get_font(size)
        text_width, _ = font.getsize(text)
        change = 0

        while text_width >= max_size:
            change += 1
            size -= 1
            font = self.get_font(size)
            text_width, _ = font.getsize(text)

        return font, text_width, change
