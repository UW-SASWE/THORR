# TODO: Add docstring

import argparse
import sys
import geemap
import ee
from pathlib import Path
import pandas as pd
import geopandas as gpd
import os
from pathlib import Path
import time
from random import randint
import json
import datetime

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


def extractTempSeries(
    reach,
    startDate,
    endDate,
    # ndwi_threshold=0.2,
    imageCollection="LANDSAT/LC08/C02/T1_L2",
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
        .filterBounds(reach)
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
        )
        meanL8nonwater = (
            processedL8.reduce(ee.Reducer.mean())
            # .addBands(ndwi, ["NDWI"], True)
            .updateMask(nonWaterMask).set("system:time_start", date)
        )

        # get the mean temperature of the reache
        watertemp = meanL8water.select(["Celcius_mean"]).reduceRegion(
            reducer=ee.Reducer.mean(), geometry=reach.geometry(), scale=30
        )
        landtemp = meanL8nonwater.select(["Celcius_mean"]).reduceRegion(
            reducer=ee.Reducer.mean(), geometry=reach.geometry(), scale=30
        )
        ndvi = meanL8nonwater.select(["NDVI_mean"]).reduceRegion(
            reducer=ee.Reducer.mean(), geometry=reach.geometry(), scale=30
        )

        return ee.Feature(
            None,
            {
                "date": date.format("YYYY-MM-dd"),
                "watertemp(C)": watertemp,
                "landtemp(C)": landtemp,
                "NDVI": ndvi,
            },
        )

    dates = ee.List(
        L8.map(
            lambda image: ee.Feature(None, {"date": image.date().format("YYYY-MM-dd")})
        )
        .distinct("date")
        .aggregate_array("date")
    )

    dataSeries = ee.FeatureCollection(dates.map(extractData))

    return dataSeries


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
    data, table_name, reach_name, connection, date_col="date", value_col="value"
):
    data = data.copy()
    data[date_col] = pd.to_datetime(data[date_col])
    data = data[[date_col, value_col]]
    data = data.dropna()
    # data = data[data[value_col] != -9999]
    data = data.sort_values(by=date_col)

    cursor = connection.cursor()

    for i, row in data.iterrows():
        query = f"""
        INSERT INTO {table_name} (Date, ReachID, Value)
        SELECT '{row[date_col]}', (SELECT ReachID FROM Reaches WHERE Name = "{reach_name}"), {row[value_col]}
        WHERE NOT EXISTS (SELECT * FROM {table_name} WHERE Date = '{row[date_col]}' AND ReachID = (SELECT ReachID FROM Reaches WHERE Name = "{reach_name}"))
        """

        cursor.execute(query)
        connection.commit()


def reachwiseExtraction(
    reaches,
    reach_id,
    startDate,
    endDate,
    ndwi_threshold=0.2,
    imageCollection="LANDSAT/LC09/C02/T1_L2",
    checkpoint_path=None,
    connection=None,
):
    if checkpoint_path is None:
        checkpoint = {"river_index": 0, "reach_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    dates = divideDates(startDate, endDate)
    waterTempSeriesList = []
    landTempSeriesList = []

    dataSeriesList = []

    for date in dates:
        startDate_ = date[0]
        endDate_ = date[1]

        reach = reaches.filter(ee.Filter.eq("reach_id", ee.String(reach_id)))
        # waterTempSeries, landTempSeries= extractTempSeries(
        #     reservoir, startDate_, endDate_, ndwi_threshold, imageCollection
        # )
        # waterTempSeries = geemap.ee_to_pandas(waterTempSeries)
        # landTempSeries = geemap.ee_to_pandas(landTempSeries)
        dataSeries = extractTempSeries(
            reach,
            startDate_,
            endDate_,
            # ndwi_threshold,
            imageCollection,
        )
        dataSeries = geemap.ee_to_gdf(dataSeries)

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
            dataSeries["watertemp(C)"].apply(lambda x: x["Celcius_mean"]).astype(float)
        )
        dataSeries["landtemp(C)"] = (
            dataSeries["landtemp(C)"].apply(lambda x: x["Celcius_mean"]).astype(float)
        )
        dataSeries["NDVI"] = (
            dataSeries["NDVI"].apply(lambda x: x["NDVI_mean"]).astype(float)
        )

        # append time series to list
        # waterTempSeriesList.append(waterTempSeries)
        # landTempSeriesList.append(landTempSeries)
        dataSeriesList.append(dataSeries)

        s_time = randint(5, 10)
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
    # dataSeries_df.to_csv(
    #     data_dir / "reaches" / f"{reach_id}.csv", index=False
    # )

    # land temp
    entryToDB(
        dataSeries_df,
        "ReachLandsatLandTemp",
        reach_id,
        connection,
        date_col="date",
        value_col="landtemp(C)",
    )
    # water temp
    entryToDB(
        dataSeries_df,
        "ReachLandsatWaterTemp",
        reach_id,
        connection,
        date_col="date",
        value_col="watertemp(C)",
    )
    # NDVI
    entryToDB(
        dataSeries_df,
        "ReachNDVI",
        reach_id,
        connection,
        date_col="date",
        value_col="NDVI",
    )


def runExtraction(
    data_dir,
    rivers,
    reaches_gdf,
    start_date,
    end_date,
    checkpoint_path=None,
    connection=None,
    logger=None,
):
    if checkpoint_path is None:
        checkpoint = {"river_index": 0, "reach_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    unique_rivers = rivers[checkpoint["river_index"] :]

    for river in unique_rivers:
        reaches_gdf[reaches_gdf["GNIS_Name"] == river].to_file(
            data_dir / "reaches" / "rivers.shp"
        )
        reach_ids = reaches_gdf[reaches_gdf["GNIS_Name"] == river]["reach_id"].tolist()
        reach_ids = reach_ids[checkpoint["reach_index"] :]

        reaches = geemap.shp_to_ee(data_dir / "reaches" / "rivers.shp")

        if reach_ids is None:
            ee_reach_ids = reaches.select("reach_id", retainGeometry=False).getInfo()
            reach_ids = [i["properties"]["reach_id"] for i in ee_reach_ids["features"]][
                checkpoint["reach_index"] :
            ]
            # reach_ids = gdf["reach_id"].tolist()

        for reach_id in reach_ids:
            # Landsat8 Data
            reachwiseExtraction(
                reaches,
                reach_id,
                start_date,
                end_date,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC08/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                connection=connection,
            )

            # Landsat9 Data
            reachwiseExtraction(
                reaches,
                reach_id,
                start_date,
                end_date,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC09/C02/T1_L2",
                checkpoint_path=checkpoint_path,
                connection=connection,
            )

            checkpoint["reach_index"] += 1
            json.dump(checkpoint, open(checkpoint_path, "w"))
            # if logger is not None:
            #     logger.info(f"Reach {reach_id} done!")
            # else:
            #     print(f"Reach {reach_id} done!")

        checkpoint["reach_index"] = 0
        checkpoint["river_index"] += 1
        json.dump(checkpoint, open(checkpoint_path, "w"))

        # s_time = randint(30,120)
        # time.sleep(s_time)
        if logger is not None:
            logger.info(f"{river} done!")
        else:
            print(f"{river} done!")


def get_reach_data(
    reaches_shp,
    data_dir,
    connection,
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

    reaches_gdf = gpd.read_file(reaches_shp)
    reaches_gdf = reaches_gdf.to_crs(epsg=4326)

    rivers = reaches_gdf["GNIS_Name"].unique()

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
            runExtraction(
                data_dir=data_dir,
                rivers=rivers,
                reaches_gdf=reaches_gdf,
                start_date=start_date,
                end_date=end_date,
                checkpoint_path=data_dir / "reaches" / "checkpoint.json",
                connection=connection,
                logger=logger,
            )
            repeated_tries = 0  # reset repeated_tries

        except Exception as e:
            if logger is not None:
                logger.error(f"Error: {e}")
            else:
                print(f"Error: {e}")
            # sleep for 0.5 - 3 minutes
            s_time = randint(30, 120)
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
            if repeated_tries > 3:
                checkpoint["reach_index"] += 1
                current_river = reaches_gdf["GNIS_Name"].unique()[
                    checkpoint["river_index"]
                ]
                if checkpoint["reach_index"] >= len(
                    reaches_gdf[reaches_gdf["GNIS_Name"] == current_river][
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


def main(args):
    config_path = Path(args.cfg)
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

    get_reach_data(
        reaches_shp=reaches_shp,
        data_dir=data_dir,
        ee_credentials=ee_credentials,
        connection=connection,
        start_date=start_date,
        end_date=end_date,
        logger=logger,
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
