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
# import HydroErr as he
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
def get_db_connection(package_dir, db_config_path, logger=None, return_conn=False):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    from sql import connect  # utility functions for connecting to MySQL

    conn = connect.Connect(Path(db_config_path), logger=logger)
    connection = conn.conn

    if return_conn:
        return conn
    else:
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
    end_date_ = first_day_of_next_month - datetime.timedelta(
        days=first_day_of_next_month.day
    )

    # format dates as strings
    start_date = start_date_.strftime("%Y-%m-%d")
    end_date = end_date_.strftime("%Y-%m-%d")

    return start_date, end_date


def estimate_temperature(
    start_date,
    end_date,
    connection,
    scalers,  # path to scaler
    model_var1,  # path to model variation 1
    model_var2,  # path to model variation 2
    reaches_and_dams,  # path to reaches and dams csv file
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
        WHERE ReachLandsatWaterTemp.Date > "{start_date}" and ReachLandsatWaterTemp.Date < "{end_date}"
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

    df["Date"] = pd.to_datetime(df["Date"])
    df["DayOfYear"] = df["Date"].dt.dayofyear

    # TODO: add reservoir dynamics data. This will require a join with the reservoir dynamics table. Generate data from RAT.

    # dels = pd.read_csv(proj_dir / "Methods/3.WaterTempEst/rat_dels.csv")
    # dels["Date"] = pd.to_datetime(dels["Date"])
    # sarea = pd.read_csv(proj_dir / "Methods/3.WaterTempEst/rat_sarea.csv")
    # sarea["Date"] = pd.to_datetime(sarea["Date"])
    reaches_and_dams = pd.read_csv(reaches_and_dams)

    # load scalers and model variation 1
    with open(scalers, "rb") as f:
        scalers = pickle.load(f)

        dayofmonth_scaler = scalers["dayofmonth_scaler"]
        month_scaler = scalers["month_scaler"]
        watertemp_scaler = scalers["watertemp_scaler"]
        landtemp_scaler = scalers["landtemp_scaler"]
        width_scaler = scalers["width_scaler"]
        NDVI_scaler = scalers["NDVI_scaler"]
        climate_scaler = scalers["climate_scaler"]
        dels_scaler = scalers["dels_scaler"]
        sarea_scaler = scalers["sarea_scaler"]
        rel_dist_scaler = scalers["rel_dist_scaler"]

    with open(model_var1, "rb") as f:
        model_var1_trained = pickle.load(f)  # trained model variation 1

    # replace missing values for dels, sarea, and rel_dist with the 0
    # df["dels"].fillna(0, inplace=True)
    # df["sarea"].fillna(0, inplace=True)
    # df["rel_dist"].fillna(0, inplace=True)

    # Scale values
    df["DayOfMonth_scaled"] = dayofmonth_scaler.transform(df[["DayOfMonth"]])
    df["Month_scaled"] = month_scaler.transform(df[["Month"]])
    df["LandTemp_scaled"] = landtemp_scaler.transform(df[["LandTemp"]])
    df["WaterTemp_scaled"] = watertemp_scaler.transform(df[["WaterTemp"]])
    df["Width_scaled"] = width_scaler.transform(df[["Width"]])
    df["NDVI_scaled"] = NDVI_scaler.transform(df[["NDVI"]])
    df["ClimateClass_scaled"] = climate_scaler.transform(df[["ClimateClass"]])
    # df["dels_scaled"] = dels_scaler.transform(df[["dels"]])
    # df["sarea_scaled"] = sarea_scaler.transform(df[["sarea"]])
    # df["rel_dist_scaled"] = rel_dist_scaler.transform(df[["rel_dist"]])

    # X and y to be used for prediction
    X = df[
        [
            "DayOfMonth_scaled",
            "Month_scaled",
            "LandTemp_scaled",
            "Width_scaled",
            "NDVI_scaled",
            "ClimateClass_scaled",
            # "dels_scaled",
            # "sarea_scaled",
            # "rel_dist_scaled",
        ]
    ]
    df["est1"] = model_var1_trained.predict(X)
    df.sort_values(by=['ReachID', 'Date'], inplace=True)

    # insert estimates into database
    cursor = connection.conn.cursor()

    # done = []
    for i, row in df.iterrows():
        query = f"""
        INSERT INTO ReachEstimatedWaterTemp (Date, ReachID, Value, Tag)
        SELECT '{row['Date'].date()}', (SELECT ReachID FROM Reaches WHERE ReachID = {row['ReachID']}), {row['est1']}, "SM"
        WHERE NOT EXISTS (SELECT * FROM ReachEstimatedWaterTemp WHERE Date = '{row['Date'].date()}' AND ReachID = {row['ReachID']}  AND Tag = "SM");
        """

        # print(query)
        # break

        cursor.execute(query)
        connection.conn.commit()

        query = f"""
        UPDATE ReachEstimatedWaterTemp
        SET Value = {row['est1']}
        WHERE Date = '{row['Date']}' AND ReachID = {row['ReachID']} AND Tag = "SM";
        """

        cursor.execute(query)
        connection.conn.commit()

        # print(row['ReachID'], row['Date'])
        # if i not in done:
        #     done.append(i)
        #     print(row['ReachID'], "complete")

        # break

    #TODO: add model variation 2

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
        logger_format="%(asctime)s - %(name)s - reach-temperature-est - %(levelname)s - %(message)s",
    )

    # get database connection
    connection = get_db_connection(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        db_config_path=db_config_path,  # db_config_path
        logger=logger,
        return_conn=True,
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

    estimate_temperature(
        start_date=start_date,
        end_date=end_date,
        connection=connection,
        scalers=Path(project_dir, config_dict["ml"]["scalers"]),
        model_var1=Path(project_dir, config_dict["ml"]["model_var1"]),
        model_var2=Path(project_dir, config_dict["ml"]["model_var2"]),
        reaches_and_dams=Path(project_dir, config_dict["data"]["reaches_and_dams"]),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, help="path to config file", required=True
    )

    main(args=parser.parse_args())
