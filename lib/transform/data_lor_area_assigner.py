import json
import os

import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def assign_lor_area(source_path, results_path, clean=False, quiet=False):
    # Load geojson
    geojson = read_geojson_file(
        os.path.join(source_path, "berlin-lor-geodata", f"berlin-lor-planning-areas-from-2021.geojson"))

    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        # Make results path
        subdir = subdir.replace(f"{source_path}/", "")
        os.makedirs(os.path.join(results_path, subdir), exist_ok=True)

        for file_name in [file_name for file_name in sorted(files) if file_name.endswith(".csv")]:
            source_file_path = os.path.join(source_path, subdir, file_name)
            assign_lor_area_id(source_file_path, geojson=geojson, clean=clean, quiet=quiet)


def assign_lor_area_id(source_file_path, geojson, clean, quiet):
    dataframe = read_csv_file(source_file_path)
    dataframe = dataframe.assign(
        planning_area_id=lambda df: df.apply(lambda row: build_planning_area_id(
            row["lat"], row["lon"], geojson), axis=1))

    dataframe_errors = dataframe["planning_area_id"].isnull().sum()

    # Write csv file
    if dataframe.shape[0] > 0:
        dataframe.to_csv(source_file_path, index=False)
    if not quiet:
        print(f"✓ Assign LOR area IDs to {os.path.basename(source_file_path)} with {dataframe_errors} errors")
    else:
        if not quiet:
            print(dataframe.head())
            print(f"✗️ Empty {os.path.basename(source_file_path)}")


def build_planning_area_id(lat, lon, geojson):
    point = Point(lon, lat)

    for feature in geojson["features"]:
        id = feature["properties"]["id"]
        coordinates = feature["geometry"]["coordinates"]
        polygon = build_polygon(coordinates)
        if point.within(polygon):
            return id

    return None


def build_polygon(coordinates) -> Polygon:
    points = [tuple(point) for point in coordinates[0][0]]
    return Polygon(points)


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"id": "str"})
    else:
        return None


def read_geojson_file(file_path):
    with open(file=file_path, mode="r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file, strict=False)
