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


from thorr.utils import config as cfg
from thorr.utils import database
from thorr.utils import logger

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


def divideDates(startDate, endDate):
    """
    Divide the timeframe into years

    Parameters:
    -----------
    startDate: str
        start date
    endDate: str
        end date

    Returns:
    --------
    list
        list of tuples of start and end dates
    """

    # convert start and end dates to datetime objects
    startDate_ = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    endDate_ = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    # get years from start and end dates
    # startYear = pd.to_datetime(startDate).year
    # endYear = pd.to_datetime(endDate).year
    startYear = startDate_.year
    endYear = endDate_.year

    # divide the timeframe into years
    dates = []
    for year in range(startYear, endYear + 1):
        if year == startYear and year == endYear:
            dates.append([startDate, endDate])
        elif year == startYear:
            dates.append([startDate, f"{year}-12-31"])
        elif year == endYear:
            # if the difference end date and start of the year is less than 30 days, then replace the end date of the previous append with the end date
            # the purpose of this is to avoid having a date range of less than 30 days (especially at the beginning of the last year)
            if (endDate_ - datetime.datetime(year, 1, 1)).days < 45:
                dates[-1][1] = endDate
            else:
                dates.append([f"{year}-01-01", endDate])
        else:
            dates.append([f"{year}-01-01", f"{year}-12-31"])

    return dates


def prepL8(image):
    """
    Prepare Landsat 8 image for analysis

    Parameters:
    -----------
    image: ee.Image
        Landsat 8 image

    Returns:
    --------
    ee.Image
        prepared Landsat 8 image
    """

    # develop masks for unwanted pixels (fill, cloud, shadow)
    qa_mask = image.select("QA_PIXEL").bitwiseAnd(int("11111", 2)).eq(0)
    saturation_mask = image.select("QA_RADSAT").eq(0)

    # apply scaling factors to the appropriate bands
    def getFactorImage(factorNames):
        factorList = image.toDictionary().select(factorNames).values()
        return ee.Image.constant(factorList)

    scaleImg = getFactorImage(["REFLECTANCE_MULT_BAND_.|TEMPERATURE_MULT_BAND_ST_B10"])
    offsetImg = getFactorImage(["REFLECTANCE_ADD_BAND_.|TEMPERATURE_ADD_BAND_ST_B10"])
    scaled = image.select("SR_B.|ST_B10").multiply(scaleImg).add(offsetImg)

    # replace original bands with scaled bands and apply masks
    return (
        image.addBands(scaled, overwrite=True)
        .updateMask(qa_mask)
        .updateMask(saturation_mask)
    )


def addNDVI(image):
    """
    Add NDVI band to image

    Parameters:
    -----------
    image: ee.Image
        Landsat 8 image

    Returns:
    --------
    ee.Image
        Landsat 8 image with NDVI band
    """

    # ndvi = image.expression(
    #     "NDVI = (NIR - red)/(NIR + red)",
    #     {"red": image.select("SR_B4"), "NIR": image.select("SR_B5")},
    # ).rename("NDVI")

    ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

    return image.addBands(ndvi)


def addCelcius(image):
    """
    Add Celcius band to image

    Parameters:
    -----------
    image: ee.Image
        Landsat 8 image

    Returns:
    --------
    ee.Image
        Landsat 8 image with Celcius band
    """
    celcius = image.select("ST_B10").subtract(273.15).rename("Celcius")

    return image.addBands(celcius)


def prepL4(image):

    # develop masks for unwanted pixels (fill, cloud, shadow)
    qa_mask = image.select("QA_PIXEL").bitwiseAnd(int("11111", 2)).eq(0)
    saturation_mask = image.select("QA_RADSAT").eq(0)

    # apply scaling factors to the appropriate bands
    opticalBands = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermalBand = image.select("ST_B6").multiply(0.00341802).add(149.0)

    # replace original bands with scaled bands and apply masks
    return (
        image.addBands(opticalBands, overwrite=True)
        .addBands(thermalBand, overwrite=True)
        .updateMask(qa_mask)
        .updateMask(saturation_mask)
    )


def addL4NDVI(image):

    # ndvi = image.expression(
    #     "NDVI = (NIR - red)/(NIR + red)",
    #     {"red": image.select("SR_B4"), "NIR": image.select("SR_B5")},
    # ).rename("NDVI")

    ndvi = image.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")

    return image.addBands(ndvi)


def addL4Celcius(image):
    celcius = image.select("ST_B6").subtract(273.15).rename("Celcius")

    return image.addBands(celcius)


def extractTempSeries(
    element,
    startDate,
    endDate,
    # ndwi_threshold=0.2,
    imageCollection="LANDSAT/LC08/C02/T1_L2",
    logger=None,
    element_type="dam"
):
    """
    Extract temperature time series for a reservoir

    Parameters:
    -----------
    reservoir: ee.Feature
        reservoir
    startDate: str
        start date
    endDate: str
        end date

    Returns:
    --------
    ee.ImageCollection
        temperature time series
    """

    L8 = (
        ee.ImageCollection(imageCollection)
        .filterDate(startDate, endDate)
        .filterBounds(element)
    )

    def extractData(date):
        date = ee.Date(date)
        # prepare Landsat 8 image and add the NDWI band, and Celcius band
        processedL8 = (
            L8.filterDate(date, date.advance(1, "day"))
            .map(prepL8)
            .map(addCelcius)
            .map(addNDVI)
            # .map(addNDWI)
        )

        # get quality NDWI and use it as the water mask
        # ndwi = processedL8.qualityMosaic("NDWI").select("NDWI")
        # waterMaskNdwi = ndwi.gte(ndwi_threshold)
        # nonWaterMask = ndwi.lt(ndwi_threshold)

        mosaic = processedL8.mosaic()
        waterMask = mosaic.select("QA_PIXEL").bitwiseAnd(int("10000000", 2)).neq(0)
        nonWaterMask = mosaic.select("QA_PIXEL").bitwiseAnd(int("10000000", 2)).eq(0)

        # find the mean of the images in the collection
        meanL8water = (
            processedL8.reduce(ee.Reducer.mean())
            # .addBands(ndwi, ["NDWI"], True)
            .updateMask(waterMask).set("system:time_start", date)
        ).clip(element.geometry())
        # meanL8nonwater = (
        #     processedL8.reduce(ee.Reducer.mean())
        #     # .addBands(ndwi, ["NDWI"], True)
        #     .updateMask(nonWaterMask).set("system:time_start", date)
        # )

        # get the mean temperature of the reache
        watertemp = meanL8water.select(["Celcius_mean"]).reduceRegion(
            reducer=ee.Reducer.median(),
            # reducer=ee.Reducer.mean(),
            geometry=element.geometry(),
            scale=30,
        )
        if element_type == "reach":
            meanL8nonwater = (
                processedL8.reduce(ee.Reducer.mean())
                # .addBands(ndwi, ["NDWI"], True)
                .updateMask(nonWaterMask).set("system:time_start", date)
            )
            landtemp = meanL8nonwater.select(["Celcius_mean"]).reduceRegion(
                reducer=ee.Reducer.median(),
                # reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )
            ndvi = meanL8nonwater.select(["NDVI_mean"]).reduceRegion(
                reducer=ee.Reducer.median(),
                # reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )

        if element_type == "dam":
            return ee.Feature(
                None,
                {
                    "date": date.format("YYYY-MM-dd"),
                    "watertemp(C)": watertemp,
                    # "landtemp(C)": landtemp,
                    # "NDVI": ndvi,
                },
            )
        elif element_type == "reach":
            return ee.Feature(
                None,
                {
                    "date": date.format("YYYY-MM-dd"),
                    "watertemp(C)": watertemp,
                    "landtemp(C)": landtemp,
                    "NDVI": ndvi,
                },
            )

    try:
        dates = ee.List(
            L8.map(
                lambda image: ee.Feature(
                    None, {"date": image.date().format("YYYY-MM-dd")}
                )
            )
            .distinct("date")
            .aggregate_array("date")
        )

        dataSeries = ee.FeatureCollection(dates.map(extractData))
        # print(startDate, endDate)

        return dataSeries
    except Exception as e:
        # print(e, startDate, endDate)
        if logger is not None:
            logger.info(f"{e}")
        else:
            print(f"{e}")
        return None


def extractL4TempSeries(
    element,
    startDate,
    endDate,
    # ndwi_threshold=0.2,
    imageCollection="LANDSAT/LT04/C02/T1_L2",
    logger=None,
    element_type="dam",
):
    L4 = (
        ee.ImageCollection(imageCollection)
        .filterDate(startDate, endDate)
        .filterBounds(element)
        .filter(ee.Filter.eq("PROCESSING_LEVEL", "L2SP"))
    )

    def extractData(date):
        date = ee.Date(date)

        processedL4 = (
            L4.filterDate(date, date.advance(1, "day"))
            .map(prepL4)
            .map(addL4Celcius)
            .map(addL4NDVI)
        )

        mosaic = processedL4.mosaic()
        waterMask = mosaic.select("QA_PIXEL").bitwiseAnd(int("10000000", 2)).neq(0)
        nonWaterMask = mosaic.select("QA_PIXEL").bitwiseAnd(int("10000000", 2)).eq(0)

        # find the mean of the images in the collection
        meanL4water = (
            processedL4.reduce(ee.Reducer.mean())
            # .addBands(ndwi, ["NDWI"], True)
            .updateMask(waterMask).set("system:time_start", date)
        ).clip(element.geometry())
        # meanL4nonwater = (
        #     processedL4.reduce(ee.Reducer.mean())
        #     # .addBands(ndwi, ["NDWI"], True)
        #     .updateMask(nonWaterMask).set("system:time_start", date)
        # )

        # get the mean temperature of the reache
        watertemp = meanL4water.select(["Celcius_mean"]).reduceRegion(
            reducer=ee.Reducer.median(),
            # reducer=ee.Reducer.mean(),
            geometry=element.geometry(),
            scale=30,
        )
        if element_type == "reach":
            meanL4nonwater = (
                processedL4.reduce(ee.Reducer.mean())
                # .addBands(ndwi, ["NDWI"], True)
                .updateMask(nonWaterMask).set("system:time_start", date)
            )
            landtemp = meanL4nonwater.select(["Celcius_mean"]).reduceRegion(
                reducer=ee.Reducer.median(),
                # reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )
            ndvi = meanL4nonwater.select(["NDVI_mean"]).reduceRegion(
                reducer=ee.Reducer.median(),
                # reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )

        if element_type == "dam":
            return ee.Feature(
                None,
                {
                    "date": date.format("YYYY-MM-dd"),
                    "watertemp(C)": watertemp,
                    # "landtemp(C)": landtemp,
                    # "NDVI": ndvi,
                },
            )
        elif element_type == "reach":
            return ee.Feature(
                None,
                {
                    "date": date.format("YYYY-MM-dd"),
                    "watertemp(C)": watertemp,
                    "landtemp(C)": landtemp,
                    "NDVI": ndvi,
                },
            )

    try:

        # print("Breakpoint extractL4TempSeries 1")
        dates = ee.List(
            L4.map(
                lambda image: ee.Feature(
                    None, {"date": image.date().format("YYYY-MM-dd")}
                )
            )
            .distinct("date")
            .aggregate_array("date")
        )
        # print("Breakpoint extractL4TempSeries 2")
        dataSeries = ee.FeatureCollection(dates.map(extractData))
        # print(startDate, endDate, "No error")

        return dataSeries
    except Exception as e:
        # print('There was an error')
        if logger is not None:
            logger.info(f"{e}")
        else:
            print(f"{e}")
        return None


def ee_to_df(featureCollection):
    """
    Convert an ee.FeatureCollection to a pandas.DataFrame

    Parameters:
    -----------
    featureCollection: ee.FeatureCollection
        feature collection

    Returns:
    --------
    pandas.DataFrame
        dataframe
    """

    columns = featureCollection.first().propertyNames().getInfo()
    rows = (
        featureCollection.reduceColumns(ee.Reducer.toList(len(columns)), columns)
        .values()
        .get(0)
        .getInfo()
    )

    df = pd.DataFrame(rows, columns=columns)
    df.drop(columns=["system:index"], inplace=True)

    return df


def download_ee_csv(downloadUrl):
    """
    Download an ee.FeatureCollection as a csv file

    Parameters:
    -----------
    downloadUrl: str
        download url

    Returns:
    --------
    pandas.DataFrame
        dataframe
    """

    df = pd.read_csv(downloadUrl)
    df.drop(columns=["system:index", ".geo"], inplace=True)

    return df


def entryToDB(
    data,
    table_name,
    element_id,
    # connection=N,
    date_col="date",
    value_col="value",
    entry_key={
        "Date": None,
        "DamID": None,
        # "LandTempC": None,
        "WaterTempC": None,
        # "NDVI": None,
        "Mission": None,
    },
    db=None,
    db_type=None,
):
    # print('running entryToDB')
    data = data.copy()
    data[entry_key["Date"]] = pd.to_datetime(data[entry_key["Date"]])
    data = data[[value for value in entry_key.values() if value]]
    data = data.dropna(
        how="all",
        subset=[
            value
            for value in entry_key.values()
            if value not in [entry_key["Date"], entry_key["Mission"]]
        ],
    )
    # data = data[data[value_col] != -9999]
    data = data.sort_values(by=entry_key["Date"])


    connection = db.connection
    cursor = connection.cursor()

    if db_type == "mysql":
        if table_name == "DamData":
            element_id
            data = data.fillna("NULL")

            # data.to_csv('data.csv')
            # print(', '.join([str(value) for value in entry_key.values() if value!=entry_key['Date']]))

            for i, row in data.iterrows():
                # print(', '.join([str(row[value]) for value in entry_key.values() if value!=entry_key['Date']]))
                query = f"""
                INSERT INTO {table_name} (Date, DamID, {', '.join([str(key) for key in entry_key.keys() if key!='Date'])})
                SELECT '{row[entry_key['Date']]}', {element_id}, {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
                WHERE NOT EXISTS (SELECT * FROM {table_name} WHERE Date = '{row[entry_key['Date']]}' AND DamID = {element_id})
                """

                cursor.execute(query)
                connection.commit()
        elif table_name == "ReachData":
            data = data.fillna("NULL")

            # data.to_csv('data.csv')
            # print(', '.join([str(value) for value in entry_key.values() if value!=entry_key['Date']]))

            cursor = connection.cursor()

            for i, row in data.iterrows():
                # print(', '.join([str(row[value]) for value in entry_key.values() if value!=entry_key['Date']]))
                query = f"""
                INSERT INTO {table_name} (Date, ReachID, {', '.join([str(key) for key in entry_key.keys() if key!='Date'])})
                SELECT '{row[entry_key['Date']]}', {element_id}, {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
                WHERE NOT EXISTS (SELECT * FROM {table_name} WHERE Date = '{row[entry_key['Date']]}' AND ReachID = {element_id})
                """

                cursor.execute(query)
                connection.commit()
    elif db_type == "postgresql":
        schema = db.schema

        if table_name == "DamData":
            data = data.fillna("NULL")

            for i, row in data.iterrows():
                query = f"""
                INSERT INTO {schema}."{table_name}" ("Date", "DamID", {', '.join(['"'+str(key)+'"' for key in entry_key.keys() if key!='Date'])})
                SELECT CAST('{row[entry_key['Date']]}' AS date), '{element_id}', {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
                WHERE NOT EXISTS (SELECT * FROM {schema}."{table_name}" WHERE "Date" = CAST('{row[entry_key['Date']]}' AS date) AND "DamID" = {element_id})
                """

                # print(query)
                cursor.execute(query)
                connection.commit()
        elif table_name == "ReachData":
            data = data.fillna("NULL")

            for i, row in data.iterrows():
                query = f"""
                INSERT INTO {schema}."{table_name}" ("Date", "ReachID", {', '.join(['"'+str(key)+'"' for key in entry_key.keys() if key!='Date'])})
                SELECT CAST('{row[entry_key['Date']]}' AS date), '{element_id}', {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
                WHERE NOT EXISTS (SELECT * FROM {schema}."{table_name}" WHERE "Date" = CAST('{row[entry_key['Date']]}' AS date) AND "ReachID" = {element_id})
                """

                # print(query)
                cursor.execute(query)
                connection.commit()
        

def damwiseExtraction(
    dams,
    dam_id,
    # dam_name,
    startDate,
    endDate,
    ndwi_threshold=0.2,
    imageCollection="LANDSAT/LC09/C02/T1_L2",
    checkpoint_path=None,
    db=None,
    db_type=None,
    # connection=None,
    logger=None,
):
    # print('running damwiseExtraction')
    # print(dam_id)
    # dam_name = " ".join(dam_id.split("_")[1:])
    # dam_name = dam_name
    # print(dam_name)

    missions = {
        "LANDSAT/LC09/C02/T1_L2": "L9",
        "LANDSAT/LC08/C02/T1_L2": "L8",
        "LANDSAT/LE07/C02/T1_L2": "L7",
        "LANDSAT/LT05/C02/T1_L2": "L5",
        "LANDSAT/LT04/C02/T1_L2": "L4",
    }

    if checkpoint_path is None:
        checkpoint = {"reservoir_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    # print(checkpoint)

    dates = divideDates(startDate, endDate)
    waterTempSeriesList = []
    landTempSeriesList = []

    dataSeriesList = []

    for date in dates:
        startDate_ = date[0]
        endDate_ = date[1]

        dam = dams.filter(ee.Filter.eq("dam_id", dam_id))
        # waterTempSeries, landTempSeries= extractTempSeries(
        #     reservoir, startDate_, endDate_, ndwi_threshold, imageCollection
        # )
        # waterTempSeries = geemap.ee_to_pandas(waterTempSeries)
        # landTempSeries = geemap.ee_to_pandas(landTempSeries)

        # print("Breakpoint damwise 1")
        match imageCollection:
            case "LANDSAT/LC09/C02/T1_L2" | "LANDSAT/LC08/C02/T1_L2":
                dataSeries = extractTempSeries(
                    dam,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "dam"
                )
            case (
                "LANDSAT/LT04/C02/T1_L2"
                | "LANDSAT/LT05/C02/T1_L2"
                | "LANDSAT/LE07/C02/T1_L2"
            ):
                dataSeries = extractL4TempSeries(
                    dam,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "dam"
                )
            case _:
                pass
        
        # print("Breakpoint damwise 2")
        # dataSeries = extractTempSeries(
        #     reach,
        #     startDate_,
        #     endDate_,
        #     # ndwi_threshold,
        #     imageCollection,
        # )
        # if dataSeries is not None:
        if dataSeries.size().getInfo(): # truthy check to see if the dataSeries is not empty
            # print(dataSeries.size().getInfo())
            dataSeries = geemap.ee_to_df(dataSeries)
        else:
            dataSeries = pd.DataFrame()

        # print("Breakpoint damwise 3")
        if not dataSeries.empty:
            # print(dataSeries.head())

            # convert date column to datetime
            # waterTempSeries["date"] = pd.to_datetime(waterTempSeries["date"])
            # landTempSeries["date"] = pd.to_datetime(landTempSeries["date"])
            dataSeries["date"] = pd.to_datetime(dataSeries["date"])

            # waterTempSeries["temp(C)"] = (
            #     waterTempSeries["temp(C)"]
            #     .apply(lambda x: x["Celcius_mean"])
            #     .astype(float)
            # )
            # landTempSeries["temp(C)"] = (
            #     landTempSeries["temp(C)"]
            #     .apply(lambda x: x["Celcius_mean"])
            #     .astype(float)
            # )

            # print("Breakpoint damwise 4")
            dataSeries["watertemp(C)"] = (
                dataSeries["watertemp(C)"]
                .apply(lambda x: x["Celcius_mean"])
                .astype(float)
            )
            # dataSeries["landtemp(C)"] = (
            #     dataSeries["landtemp(C)"]
            #     .apply(lambda x: x["Celcius_mean"])
            #     .astype(float)
            # )
            # dataSeries["NDVI"] = (
            #     dataSeries["NDVI"].apply(lambda x: x["NDVI_mean"]).astype(float)
            # )
            dataSeries["Mission"] = missions[imageCollection]

            # append time series to list
            # waterTempSeriesList.append(waterTempSeries)
            # landTempSeriesList.append(landTempSeries)
            dataSeriesList.append(dataSeries)

        s_time = randint(3, 8)
        time.sleep(s_time)

    # concatenate all time series
    # waterTempSeries_df = pd.concat(waterTempSeriesList, ignore_index=True)
    # landTempSeries_df = pd.concat(landTempSeriesList, ignore_index=True)
    dataSeries_df = pd.concat(dataSeriesList, ignore_index=True)

    # sort by date
    # waterTempSeries_df.sort_values(by="date", inplace=True)
    # landTempSeries_df.sort_values(by="date", inplace=True)
    dataSeries_df.sort_values(by="date", inplace=True)
    # #drop null values
    # # waterTempSeries_df.dropna(inplace=True)
    # # landTempSeries_df.dropna(inplace=True)
    # dataSeries_df.dropna(inplace=True)
    # remove duplicates
    # waterTempSeries_df.drop_duplicates(subset="date", inplace=True)
    # landTempSeries_df.drop_duplicates(subset="date", inplace=True)
    dataSeries_df.drop_duplicates(subset="date", inplace=True)

    # save time series to csv
    # waterTempSeries_df.to_csv(
    #     data_dir / "reaches" / f"{reach_id}_watertemp.csv", index=False
    # )
    # landTempSeries_df.to_csv(
    #     data_dir / "reaches" / f"{reach_id}_landtemp.csv", index=False
    # )
    # print(dataSeries_df.head())
    # dataSeries_df.to_csv(
    #     data_dir / "reservoir" / f"{reach_id}.csv", index=False
    # )

    # # land temp
    # entryToDB(
    #     dataSeries_df,
    #     "ReachLandsatLandTemp",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="landtemp(C)",
    # )
    # # water temp
    # entryToDB(
    #     dataSeries_df,
    #     "ReachLandsatWaterTemp",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="watertemp(C)",
    # )
    # # NDVI
    # entryToDB(
    #     dataSeries_df,
    #     "ReachNDVI",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="NDVI",
    # )

    entryToDB(
        dataSeries_df,
        "DamData",
        dam_id,
        # connection,
        entry_key={
            "Date": "date",
            # "LandTempC": "landtemp(C)",
            "WaterTempC": "watertemp(C)",
            # "NDVI": "NDVI",
            "Mission": "Mission",
        },
        db=db,
        db_type=db_type,
    )

def reachwiseExtraction(
    reaches,
    reach_id,
    # dam_name,
    startDate,
    endDate,
    ndwi_threshold=0.2,
    imageCollection="LANDSAT/LC09/C02/T1_L2",
    checkpoint_path=None,
    db=None,
    db_type=None,
    # connection=None,
    logger=None,
):
    # print('running damwiseExtraction')
    # print(dam_id)
    # dam_name = " ".join(dam_id.split("_")[1:])
    # dam_name = dam_name
    # print(dam_name)

    missions = {
        "LANDSAT/LC09/C02/T1_L2": "L9",
        "LANDSAT/LC08/C02/T1_L2": "L8",
        "LANDSAT/LE07/C02/T1_L2": "L7",
        "LANDSAT/LT05/C02/T1_L2": "L5",
        "LANDSAT/LT04/C02/T1_L2": "L4",
    }

    if checkpoint_path is None:
        checkpoint = {"river_index": 0, "reach_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    # print(checkpoint)

    dates = divideDates(startDate, endDate)
    waterTempSeriesList = []
    landTempSeriesList = []

    dataSeriesList = []

    for date in dates:
        startDate_ = date[0]
        endDate_ = date[1]

        reach = reaches.filter(ee.Filter.eq("reach_id", reach_id))
        # waterTempSeries, landTempSeries= extractTempSeries(
        #     reservoir, startDate_, endDate_, ndwi_threshold, imageCollection
        # )
        # waterTempSeries = geemap.ee_to_pandas(waterTempSeries)
        # landTempSeries = geemap.ee_to_pandas(landTempSeries)

        # print("Breakpoint damwise 1")
        match imageCollection:
            case "LANDSAT/LC09/C02/T1_L2" | "LANDSAT/LC08/C02/T1_L2":
                dataSeries = extractTempSeries(
                    reach,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "reach"
                )
            case (
                "LANDSAT/LT04/C02/T1_L2"
                | "LANDSAT/LT05/C02/T1_L2"
                | "LANDSAT/LE07/C02/T1_L2"
            ):
                dataSeries = extractL4TempSeries(
                    reach,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "reach"
                )
            case _:
                pass
        
        # print("Breakpoint damwise 2")
        # dataSeries = extractTempSeries(
        #     reach,
        #     startDate_,
        #     endDate_,
        #     # ndwi_threshold,
        #     imageCollection,
        # )
        # if dataSeries is not None:
        if dataSeries.size().getInfo(): # truthy check to see if the dataSeries is not empty
            # print(dataSeries.size().getInfo())
            dataSeries = geemap.ee_to_df(dataSeries)
        else:
            dataSeries = pd.DataFrame()

        # print("Breakpoint damwise 3")
        if not dataSeries.empty:
            # print(dataSeries.head())

            # convert date column to datetime
            # waterTempSeries["date"] = pd.to_datetime(waterTempSeries["date"])
            # landTempSeries["date"] = pd.to_datetime(landTempSeries["date"])
            dataSeries["date"] = pd.to_datetime(dataSeries["date"])

            # waterTempSeries["temp(C)"] = (
            #     waterTempSeries["temp(C)"]
            #     .apply(lambda x: x["Celcius_mean"])
            #     .astype(float)
            # )
            # landTempSeries["temp(C)"] = (
            #     landTempSeries["temp(C)"]
            #     .apply(lambda x: x["Celcius_mean"])
            #     .astype(float)
            # )

            dataSeries["watertemp(C)"] = (
                dataSeries["watertemp(C)"]
                .apply(lambda x: x["Celcius_mean"])
                .astype(float)
            )
            dataSeries["landtemp(C)"] = (
                dataSeries["landtemp(C)"]
                .apply(lambda x: x["Celcius_mean"])
                .astype(float)
            )
            dataSeries["NDVI"] = (
                dataSeries["NDVI"].apply(lambda x: x["NDVI_mean"]).astype(float)
            )
            dataSeries["Mission"] = missions[imageCollection]

            # append time series to list
            # waterTempSeriesList.append(waterTempSeries)
            # landTempSeriesList.append(landTempSeries)
            dataSeriesList.append(dataSeries)

        s_time = randint(3, 8)
        time.sleep(s_time)

    # concatenate all time series
    # waterTempSeries_df = pd.concat(waterTempSeriesList, ignore_index=True)
    # landTempSeries_df = pd.concat(landTempSeriesList, ignore_index=True)
    dataSeries_df = pd.concat(dataSeriesList, ignore_index=True)

    # sort by date
    # waterTempSeries_df.sort_values(by="date", inplace=True)
    # landTempSeries_df.sort_values(by="date", inplace=True)
    dataSeries_df.sort_values(by="date", inplace=True)
    # #drop null values
    # # waterTempSeries_df.dropna(inplace=True)
    # # landTempSeries_df.dropna(inplace=True)
    # dataSeries_df.dropna(inplace=True)
    # remove duplicates
    # waterTempSeries_df.drop_duplicates(subset="date", inplace=True)
    # landTempSeries_df.drop_duplicates(subset="date", inplace=True)
    dataSeries_df.drop_duplicates(subset="date", inplace=True)

    # save time series to csv
    # waterTempSeries_df.to_csv(
    #     data_dir / "reaches" / f"{reach_id}_watertemp.csv", index=False
    # )
    # landTempSeries_df.to_csv(
    #     data_dir / "reaches" / f"{reach_id}_landtemp.csv", index=False
    # )
    # print(dataSeries_df.head())
    # dataSeries_df.to_csv(
    #     data_dir / "reservoir" / f"{reach_id}.csv", index=False
    # )

    # # land temp
    # entryToDB(
    #     dataSeries_df,
    #     "ReachLandsatLandTemp",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="landtemp(C)",
    # )
    # # water temp
    # entryToDB(
    #     dataSeries_df,
    #     "ReachLandsatWaterTemp",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="watertemp(C)",
    # )
    # # NDVI
    # entryToDB(
    #     dataSeries_df,
    #     "ReachNDVI",
    #     reach_id,
    #     connection,
    #     date_col="date",
    #     value_col="NDVI",
    # )

    entryToDB(
        dataSeries_df,
        "ReachData",
        reach_id,
        # connection,
        entry_key={
            "Date": "date",
            "LandTempC": "landtemp(C)",
            "WaterTempC": "watertemp(C)",
            "NDVI": "NDVI",
            "Mission": "Mission",
        },
        db=db,
        db_type=db_type,
    )


def runReservoirExtraction(
    data_dir,
    reservoirs_gdf,
    start_date,
    end_date,
    checkpoint_path=None,
    db=None,
    db_type="mysql",
    # connection=None,
    logger=None,
):
    if checkpoint_path is None:
        checkpoint = {"reservoir_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    # unique_rivers = rivers[checkpoint["river_index"] :]

    # for river in unique_rivers:
    reservoirs_gdf.to_file(data_dir / "reservoirs" / "reservoirs.shp")
    dam_ids = reservoirs_gdf["dam_id"].tolist()
    dam_names = reservoirs_gdf["DAM_NAME"].tolist()
    dam_ids = dam_ids[checkpoint["reservoir_index"] :]
    
    dams = geemap.shp_to_ee(data_dir / "reservoirs" / "reservoirs.shp")
    # if reach_ids is None:
    #     ee_reach_ids = reaches.select("reach_id", retainGeometry=False).getInfo()
    #     reach_ids = [i["properties"]["reach_id"] for i in ee_reach_ids["features"]][
    #         checkpoint["reach_index"] :
    #     ]
    #     # reach_ids = gdf["reach_id"].tolist()

    # print(start_date, end_date)

    for dam_name, dam_id in zip(dam_names, dam_ids):
        # Landsat9 Data
        if datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ) >= datetime.datetime.strptime("2021-10-01", "%Y-%m-%d"):
            # print("Landsat9")
            damwiseExtraction(
                dams=dams,
                dam_id=dam_id,
                # dam_name=dam_name,
                startDate=max(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("2021-10-01", "%Y-%m-%d"),
                ).strftime(
                    "%Y-%m-%d"
                ),  # clip the start date to 2021-10-01
                endDate=end_date,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC09/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )

        # Landsat8 Data
        if datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ) >= datetime.datetime.strptime("2013-03-01", "%Y-%m-%d"):
            # print("Landsat8")
            damwiseExtraction(
                dams,
                dam_id,
                # dam_name,
                max(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("2013-03-01", "%Y-%m-%d"),
                ).strftime(
                    "%Y-%m-%d"
                ),  # clip the start date to 2021-10-01
                end_date,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC08/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )

        # Landsat7 Data
        # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1999-03-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"):
        if datetime.datetime.strptime(
            start_date, "%Y-%m-%d"
        ) < datetime.datetime.strptime(
            "2024-01-31", "%Y-%m-%d"
        ) and datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ) > datetime.datetime.strptime(
            "1999-05-01", "%Y-%m-%d"
        ):
            # print("Landsat7")
            damwiseExtraction(
                dams,
                dam_id,
                # dam_name,
                max(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("1999-05-01", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                min(
                    datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("2024-01-31", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                # ndwi_threshold,
                imageCollection="LANDSAT/LE07/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )

        # Landsat5 Data
        # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1984-03-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"):
        if datetime.datetime.strptime(
            start_date, "%Y-%m-%d"
        ) < datetime.datetime.strptime(
            "2012-05-31", "%Y-%m-%d"
        ) and datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ) > datetime.datetime.strptime(
            "1984-03-01", "%Y-%m-%d"
        ):
            # print("Landsat5")
            damwiseExtraction(
                dams,
                dam_id,
                # dam_name,
                max(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("1984-03-01", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                min(
                    datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                # ndwi_threshold,
                imageCollection="LANDSAT/LT05/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )

        # Landsat4 Data
        # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1982-08-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("1993-06-30", "%Y-%m-%d"):
        if datetime.datetime.strptime(
            start_date, "%Y-%m-%d"
        ) < datetime.datetime.strptime(
            "1993-06-30", "%Y-%m-%d"
        ) and datetime.datetime.strptime(
            end_date, "%Y-%m-%d"
        ) > datetime.datetime.strptime(
            "1982-08-01", "%Y-%m-%d"
        ):
            # print("Landsat4")
            damwiseExtraction(
                dams,
                dam_id,
                # dam_name,
                max(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("1982-08-01", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                min(
                    datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                    datetime.datetime.strptime("1993-06-30", "%Y-%m-%d"),
                ).strftime("%Y-%m-%d"),
                # ndwi_threshold,
                imageCollection="LANDSAT/LT04/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )

        checkpoint["reservoir_index"] += 1
        json.dump(checkpoint, open(checkpoint_path, "w"))

        if logger is not None:
            logger.info(f"{dam_name} done!")
        else:
            print(f"{dam_name} done!")

def runReachExtraction(
    data_dir,
    rivers,
    reaches_gdf,
    start_date,
    end_date,
    checkpoint_path=None,
    db=None,
    db_type="mysql",
    # connection=None,
    logger=None,
):
    
    if checkpoint_path is None:
        checkpoint = {"river_index": 0, "reach_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)
    
    unique_rivers = rivers[checkpoint["river_index"] :]

    for river in unique_rivers:
        reaches_gdf[reaches_gdf["river_id"] == river].to_file(
            data_dir / "reaches" / "rivers.shp"
        )

        reach_ids = reaches_gdf[reaches_gdf["river_id"] == river]["reach_id"].tolist()

        # print(reach_ids)
        reach_ids = reach_ids[checkpoint["reach_index"] :]

        reaches = geemap.shp_to_ee(data_dir / "reaches" / "rivers.shp")

        if reach_ids is None:
            ee_reach_ids = reaches.select("reach_id", retainGeometry=False).getInfo()
            reach_ids = [i["properties"]["reach_id"] for i in ee_reach_ids["features"]][
                checkpoint["reach_index"] :
            ]
            # reach_ids = gdf["reach_id"].tolist()
            
        for reach_id in reach_ids:
            # Landsat9 Data
            if datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) >= datetime.datetime.strptime("2021-10-01", "%Y-%m-%d"):
                # print("Landsat9")
                reachwiseExtraction(
                    reaches,
                    reach_id,
                    # dam_name=dam_name,
                    startDate=max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2021-10-01", "%Y-%m-%d"),
                    ).strftime(
                        "%Y-%m-%d"
                    ),  # clip the start date to 2021-10-01
                    endDate=end_date,
                    # ndwi_threshold,
                    imageCollection="LANDSAT/LC09/C02/T1_L2",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

            # Landsat8 Data
            if datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) >= datetime.datetime.strptime("2013-03-01", "%Y-%m-%d"):
                # print("Landsat8")
                    reachwiseExtraction(
                        reaches,
                        reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2013-03-01", "%Y-%m-%d"),
                    ).strftime(
                        "%Y-%m-%d"
                    ),  # clip the start date to 2021-10-01
                    end_date,
                    # ndwi_threshold,
                    imageCollection="LANDSAT/LC08/C02/T1_L2",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

            # Landsat7 Data
            # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1999-03-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"):
            if datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ) < datetime.datetime.strptime(
                "2024-01-31", "%Y-%m-%d"
            ) and datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) > datetime.datetime.strptime(
                "1999-05-01", "%Y-%m-%d"
            ):
                # print("Landsat7")
                        reachwiseExtraction(
                            reaches,
                            reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("1999-05-01", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    min(
                        datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2024-01-31", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    # ndwi_threshold,
                    imageCollection="LANDSAT/LE07/C02/T1_L2",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

        # Landsat5 Data
        # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1984-03-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"):
            if datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ) < datetime.datetime.strptime(
                "2012-05-31", "%Y-%m-%d"
            ) and datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) > datetime.datetime.strptime(
                "1984-03-01", "%Y-%m-%d"
            ):
                # print("Landsat5")
                    reachwiseExtraction(
                        reaches,
                        reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("1984-03-01", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    min(
                        datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2012-05-31", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    # ndwi_threshold,
                    imageCollection="LANDSAT/LT05/C02/T1_L2",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

            # Landsat4 Data
            # if datetime.datetime.strptime(start_date, "%Y-%m-%d") >= datetime.datetime.strptime("1982-08-01", "%Y-%m-%d") and datetime.datetime.strptime(end_date, "%Y-%m-%d") <= datetime.datetime.strptime("1993-06-30", "%Y-%m-%d"):
            if datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ) < datetime.datetime.strptime(
                "1993-06-30", "%Y-%m-%d"
            ) and datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) > datetime.datetime.strptime(
                "1982-08-01", "%Y-%m-%d"
            ):
                # print("Landsat4")
                    reachwiseExtraction(
                        reaches,
                        reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("1982-08-01", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    min(
                        datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("1993-06-30", "%Y-%m-%d"),
                    ).strftime("%Y-%m-%d"),
                    # ndwi_threshold,
                    imageCollection="LANDSAT/LT04/C02/T1_L2",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

            checkpoint["reach_index"] += 1
            json.dump(checkpoint, open(checkpoint_path, "w"))

        checkpoint["reach_index"] = 0
        checkpoint["river_index"] += 1
        json.dump(checkpoint, open(checkpoint_path, "w"))

        # s_time = randint(30,120)
        # time.sleep(s_time)
        if logger is not None:
            logger.info(f"{river} done!")
        else:
            print(f"{river} done!")


def fetch_reservoir_gdf(db, db_type="postgresql"):
    if db_type == "postgresql":
        schema = db.schema
        query = f"""
        SELECT
            "DamID" AS dam_id,
            "Name" AS DAM_NAME,
            ST_AsBinary("ReservoirGeometry") AS geometry,
            ST_SRID("ReservoirGeometry") AS srid
        FROM
            {schema}."Dams"
        ORDER By
            "DamID"
        """
        connection = db.connection
        cursor = connection.cursor()
        cursor.execute(query)
        reservoirs_gdf = pd.DataFrame(cursor.fetchall(), columns=["dam_id", "DAM_NAME", "geometry", "srid"])
        reservoirs_gdf["geometry"] = gpd.GeoSeries.from_wkb(reservoirs_gdf["geometry"])
        reservoirs_gdf = gpd.GeoDataFrame(reservoirs_gdf, geometry="geometry")
        reservoirs_gdf = reservoirs_gdf.set_crs(epsg=reservoirs_gdf["srid"].iloc[0])

    elif db_type == "mysql":
        query = f"""
        SELECT
            DamID AS DAM_ID,
            Name AS DAM_NAME,
            ST_AsText(ReservoirGeometry, 'axis-order=long-lat') AS geometry,
            ST_SRID(geometry) AS SRID
        FROM
            Dams
        """
        connection = db.connection
        cursor = connection.cursor()
        cursor.execute(query)
        reservoirs_gdf = pd.DataFrame(cursor.fetchall(), columns=["dam_id", "DAM_NAME", "geometry"])
        reservoirs_gdf["geometry"] = gpd.GeoSeries.from_wkt(reservoirs_gdf["geometry"])
        reservoirs_gdf = gpd.GeoDataFrame(reservoirs_gdf, geometry="geometry")
        reservoirs_gdf = reservoirs_gdf.set_crs(epsg=reservoirs_gdf["srid"].iloc[0])

    return reservoirs_gdf

def fetch_reach_gdf(db, db_type="postgresql"):
    if db_type == "postgresql":
        schema = db.schema
        query = f"""
        SELECT
            "ReachID" AS reach_id,
            "Name" AS reach_name,
            "RiverID" AS river_id,
            ST_AsBinary("buffered_geometry") AS geometry,
            ST_SRID("buffered_geometry") AS srid
        FROM
            {schema}."Reaches"
        ORDER By
            "ReachID"
        """
        connection = db.connection
        cursor = connection.cursor()
        cursor.execute(query)
        reaches_gdf = pd.DataFrame(cursor.fetchall(), columns=["reach_id", "reach_name", "river_id", "geometry", "srid"])
        reaches_gdf["geometry"] = gpd.GeoSeries.from_wkb(reaches_gdf["geometry"])
        reaches_gdf = gpd.GeoDataFrame(reaches_gdf, geometry="geometry")
        reaches_gdf = reaches_gdf.set_crs(epsg=reaches_gdf["srid"].iloc[0])

    elif db_type == "mysql":
        query = f"""
        SELECT
            ReachID AS reach_id,
            Name AS reach_name,
            RiverID AS river_id,
            ST_AsText(geometry, 'axis-order=long-lat') AS geometry,
            ST_SRID(geometry) AS SRID
        FROM
            Reaches
        ORDER By
            ReachID
        """
        connection = db.connection
        cursor = connection.cursor()
        cursor.execute(query)
        reaches_gdf = pd.DataFrame(cursor.fetchall(), columns=["reach_id", "reach_name", "river_id", "geometry", "srid"])
        reaches_gdf["geometry"] = gpd.GeoSeries.from_wkt(reaches_gdf["geometry"])
        reaches_gdf = gpd.GeoDataFrame(reaches_gdf, geometry="geometry")
        reaches_gdf = reaches_gdf.set_crs(epsg=reaches_gdf["srid"].iloc[0])

    return reaches_gdf


def get_reservoir_data(
    db,
    db_type,
    data_dir,
    # connection,
    ee_credentials,
    # temperature_gauges_shp,
    start_date,
    end_date,
    # ndwi_threshold=0.2,
    # imageCollection="LANDSAT/LC08/C02/T1_L2",
    logger=None,
):
    service_account = ee_credentials["service_account"]
    credentials = ee.ServiceAccountCredentials(
        service_account, ee_credentials["private_key_path"]
    )
    ee.Initialize(credentials)

    reservoirs_gdf = fetch_reservoir_gdf(db, db_type)
    reservoirs_gdf = reservoirs_gdf.to_crs(epsg=4326)

    reservoirs = reservoirs_gdf["DAM_NAME"].to_list()

    try:
        with open(data_dir / "reservoirs" / "checkpoint.json", "r") as f:
            checkpoint = json.load(f)
    except Exception as e:
        if logger is not None:
            logger.error(f"Error: {e}")
            logger.info("Creating new checkpoint...")
        else:
            print(f"Error: {e}")
            print("Creating new checkpoint...")

        checkpoint = {"reservoir_index": 0}
        # save checkpoint
        json.dump(checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w"))

    repeated_tries = 0

    while checkpoint["reservoir_index"] < len(reservoirs):
        try:
            # extract temperature time series for each reservoir
            # print("running reservoir extraction")
            runReservoirExtraction(
                data_dir=data_dir,
                reservoirs_gdf=reservoirs_gdf,
                start_date=start_date,
                end_date=end_date,
                checkpoint_path=data_dir / "reservoirs" / "checkpoint.json",
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )
            repeated_tries = 0  # reset repeated_tries

        except Exception as e:
            if logger is not None:
                logger.error(f"Error: {e}")
            else:
                print(f"Error: {e}")

            # sleep for 0.5 - 3 minutes
            s_time = randint(15, 45)
            if logger is not None:
                logger.info(f"Sleeping for {s_time} seconds...")
            else:
                print(f"Sleeping for {s_time} seconds...")
            time.sleep(s_time)
            if logger is not None:
                logger.info("Restarting from checkpoint...")
            else:
                print("Restarting from checkpoint...")  # restart from checkpoint

            repeated_tries += 1

            # if repeated_tries > 3, increment river_index and reset reach_index
            if repeated_tries > 5:
                checkpoint["reservoir_index"] += 1

                repeated_tries = 0

                json.dump(
                    checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w")
                )

        finally:
            # load checkpoint
            with open(data_dir / "reservoirs" / "checkpoint.json", "r") as f:
                checkpoint = json.load(f)

    if checkpoint["reservoir_index"] >= len(reservoirs):
        checkpoint["reservoir_index"] = 0
        json.dump(checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w"))

    if logger is not None:
        logger.info("All done!")
    else:
        print("All done!")

    # # print("Test okay")

def get_reach_data(
    db,
    db_type,
    data_dir,
    # connection,
    ee_credentials,
    # temperature_gauges_shp,
    start_date,
    end_date,
    # ndwi_threshold=0.2,
    # imageCollection="LANDSAT/LC08/C02/T1_L2",
    logger=None,
):
    service_account = ee_credentials["service_account"]
    credentials = ee.ServiceAccountCredentials(
        service_account, ee_credentials["private_key_path"]
    )
    ee.Initialize(credentials)

    reaches_gdf = fetch_reach_gdf(db, db_type)
    reaches_gdf = reaches_gdf.to_crs(epsg=4326)

    # reaches = reaches_gdf["reach_name"].to_list()

    rivers = reaches_gdf["river_id"].unique()


    try:
        with open(data_dir / "reaches" / "checkpoint.json", "r") as f:
            checkpoint = json.load(f)
    except Exception as e:
        if logger is not None:
            logger.error(f"Error: {e}")
        else:
            print(f"Error: {e}")

        if logger is not None:
            logger.info("Creating new checkpoint...")
        else:
            print("Creating new checkpoint...")
        checkpoint = {"river_index": 0, "reach_index": 0}
        # save checkpoint
        json.dump(checkpoint, open(data_dir / "reaches" / "checkpoint.json", "w"))

    repeated_tries = 0

    while checkpoint["river_index"] < len(rivers):
        try:
            # extract temperature time series for each reach
            runReachExtraction(
                data_dir=data_dir,
                rivers=rivers,
                reaches_gdf=reaches_gdf,
                start_date=start_date,
                end_date=end_date,
                checkpoint_path=data_dir / "reaches" / "checkpoint.json",
                db=db,
                db_type=db_type,
                # connection=connection,
                logger=logger,
            )
            repeated_tries = 0  # reset repeated_tries

        except Exception as e:
            if logger is not None:
                logger.error(f"Error: {e}")
            else:
                print(f"Error: {e}")
            # sleep for 0.5 - 3 minutes
            s_time = randint(15, 45)
            if logger is not None:
                logger.info(f"Sleeping for {s_time} seconds...")
            else:
                print(f"Sleeping for {s_time} seconds...")
            time.sleep(s_time)

            if logger is not None:
                logger.info("Restarting from checkpoint...")
            else:
                print("Restarting from checkpoint...")  # restart from checkpoint

            repeated_tries += 1  # increment repeated_tries

            # if repeated_tries > 3, increment river_index and reset reach_index
            if repeated_tries > 5:
                checkpoint["reach_index"] += 1
                current_river = rivers[
                    checkpoint["river_index"]
                ]
                if checkpoint["reach_index"] >= len(
                    reaches_gdf[reaches_gdf["river_id"] == current_river][
                        "reach_id"
                    ].tolist()
                ):
                    checkpoint["reach_index"] = 0
                    checkpoint["river_index"] += 1
                repeated_tries = 0

                # save checkpoint
                json.dump(
                    checkpoint, open(data_dir / "reaches" / "checkpoint.json", "w")
                )

        finally:
            # save checkpoint
            with open(data_dir / "reaches" / "checkpoint.json", "r") as f:
                checkpoint = json.load(f)

    if checkpoint["river_index"] >= len(rivers):
        checkpoint["river_index"] = 0
        checkpoint["reach_index"] = 0
        json.dump(checkpoint, open(data_dir / "reaches" / "checkpoint.json", "w"))

    if logger is not None:
        logger.info("All done!")
    else:
        print("All done!")

    # print("Test okay")

# function to initialize the retrieval process
def init_retrieval(config, db_type="mysql", element="reach"):
    config_path = Path(config)
    config_dict = cfg.read_config(
        config_path,
        # required_sections=["project", "mysql", "data", "ee"]
    )

    project_dir = Path(config_dict["project"]["project_dir"])
    db_config_path = project_dir / config_dict[db_type]["db_config_path"]

    ee_credentials = {
        "service_account": config_dict["ee"]["service_account"],
        "private_key_path": config_dict["ee"]["private_key_path"],
    }

    log = logger.Logger(
        project_title=config_dict["project"]["title"], log_dir="tests"
    ).get_logger()

    db = database.Connect(db_config_path, db_type=db_type)

    data_dir = Path(project_dir, "Data/GEE")
    os.makedirs(data_dir / "reservoirs", exist_ok=True)
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

    # validate start and end dates
    start_date, end_date = validate_start_end_dates(start_date, end_date, logger=log)

    if element == "reach":
        get_reach_data(
            db, db_type, data_dir, ee_credentials, start_date, end_date, logger=log)
        # pass
    elif element == "reservoir":
        get_reservoir_data(
            db, db_type, data_dir, ee_credentials, start_date, end_date, logger=log)
        # pass

    

    # get_reservoir_data(
    #     reservoirs_shp=reservoirs_shp,
    #     data_dir=data_dir,
    #     ee_credentials=ee_credentials,
    #     connection=connection,
    #     start_date=start_date,
    #     end_date=end_date,
    #     logger=logger,
    #     # temperature_gauges_shp=temperature_gauges_shp,
    #     # startDate=startDate,
    #     # endDate=endDate,
    #     # ndwi_threshold=ndwi_threshold,
    #     # imageCollection=imageCollection,
    # )

def main(args):
    config_path = Path(args.config)
    db_type = args.db_type
    init_retrieval(config_path, db_type=db_type, element=args.element)
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, help="path to config file", required=True
    )
    parser.add_argument(
        "-db", "--db_type", default="mysql", type=str, help="type of database: either 'mysql' or 'postgresql'", required=False
    )
    parser.add_argument(
        "-e", "--element", type=str, default="reach", help="element to retrieve data for: reach or reservoir", required=False
    )

    main(args=parser.parse_args())
