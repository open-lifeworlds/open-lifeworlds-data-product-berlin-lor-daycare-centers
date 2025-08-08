import os

import pandas as pd

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def assign_population(
    data_transformation, source_path, results_path, clean=False, quiet=False
):
    for input_port_group in data_transformation.input_port_groups or []:
        for input_port in input_port_group.input_ports or []:
            for file in input_port.files or []:
                population_file_path = os.path.join(
                    source_path, file.population_file_name
                )

                for source_file in file.source_files or []:
                    source_file_path = os.path.join(
                        source_path, input_port.id, source_file.source_file_name
                    )
                    results_file_path = os.path.join(
                        results_path, input_port.id, source_file.source_file_name
                    )

                    assign_inhabitants(
                        source_file_path=source_file_path,
                        results_file_path=results_file_path,
                        population_file_path=population_file_path,
                        clean=clean,
                        quiet=quiet,
                    )

                    assign_inhabitants_age_below_6(
                        source_file_path=source_file_path,
                        results_file_path=results_file_path,
                        population_file_path=population_file_path,
                        clean=clean,
                        quiet=quiet,
                    )


def assign_inhabitants(
    source_file_path,
    results_file_path,
    population_file_path,
    clean,
    quiet,
):
    dataframe = read_csv_file(source_file_path)
    population_dataframe = read_csv_file(population_file_path)

    dataframe_errors = 0

    if "inhabitants" not in dataframe.columns or clean:
        dataframe = dataframe.assign(
            inhabitants=lambda df: df.apply(
                lambda row: population_dataframe[
                    population_dataframe["id"].astype(str).str.zfill(len(row["id"]))
                    == str(row["id"])
                ].iloc[0]["inhabitants"],
                axis=1,
            )
        )

        dataframe_errors += dataframe["inhabitants"].isnull().sum()

        # Write csv file
        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
        dataframe.to_csv(results_file_path, index=False)

        not quiet and print(
            f"✓ Assign inhabitants to {os.path.basename(source_file_path)} with {dataframe_errors} errors"
        )


def assign_inhabitants_age_below_6(
    source_file_path,
    results_file_path,
    population_file_path,
    clean,
    quiet,
):
    dataframe = read_csv_file(source_file_path)
    population_dataframe = read_csv_file(population_file_path)

    dataframe_errors = 0

    if "inhabitants_age_below_6" not in dataframe.columns or clean:
        dataframe = dataframe.assign(
            inhabitants_age_below_6=lambda df: df.apply(
                lambda row: population_dataframe[
                    population_dataframe["id"].astype(str).str.zfill(len(row["id"]))
                    == str(row["id"])
                ].iloc[0]["inhabitants_age_below_6"],
                axis=1,
            )
        )

        dataframe_errors += dataframe["inhabitants_age_below_6"].isnull().sum()

        # Write csv file
        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
        dataframe.to_csv(results_file_path, index=False)

        not quiet and print(
            f"✓ Assign inhabitants age below 6 to {os.path.basename(source_file_path)} with {dataframe_errors} errors"
        )


def read_csv_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as csv_file:
            return pd.read_csv(csv_file, dtype=str)
    else:
        return None
