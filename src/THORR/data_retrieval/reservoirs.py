# TODO: Add docstring

import argparse
import sys
import geemap
import ee
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import os
from pathlib import Path
import time
from random import randint
import json
import datetime


# TODO: use the utils package to read the configuration file

def read_config(config_path, required_sections=[]):
    """
    Read configuration file

    Parameters:
    -----------
    config_path: str
        path to configuration file
    required_sections: list
        list of required sections in the configuration file

    Returns:
    --------
    dict
        dictionary of configuration parameters
    """

    config = ConfigParser()
    config.read(config_path)

    if required_sections:
        for section in required_sections:
            if section not in config.sections():
                raise Exception(
                    f"Section {section} not found in the {config_path} file"
                )
        # create a dictionary of parameters
        config_dict = {
            section: dict(config.items(section)) for section in required_sections
        }
    else:
        config_dict = {
            section: dict(config.items(section)) for section in config.sections()
        }

    return config_dict

# import connect
# TODO: convert this to a function in the utils package
def get_db_connection(package_dir, db_config_path):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    from sql import connect  # utility functions for connecting to MySQL

    conn = connect.Connect(Path(db_config_path))
    connection = conn.conn

    return connection

def main(args):
    config_path = Path(args.cfg)
    config_dict = read_config(
        config_path, required_sections=["project", "mysql", "data"]
    )

    project_dir = Path(config_dict["project"]["project_dir"])
    db_config_path = project_dir / config_dict["mysql"]["db_config_path"]

    # get database connection
    connection = get_db_connection(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        db_config_path=db_config_path,  # db_config_path
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, help="path to config file", required=True)

    main(args=parser.parse_args())
