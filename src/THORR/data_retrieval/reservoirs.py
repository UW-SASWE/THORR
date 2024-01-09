# TODO: Add docstring

import argparse
import sys
import geemap
import ee
from pathlib import Path
import pandas as pd
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
    reservoir,
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
        .filterBounds(reservoir)
    )

    def extractTemp(date):
        date = ee.Date(date)
        # prepare Landsat 8 image and add the NDWI band, and Celcius band
        processedL8 = (
            L8.filterDate(date, date.advance(1, "day"))
            .map(prepL8)
            .map(addCelcius)
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
        meanL8 = (
            processedL8.reduce(ee.Reducer.mean())
            .updateMask(waterMask)
            .set("system:time_start", date)
        )

        # get the mean temperature of the reservoir
        temp = meanL8.select(["Celcius_mean"]).reduceRegion(
            reducer=ee.Reducer.mean(), geometry=reservoir.geometry(), scale=30
        )

        return ee.Feature(None, {"date": date.format("YYYY-MM-dd"), "temp(C)": temp})

    dates = ee.List(
        L8.map(
            lambda image: ee.Feature(None, {"date": image.date().format("YYYY-MM-dd")})
        )
        .distinct("date")
        .aggregate_array("date")
        .getInfo()
    )

    tempSeries = ee.FeatureCollection(dates.map(extractTemp))

    return tempSeries


def runExtraction(
    data_dir,
    uniq_ids,
    dam_names,
    start_date,
    end_date,
    reservoirs,
    checkpoint_path=None,
    connection=None,
):
    if checkpoint_path is None:
        checkpoint = {"reservoir_index": 0}
    else:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

    uniq_ids_ = uniq_ids[checkpoint["reservoir_index"] :]
    dam_names_ = dam_names[checkpoint["reservoir_index"] :]

    for dam_name, uniq_id in zip(dam_names_, uniq_ids_):
        tempSeriesList = []

        # check if file exists
        if os.path.isfile(data_dir / "reservoirs" / f"{uniq_id}.csv"):
            existing_df = pd.read_csv(data_dir / "reservoirs" / f"{uniq_id}.csv")
            existing_df["date"] = pd.to_datetime(existing_df["date"])
            tempSeriesList.append(existing_df)
            # print("File exists!")

        # for landsat8
        dates = divideDates(start_date, end_date)
        # dates = divideDates(L8startDate, L8endDate)
        for date in dates:
            startDate_ = date[0]
            endDate_ = date[1]

            reservoir = reservoirs.filter(ee.Filter.eq("DAM_NAME", ee.String(dam_name)))
            tempSeries = extractTempSeries(
                reservoir,
                startDate_,
                endDate_,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC08/C02/T1_L2",
            )
            tempSeries = geemap.ee_to_pandas(tempSeries)

            # convert date column to datetime
            tempSeries["date"] = pd.to_datetime(tempSeries["date"])
            tempSeries["temp(C)"] = (
                tempSeries["temp(C)"].apply(lambda x: x["Celcius_mean"]).astype(float)
            )

            # append time series to list
            tempSeriesList.append(tempSeries)

        # for landsat9
        # dates = divideDates(startDate, endDate)
        # dates = divideDates(L9startDate, L9endDate)
        for date in dates:
            startDate_ = date[0]
            endDate_ = date[1]

            reservoir = reservoirs.filter(ee.Filter.eq("DAM_NAME", ee.String(dam_name)))
            tempSeries = extractTempSeries(
                reservoir,
                startDate_,
                endDate_,
                # ndwi_threshold,
                imageCollection="LANDSAT/LC09/C02/T1_L2",
            )
            tempSeries = geemap.ee_to_pandas(tempSeries)

            # convert date column to datetime
            tempSeries["date"] = pd.to_datetime(tempSeries["date"])
            tempSeries["temp(C)"] = (
                tempSeries["temp(C)"].apply(lambda x: x["Celcius_mean"]).astype(float)
            )

            # append time series to list
            tempSeriesList.append(tempSeries)

        # concatenate all time series
        tempSeries_df = pd.concat(tempSeriesList, ignore_index=True)

        # sort by date
        tempSeries_df.sort_values(by="date", inplace=True)
        # remove duplicates
        tempSeries_df.drop_duplicates(subset="date", inplace=True)

        # save time series to csv
        tempSeries_df.to_csv(data_dir / "reservoirs" / f"{uniq_id}.csv", index=False)

        cursor = connection.cursor()

        data = tempSeries_df.dropna().copy()
        # convert the date column to datetime YYYY-MM-DD
        data["date"] = pd.to_datetime(data["date"])
        data["date"] = data["date"].dt.date

        for i, row in data.iterrows():
            query = f"""
            INSERT INTO DamLandsatWaterTemp (Date, DamID, Value)
            SELECT '{row['date']}', (SELECT DamID FROM Dams WHERE Name = "{dam_name}"), {row['temp(C)']}
            WHERE NOT EXISTS (SELECT * FROM DamLandsatWaterTemp WHERE Date = '{row['date']}' AND DamID = (SELECT DamID FROM Dams WHERE Name = "{dam_name}"))
            """
            try:
                cursor.execute(query)
                connection.commit()
            except:
                print(query)
                raise Exception("Error!")

        checkpoint["reservoir_index"] += 1
        json.dump(checkpoint, open(checkpoint_path, "w"))

        print(f"{dam_name} done!")


def get_reservoir_data(
    reservoirs_shp,
    data_dir,
    connection,
    # temperature_gauges_shp,
    start_date,
    end_date,
    # ndwi_threshold=0.2,
    # imageCollection="LANDSAT/LC08/C02/T1_L2",
):
    ee.Initialize()

    reservoirs = geemap.shp_to_ee(reservoirs_shp)

    ee_dam_names = reservoirs.select("DAM_NAME", retainGeometry=False).getInfo()
    ee_uniq_ids = reservoirs.select("uniq_id", retainGeometry=False).getInfo()
    dam_names = [i["properties"]["DAM_NAME"] for i in ee_dam_names["features"]]
    uniq_ids = [i["properties"]["uniq_id"] for i in ee_uniq_ids["features"]]

    try:
        with open(data_dir / "reservoirs" / "checkpoint.json", "r") as f:
            checkpoint = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        print("Creating new checkpoint...")
        checkpoint = {"reservoir_index": 0}
        # save checkpoint
        json.dump(checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w"))

    repeated_tries = 0

    while checkpoint["reservoir_index"] < len(dam_names):
        try:
            # extract temperature time series for each reservoir
            runExtraction(
                data_dir=data_dir,
                uniq_ids=uniq_ids,
                dam_names=dam_names,
                start_date=start_date,
                end_date=end_date,
                reservoirs=reservoirs,
                checkpoint_path=data_dir / "reservoirs" / "checkpoint.json",
                connection=connection,
                
            )
            repeated_tries = 0  # reset repeated_tries

        except Exception as e:
            print(f"Error: {e}")

            # sleep for 0.5 - 3 minutes
            s_time = randint(30, 120)
            print(f"Sleeping for {s_time} seconds...")
            time.sleep(s_time)
            print("Restarting from checkpoint...")  # restart from checkpoint

            repeated_tries += 1

            if repeated_tries > 3:
                checkpoint["reservoir_index"] += 1

                repeated_tries = 0

                json.dump(
                    checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w")
                )

        finally:
            # load checkpoint
            with open(data_dir / "reservoirs" / "checkpoint.json", "r") as f:
                checkpoint = json.load(f)

    if checkpoint["reservoir_index"] >= len(dam_names):
        checkpoint["reservoir_index"] = 0
        json.dump(checkpoint, open(data_dir / "reservoirs" / "checkpoint.json", "w"))

    print("All done!")

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
    start_date, end_date = validate_start_end_dates(start_date, end_date)

    print(start_date, end_date)

    # start_date = config_dict["project"]["start_date"]
    # print(start_date)

    get_reservoir_data(
        reservoirs_shp=reservoirs_shp,
        data_dir=data_dir,
        connection=connection,
        start_date=start_date,
        end_date=end_date,
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
