# from context import thorr
from thorr.utils import config as cfg
from thorr.utils import database
from thorr.utils import logger
from thorr.data import retrieval
import os


# test reading the configuration file
def test_read_config(config_file="tests/data/thorr_config.ini", required_sections=[]):

    config = cfg.read_config(config_file, required_sections)

    assert config.keys() == {
        "mysql",
        "postgresql",
        "project",
        "data",
        "data.geopackage_layers",
        "ee",
        "ml",
    }, "Error in reading configuration file"

    # print(config.keys())
    print("Config file read successfully")

test_read_config()


# # test connecting to the database
# def test_db_connection(
#     config_file="tests/data/thorr_config.ini", section=["mysql"], db_type="mysql"
# ):
#     config = cfg.read_config(config_path=config_file, required_sections=section)

#     db_config_path = config[section[0]]["db_config_path"]

#     db = database.Connect(
#         config_file=db_config_path, section=section[0], db_type=db_type
#     )

#     if db_type == "mysql":
#         assert db.connection.is_connected(), "Error in connecting to the database"
#     elif db_type == "postgresql":
#         assert not db.connection.closed, "Error in connecting to the database"


# test_db_connection(
#     config_file="tests/data/thorr_config.ini",
#     section=["postgresql"],
#     db_type="postgresql",
# )


# def test_db_setup(
#     config_file="tests/data/thorr_config.ini",
#     section=["mysql"],
#     db_type="mysql",
#     db_name="thorr",
# ):
#     config = cfg.read_config(config_path=config_file, required_sections=section)

#     db_config_path = config[section[0]]["db_config_path"]
#     try:
#         database.db_setup(db_config_path, section=section[0], db_type=db_type)
#     except Exception as e:
#         print(e)


# # test_db_setup(section=["postgresql"], db_type="postgresql")


# def test_data_upload(
#     config_file="tests/data/thorr_config.ini",
#     db_type="postgresql",
#     db_name="thorr_pkg_test",
# ):
#     config = cfg.read_config(config_path=config_file)

#     if db_type == "mysql":
#         db_config_path = config["mysql"]["db_config_path"]
#     elif db_type == "postgresql":
#         db_config_path = config["postgresql"]["db_config_path"]
#     # print(config["data"])
#     data_paths = config["data"]
#     geopakage_layers = config["data.geopackage_layers"]

#     try:
#         database.upload_gis(db_config_path, data_paths, gpkg_layers=geopakage_layers, db_type=db_type)
#     except Exception as e:
#         print(e)


# test_data_upload(
#     config_file="tests/data/thorr_config.ini", db_type="postgresql", db_name="thorr"
# )


# # test logging
# def test_logging(config_file="tests/data/thorr_config.ini"):
#     config = cfg.read_config(config_path=config_file)

#     log = logger.Logger(
#         project_title=config["project"]["title"], log_dir="tests"
#     ).get_logger()

#     log.info("Testing logging")

#     assert os.path.exists(log.log_file), "Error in logging"


# # test_logging()

# # # test_retrieval - reservoirs
# # retrieval.init_retrieval(config=".env/config/thorr_config.ini", db_type="postgresql", element="reach")
