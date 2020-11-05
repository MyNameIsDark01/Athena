# Athena

Athena is a utility which generates the current Fortnite Item Shop into a stylized image and shares it on Twitter.
There are two style: old and new.

## Creator

This utility is made by [EthanC](www.github.com/EthanC). I translated it and updated when necessary.

## Example

You can choose between two Icon Styles, the first is the old Icon Style, and the second is a remake of the old icons.

<p align="center">
    <img src="https://github.com/MyNameIsDark01/Athena/blob/master/old.png" width="650px" draggable="false">
</p>

<p align="center">
    <img src="https://github.com/MyNameIsDark01/Athena/blob/master/new.png" width="650px" draggable="false">
</p>

## Requirements

IF you want install all requirements in one click write this on shell:

    `pip install -r requirements.txt` **(WINDOWS)**
    `pip3 install -r requirements.txt` **(LINUX/UBUNTU)**

- [Python 3.7](https://www.python.org/downloads/)
- [Requests](http://docs.python-requests.org/en/master/user/install/)
- [coloredlogs](https://pypi.org/project/coloredlogs/)
- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html#basic-installation)
- [python-twitter](https://github.com/bear/python-twitter#installing)

A [Fortnite-API API Key](https://fortnite-api.com/profile) isn't required to obtain the Item Shop data, [Twitter API credentials](https://developer.twitter.com/en/apps) are required to Tweet the image.

## Usage

Open `configuration.py` in your preferred text editor, fill the configurable values. Once finished, save the file.

- `DELAY_START`: Set to `0` to begin the process immediately
- `LANGUAGE`: Set the language for the Item Shop data ([Supported Languages](https://fortnite-api.com/documentation))
- `DATE_LANGUAGE`: Set the language for the date above the items ([Supported Languages](https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages))
- `STYLE`: You can set `old` or `new`
- `CREATOR_CODE`: Leave blank to omit the Support-A-Creator tag section of the Tweet
- `TwitterConfig.ENABLED`: Set `enabled` to `false` if you wish for `itemshop.png` to not be Tweeted

Edit the images found in `assets/images/` to your liking, avoid changing image dimensions for optimal results.

Athena is designed to be ran using a scheduler, such as [cron](https://en.wikipedia.org/wiki/Cron).

```
python itemshop.py
```

## Credits

- Item Shop data provided by [Fortnite-API](https://fortnite-api.com/)
- Burbank font property of [Adobe](https://fonts.adobe.com/fonts/burbank)
- Luckiest Guy font property of [Google](https://fonts.google.com/specimen/Luckiest+Guy)
