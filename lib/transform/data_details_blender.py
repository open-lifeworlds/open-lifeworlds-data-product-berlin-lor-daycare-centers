import json
import math
import os
import re
import pandas as pd
from openlifeworlds.config.data_transformation_loader import DataTransformation

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def blend_data_details(
    data_transformation: DataTransformation,
    source_path,
    results_path,
    clean=False,
    quiet=False,
):
    for subdir, dirs, files in sorted(os.walk(source_path)):
        if bool(re.search(r"berlin-daycare-centers-\d{4}-\d{2}$", subdir)):
            for f in [
                file_name
                for file_name in sorted(files)
                if file_name.endswith(".csv")
                and not file_name.endswith("-city.csv")
                and not file_name.endswith("-districts.csv")
                and not file_name.endswith("-forecast-areas.csv")
                and not file_name.endswith("-district-regions.csv")
                and not file_name.endswith("-planning-areas.csv")
            ]:
                file_name, file_extension = os.path.splitext(f)

                source_file_path = os.path.join(
                    source_path,
                    subdir.split(os.sep)[-1],
                    f"{file_name}{file_extension}",
                )
                results_file_path = os.path.join(
                    results_path,
                    "berlin-lor-daycare-centers-details-geojson",
                    f"{file_name}.geojson",
                )

                with open(source_file_path, "r") as csv_file:
                    dataframe_details = pd.read_csv(csv_file, dtype=str)

                    geojson = {"type": "FeatureCollection", "features": []}

                    for _, detail in dataframe_details.iterrows():
                        properties = {
                            "id": detail["id"],
                            "name": detail["name"],
                            "phone-number": detail["phone_number"],
                            "places": int(detail["places"]),
                            "type": detail["type"],
                            "sponsor-id": detail["sponsor_id"],
                            "sponsor-name": detail["sponsor_name"],
                            "street": detail["street"],
                            "zip-code": int(float(detail["zip_code"]))
                            if not math.isnan(float(detail["zip_code"]))
                            else math.nan,
                            "lat": float(detail["lat"]),
                            "lon": float(detail["lon"]),
                            "planning-area-id": int(detail["planning_area_id"]),
                        }
                        properties_filtered = {
                            key: value
                            for key, value in properties.items()
                            if not (isinstance(value, float) and math.isnan(value))
                        }

                        geojson["features"].append(
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        float(detail["lon"]),
                                        float(detail["lat"]),
                                    ],
                                },
                                "properties": properties_filtered,
                            }
                        )

                    # Save geojson
                    if clean or not os.path.exists(results_file_path):
                        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
                        with open(
                            results_file_path, "w", encoding="utf-8"
                        ) as geojson_file:
                            json.dump(geojson, geojson_file, ensure_ascii=False)

                            not quiet and print(
                                f"✓ Convert {os.path.basename(results_file_path)}"
                            )
                    else:
                        not quiet and print(
                            f"✓ Already exists {os.path.basename(results_file_path)}"
                        )
