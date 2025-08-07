import os
import shutil

from openlifeworlds.config.data_transformation_loader import DataTransformation
from openlifeworlds.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def copy_geodata(
    source_path,
    results_path,
    clean=False,
    quiet=False,
):
    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):
        for file_name in [
            file_name for file_name in sorted(files) if file_name.endswith(".geojson")
        ]:
            source_file_path = os.path.join(
                source_path, subdir.split(os.sep)[-1], file_name
            )
            results_file_path = os.path.join(
                results_path, subdir.split(os.sep)[-1], file_name
            )

            if os.path.exists(source_file_path):
                if clean or not os.path.exists(results_file_path):
                    os.makedirs(
                        os.path.join(results_path, subdir.split(os.sep)[-1]),
                        exist_ok=True,
                    )
                    shutil.copyfile(source_file_path, results_file_path)
                    not quiet and print(
                        f"✓ Copy {os.path.basename(source_file_path)} to {os.path.basename(results_file_path)}"
                    )
                else:
                    not quiet and print(
                        f"✓ Already exists {os.path.basename(results_file_path)}"
                    )
            else:
                not quiet and print(
                    f"✗️ Error: Source file does not exist {os.path.basename(source_file_path)}"
                )
