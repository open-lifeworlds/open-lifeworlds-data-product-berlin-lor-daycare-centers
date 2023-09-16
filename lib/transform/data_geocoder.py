import os
import re

import pandas as pd
from geopandas.tools import geocode
from tqdm import tqdm

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def geocode_location(source_path, results_path, data_path, clean=False, quiet=False):
    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        # Make results path
        subdir = subdir.replace(f"{source_path}/", "")
        os.makedirs(os.path.join(results_path, subdir), exist_ok=True)

        for file_name in [file_name for file_name in sorted(files) if file_name.endswith("-details.csv")]:
            source_file_path = os.path.join(source_path, subdir, file_name)
            geocode_cache_file_path = os.path.join(data_path, "geocoding-cache.csv")

            geocode_csv(source_file_path, geocode_cache_file_path, clean=clean, quiet=quiet)
            extend_latlon(source_file_path, clean=clean, quiet=quiet)
            extend_address(source_file_path, clean=clean, quiet=quiet)


def geocode_csv(source_file_path, geocode_cache_file_path, clean, quiet):
    dataframe = read_csv_file(source_file_path)

    if "geometry" not in dataframe.columns and "lat" not in dataframe.columns and "lon" not in dataframe.columns:
        dataframe = dataframe \
            .assign(combined_address=lambda df: df["street"].apply(lambda row: row + " ") + df["zip_code"].apply(
            lambda row: str(int(row)) + " Berlin"))

        # Initialize list for geo information
        dataframe_geo_list = []

        # Read geocoding cache
        if os.path.exists(geocode_cache_file_path):
            geocoding_cache = read_csv_file(geocode_cache_file_path)
            geocoding_cache.set_index("combined_address", inplace=True)
        else:
            geocoding_cache = pd.DataFrame(columns=["combined_address", "geometry", "address"])
            geocoding_cache.set_index("combined_address", inplace=True)
            
        geocode_statistics = {
            "from_cache": 0,
            "new_geocoding": 0,
        }

        # Iterate over dataframe
        for index, row in tqdm(dataframe.iterrows(), desc="Geocode addresses", unit="facility",
                               total=dataframe.shape[0]):

            geocoding_cache_index = row["combined_address"]

            # Check if address is already in cache
            if geocoding_cache_index in geocoding_cache.index:
                geocode_statistics["from_cache"] += 1

                # Read from geolocation cache
                row_dataframe_geo = pd.DataFrame(geocoding_cache.loc[geocoding_cache_index]).T
                dataframe_geo_list.append(row_dataframe_geo)
            else:
                geocode_statistics["new_geocoding"] += 1

                row_dataframe_geo = geocode(pd.DataFrame(row).T["combined_address"], user_agent="open-lifeworlds",
                                            timeout=4)
                dataframe_geo_list.append(row_dataframe_geo)

                # Store result in cache
                geocoding_cache.loc[geocoding_cache_index] = {
                    "geometry": row_dataframe_geo.iloc[0]["geometry"],
                    "address": row_dataframe_geo.iloc[0]["address"]
                }
                geocoding_cache.to_csv(geocode_cache_file_path, index=True)

        print(f"✓ Read geolocation from cache {geocode_statistics['from_cache']} / new geocoding {geocode_statistics['new_geocoding']}")

        dataframe_geo = pd.concat(dataframe_geo_list)
        dataframe_geo.reset_index(drop=True, inplace=True)
        dataframe = dataframe.join(dataframe_geo)
        dataframe_errors = dataframe["address"].isna().sum()

        # Write csv file
        if dataframe.shape[0] > 0:
            dataframe.to_csv(source_file_path, index=False)
            if not quiet:
                print(f"✓ Geocode {os.path.basename(source_file_path)} with {dataframe_errors} errors")
        else:
            if not quiet:
                print(dataframe.head())
                print(f"✗️ Empty {os.path.basename(source_file_path)}")
    else:
        print(f"✓ Already geocoded {os.path.basename(source_file_path)}")


def extend_latlon(source_file_path, clean, quiet):
    dataframe = read_csv_file(source_file_path)
    if "lat" not in dataframe.columns or "lon" not in dataframe.columns:
        dataframe = dataframe \
            .assign(lat=lambda df: df["geometry"].apply(lambda row: build_lat(row))) \
            .assign(lon=lambda df: df["geometry"].apply(lambda row: build_lon(row))) \
            .drop(["geometry"], axis=1, errors="ignore")

        # Write csv file
        if dataframe.shape[0] > 0:
            dataframe.to_csv(source_file_path, index=False)
        if not quiet:
            print(f"✓ Extend lonlat for {os.path.basename(source_file_path)}")
        else:
            if not quiet:
                print(dataframe.head())
                print(f"✗️ Empty {os.path.basename(source_file_path)}")
    else:
        print(f"✓ Already extended lonlat for {os.path.basename(source_file_path)}")


def extend_address(source_file_path, clean, quiet):
    dataframe = read_csv_file(source_file_path)
    if "city" not in dataframe.columns:
        dataframe = dataframe \
            .drop(["street", "zip_code", "combined_address"], axis=1, errors="ignore") \
            .assign(street=lambda df: df["address"].apply(lambda row: build_street(row))) \
            .assign(zip_code=lambda df: df["address"].apply(lambda row: build_zip_code(row)).astype(int)) \
            .assign(city=lambda df: df["address"].apply(lambda row: build_city(row))) \
            .drop(["address"], axis=1, errors="ignore")

        dataframe_errors = dataframe["city"].isnull().sum()

        # Write csv file
        if dataframe.shape[0] > 0:
            dataframe.to_csv(source_file_path, index=False)
        if not quiet:
            print(f"✓ Extend address for {os.path.basename(source_file_path)} with {dataframe_errors} errors")
        else:
            if not quiet:
                print(dataframe.head())
                print(f"✗️ Empty {os.path.basename(source_file_path)}")
    else:
        print(f"✓ Already extended addresses for {os.path.basename(source_file_path)}")


def build_lat(row):
    if row is None or row == "POINT EMPTY":
        return None

    elements = row.replace("POINT (", "").replace(")", "").split(" ")
    return elements[1] if len(elements) == 2 else None


def build_lon(row):
    if row is None or row == "POINT EMPTY":
        return None

    elements = row.replace("POINT (", "").replace(")", "").split(" ")
    return elements[0] if len(elements) == 2 else None


def build_street(row):
    if row is None or pd.isnull(row):
        return None

    elements = [item.strip() for item in row.split(",")] if not pd.isnull(row) else []

    # Determine first field that is a number
    house_number_index = next((i for i, item in enumerate(elements) if item[0].strip().isdigit()), None)

    return elements[int(house_number_index) + 1].strip() + " " + elements[int(house_number_index)].strip() \
        if house_number_index is not None and len(elements) >= house_number_index + 1 else None


def build_zip_code(row):
    if row is None or pd.isnull(row):
        return None

    elements = [item.strip() for item in row.split(",")]
    return next((value for value in reversed(elements) if re.compile(r"\b\d{5}\b").search(str(value))), None)


def build_city(row):
    if row is None or pd.isnull(row):
        return None

    elements = [item.strip() for item in row.split(",")]
    return elements[-2].strip() if len(elements) >= 2 else None


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype={"id": "str"})
    else:
        return None
