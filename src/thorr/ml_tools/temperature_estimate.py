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
            LEFT JOIN THORR."Reaches" USING ("ReachID")
        WHERE
            "LandTempC" IS NOT NULL
            AND "NDVI" IS NOT NULL
            AND "EstTempC" IS NULL;
        """


        # fetch the data into a dataframe as df
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
            print(df.head())

    # create a DOY column
    # fill na values of the mean width values with 15
    # define features
    # load model_fn
    # estimate models
    # upload estimates to the database

    # if element == "reach":


def main(args):
    config_path = Path(args.config)
    db_type = args.db_type
    estimate_temperature(config_path, db_type=db_type, element=args.element)
    pass


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