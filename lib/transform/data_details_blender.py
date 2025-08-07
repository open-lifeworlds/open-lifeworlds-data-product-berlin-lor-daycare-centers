import json
import os

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
    for input_port_group in data_transformation.input_port_groups or []:
        for input_port in input_port_group.input_ports or []:
            source_file_path = os.path.join(
                source_path, input_port.id, f"{input_port.id}.csv"
            )
            results_file_path = os.path.join(
                results_path,
                f"{input_port_group.id}-geojson",
                f"{input_port.id}.geojson",
            )

            with open(source_file_path, "r") as csv_file:
                dataframe_details = pd.read_csv(csv_file, dtype=str)

                geojson = {"type": "FeatureCollection", "features": []}

                for _, detail in dataframe_details.iterrows():
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
                            "properties": {
                                "id": detail["id"],
                                "name": detail["name"],
                                "phone-number": detail["phone_number"],
                                "places": int(detail["places"]),
                                "type": detail["type"],
                                "sponsor-id": detail["sponsor_id"],
                                "sponsor-name": detail["sponsor_name"],
                                "street": detail["street"],
                                "zip-code": detail["zip_code"],
                                "lat": float(detail["lat"]),
                                "lon": float(detail["lon"]),
                                "planning-area-id": int(detail["planning_area_id"]),
                            },
                        }
                    )

                # Save geojson
                if clean or not os.path.exists(results_file_path):
                    os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
                    with open(results_file_path, "w", encoding="utf-8") as geojson_file:
                        json.dump(geojson, geojson_file, ensure_ascii=False)

                        not quiet and print(
                            f"✓ Convert {os.path.basename(results_file_path)}"
                        )
                else:
                    not quiet and print(
                        f"✓ Already exists {os.path.basename(results_file_path)}"
                    )
