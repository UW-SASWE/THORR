from pathlib import Path
import configparser
import requests
import zipfile


def create_config_file(proj_dir, config_filepath: Path, name=None, region=None) -> None:
    if not name:
        name = proj_dir.split("/")[-1]
    if region:
        region = region
    else:
        region = "global"

    config = {
        "project": {
            "name": name,
            "project_dir": proj_dir,
            "region": region,
            "description": "",
            "start_date": "",
            "end_date": "",
        },
        "database": {
            "type": "options: mysql or postgresql",
            "user": "",
            "password": "",
            "host": "",
            "port": "",
            "database": "",
            "schema": "",
        },
        "data": {
            "gis_geopackage": f"data/gis/{region}_gis.gpkg",
            "ml_model": f"data/ml/{region}_ml.joblib",
        },
        "data.geopackage_layers": {
            "basins": "Basins",
            "rivers": "Rivers",
            "dams": "Dams",
            "reservoirs": "Reservoirs",
            "reaches": "Reaches",
            "buffered_reaches": "BufferedReaches",
        },
        "ee": {
            "private_key_path": "/path/to/earth/engine/private/key.json",
            "service_account": "service_account_email",
        },
    }
    config_obj = configparser.ConfigParser()
    with open(config_filepath, "w") as f:
        for section, options in config.items():
            config_obj.add_section(section)
            for option, value in options.items():
                config_obj.set(section, option, value)
        config_obj.write(f)


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

    config_obj = configparser.ConfigParser()
    config_obj.read(config_path)

    if required_sections:
        for section in required_sections:
            if section not in config_obj.sections():
                raise Exception(
                    f"Section {section} not found in the {config_path} file"
                )

        # create a dictionary of parameters
        config_dict = {
            section: dict(config_obj.items(section)) for section in required_sections
        }
    else:
        config_dict = {
            section: dict(config_obj.items(section))
            for section in config_obj.sections()
        }

    return config_dict


def download_data(url, file_Path, region):
    download_folder = file_Path.parent
    download_folder.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)

    # download the models
    if response.status_code == 200:
        with open(file_Path, "wb") as file:
            file.write(response.content)
            
    with zipfile.ZipFile(file_Path, "r") as zip_ref:
        files = zip_ref.namelist()
        regions = [file.split("/")[-1].split("_")[0] for file in files]
        if region in regions:
            zip_ref.extract(files[regions.index(region)], download_folder)
        else:
            print("Region not found in the data")
            print("Available regions are:")
            print(regions)
            print("Please try again with one of the available regions")

    # delete the zip file
    file_Path.unlink()