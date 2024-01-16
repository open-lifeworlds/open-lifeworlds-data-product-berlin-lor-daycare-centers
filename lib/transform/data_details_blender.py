import json
import os

import pandas as pd

from lib.tracking_decorator import TrackingDecorator

key_figure_group = "berlin-lor-daycare-centers"


@TrackingDecorator.track_time
def blend_data_details(source_path, results_path, clean=False, quiet=False):
    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        statistics_name = subdir.replace(f"{source_path}/", "")

        if statistics_name.startswith("berlin-lor-daycare-centers-2"):
            for file_name in [file_name for file_name in sorted(files) if file_name.endswith("-details.csv")]:
                source_file_path = os.path.join(source_path, subdir, file_name)
                blend_details_into_geojson(source_file_path, statistics_name, clean=clean, quiet=quiet)


def blend_details_into_geojson(source_file_path, statistics_name, clean, quiet):
    source_file_name, source_file_extension = os.path.splitext(source_file_path)
    target_file_path = f"{source_file_name}.geojson"

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    dataframe_details = read_csv_file(source_file_path)

    for _, detail in dataframe_details.iterrows():
        geojson["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(detail["lon"]), float(detail["lat"])]
            },
            "properties": {
                "id": detail["id"],
                "name": detail["name"],
                "type": detail["type"],
                "street": detail["street"],
                "zip-code": detail["zip_code"],
                "city": detail["city"],
                "phone-number": detail["phone_number"],
                "places": int(detail["places"]),
                "sponsor-id": detail["sponsor_id"],
                "sponsor-name": detail["sponsor_name"],
                "lat": float(detail["lat"]),
                "lon": float(detail["lon"]),
                "planning-area-id": int(detail["planning_area_id"])
            }
        })

    # Write geojson file
    write_geojson_file(
        file_path=os.path.join(target_file_path),
        statistic_name=statistics_name,
        geojson_content=geojson,
        clean=clean,
        quiet=quiet
    )


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"id": "str", "phone_number": "str"}, header=0, index_col=False).fillna(
                "")
    else:
        return None


def write_geojson_file(file_path, statistic_name, geojson_content, clean, quiet):
    if not os.path.exists(file_path) or clean:

        # Make results path
        path_name = os.path.dirname(file_path)
        os.makedirs(os.path.join(path_name), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as geojson_file:
            json.dump(geojson_content, geojson_file, ensure_ascii=False)

            if not quiet:
                print(f"✓ Blend data from {statistic_name} into {os.path.basename(file_path)}")
    else:
        print(f"✓ Already exists {os.path.basename(file_path)}")
