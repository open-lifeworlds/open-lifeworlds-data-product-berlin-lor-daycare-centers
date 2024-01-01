import json
import os

import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def assign_lor_area(source_path, results_path, data_path, clean=False, quiet=False):
    # Load geojson
    geojson = read_geojson_file(
        os.path.join(source_path, "berlin-lor-geodata-geojson", f"berlin-lor-planning-areas-from-2021.geojson"))

    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        # Make results path
        subdir = subdir.replace(f"{source_path}/", "")
        os.makedirs(os.path.join(results_path, subdir), exist_ok=True)

        # Make data path
        os.makedirs(data_path, exist_ok=True)

        for file_name in [file_name for file_name in sorted(files) if file_name.endswith("-details.csv")]:
            source_file_path = os.path.join(source_path, subdir, file_name)
            planning_area_cache_file_path = os.path.join(data_path, "lor-area-cache.csv")

            assign_lor_area_id(source_file_path, planning_area_cache_file_path, geojson=geojson, clean=clean,
                               quiet=quiet)


def assign_lor_area_id(source_file_path, planning_area_cache_file_path, geojson, clean, quiet):
    dataframe = read_csv_file(source_file_path)

    if "planning_area_id" not in dataframe.columns:

        # Read LOR area cache
        if os.path.exists(planning_area_cache_file_path):
            lor_area_cache = read_csv_file(planning_area_cache_file_path)
            lor_area_cache.set_index("latlon", inplace=True)
        else:
            lor_area_cache = pd.DataFrame(columns=["latlon", "planning_area_id"])
            lor_area_cache.set_index("latlon", inplace=True)

        dataframe = dataframe.assign(
            planning_area_id=lambda df: df.apply(lambda row: build_planning_area_id(
                row["lat"], row["lon"], geojson, lor_area_cache, planning_area_cache_file_path), axis=1))
        dataframe_errors = dataframe["planning_area_id"].isnull().sum()

        # Write csv file
        dataframe.assign(planning_area_id=lambda df: df["planning_area_id"].astype(int).astype(str).str.zfill(8))
        dataframe.to_csv(source_file_path, index=False)
        if not quiet:
            print(f"✓ Assign LOR area IDs to {os.path.basename(source_file_path)} with {dataframe_errors} errors")
    else:
        print(f"✓ Already assigned LOR area IDs to {os.path.basename(source_file_path)}")


def build_planning_area_id(lat, lon, geojson, lor_area_cache, lor_area_cache_file_path):
    planning_area_cache_index = f"{lat}_{lon}"

    # Check if planning area is already in cache
    if planning_area_cache_index in lor_area_cache.index:
        return lor_area_cache.loc[planning_area_cache_index]["planning_area_id"]
    else:
        point = Point(lon, lat)

        planning_area_id = None

        for feature in geojson["features"]:
            id = feature["properties"]["id"]
            coordinates = feature["geometry"]["coordinates"]
            polygon = build_polygon(coordinates)
            if point.within(polygon):
                planning_area_id = id

        # Store result in cache
        if planning_area_id is not None:
            lor_area_cache.loc[planning_area_cache_index] = {
                "planning_area_id": planning_area_id
            }
            lor_area_cache.assign(
                planning_area_id=lambda df: df["planning_area_id"].astype(int).astype(str).str.zfill(8))
            lor_area_cache.to_csv(lor_area_cache_file_path, index=True)
            return planning_area_id
        else:
            return 0


def build_polygon(coordinates) -> Polygon:
    points = [tuple(point) for point in coordinates[0][0]]
    return Polygon(points)


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"planning_area_id": "str"})
    else:
        return None


def read_geojson_file(file_path):
    with open(file=file_path, mode="r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file, strict=False)
