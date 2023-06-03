import json
import os

import pandas as pd

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def summarize(source_path, results_path, clean=False, quiet=False):
    # Load geojson
    geojson = read_geojson_file(
        os.path.join(source_path, "berlin-lor-geodata", f"berlin-lor-planning-areas-from-2021.geojson"))

    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        # Make results path
        subdir = subdir.replace(f"{source_path}/", "")
        os.makedirs(os.path.join(results_path, subdir), exist_ok=True)

        for file_name in [file_name for file_name in sorted(files) if file_name.endswith("-details.csv")]:
            source_file_path = os.path.join(source_path, subdir, file_name)
            summarize_csv_file(source_file_path, geojson=geojson, clean=clean, quiet=quiet)


def summarize_csv_file(source_file_path, geojson, clean, quiet):
    source_file_name, source_file_extension = os.path.splitext(source_file_path)
    target_file_path = f"{source_file_name.replace('-details', '')}{source_file_extension}"

    if not os.path.exists(target_file_path):
        dataframe_details = read_csv_file(source_file_path)

        dataframe = dataframe_details.groupby("planning_area_id").agg(
            daycare_centers=("planning_area_id", "size"),
            places=("places", "sum")
        ).reset_index().sort_values(by="planning_area_id") \
            .assign(planning_area_id=lambda df: df["planning_area_id"].astype(int))

        # Write csv file
        if dataframe.shape[0] > 0:
            dataframe.to_csv(target_file_path, index=False)
        if not quiet:
            print(f"✓ Summarize {os.path.basename(source_file_path)}")
        else:
            if not quiet:
                print(dataframe.head())
                print(f"✗️ Empty {os.path.basename(source_file_path)}")
    else:
        print(f"✓ Already summarized {os.path.basename(source_file_path)}")


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"id": "str"})
    else:
        return None


def read_geojson_file(file_path):
    with open(file=file_path, mode="r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file, strict=False)
