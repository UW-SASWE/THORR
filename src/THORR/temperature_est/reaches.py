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


from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import (
    KFold,
    ShuffleSplit,
    RepeatedKFold,
    train_test_split,
    GridSearchCV,
)
from sklearn.linear_model import ElasticNetCV, ElasticNet
from sklearn.ensemble import RandomForestRegressor

import numpy as np
# from datetime import datetime, date, timedelta
import datetime

# import matplotlib.pyplot as plt

# import tensorflow as tf
import HydroErr as he
import pickle

# TODO: use the utils package to read the configuration file
from configparser import ConfigParser


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
def get_db_connection(package_dir, db_config_path, logger=None):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    from sql import connect  # utility functions for connecting to MySQL

    conn = connect.Connect(Path(db_config_path), logger=logger)
    connection = conn.conn

    return connection


def get_logger(
    package_dir,
    project_title,
    log_dir,
    logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    import logger

    logger = logger.Logger(
        project_title=project_title, log_dir=log_dir, logger_format=logger_format
    ).get_logger()

    return logger

def validate_start_end_dates(start_date, end_date, logger=None):
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
        if logger is not None:
            logger.info(f"End date is set to {end_date_}")
        else:
            print(f"End date is set to {end_date_}")
    else:
        end_date_ = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if end_date_ > today:
            end_date_ = today
            if logger is not None:
                logger.info(f"End date is set to {end_date_}")
            else:
                print(f"End date is set to {end_date_}")

    if start_date is None:
        start_date_ = end_date_ - datetime.timedelta(days=90)
        if logger is not None:
            logger.info(f"Start date is set to {start_date_}")
        else:
            print(f"Start date is set to {start_date_}")
    else:
        start_date_ = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    # check if start date is greater than end date
    if start_date_ > end_date_:
        start_date_ = end_date_ - datetime.timedelta(days=90)
        if logger is not None:
            logger.info(f"Start date is set to {start_date_}")
        else:
            print(f"Start date is set to {start_date_}")
        # raise Exception("Start date cannot be greater than end date!")

    # check if start date is greater than today's date
    if start_date_ > today:
        if logger is not None:
            logger.error("Start date cannot be greater than today's date!")
        else:
            print("Start date cannot be greater than today's date!")
        raise Exception("Start date cannot be greater than today's date!")

    # check if end date is greater than today's date
    if end_date_ > today:
        if logger is not None:
            logger.error("End date cannot be greater than today's date!")
        else:
            print("End date cannot be greater than today's date!")
        raise Exception("End date cannot be greater than today's date!")
    
    # convert the start date to the first day of the month
    start_date_ = start_date_.replace(day=1)

    # convert the end date to the last day of the month
    first_day_of_next_month = end_date_.replace(day=28) + datetime.timedelta(days=4)
    end_date_ = first_day_of_next_month - datetime.timedelta(days=first_day_of_next_month.day)

    # format dates as strings
    start_date = start_date_.strftime("%Y-%m-%d")
    end_date = end_date_.strftime("%Y-%m-%d")

    return start_date, end_date

def estimate_temperature(
        start_date,
        end_date,
        connection,
):
    query = f"""
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(Month, 2, '00'),
                        '-',
                        LPAD(DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        Month,
        DayOfMonth,
        ROUND(WaterTemp, 2) as WaterTemp,
        ROUND(LandTemp, 2) as LandTemp,
        ROUND(NDVI, 2) as NDVI,
        ClimateClass,
        --     ROUND(((watertemp - WaterTemperature) / WaterTemperature),
        --             2) AS PercentDeviation,
        --     ROUND((watertemp - WaterTemperature), 2) AS Deviation,
        Width,
        ReachID,
        ReachName
        -- ROUND(InsituTemp, 2) AS InsituTemp
    FROM
        (SELECT 
            IF(DAY(ReachLandsatWaterTemp.date) < 15, 1, 15) AS DayOfMonth,
                MONTH(ReachLandsatWaterTemp.date) AS Month,
                YEAR(ReachLandsatWaterTemp.date) AS Year,
                AVG(ReachLandsatWaterTemp.Value) AS WaterTemp,
                AVG(ReachLandsatLandTemp.Value) AS LandTemp,
                AVG(ReachNDVI.Value) AS NDVI,
                IFNULL(Reaches.WidthMean, 30) AS Width,
                Reaches.ClimateClass AS ClimateClass,
                ReachLandsatWaterTemp.ReachID AS ReachID,
                Reaches.Name AS ReachName
        FROM
            ReachLandsatWaterTemp
        INNER JOIN ReachLandsatLandTemp USING (date , ReachID)
        INNER JOIN ReachNDVI USING (date , ReachID)
        INNER JOIN Reaches USING (ReachID)
        WHERE ReachLandsatWaterTemp.Date > {start_date} and ReachLandsatWaterTemp.Date < {end_date}
        GROUP BY DayOfMonth , Month , Year , ClimateClass , ReachID , Width) AS T
    --     --         INNER JOIN
    --     --     ReachLandsatLTMSemiMonthly USING (DayOfMonth , Month , ReachID)
    --         LEFT JOIN
    --     (SELECT 
    --         IF(DAY(ReachInsituWaterTemp.date) < 15, 1, 15) AS DayOfMonth,
    --             MONTH(ReachInsituWaterTemp.date) AS Month,
    --             YEAR(ReachInsituWaterTemp.date) AS Year,
    --             AVG(ReachInsituWaterTemp.Value) AS InsituTemp,
    --             ReachInsituWaterTemp.ReachID AS ReachID
    --     FROM
    --         ReachInsituWaterTemp
    --     INNER JOIN Reaches USING (ReachID)
    --     WHERE
    --         ReachInsituWaterTemp.Value > 0
    --     GROUP BY DayOfMonth , Month , Year , ReachID) AS I USING (DayOfMonth , Month , Year , ReachID)
    -- ORDER BY RAND();
    """



    df = connection.query_with_fetchmany(query, chunksize=100)

    pass


def main(args):
    config_path = Path(args.config)
    config_dict = read_config(
        config_path,
        # required_sections=["project", "mysql", "data", "ee"]
    )

    project_dir = Path(config_dict["project"]["project_dir"])
    db_config_path = project_dir / config_dict["mysql"]["db_config_path"]

    ee_credentials = {
        "service_account": config_dict["ee"]["service_account"],
        "private_key_path": config_dict["ee"]["private_key_path"],
    }

    logger = get_logger(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        project_title=config_dict["project"]["title"],
        log_dir=Path(project_dir, "logs"),
        logger_format="%(asctime)s - %(name)s - reaches - %(levelname)s - %(message)s",
    )

    # get database connection
    connection = get_db_connection(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        db_config_path=db_config_path,  # db_config_path
        logger=logger,
    )

    reaches_shp = Path(project_dir, config_dict["data"]["reaches_shp"])
    data_dir = Path(project_dir, "Data/GEE")
    os.makedirs(data_dir / "reaches", exist_ok=True)

    # get start date from config file
    if (
        "start_date" not in config_dict["project"]
        or not config_dict["project"]["start_date"]
    ):
        start_date = None
    else:
        start_date = config_dict["project"]["start_date"]

    # get end date from config file
    if (
        "end_date" not in config_dict["project"]
        or not config_dict["project"]["end_date"]
    ):
        end_date = None
    else:
        end_date = config_dict["project"]["end_date"]

    # TODO: check the validity of the start and end dates. For example, if the start date is greater than the end date, then raise an exception. if the start date is greater than today's date, then raise an exception. If the end date is greater than today's date, then make it today's date.

    # validate start and end dates
    start_date, end_date = validate_start_end_dates(start_date, end_date, logger=logger)

    # print(start_date, end_date)

    # start_date = config_dict["project"]["start_date"]
    # print(start_date)

    # logger.info("Getting reservoir data...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, help="path to config file", required=True
    )

    main(args=parser.parse_args())