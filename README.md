# Thermal History Of Regulated Rivers (THORR)

THORR is a data-driven approach to estimating water temperature in regulated rivers. We piloted the project in the Columbia River basin which is located northwest of the United States and southwest of Canada. The thermal stratification of deep reservoirs causes a thermal difference between the upstream and downstream sections of dams. Because of the spatial limitation of in-situ water temperature probes, it is difficult to obtain a spatially continuous representation of the temperature variation along regulated rivers. Satellite remote sensing offers a spatial advantage over point-based in-situ measurements. However, some of the challenges with remote sensing of water temperature include obstruction by clouds and the difficulty in obtaining the water temperature for narrow rivers. This results in temporal gaps in the satellite-based temperature. Also, because the satellites recorded the "skin" surface temperature, it is worth noting that remotely sensed water temperature may differ from in-situ water temperature measurements.

This GitHub contains the code and data used in the project as well as a copy of the THORR web app.

The [Data](https://github.com/UW-SASWE/THORR/tree/main/Data) folder contains all the GIS shapefiles, in-situ temperature records, and satellite data obtained from Landsat.  
The [Methods](https://github.com/UW-SASWE/THORR/tree/main/Methods) folder contains Jupyter Notebooks that were used to obtain and process the data and the code for the model development and evaluation.  
The results of this study can be found in the [Results](https://github.com/UW-SASWE/THORR/tree/main/Results) folder.  
Finally, the [Webapp](https://github.com/UW-SASWE/THORR/tree/main/Webapp) folder contains a clone of the [online tool](https://depts.washington.edu/saswe/hydrothermalviewer/) for viewing the spatially continuous thermal profile of the Columbia River and its adjoining tributaries.

Zenodo: [![DOI](https://zenodo.org/badge/721908733.svg)](https://zenodo.org/doi/10.5281/zenodo.10246698)

