import os
import configparser

class Config(object):
    def __init__(self, config_file="dashboard.conf"):
        self.config = configparser.RawConfigParser()
        # Locates and opens the config.
        # First from the CONFIG_DIR
        # Second from the config_file input param
        # Defaults to dashboard.conf
        self.config.read(os.getenv('CONFIG_PATH', config_file))

    def get_string_value(self, section, config):
        value = os.getenv(f"{section}_{config}".upper(), None)
        if value is None:
            value = self.config.get(section, config)
        return value

    def get_int_value(self, section, config):
        return int(self.get_string_value(section, config))
