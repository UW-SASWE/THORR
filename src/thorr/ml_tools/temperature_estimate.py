# TODO: Add docstring

import argparse
import sys
import geemap
import ee
import pandas as pd
import geopandas as gpd
import os
from pathlib import Path
import time
from random import randint
import json
import datetime

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import json
import sys

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, mean_squared_error, r2_score

from sklearn.model_selection import (
    KFold,
    ShuffleSplit,
    RepeatedKFold,
    train_test_split,
    ParameterGrid,
)
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import ElasticNetCV, ElasticNet

from joblib import dump, load

from permetrics.regression import RegressionMetric
import os

from thorr.utils import config as cfg
from thorr.utils import database
from thorr.utils import logger
from thorr.utils.misc import validate_start_end_dates


def estimate_temperature(config_path, db_type="postgresql", element="reach"):
    config_path = Path(config_path)
    config_dict = cfg.read_config(config_path)

    project_dir = Path(config_dict["project"]["project_dir"])
    db_config_path = project_dir / config_dict[db_type]["db_config_path"]

    log = logger.Logger(
        project_title=config_dict["project"]["title"], log_dir="tests"
    ).get_logger()


    db = database.Connect(db_config_path, db_type=db_type)

    model_fn = project_dir / config_dict["ml"]["model_fn"]

    connection = db.connection

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

    # validate start and end dates
    start_date, end_date = validate_start_end_dates(start_date, end_date, logger=log)
    
    # define a query to fetch the data from the database
    # make date pd datetime format
    if db_type == "postgresql":
        schema = db.schema
        query = f"""
        SELECT
            "ReachID",
            "Date",
            "LandTempC",
            "WaterTempC",
            "NDVI",
            "Mission",
            "WidthMean",
            "Name",
            "ClimateClass",
            "EstTempC"
        FROM
            {schema}."ReachData"
            LEFT JOIN {schema}."Reaches" USING ("ReachID")
        WHERE
            "LandTempC" IS NOT NULL
            AND "NDVI" IS NOT NULL
            AND "Date" >= '{start_date}'
            AND "Date" <= '{end_date}';
        """


        # fetch the data into a dataframe as df
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
            df["Date"] = pd.to_datetime(df["Date"])

    # create a DOY column
    df["DOY"] = df["Date"].dt.dayofyear
    # fill na values of the mean width values with 15
    df[["WidthMean"]] = df[["WidthMean"]].fillna(15)
    # define features
    features = [
        "NDVI",
        "LandTempC",
        "ClimateClass",
        "DOY",
        "WidthMean",
    ]
    
    # load model_fn
    rfr = load(model_fn)
    # estimate models
    df['EstTempC'] = rfr.predict(df[features])
    
    # upload estimates to the database
    if db_type == "postgresql":
        if element == "reach":
            for i, row in df.iterrows():
                # if i % 10000 == 0:
                #     print(f"Processing row {i} of {len(df)}")
                
                query = f"""
                UPDATE {schema}."ReachData"
                SET
                    "EstTempC" = {round(row['EstTempC'], 2)}
                WHERE
                    (
                        "ReachID" = (
                            SELECT
                                "ReachID"
                            FROM
                                {schema}."Reaches"
                            WHERE
                                "Name" = '{row['Name']}'
                        )
                    )
                    AND ("Date" = '{row['Date']}')
                    AND ("EstTempC" IS NULL);
                """
                print(query)
                break
                
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

        elif element == "reservoir":
            pass
    elif db_type == "mysql":
        pass

    log.info("Temperature estimates have been successfully uploaded to the database.")


def main(args):
    config_path = Path(args.config)
    db_type = args.db_type
    estimate_temperature(config_path, db_type=db_type, element=args.element)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, help="path to config file", required=True
    )
    parser.add_argument(
        "-db",
        "--db_type",
        default="mysql",
        type=str,
        help="type of database: either 'mysql' or 'postgresql'",
        required=False,
    )
    parser.add_argument(
        "-e",
        "--element",
        type=str,
        default="reach",
        help="element to retrieve data for: reach or reservoir",
        required=False,
    )

    main(args=parser.parse_args())
