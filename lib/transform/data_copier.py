import os
import shutil
from datetime import datetime

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def copy_data(source_path, results_path, clean=False, quiet=False):
    timestamp = datetime.now().strftime("%Y-%m")

    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):
        for source_file_name in sorted(files):
            subdir = subdir.replace(f"{source_path}/", "")
            results_file_name = source_file_name

            # Make results path
            os.makedirs(os.path.join(results_path, subdir.replace("-csv", "") + (
                f"-{timestamp}" if "daycare-centers" in subdir else "")), exist_ok=True)

            source_file_path = os.path.join(source_path, subdir, source_file_name)
            results_file_path = os.path.join(results_path,
                                             subdir.replace("-csv", "") + (
                                                 f"-{timestamp}" if "daycare-centers" in subdir else ""),
                                             results_file_name)

            # Check if file needs to be copied
            if clean or not os.path.exists(results_file_path):
                shutil.copyfile(source_file_path, results_file_path)

                if not quiet:
                    print(f"✓ Copy {results_file_name}")
            else:
                print(f"✓ Already exists {results_file_name}")
