import json
import os
import re
import pandas as pd

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def aggregate_data(source_path, results_path, clean=False, quiet=False):
    # Iterate over files
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
                    subdir.split(os.sep)[-1],
                    f"{file_name}-city{file_extension}",
                )
                aggregate_csv_file(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    aggregation_attribute="city_id",
                    digits=0,
                    clean=clean,
                    quiet=quiet,
                )

                results_file_path = os.path.join(
                    results_path,
                    subdir.split(os.sep)[-1],
                    f"{file_name}-districts{file_extension}",
                )
                aggregate_csv_file(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    aggregation_attribute="district_id",
                    digits=2,
                    clean=clean,
                    quiet=quiet,
                )

                results_file_path = os.path.join(
                    results_path,
                    subdir.split(os.sep)[-1],
                    f"{file_name}-forecast-areas{file_extension}",
                )
                aggregate_csv_file(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    aggregation_attribute="forecast_area_id",
                    digits=4,
                    clean=clean,
                    quiet=quiet,
                )

                results_file_path = os.path.join(
                    results_path,
                    subdir.split(os.sep)[-1],
                    f"{file_name}-district-regions{file_extension}",
                )
                aggregate_csv_file(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    aggregation_attribute="district_region_id",
                    digits=6,
                    clean=clean,
                    quiet=quiet,
                )

                results_file_path = os.path.join(
                    results_path,
                    subdir.split(os.sep)[-1],
                    f"{file_name}-planning-areas{file_extension}",
                )
                aggregate_csv_file(
                    source_file_path=source_file_path,
                    results_file_path=results_file_path,
                    aggregation_attribute="planning_area_id",
                    digits=8,
                    clean=clean,
                    quiet=quiet,
                )


def aggregate_csv_file(
    source_file_path, results_file_path, aggregation_attribute, digits, clean, quiet
):
    if not os.path.exists(results_file_path):
        dataframe_details = read_csv_file(source_file_path)

        # Remove invalid values
        dataframe_details.dropna(subset=["planning_area_id"], inplace=True)

        dataframe_details["city_id"] = 0
        dataframe_details["district_id"] = (
            dataframe_details["planning_area_id"].astype(str).str.zfill(8).str[:2]
        )
        dataframe_details["forecast_area_id"] = (
            dataframe_details["planning_area_id"].astype(str).str.zfill(8).str[:4]
        )
        dataframe_details["district_region_id"] = (
            dataframe_details["planning_area_id"].astype(str).str.zfill(8).str[:6]
        )
        dataframe_details["planning_area_id"] = (
            dataframe_details["planning_area_id"].astype(str).str.zfill(8).str[:8]
        )

        dataframe = (
            dataframe_details.groupby(aggregation_attribute)
            .agg(
                daycare_centers=(aggregation_attribute, "size"),
                places=("places", "sum"),
            )
            .reset_index()
            .sort_values(by=aggregation_attribute)
            .rename(columns={aggregation_attribute: "id"})
        )

        # Write csv file
        dataframe.to_csv(results_file_path, index=False)
        not quiet and print(f"✓ Aggregate into {os.path.basename(results_file_path)}")
    else:
        not quiet and print(
            f"✓ Already aggregated into {os.path.basename(results_file_path)}"
        )


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype=str)
    else:
        return None


def read_geojson_file(file_path):
    with open(file=file_path, mode="r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file, strict=False)
