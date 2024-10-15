import geopandas as gpd
import fiona
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from shapely.ops import split, snap
from shapely.geometry import LineString, Point
import pandas as pd

import rasterio as rio

default_projections = {
    "na": "ESRI:102010",  # NAD 1983 Equidistant Conic North America
    "sa": "ESRI:102032",  # SAD 1969 Equidistant Conic South America
    "eu": "ESRI:102031",  # ED 1950 Equidistant Conic Europe
    "af": "ESRI:102023",  # WGS 1984 Equidistant Conic for Africa
    "as_north": "ESRI:102026",  # WGS 1984 Equidistant Conic for Northern Asia
    "as_south": "ESRI:102029",  # WGS 1984 Equidistant Conic for Southern Asia
}


def line_to_segments(line, distance, segments=[]):
    """
    Function to split a line into segments of a given distance
    """

    # Cuts a line in several segments at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:

        return gpd.GeoSeries(segments + [LineString(line)])

    coords = list(line.coords)
    for i, p in enumerate(coords):

        pd = line.project(Point(p))
        if pd == distance:
            segments.append(LineString(coords[: i + 1]))
            line = LineString(coords[i:])
            return line_to_segments(line, distance, segments)
        if pd > distance:
            cp = line.interpolate(distance)
            segments.append(LineString(coords[:i] + [(cp.x, cp.y)]))
            line = LineString([(cp.x, cp.y)] + coords[i:])

            return line_to_segments(line, distance, segments)


def rivers_to_reaches(
    geopackage_path,
    grwl_path=None,
    good2_dams_path=None,
    koppen_path=None,
    geopackage_layer_dict={
        "basins": "Basins",
        "rivers": "Rivers",
    },
    basin_names=[],  # a list of basin names to process. If empty, all basins will be processed
    projection=None,
    return_gdf=False,
):
    basins = gpd.read_file(
        geopackage_path, layer=geopackage_layer_dict["basins"]
    )  # read the layer "Basins" from the geopackage

    if not basin_names:
        basin_names = basins["Name"].tolist()

    basins = basins[basins["Name"].isin(basin_names)]

    rivers = gpd.read_file(
        geopackage_path, layer=geopackage_layer_dict["rivers"]
    )  # read the layer "Rivers" from the geopackage
    dams = gpd.read_file(
        geopackage_path, layer="Dams"
    )  # read the layer "Dams" from the geopackage

    # col_river = rivers[rivers["GNIS_Name"] == "Columbia River"]
    grwl = gpd.read_file(grwl_path)
    good2_dams = gpd.read_file(good2_dams_path)

    reaches = pd.DataFrame()
    filtered_reaches = pd.DataFrame()
    buffered_reaches = pd.DataFrame()

    if projection in default_projections:
        projected_crs = default_projections[projection]
    else:
        projected_crs = None

    for basin in basins.geometry:
        # print(basin.geometry)
        # create a Azimuthal Equidistant projection centered on the basin centroid
        # get the center coordinates of the basins using convex hull

        if not projected_crs:
            lon_0, lat_0 = (
                basin.convex_hull.centroid.x,
                basin.convex_hull.centroid.y,
            )
            # define aeqd projection centered on the centroid of the basin
            projected_crs = f"+proj=aeqd +lat_0={lat_0} +lon_0={lon_0}"

        basin_rivers = rivers[rivers.within(basin)]
        # basin_rivers = basin_rivers[basin_rivers["GNIS_Name"] == "Columbia River"]
        basin_rivers = basin_rivers.to_crs(
            projected_crs
        )  # reproject the rivers to the aeqd projection
        grwl = grwl.to_crs(basins.crs)
        good2_dams = good2_dams.to_crs(basins.crs)

        basin_grwl = grwl[grwl.within(basin)]
        basin_grwl = basin_grwl.to_crs(projected_crs)

        # reservoirs = reservoirs.to_crs(basins.crs)

        # basin_reservoirs = reservoirs[reservoirs.within(basin)]
        # basin_reservoirs = basin_reservoirs.to_crs(projected_crs)

        basin_reaches = pd.DataFrame()

        for i, river in basin_rivers.iterrows():
            # print(river)

            lines = line_to_segments(river.geometry, 10000, [])
            # geoda
            # print(river.geometry.length)

            # create a new geodataframe with repited attributes of the river up to the lengt of the lines
            reaches_gdf = gpd.GeoDataFrame(geometry=lines, crs=projected_crs)
            reaches_gdf["GNIS_Name"] = river["GNIS_Name"]

            # add unique reach_id to bufferedReaches
            # countList = []
            unique_ids = []
            RKm = []
            for row, value in reaches_gdf.iterrows():
                # countList.append(value["GNIS_Name"])
                unique_ids.append("_".join(value["GNIS_Name"].split() + [str(row + 1)]))
                RKm.append(row * 10)

            # bufferedReaches["reach_id"] = unique_ids

            # add reach_id to filteredreaches
            reaches_gdf["reach_id"] = unique_ids
            reaches_gdf["RKm"] = RKm
            # print(len(lines))

            basin_reaches = gpd.GeoDataFrame(
                pd.concat([basin_reaches, reaches_gdf], ignore_index=True),
                crs=projected_crs,
            )

        basin_reaches = basin_reaches.sjoin_nearest(
            basin_grwl, how="left", distance_col="distance", max_distance=10000
        )
        basin_reaches.rename(
            columns={
                "width_max_": "WidthMax",
                "width_mean": "WidthMean",
                "width_min_": "WidthMin",
            },
            inplace=True,
        )

        # sort out reaches based on reach_id and WidthMean
        basin_reaches = basin_reaches.sort_values(
            by=["reach_id", "WidthMean"], ascending=[True, False]
        )

        basin_reaches.drop_duplicates(subset="reach_id", inplace=True)

        # # filter out reservoirs from the reaches
        # basin_filtered_reaches = basin_reaches.copy()
        # basin_filtered_reaches["geometry"] = basin_reaches.difference(basin_reservoirs.unary_union)
        # basin_filtered_reaches = basin_filtered_reaches[~basin_filtered_reaches.is_empty]

        # # replace all null values in the Width* with 30
        # basin_buffered_reaches = basin_filtered_reaches.copy()
        basin_buffered_reaches = basin_reaches.copy()

        basin_buffered_reaches_ = basin_buffered_reaches.fillna(
            {"WidthMax": 30, "WidthMean": 30}
        )
        # basin_buffered_reaches = basin_buffered_reaches.sort_values(by=["reach_id", "WidthMean"], ascending=[False, False])

        # bufferedReaches = filteredReachLines.copy()
        # bufferedReaches['geometry'] = bufferedReaches.geometry.buffer(filteredReachLines['WIDTH95']/2 + 120, resolution=5)
        basin_buffered_reaches["geometry"] = basin_buffered_reaches_.geometry.buffer(
            basin_buffered_reaches_["WidthMean"] / 2 + 120,
            # filteredReachLines_["WidthMax"] / 2 + 120,
            resolution=5,
            # cap_style=3
        )

        # reproject the reaches to the original crs
        basin_reaches = basin_reaches.to_crs(basins.crs)
        # basin_filtered_reaches = basin_filtered_reaches.to_crs(basins.crs)
        basin_buffered_reaches = basin_buffered_reaches.to_crs(basins.crs)

        reaches = gpd.GeoDataFrame(
            pd.concat([reaches, basin_reaches], ignore_index=True), crs=basins.crs
        )
        # filtered_reaches = gpd.GeoDataFrame(
        #     pd.concat([filtered_reaches, basin_filtered_reaches], ignore_index=True),
        #     crs=basins.crs,
        # )
        buffered_reaches = gpd.GeoDataFrame(
            pd.concat([buffered_reaches, basin_buffered_reaches], ignore_index=True),
            crs=basins.crs,
        )

        # Find the distance to upstream and downstream dams

        # change the projections to the same crs projected_crs
        good2_dams = good2_dams.to_crs(projected_crs)
        dams = dams.to_crs(projected_crs)
        buffered_reaches = buffered_reaches.to_crs(projected_crs)
        rivers = rivers.to_crs(projected_crs)
        reaches = reaches.to_crs(projected_crs)

        dropcols = ["index_right", "index_left"]
        good2_dams.drop(columns=dropcols, inplace=True, errors="ignore")
        buffered_reaches.drop(columns=dropcols, inplace=True, errors="ignore")

        good2_dams = gpd.sjoin(good2_dams, buffered_reaches, predicate="within")
        good2_dams.drop(columns=dropcols, inplace=True, errors="ignore")

        # snap the good2 dams to the rivers
        good2_dams_snap_geom = snap(
            good2_dams.geometry, rivers.geometry.unary_union, 0.001
        )
        # convert point z to point
        good2_dams_snap_geom = gpd.GeoDataFrame(
            good2_dams_snap_geom,
            geometry=gpd.points_from_xy(good2_dams_snap_geom.x, good2_dams_snap_geom.y),
        )
        # good2_dams_snap_geom.head()

        good2_dams.geometry = good2_dams_snap_geom.geometry

        # good2_dams = good2_dams.sjoin(rivers, predicate="intersects")
        # good2_dams = good2_dams.sjoin_nearest(rivers)
        good2_dams = good2_dams.sjoin_nearest(
            dams[["GRAND_ID", "geometry"]], how="left", max_distance=1000
        )
        # print(good2_dams.columns)

        # good2_dams["RKm"] = np.nan
        # reaches["DistToUpDam"] = np.nan
        # reaches["DistToDownDam"] = np.nan

        dam_rkm = []
        reach_dist_up = []
        reach_dist_down = []
        up_dam_grand_id = []
        down_dam_grand_id = []

        for i, row in good2_dams.iterrows():
            # get the coordinates of the dam
            dam = row["geometry"]
            # get the river
            river = rivers[rivers["GNIS_Name"] == row["GNIS_Name"]]

            # get the distance of the dam from the mouth of the river
            rkm = river.project(row["geometry"]).values[0]
            dam_rkm.append(rkm * 1e-3)
            # fig, ax = plt.subplots()
            # river.plot(ax=ax)

            # # plot the row
            # row = gpd.GeoDataFrame(row, ).T
            # row.geometry = row['geometry']

        good2_dams["RKm"] = dam_rkm

        for i, row in reaches.iterrows():
            # find the length of the reach
            reach = row["geometry"]
            length = reach.length

            reach_rkm = row["RKm"] + length * 1e-3 / 2

            up_dam = good2_dams[
                (good2_dams["GNIS_Name"] == row["GNIS_Name"])
                & (good2_dams["RKm"] > reach_rkm)
            ].sort_values("RKm")

            # print if the up_dam_rkm is not empty
            if not up_dam["RKm"].empty:
                up_dam_rkm = up_dam.iloc[0]["RKm"]
                reach_dist_up.append(up_dam_rkm - reach_rkm)
                up_dam_grand_id.append(up_dam["GRAND_ID"].values[0])
            else:
                reach_dist_up.append(np.nan)
                up_dam_grand_id.append(np.nan)

            down_dam = good2_dams[
                (good2_dams["GNIS_Name"] == row["GNIS_Name"])
                & (good2_dams["RKm"] < reach_rkm)
            ].sort_values("RKm", ascending=False)

            if not down_dam["RKm"].empty:
                down_dam_rkm = down_dam.iloc[0]["RKm"]
                reach_dist_down.append(reach_rkm - down_dam_rkm)
                down_dam_grand_id.append(down_dam["GRAND_ID"].values[0])
            else:
                reach_dist_down.append(np.nan)
                down_dam_grand_id.append(np.nan)

        reaches["DistToUpDam"] = reach_dist_up
        reaches["DistToDownDam"] = reach_dist_down
        reaches["UpDamGrandID"] = up_dam_grand_id
        reaches["DownDamGrandID"] = down_dam_grand_id

        buffered_reaches["DistToUpDam"] = reach_dist_up
        buffered_reaches["DistToDownDam"] = reach_dist_down
        buffered_reaches["UpDamGrandID"] = up_dam_grand_id
        buffered_reaches["DownDamGrandID"] = down_dam_grand_id

        # change the projections to the same crs basins.crs
        good2_dams = good2_dams.to_crs(basins.crs)
        buffered_reaches = buffered_reaches.to_crs(basins.crs)
        # dams = dams.to_crs(basins.crs)
        river = rivers.to_crs(basins.crs)
        reaches = reaches.to_crs(basins.crs)

        koppen_raster = rio.open(koppen_path)
        reprojected_reaches = buffered_reaches.to_crs(koppen_raster.crs)

        # Extract Köppen class for each reach based on centroid and add to reaches_gdf
        koppen_class = []
        for i in range(len(reprojected_reaches)):
            row = reprojected_reaches.iloc[i]
            x = row.geometry.centroid.x
            y = row.geometry.centroid.y
            row, col = koppen_raster.index(x, y)
            koppen_class.append(koppen_raster.read(1)[row, col])

        buffered_reaches["koppen"] = koppen_class
        reaches["koppen"] = koppen_class
        # filtered_reaches['koppen'] = koppen_class

        buffered_reaches = buffered_reaches.to_crs(basins.crs)
        reaches = reaches.to_crs(basins.crs)
        # filtered_reaches = filtered_reaches.to_crs(basins.crs)

        reaches.to_file(geopackage_path, layer="Reaches", driver="GPKG")
        # filtered_reaches.to_file(geopackage_fn, layer="FilteredReaches", driver="GPKG")
        buffered_reaches.to_file(
            geopackage_path, layer="BufferedReaches", driver="GPKG"
        )

    if return_gdf:
        return reaches, buffered_reaches
    else:
        return
