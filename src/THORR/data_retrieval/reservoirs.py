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

def validate_start_end_dates(start_date, end_date):
    """
    Validate start and end dates

    Parameters:
    -----------
    start_date: str
        start date
    end_date: str
        end date

    Returns:
    --------
    tuple
        start and end dates
    """
    
    # get today's date
    today = datetime.datetime.today()


    # convert start and end dates to datetime objects
    if end_date is None:
        end_date_ = today
        print(f"End date is set to {end_date_}")
    else:
        end_date_ = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if end_date_ > today:
            end_date_ = today
            print(f"End date is set to {end_date_}")    

    if start_date is None:
        start_date_ = end_date_ - datetime.timedelta(days=90)
        print(f"Start date is set to {start_date_}")
    else:
        start_date_ = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    # check if start date is greater than end date
    if start_date_ > end_date_:
        start_date_ = end_date_ - datetime.timedelta(days=90)
        print(f"Start date is set to {start_date_}")
        # raise Exception("Start date cannot be greater than end date!")

    # check if start date is greater than today's date
    if start_date_ > today:
        raise Exception("Start date cannot be greater than today's date!")

    # check if end date is greater than today's date
    if end_date_ > today:
        raise Exception("End date cannot be greater than today's date!")

    # format dates as strings
    start_date = start_date_.strftime("%Y-%m-%d")
    end_date = end_date_.strftime("%Y-%m-%d")

    return start_date, end_date

def get_reservoir_data(
    reservoirs_shp,
    # temperature_gauges_shp,
    # startDate,
    # endDate,
    # ndwi_threshold=0.2,
    # imageCollection="LANDSAT/LC08/C02/T1_L2",
):
    ee.Initialize()

    reservoirs = geemap.shp_to_ee(reservoirs_shp)

    print("Test okay")



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

    reservoirs_shp = Path(project_dir, config_dict["data"]["reservoirs_shp"])
    data_dir = Path(project_dir, "Data/GEE")
    os.makedirs(data_dir / "reservoirs", exist_ok=True)

    # get start date from config file
    if "start_date" not in config_dict["project"] or not config_dict["project"][
        "start_date"
    ]:
        start_date = None
    else:
        start_date = config_dict["project"]["start_date"]

    # get end date from config file
    if "end_date" not in config_dict["project"] or not config_dict["project"][
        "end_date"
    ]:
        end_date = None
    else:
        end_date = config_dict["project"]["end_date"]

    # TODO: check the validity of the start and end dates. For example, if the start date is greater than the end date, then raise an exception. if the start date is greater than today's date, then raise an exception. If the end date is greater than today's date, then make it today's date.
    
    # validate start and end dates
    start_date, end_date = validate_start_end_dates(start_date, end_date)

    print(start_date, end_date)

    # start_date = config_dict["project"]["start_date"]
    # print(start_date)

    get_reservoir_data(
        reservoirs_shp=reservoirs_shp,
        # temperature_gauges_shp=temperature_gauges_shp,
        # startDate=startDate,
        # endDate=endDate,
        # ndwi_threshold=ndwi_threshold,
        # imageCollection=imageCollection,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, help="path to config file", required=True)

    main(args=parser.parse_args())
