import os
import re

import pandas as pd

from lib.tracking_decorator import TrackingDecorator


@TrackingDecorator.track_time
def convert_data_to_csv(source_path, results_path, clean=False, quiet=False):
    # Iterate over files
    for subdir, dirs, files in sorted(os.walk(source_path)):

        # Make results path
        subdir = subdir.replace(f"{source_path}/", "")
        os.makedirs(os.path.join(results_path, subdir), exist_ok=True)

        for file_name in [file_name for file_name in sorted(files) if file_name.endswith("-details.xlsx")]:
            source_file_path = os.path.join(source_path, subdir, file_name)
            convert_file_to_csv(source_file_path, clean=clean, quiet=quiet)


def convert_file_to_csv(source_file_path, clean=False, quiet=False):
    source_file_name, source_file_extension = os.path.splitext(source_file_path)
    file_path_csv = f"{source_file_name}.csv"

    # Check if result needs to be generated
    if clean or not os.path.exists(file_path_csv):
        # Determine engine
        if source_file_extension == ".xlsx":
            engine = "openpyxl"
        elif source_file_extension == ".xls":
            engine = None
        else:
            return

        # year = os.path.basename(source_file_name).split(sep="-")[4]
        # month = os.path.basename(source_file_name).split(sep="-")[5]
        # day = os.path.basename(source_file_name).split(sep="-")[6]

        try:
            sheet = "Sheet1"
            skiprows = 5
            names = ["district_id", "district_name", "id", "name", "street", "zip_code", "phone_number", "places",
                     "type", "sponsor_id", "sponsor_name", "sponsor_type"]
            drop_columns = ["district_id", "district_name"]

            # Iterate over sheets
            dataframe = pd.read_excel(source_file_path, engine=engine, sheet_name=sheet, skiprows=skiprows,
                                      usecols=list(range(0, len(names))), names=names) \
                .drop(columns=drop_columns, errors="ignore") \
                .dropna() \
                .replace("–", 0) \
                .assign(id=lambda df: df["id"].astype(int)) \
                .assign(zip_code=lambda df: df["zip_code"].astype(int)) \
                .assign(places=lambda df: df["places"].astype(int)) \
                .assign(sponsor_id=lambda df: df["sponsor_id"].astype(int)) \
                .assign(name=lambda df: df["name"]
                        .apply(lambda row: row.replace('"', '')
                               .replace("str.", "straße")
                               .replace("Str.", "Straße")
                               .replace("AWO ", "")
                               .replace("EKT- ", "")
                               .replace("EKT - ", "")
                               .replace("EKT ", "")
                               .replace(" (KIB)", "")
                               .replace(" (KiB)", "")
                               .replace(" -Kita", "-Kita")
                               .replace("/Kigä City", "")
                               .replace(" Kigä City", "")
                               .replace("Kigä City", "")
                               .replace("/Kigä NordOst", "")
                               .replace("/Kitas Süd-West", "")
                               .replace("/Kitas Süd-West", "")
                               .replace(" / Kitas SüdOst", "")
                               .replace("/Hs 1u.2", "")
                               .replace("/Haus vorn rechts", "")
                               .replace(" (EG links)", "")
                               .replace(" (Wohneinheit links)", "")
                               .replace("der Kinderladen", "Kinderladen")
                               .replace("/Nachbarschaftshaus Urbanstraße", " (Nachbarschaftshaus Urbanstraße)")
                               .replace(" /Nachbarschaftshs Urbanstraße", " (Nachbarschaftshaus Urbanstraße)")
                               .replace("FRÖBEL - Kindergarten", "FRÖBEL-Kindergarten")
                               .replace("Kinder- u.Jugendzentrum", "Kinder- und Jugendzentrum")
                               .replace("Gesellschaft f.intern.Kultur- u.Bildungsarbeit",
                                        "Gesellschaft Für Internationale Kultur- Und Bildungsarbeit E.v")
                               .replace("Colbestraße9 - 13", "Colbestraße 9")
                               )) \
                .assign(name=lambda df: df["name"].apply(lambda row: re.sub(r"\"", "", row))) \
                .assign(name=lambda df: df["name"].apply(lambda row: re.sub(r"/\d+", "", row))) \
                .assign(name=lambda df: df["name"].apply(lambda row: re.sub(r"-\d+", "", row))) \
                .assign(street=lambda df: df["street"]
                        .apply(lambda row: " ".join(word.lstrip("0") for word in row.split(" "))
                               .replace("str.", "straße")
                               .replace("Str.", "Straße")
                               .replace("- ", "-")
                               .replace(" - ", "-")
                               .replace("/", "-")
                               .replace("Ecke Virchowstraße", "")
                               .replace("Ecke Eintrachtstraße", "")
                               .replace("Ecke Bornholmer Straße 11", "")
                               .replace("Oppelner Straße 21", "")
                               .replace("/Haus 23", "")
                               .replace("- Haus 25", "")
                               .replace("Haus 2", "")
                               .replace("Haus 6", "")
                               .replace("Haus 61", "")
                               .replace("Haus 35", "")
                               .replace("Haus 50", "")
                               .replace("I-II", "")
                               .replace("EG link", "")
                               .replace(",C", "")
                               .replace("u. 164", "")
                               .replace("Postadresse: nur Trägerad", "")
                               .replace("- Krampenburger Weg 2", "")
                               .replace("- Ostendstraße 15", "")
                               .replace("und 25", "")
                               .replace("Bundesallee 186187", "Bundesallee 186-187")
                               .replace("Dietzgenstraße 79tatsächlich 81", "Dietzgenstraße 81")
                               .replace("Charitéplatz 1tatsächlich: Hufelandweg 12A", "Hufelandweg 12A")
                               .replace("Bundesallee 186187", "Bundesallee 186-187")
                               .replace("Dietzgenstraße 79tatsächlich 81", "Dietzgenstraße 81")
                               .replace("Charitéplatz 1tatsächlich: Hufelandweg 12A", "Hufelandweg 12A")
                               .replace("Mertensstraße 14tatsächlich 10 - 14", "Mertensstraße 10")
                               .replace("Schwanheimer Straße 3tatsächlich 1-7", "Schwanheimer Straße 1-7")
                               .replace("Giesestraße 47tatsächlich 43", "Giesestraße 43")
                               .replace("Ratiborstraße 8Reichenberger Straße 91", "Ratiborstraße 8")
                               .replace("Mertensstraße 14tatsächlich 10 -14", "Mertensstraße 10")
                               .replace("Magistratsweg 73tatsächlich 69", "Magistratsweg 69")
                               .replace("Rathener Straße 3und 7 und 18", "Rathener Straße 7")
                               .replace("Waldowstraße 40- Manetstraße 23", "Waldowstraße 40")
                               .replace("Staehleweg 1tatsächlich 46", "Staehleweg 46")
                               .replace("Staehleweg 1tatsächlich 53", "Staehleweg 53")
                               .replace("MartinOpitzStraße", "Martin-Opitz-Straße")
                               .rstrip("EG")
                               .rstrip("EG rechts")
                               .rstrip("links")
                               .rstrip("link")
                               .rstrip("rechts")
                               .rstrip("Flughafen Tempelhof")
                               .rstrip("Am Sportplatz")
                               )) \
                .assign(street=lambda df: df["street"].apply(lambda row: re.sub(r"\(.*?\)", "", row))) \
                .assign(street=lambda df: df["street"].apply(lambda row: re.sub(r"-\d+", "", row))) \
                .assign(sponsor_name=lambda df: df["sponsor_name"].apply(lambda row: row.replace('"', ''))) \
                .assign(phone_number=lambda df: df["phone_number"]
                        .apply(lambda
                                   row: f"+4930{row.replace(' ', '').replace('/', '').replace('-', '').lstrip('‭').rstrip('‬').lstrip('030').lstrip('(030)')}" if len(
                row.replace("-", "")) > 0 else ""))

            # Write csv file
            if dataframe.shape[0] > 0:
                dataframe.to_csv(file_path_csv, index=False)
            if not quiet:
                print(f"✓ Convert {os.path.basename(file_path_csv)}")
            else:
                if not quiet:
                    print(dataframe.head())
                    print(f"✗️ Empty {os.path.basename(file_path_csv)}")
        except Exception as e:
            print(f"✗️ Exception: {str(e)}")
    elif not quiet:
        print(f"✓ Already exists {os.path.basename(file_path_csv)}")
