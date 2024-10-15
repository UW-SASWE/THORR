from context import thorr
from thorr.utils import config as cfg
from thorr.utils import database
from thorr.utils import logger
import os


# test reading the configuration file
def test_read_config(config_file="tests/data/thorr_config.ini", required_sections=[]):

    config = cfg.read_config(config_file, required_sections)

    assert config.keys() == {
        "mysql",
        "project",
        "data",
        "ee",
    }, "Error in reading configuration file"


test_read_config()


# test connecting to the database
def test_db_connection(config_file="tests/data/thorr_config.ini", section=["mysql"]):
    config = cfg.read_config(config_path=config_file, required_sections=section)

    db_config_path = config[section[0]]["db_config_path"]

    db = database.Connect(config_file=db_config_path, section=section[0])

    assert db.connection.is_connected(), "Error in connecting to the database"


test_db_connection(config_file=".env/config/thorr_config.ini")


# test logging
def test_logging(config_file="tests/data/thorr_config.ini"):
    config = cfg.read_config(config_path=config_file)

    log = logger.Logger(
        project_title=config["project"]["title"], log_dir="tests"
    ).get_logger()

    log.info("Testing logging")

    assert os.path.exists(log.log_file), "Error in logging"


test_logging()
