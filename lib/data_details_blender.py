import json
import math
import os
import re
import pandas as pd
from openlifeworlds.config.data_transformation_loader import DataTransformation

from openlifeworlds.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def blend_data_details(
    data_transformation: DataTransformation,
    source_path,
    results_path,
    clean=False,
    quiet=False,
):
    for input_port_group in data_transformation.input_port_groups or []:
        for input_port in input_port_group.input_ports or []:
            year = re.search(r"\b\d{4}\b", input_port.id).group()
            half_year = (
                re.search(r"\b\d{2}(?<!\d{4})\b", input_port.id).group()
                if re.search(r"\b\d{2}(?<!\d{4})\b", input_port.id)
                else "00"
            )

            source_file_path = os.path.join(
                source_path,
                input_port.id,
                f"{input_port.id.replace('-csv', '')}-details.csv",
            )
            target_file_path = os.path.join(
                results_path,
                f"{input_port_group.id}-geojson",
                f"{input_port_group.id}-{year}-{half_year}-details.geojson",
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
                        "planning-area-id": int(detail["geojson_feature_id"]),
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
                if clean or not os.path.exists(target_file_path):
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    with open(target_file_path, "w", encoding="utf-8") as geojson_file:
                        json.dump(geojson, geojson_file, ensure_ascii=False)

                        not quiet and print(
                            f"✓ Convert {os.path.basename(target_file_path)}"
                        )
                else:
                    not quiet and print(
                        f"✓ Already exists {os.path.basename(target_file_path)}"
                    )
