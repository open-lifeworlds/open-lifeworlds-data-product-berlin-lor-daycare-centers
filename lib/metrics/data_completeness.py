import json
import os
import unittest

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

data_path = os.path.join(script_path, "..", "..", "data")

key_figure_group = "berlin-lor-daycare-centers"

statistic_properties = [
    "daycare_centers",
    "places"
]


class FilesTestCase(unittest.TestCase):
    pass


for year in [2023]:
    for month in ["10"]:
        for lor_area_type in ["districts", "forecast-areas", "district-regions", "planning-areas"]:
            file = os.path.join(data_path, f"{key_figure_group}-{year}-{month}",
                                f"{key_figure_group}-{year}-{month}-{lor_area_type}.geojson")
            setattr(
                FilesTestCase,
                f"test_{key_figure_group}_{year}_{month}_{lor_area_type}".replace('-', '_'),
                lambda self, file=file: self.assertTrue(os.path.exists(file))
            )


class PropertiesTestCase(unittest.TestCase):
    pass


for year in [2023]:
    for month in ["10"]:
        for lor_area_type in ["districts", "forecast-areas", "district-regions", "planning-areas"]:
            file = os.path.join(data_path, f"{key_figure_group}-{year}-{month}",
                                f"{key_figure_group}-{year}-{month}-{lor_area_type}.geojson")
            if os.path.exists(file):
                with open(file=file, mode="r", encoding="utf-8") as geojson_file:
                    geojson = json.load(geojson_file, strict=False)

                for feature in geojson["features"]:
                    feature_id = feature["properties"]["id"]
                    setattr(
                        PropertiesTestCase,
                        f"test_{key_figure_group}_{year}_{month}_{lor_area_type}_{feature_id}".replace('-', '_'),
                        lambda self, feature=feature: self.assertTrue(
                            all(property in feature["properties"] for property in statistic_properties))
                    )

if __name__ == '__main__':
    unittest.main()
