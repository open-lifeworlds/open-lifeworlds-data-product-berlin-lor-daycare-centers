import json
import os
import re
import pandas as pd
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from rich.progress import track
from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def assign_lor_area(source_path, results_path, geojson_path, clean=False, quiet=False):
    # Load geojson
    geojson = read_geojson_file(geojson_path)

    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):
        if bool(re.search(r"berlin-daycare-centers-\d{4}-\d{2}$", subdir)):
            for file_name in track(
                sequence=[
                    file_name
                    for file_name in sorted(files)
                    if file_name.endswith(".csv")
                ],
                description="Assigning LOR area IDs",
                total=len(files),
                transient=True,
            ):
                source_file_path = os.path.join(
                    source_path, subdir.split(os.sep)[-1], file_name
                )
                results_file_path = os.path.join(
                    results_path, subdir.split(os.sep)[-1], file_name
                )
                planning_area_cache_file_path = os.path.join(
                    source_path, "lor-area-cache.csv"
                )

                assign_lor_area_id(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    planning_area_cache_file_path=planning_area_cache_file_path,
                    geojson=geojson,
                    clean=clean,
                    quiet=quiet,
                )


def assign_lor_area_id(
    source_file_path,
    results_file_path,
    planning_area_cache_file_path,
    geojson,
    clean,
    quiet,
):
    dataframe = read_csv_file(source_file_path)

    if "planning_area_id" not in dataframe.columns:
        # Read LOR area cache
        if os.path.exists(planning_area_cache_file_path):
            lor_area_cache = read_csv_file(planning_area_cache_file_path)
            lor_area_cache.set_index("latlon", inplace=True)
        else:
            lor_area_cache = pd.DataFrame(columns=["planning_area_id", "latlon"])
            lor_area_cache.set_index("latlon", inplace=True)

        dataframe["lat"] = dataframe["lat"].apply(str).str[:8]
        dataframe["lon"] = dataframe["lon"].apply(str).str[:8]

        for index, row in track(
            sequence=dataframe.iterrows(),
            description=f"Assigning LOR area IDs to {os.path.basename(source_file_path).replace(".csv", "")}",
            total=len(dataframe),
            transient=True,
        ):
            planning_area_id = build_planning_area_id(
                row["lat"],
                row["lon"],
                geojson,
                lor_area_cache,
                planning_area_cache_file_path,
            )
            dataframe.at[index, "planning_area_id"] = planning_area_id

        dataframe_errors = dataframe["planning_area_id"].isnull().sum()

        # Write csv file
        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
        dataframe.to_csv(results_file_path, index=False)

        not quiet and print(
            f"✓ Assign LOR area IDs to {os.path.basename(source_file_path)} with {dataframe_errors} errors"
        )
    else:
        not quiet and print(
            f"✓ Already assigned LOR area IDs to {os.path.basename(source_file_path)}"
        )


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
                planning_area_id=lambda df: df["planning_area_id"]
                .astype(int)
                .astype(str)
                .str.zfill(8)
            )

            # Persist LOR area cache
            lor_area_cache.to_csv(lor_area_cache_file_path, index=True)

            return planning_area_id.zfill(8)
        else:
            return None


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
