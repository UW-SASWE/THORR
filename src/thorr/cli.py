import typer
from typing_extensions import Annotated
from thorr.utils import create_config_file, download_data
from thorr.database import db_setup

from pathlib import Path

app = typer.Typer(rich_markup_mode=None)


@app.command()
def get_thorr_data(
    download_folder: Annotated[
        str, typer.Argument(help="Folder to download data to")
    ] = ".",
    region: Annotated[str, typer.Option(help="Region of the project")] = "global",
):

    download_folder = Path(download_folder)
    download_folder.mkdir(parents=True, exist_ok=True)

    models_url = "http://staff.washington.edu/gdarkwah/thorr_ml.zip"
    gis_url = "http://staff.washington.edu/gdarkwah/thorr_gis.zip"

    model_file_Path = download_folder / "ml_model" / models_url.split("/")[-1]
    gis_file_Path = download_folder / "gis" / gis_url.split("/")[-1]

    # download the models data
    download_data(models_url, model_file_Path, region)
    # download the gis data
    download_data(gis_url, gis_file_Path, region)

    print("Data downloaded successfully")


@app.command()
def database_setup(
    config_path: Annotated[str, typer.Argument(help="Path to the configuration file")],
    upload_gis: Annotated[
        bool, typer.Option(help="Upload GIS data to the database")
    ] = False,
):
    
    print("setting up the database")
    db_setup(config_path)

@app.command()
def new_project(
    name: Annotated[str, typer.Argument(help="Name of the new project")],
    dir: Annotated[str, typer.Argument(help="Directory of the new project")] = ".",
    new_config: Annotated[
        bool,
        typer.Option(
            # "--new_config",
            # "-n",
            help="Create a new config file"
        ),
    ] = True,
    get_data: Annotated[
        bool,
        typer.Option(
            # "--get_data",
            # "-g",
            help="Download data including trained THORR models"
        ),
    ] = False,
    region: Annotated[str, typer.Option(help="Region of the project")] = "global",
):

    print(f"Creating new project {name} in {dir}")

    proj_dir = Path(dir) / name
    env_dir = proj_dir / ".env"
    data_dir = proj_dir / "data"

    # create a folder with the name of the project
    proj_dir.mkdir(parents=True, exist_ok=True)
    env_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    # create a config file and a copy for backup
    if new_config:
        create_config_file(str(proj_dir), env_dir / f"{name}_config.ini", region=region)
        create_config_file(str(proj_dir), env_dir / f"{name}_config_copy.ini")

    # TODO: download data from the internet
    if get_data:
        get_thorr_data(str(data_dir), region=region)

    print("Project created successfully")
