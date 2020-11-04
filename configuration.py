"""
Configuration file for Athena
"""


class Config:
    DELAY_START: int = 0
    FORTINTE_API_KEY: str = ""
    LANGUAGE: str = "en"
    DATE_LANGUAGE: str = "en"
    STYLE: str = "old"  # old / new
    CREATOR_CODE: str = "YourSupportACreatorCode"


class TwitterConfig:
    ENABLED: bool = False
    API_KEY: str = "XXXXXXXXXX"
    API_SECRET: str = "XXXXXXXXXX"
    ACCESS_TOKEN: str = "XXXXXXXXXX"
    ACCESS_SECRET: str = "XXXXXXXXXX"
