import typer
from typing_extensions import Annotated
from thorr.utils import create_config_file

from pathlib import Path
import zipfile

app = typer.Typer(rich_markup_mode=None)

@app.command()
def download_data(
    download_folder: Annotated[
        str, typer.Argument(help="Folder to download data to")
    ] = ".",
    region: Annotated[str, typer.Option(help="Region of the project")] = "global",
):
    import requests

    download_folder = Path(download_folder)
    download_folder.mkdir(parents=True, exist_ok=True)

    models_url = "http://staff.washington.edu/gdarkwah/thorr_ml.zip"

    response = requests.get(models_url)
    file_Path = download_folder / models_url.split("/")[-1]

    # download the models
    if response.status_code == 200:
        with open(file_Path, "wb") as file:
            file.write(response.content)
        # print("File downloaded successfully")
    # else:
    #     print("Failed to download file")

    # extract the models to the download folder
    with zipfile.ZipFile(file_Path, "r") as zip_ref:
        zip_ref.extractall(download_folder)
    # print("Data extracted successfully")


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
        download_data(str(data_dir / "ml_model"), region=region)
