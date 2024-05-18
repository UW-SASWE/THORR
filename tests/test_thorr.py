from context import thorr
from thorr.utils import config as cfg
import os

# test reading the configuration file
def test_read_config(config_file="tests/data/thorr_config.ini", required_sections=[]):

    config = cfg.read_config(config_file, required_sections)

    assert config.keys() == {'mysql', 'project', 'data', 'ee'}, "Error in reading configuration file"

test_read_config()