from thorr.utils import read_config, Logger, validate_start_end_dates
from thorr.database import Connect as db_connect

from pathlib import Path
import pandas as pd
from joblib import load


# temperature estimate
def est_temp_reaches(config_path, element_type="reaches"):
    config_dict = read_config(config_path)

    proj_dir = Path(config_dict["project"]["project_dir"])

    log = Logger(
        project_title=config_dict["project"]["name"],
        logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_dir=Path(proj_dir / "logs"),
    ).get_logger()

    db_type = config_dict["database"]["type"].lower()
    db = db_connect(config_path, logger=log, db_type=db_type)

    model_fn = proj_dir / config_dict["data"]["ml_model"]

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

    if db_type == "postgresql":
        schema = db.schema
        query1 = f"""
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
    elif db_type == "mysql":
        # TODO: implement the query for mysql
        pass

    # fetch the data into a dataframe as df
    with connection.cursor() as cursor:
        cursor.execute(query1)
        df = pd.DataFrame(
            cursor.fetchall(), columns=[desc[0] for desc in cursor.description]
        )
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
    ml_model = load(model_fn)
    # estimate models
    df["EstTempC"] = ml_model.predict(df[features])

    # upload estimates to the database
    if db_type == "postgresql":
        for i, row in df.iterrows():
            # if i % 10000 == 0:
            #     print(f"Processing row {i} of {len(df)}")

            query2 = f"""
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

            with connection.cursor() as cursor:
                cursor.execute(query2)
                connection.commit()
    elif db_type == "mysql":
        # TODO: implement the query for mysql
        pass

    log.info("Temperature estimates have been successfully uploaded to the database.")


def est_temp_reservoirs(config_path, element_type):
    print("Current version does not support temperature estimate for reservoirs")
    print("Please use the reaches option")
