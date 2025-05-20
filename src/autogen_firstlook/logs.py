import logging

from autogen_firstlook.settings import Settings

CUSTOM_LOGGER_NAME = "autogen_firstlook"

logger = logging.getLogger(CUSTOM_LOGGER_NAME)


def config_logs(settings: Settings):
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(settings.log_level)
