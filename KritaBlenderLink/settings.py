from krita import Krita
from .logger import logger

import json


class Settings:
    data = {}
    instance = None

    def __init__(self) -> None:
        x = Krita.instance().readSetting("", "blenderKritaSettings", "")
        Settings.instance = self
        logger.debug("Read settings raw string: %s", x)
        if not x:
            Settings.instance.data = {"listenCanvas": True}
            Krita.instance().writeSetting(
                "", "blenderKritaSettings", json.dumps(Settings.instance.data)
            )
        else:
            Settings.instance.data = json.loads(x)

    def save_settings():
        settings = Settings.instance.data
        logger.debug("Saving settings dict: %s", settings)
        if not settings:
            settings = {"listenCanvas": True}
        Krita.instance().writeSetting("", "blenderKritaSettings", json.dumps(settings))

    def getSetting(name: str):
        settings = Settings.instance.data
        if name in settings:
            return settings[name]
        else:
            return None

    def setSetting(name: str, value):
        settings = Settings.instance.data
        settings[name] = value
        Krita.instance().writeSetting("", "blenderKritaSettings", json.dumps(settings))


Settings()
