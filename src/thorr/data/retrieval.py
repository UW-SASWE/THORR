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

from thorr.utils import (
    read_config,
    Logger,
    validate_start_end_dates,
    fetch_reach_gdf,
    fetch_reservoir_gdf,
)
from thorr.database import Connect as db_connect

REGIONS = {
    "global": "Global",
    "ucr": "Upper Colorado Region",
    "glr": "Great Lakes Region",
    "ohr": "Ohio Region",
    "lcr": "Lower Colorado Region",
    "pnr": "Pacific Northwest Region",
    "umr": "Upper Mississippi Region",
    "car": "Caribbean Region",
    "tnr": "Tennessee Region",
    "rgr": "Rio Grande Region",
    "sag": "South Atlantic-Gulf Region",
    "mar": "Mid Atlantic Region",
    "tgr": "Texas-Gulf Region",
    "srr": "Souris-Red-Rainy Region",
    "akr": "Alaska Region",
    "mir": "Missouri Region",
    "ner": "New England Region",
    "awr": "Arkansas-White-Red Region",
    "cal": "California Region",
    "lmr": "Lower Mississippi Region",
}


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
    element_type="dam",
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


def extractHLSL30BandData(
    element,
    startDate,
    endDate,
    # ndwi_threshold=0.2,
    imageCollection="NASA/HLS/HLSL30/v002",
    logger=None,
    element_type="reach",
):

    hlsl30 = (
        ee.ImageCollection(imageCollection)
        .filterDate(startDate, endDate)
        .filterBounds(element)
    )

    def extractData(date):
        date = ee.Date(date)

        processed_hlsl30 = hlsl30.filterDate(date, date.advance(1, "day"))
        hlsl30_mosaic = processed_hlsl30.mosaic()

        waterMask = hlsl30_mosaic.select("Fmask").bitwiseAnd(int("100000", 2)).neq(0)
        nonWaterMask = hlsl30_mosaic.select("Fmask").bitwiseAnd(int("100000", 2)).eq(0)

        hlsl30_water = (
            processed_hlsl30.reduce(ee.Reducer.mean())
            .updateMask(waterMask)
            .set("system:time_start", date)
        ).clip(element.geometry())

        band_data = {
            "B1": {"b1_mean": None, "b1_median": None, "b1_std": None},
            "B2": {"b2_mean": None, "b2_median": None, "b2_std": None},
            "B3": {"b3_mean": None, "b3_median": None, "b3_std": None},
            "B4": {"b4_mean": None, "b4_median": None, "b4_std": None},
            "B5": {"b5_mean": None, "b5_median": None, "b5_std": None},
            "B6": {"b6_mean": None, "b6_median": None, "b6_std": None},
            "B7": {"b7_mean": None, "b7_median": None, "b7_std": None},
            "B9": {"b9_mean": None, "b9_median": None, "b9_std": None},
            "B10": {"b10_mean": None, "b10_median": None, "b10_std": None},
            "B11": {"b11_mean": None, "b11_median": None, "b11_std": None},
        }

        for band in band_data.keys():
            band_data[band][f"{band.lower()}_mean"] = hlsl30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )
            band_data[band][f"{band.lower()}_median"] = hlsl30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.median(),
                geometry=element.geometry(),
                scale=30,
            )
            band_data[band][f"{band.lower()}_std"] = hlsl30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.stdDev(),
                geometry=element.geometry(),
                scale=30,
            )

        return ee.Feature(
            None,
            {
                "date": date.format("YYYY-MM-dd"),
                **band_data["B1"],
                **band_data["B2"],
                **band_data["B3"],
                **band_data["B4"],
                **band_data["B5"],
                **band_data["B6"],
                **band_data["B7"],
                **band_data["B9"],
                **band_data["B10"],
                **band_data["B11"],
            },
        )

    try:
        dates = ee.List(
            hlsl30.map(
                lambda image: ee.Feature(
                    None, {"date": image.date().format("YYYY-MM-dd")}
                )
            )
            .distinct("date")
            .aggregate_array("date")
        )
        dataSeries = ee.FeatureCollection(dates.map(extractData))
        return dataSeries
    except Exception as e:
        print(e, startDate, endDate)

    #     # return dataSeries
    # except Exception as e:
    #     # print(e, startDate, endDate)
    #     if logger is not None:
    #         logger.info(f"{e}")
    #     else:
    #         print(f"{e}")
    #     return None


def extractHLSS30BandData(
    element,
    startDate,
    endDate,
    # ndwi_threshold=0.2,
    imageCollection="NASA/HLS/HLSS30/v002",
    logger=None,
    element_type="reach",
):

    hlss30 = (
        ee.ImageCollection(imageCollection)
        .filterDate(startDate, endDate)
        .filterBounds(element)
    )

    def extractData(date):
        date = ee.Date(date)

        processed_hlss30 = hlss30.filterDate(date, date.advance(1, "day"))
        hlss30_mosaic = processed_hlss30.mosaic()

        waterMask = hlss30_mosaic.select("Fmask").bitwiseAnd(int("100000", 2)).neq(0)
        nonWaterMask = hlss30_mosaic.select("Fmask").bitwiseAnd(int("100000", 2)).eq(0)

        hlss30_water = (
            processed_hlss30.reduce(ee.Reducer.mean())
            .updateMask(waterMask)
            .set("system:time_start", date)
        ).clip(element.geometry())

        band_data = {
            "B1": {"b1_mean": None, "b1_median": None, "b1_std": None},
            "B2": {"b2_mean": None, "b2_median": None, "b2_std": None},
            "B3": {"b3_mean": None, "b3_median": None, "b3_std": None},
            "B4": {"b4_mean": None, "b4_median": None, "b4_std": None},
            "B5": {"b5_mean": None, "b5_median": None, "b5_std": None},
            "B6": {"b6_mean": None, "b6_median": None, "b6_std": None},
            "B7": {"b7_mean": None, "b7_median": None, "b7_std": None},
            "B8": {"b8_mean": None, "b8_median": None, "b8_std": None},
            "B8A": {"b8a_mean": None, "b8a_median": None, "b8a_std": None},
            "B9": {"b9_mean": None, "b9_median": None, "b9_std": None},
            "B10": {"b10_mean": None, "b10_median": None, "b10_std": None},
            "B11": {"b11_mean": None, "b11_median": None, "b11_std": None},
            "B12": {"b12_mean": None, "b12_median": None, "b12_std": None},
        }

        for band in band_data.keys():
            band_data[band][f"{band.lower()}_mean"] = hlss30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=element.geometry(),
                scale=30,
            )
            band_data[band][f"{band.lower()}_median"] = hlss30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.median(),
                geometry=element.geometry(),
                scale=30,
            )
            band_data[band][f"{band.lower()}_std"] = hlss30_water.select(
                f"{band.upper()}_mean"
            ).reduceRegion(
                reducer=ee.Reducer.stdDev(),
                geometry=element.geometry(),
                scale=30,
            )

        return ee.Feature(
            None,
            {
                "date": date.format("YYYY-MM-dd"),
                **band_data["B1"],
                **band_data["B2"],
                **band_data["B3"],
                **band_data["B4"],
                **band_data["B5"],
                **band_data["B6"],
                **band_data["B7"],
                **band_data["B8"],
                **band_data["B8A"],
                **band_data["B9"],
                **band_data["B10"],
                **band_data["B11"],
                **band_data["B12"],
            },
        )

    try:
        dates = ee.List(
            hlss30.map(
                lambda image: ee.Feature(
                    None, {"date": image.date().format("YYYY-MM-dd")}
                )
            )
            .distinct("date")
            .aggregate_array("date")
        )
        dataSeries = ee.FeatureCollection(dates.map(extractData))
        return dataSeries
    except Exception as e:
        print(e, startDate, endDate)

    #     # return dataSeries
    # except Exception as e:
    #     # print(e, startDate, endDate)
    #     if logger is not None:
    #         logger.info(f"{e}")
    #     else:
    #         print(f"{e}")
    #     return None


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
    if table_name == "DamData" or table_name == "ReachData":
        data = data.dropna(
            how="all",
            subset=[
                value
                for value in entry_key.values()
                if value not in [entry_key["Date"], entry_key["Mission"]]
            ],
        )
    else:
        data = data.dropna(
            how="all",
            subset=[
                value
                for value in entry_key.values()
                if value not in [entry_key["Date"]]
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

        # if table_name == "DamData":
        #     data = data.fillna("NULL")

        #     for i, row in data.iterrows():
        #         query = f"""
        #         INSERT INTO {schema}."{table_name}" ("Date", "DamID", {', '.join(['"'+str(key)+'"' for key in entry_key.keys() if key!='Date'])})
        #         SELECT CAST('{row[entry_key['Date']]}' AS date), '{element_id}', {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
        #         WHERE NOT EXISTS (SELECT * FROM {schema}."{table_name}" WHERE "Date" = CAST('{row[entry_key['Date']]}' AS date) AND "DamID" = {element_id})
        #         """

        #         # print(query)
        #         cursor.execute(query)
        #         connection.commit()
        # elif table_name == "ReachData":
        #     data = data.fillna("NULL")

        #     for i, row in data.iterrows():
        #         query = f"""
        #         INSERT INTO {schema}."{table_name}" ("Date", "ReachID", {', '.join(['"'+str(key)+'"' for key in entry_key.keys() if key!='Date'])})
        #         SELECT CAST('{row[entry_key['Date']]}' AS date), '{element_id}', {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"], entry_key['Mission']]])}, '{row[entry_key['Mission']]}'
        #         WHERE NOT EXISTS (SELECT * FROM {schema}."{table_name}" WHERE "Date" = CAST('{row[entry_key['Date']]}' AS date) AND "ReachID" = {element_id})
        #         """

        #         # print(query)
        #         cursor.execute(query)
        #         connection.commit()

        match table_name:
            case "DamData":
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

            case "ReachData":
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

            case "ReachHLSS30" | "ReachHLSL30":
                data = data.fillna("NULL")

                for i, row in data.iterrows():
                    query = f"""
                    INSERT INTO {schema}."{table_name}" ("Date", "ReachID", {', '.join(['"'+str(key)+'"' for key in entry_key.keys() if key!='Date'])})
                    SELECT CAST('{row[entry_key['Date']]}' AS date), '{element_id}', {', '.join([str(row[value]) for value in entry_key.values() if value not in [entry_key["Date"]]])}
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
                    "dam",
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
                    "dam",
                )
            case "NASA/HLS/HLSL30/v002":
                pass
            case "NASA/HLS/HLSS30/v002":
                pass
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
        if (
            dataSeries.size().getInfo()
        ):  # truthy check to see if the dataSeries is not empty
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
                    "reach",
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
                    "reach",
                )
            case "NASA/HLS/HLSL30/v002":
                # print('extracting HLSL30 data')
                dataSeries = extractHLSL30BandData(
                    reach,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "reach",
                )
            case "NASA/HLS/HLSS30/v002":
                # print('extracting HLSS30 data')
                dataSeries = extractHLSS30BandData(
                    reach,
                    startDate_,
                    endDate_,
                    # ndwi_threshold,
                    imageCollection,
                    logger,
                    "reach",
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
        if (
            dataSeries.size().getInfo()
        ):  # truthy check to see if the dataSeries is not empty
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

            match imageCollection:
                case (
                    "LANDSAT/LC09/C02/T1_L2"
                    | "LANDSAT/LC08/C02/T1_L2"
                    | "LANDSAT/LT04/C02/T1_L2"
                    | "LANDSAT/LT05/C02/T1_L2"
                    | "LANDSAT/LE07/C02/T1_L2"
                ):
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
                case "NASA/HLS/HLSL30/v002" | "NASA/HLS/HLSS30/v002":
                    for column in dataSeries.columns:
                        if column != "date":
                            dataSeries[column] = (
                                dataSeries[column]
                                .apply(
                                    lambda x: x[column.upper().split("_")[0] + "_mean"]
                                )
                                .astype(float)
                            )
                    # print(dataSeries.head())

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

    if imageCollection == "NASA/HLS/HLSL30/v002":
        entryToDB(
            dataSeries_df,
            "ReachHLSL30",
            reach_id,
            # connection,
            entry_key={
                "Date": "date",
                "b01_mean": "b1_mean",
                "b01_median": "b1_median",
                "b01_std": "b1_std",
                "b02_mean": "b2_mean",
                "b02_median": "b2_median",
                "b02_std": "b2_std",
                "b03_mean": "b3_mean",
                "b03_median": "b3_median",
                "b03_std": "b3_std",
                "b04_mean": "b4_mean",
                "b04_median": "b4_median",
                "b04_std": "b4_std",
                "b05_mean": "b5_mean",
                "b05_median": "b5_median",
                "b05_std": "b5_std",
                "b06_mean": "b6_mean",
                "b06_median": "b6_median",
                "b06_std": "b6_std",
                "b07_mean": "b7_mean",
                "b07_median": "b7_median",
                "b07_std": "b7_std",
                "b09_mean": "b9_mean",
                "b09_median": "b9_median",
                "b09_std": "b9_std",
                "b10_mean": "b10_mean",
                "b10_median": "b10_median",
                "b10_std": "b10_std",
                "b11_mean": "b11_mean",
                "b11_median": "b11_median",
                "b11_std": "b11_std",
            },
            db=db,
            db_type=db_type,
        )
    elif imageCollection == "NASA/HLS/HLSS30/v002":
        entryToDB(
            dataSeries_df,
            "ReachHLSS30",
            reach_id,
            # connection,
            entry_key={
                "Date": "date",
                "b01_mean": "b1_mean",
                "b01_median": "b1_median",
                "b01_std": "b1_std",
                "b02_mean": "b2_mean",
                "b02_median": "b2_median",
                "b02_std": "b2_std",
                "b03_mean": "b3_mean",
                "b03_median": "b3_median",
                "b03_std": "b3_std",
                "b04_mean": "b4_mean",
                "b04_median": "b4_median",
                "b04_std": "b4_std",
                "b05_mean": "b5_mean",
                "b05_median": "b5_median",
                "b05_std": "b5_std",
                "b06_mean": "b6_mean",
                "b06_median": "b6_median",
                "b06_std": "b6_std",
                "b07_mean": "b7_mean",
                "b07_median": "b7_median",
                "b07_std": "b7_std",
                "b08_mean": "b8_mean",
                "b08_median": "b8_median",
                "b08_std": "b8_std",
                "b8a_mean": "b8a_mean",
                "b8a_median": "b8a_median",
                "b8a_std": "b8a_std",
                "b09_mean": "b9_mean",
                "b09_median": "b9_median",
                "b09_std": "b9_std",
                "b10_mean": "b10_mean",
                "b10_median": "b10_median",
                "b10_std": "b10_std",
                "b11_mean": "b11_mean",
                "b11_median": "b11_median",
                "b11_std": "b11_std",
                "b12_mean": "b12_mean",
                "b12_median": "b12_median",
                "b12_std": "b12_std",
            },
            db=db,
            db_type=db_type,
        )
    else:
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
            
            # hlss30 data
            if datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) >= datetime.datetime.strptime("2015-11-15", "%Y-%m-%d"):
                reachwiseExtraction(
                    reaches,
                    reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2015-11-15", "%Y-%m-%d"),
                    ).strftime(
                        "%Y-%m-%d"
                    ),  # clip the start date to 2015-11-15
                    end_date,
                    # ndwi_threshold,
                    imageCollection="NASA/HLS/HLSS30/v002",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

            # hlsl30 data
            if datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ) >= datetime.datetime.strptime("2013-04-01", "%Y-%m-%d"):
                reachwiseExtraction(
                    reaches,
                    reach_id,
                    # dam_name,
                    max(
                        datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                        datetime.datetime.strptime("2013-04-01", "%Y-%m-%d"),
                    ).strftime(
                        "%Y-%m-%d"
                    ),  # clip the start date to 2013-04-01
                    end_date,
                    # ndwi_threshold,
                    imageCollection="NASA/HLS/HLSL30/v002",
                    checkpoint_path=checkpoint_path,
                    db=db,
                    db_type=db_type,
                    # connection=connection,
                    logger=logger,
                )

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
    region=None,
    logger=None,
    selected_reaches=None, # Only for research purposes
):
    service_account = ee_credentials["service_account"]
    credentials = ee.ServiceAccountCredentials(
        service_account, ee_credentials["private_key_path"]
    )
    ee.Initialize(credentials)

    reaches_gdf = fetch_reach_gdf(db, db_type, region=region)
    reaches_gdf = reaches_gdf.to_crs(epsg=4326)

    ## For research purposes only -- to limit the number of reaches to specific selected reaches
    if selected_reaches is not None:
        reaches_gdf = reaches_gdf[reaches_gdf["reach_id"].isin(selected_reaches)].copy()
    ## End of research purposes only

    # reaches = reaches_gdf["reach_name"].to_list()
    # print(reaches_gdf[reaches_gdf["river_id"]==5])

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
                current_river = rivers[checkpoint["river_index"]]
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

## for research purposes only
def get_station_buffer_data(
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
    region=None,
    logger=None,
    selected_reaches=None, # Only for research purposes
):
    service_account = ee_credentials["service_account"]
    credentials = ee.ServiceAccountCredentials(
        service_account, ee_credentials["private_key_path"]
    )
    ee.Initialize(credentials)

    reaches_gdf = fetch_reach_gdf(db, db_type, region=region)
    reaches_gdf = reaches_gdf.to_crs(epsg=4326)

    ## For research purposes only -- to limit the number of reaches to specific selected reaches
    if selected_reaches is not None:
        reaches_gdf = reaches_gdf[reaches_gdf["reach_id"].isin(selected_reaches)].copy()
    ## End of research purposes only

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
                current_river = rivers[checkpoint["river_index"]]
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
## end of research purposes only

def retrieve(config_path, element_type="reaches"):

    config_dict = read_config(Path(config_path))

    proj_dir = Path(config_dict["project"]["project_dir"])
    region = config_dict["project"]["region"]
    ee_credentials = {
        "service_account": config_dict["ee"]["service_account"],
        "private_key_path": config_dict["ee"]["private_key_path"],
    }

    log = Logger(
        project_title=config_dict["project"]["name"],
        logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_dir=Path(proj_dir / "logs"),
    ).get_logger()

    db_type = config_dict["database"]["type"].lower()
    db = db_connect(config_path, logger=log, db_type=db_type)

    data_dir = proj_dir / "data" / "GEE"

    if element_type == "reaches":
        reaches_dir = data_dir / "reaches"
        reaches_dir.mkdir(parents=True, exist_ok=True)
    elif element_type == "reservoirs":
        reservoirs_dir = data_dir / "reservoirs"
        reservoirs_dir.mkdir(parents=True, exist_ok=True)

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

    if element_type == "reaches":
        get_reach_data(
            db,
            db_type,
            data_dir,
            ee_credentials,
            start_date,
            end_date,
            logger=log,
            region=region,
        )
        # print("Retrieving reaches data")
        # pass
    elif element_type == "reservoirs":
        get_reservoir_data(
            db, db_type, data_dir, ee_credentials, start_date, end_date, logger=log
        )
        # print("Retrieving reservoirs data")

    # print(proj_dir, ee_credentials)


def retrieve_selected(config_path, element_type="reaches"):

    config_dict = read_config(Path(config_path))

    proj_dir = Path(config_dict["project"]["project_dir"])
    region = config_dict["project"]["region"]
    ee_credentials = {
        "service_account": config_dict["ee"]["service_account"],
        "private_key_path": config_dict["ee"]["private_key_path"],
    }

    log = Logger(
        project_title=config_dict["project"]["name"],
        logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_dir=Path(proj_dir / "logs"),
    ).get_logger()

    db_type = config_dict["database"]["type"].lower()
    db = db_connect(config_path, logger=log, db_type=db_type)

    data_dir = proj_dir / "data" / "GEE"

    if element_type == "reaches":
        reaches_dir = data_dir / "reaches"
        reaches_dir.mkdir(parents=True, exist_ok=True)
    elif element_type == "reservoirs":
        reservoirs_dir = data_dir / "reservoirs"
        reservoirs_dir.mkdir(parents=True, exist_ok=True)

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

    selected_ids = config_dict["selection"].get("selected_ids", None)

    # convert selected_ids to list
    if selected_ids is not None:
        selected_ids = [int(i) for i in selected_ids.split(",")]

    
    if element_type == "reaches":
        get_reach_data(
            db,
            db_type,
            data_dir,
            ee_credentials,
            start_date,
            end_date,
            logger=log,
            region=region,
            selected_reaches=selected_ids,
        )


def retrieve_station_buffer(config_path, element_type="reaches"):

    config_dict = read_config(Path(config_path))

    proj_dir = Path(config_dict["project"]["project_dir"])
    region = config_dict["project"]["region"]
    ee_credentials = {
        "service_account": config_dict["ee"]["service_account"],
        "private_key_path": config_dict["ee"]["private_key_path"],
    }

    log = Logger(
        project_title=config_dict["project"]["name"],
        logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_dir=Path(proj_dir / "logs"),
    ).get_logger()

    db_type = config_dict["database"]["type"].lower()
    db = db_connect(config_path, logger=log, db_type=db_type)

    data_dir = proj_dir / "data" / "GEE"

    reaches_dir = data_dir / "reaches"
    reaches_dir.mkdir(parents=True, exist_ok=True)
    
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

    selected_ids = config_dict["selection"].get("selected_ids", None)

    # convert selected_ids to list
    if selected_ids is not None:
        selected_ids = [int(i) for i in selected_ids.split(",")]

    
    get_station_buffer_data(
        db,
        db_type,
        data_dir,
        ee_credentials,
        start_date,
        end_date,
        logger=log,
        region=region,
    )
