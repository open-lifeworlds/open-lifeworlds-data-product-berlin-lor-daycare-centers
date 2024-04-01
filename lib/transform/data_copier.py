import os
import re
import shutil

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def copy_data(source_path, results_path, clean=False, quiet=False):
    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):
        for source_file_name in sorted(files):
            subdir = subdir.replace(f"{source_path}/", "")
            results_file_name = source_file_name

            if "daycare-centers" in subdir:
                year = re.findall(r"\b\d{4}\b", source_file_name)[0]
                month = re.findall(r"\b\d{2}\b", source_file_name)[0]
                timestamp = f"{year}-{month}"

                # Make results path
                os.makedirs(os.path.join(results_path, subdir.replace("-csv", "") + f"-{timestamp}"), exist_ok=True)

                source_file_path = os.path.join(source_path, subdir, source_file_name)
                results_file_path = os.path.join(results_path, subdir.replace("-csv", "") + f"-{timestamp}",
                                                 results_file_name)
            else:
                # Make results path
                os.makedirs(os.path.join(results_path, subdir.replace("-csv", "")), exist_ok=True)

                source_file_path = os.path.join(source_path, subdir, source_file_name)
                results_file_path = os.path.join(results_path, subdir.replace("-csv", ""), results_file_name)

            # Check if file needs to be copied
            if clean or not os.path.exists(results_file_path):
                shutil.copyfile(source_file_path, results_file_path)

                if not quiet:
                    print(f"✓ Copy {results_file_name}")
            else:
                print(f"✓ Already exists {results_file_name}")
