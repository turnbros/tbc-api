import os
import configparser

default_config_file="dashboard.conf"
config_parser = configparser.RawConfigParser()
config_parser.read(os.getenv('CONFIG_PATH', default_config_file))

def get_string_value(section, config):
    value = os.getenv(f"{section}_{config}".upper(), None)
    if value is None:
        value = config_parser.get(section, config)
    return value

def get_int_value(section, config):
    return int(get_string_value(section, config))
