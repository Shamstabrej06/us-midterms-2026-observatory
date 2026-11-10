import zipfile
import os
import shutil

zip_path = r"C:\Users\shams\Microsoft\Power BI Desktop Store App\User.zip"
temp_zip = zip_path + ".tmp"

with zipfile.ZipFile(zip_path, "r") as zin:
    with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "FeatureSwitches/FeatureSwitches.xml":
                xml_str = data.decode("utf-8")
                print("Original XML:\n", xml_str)
                # Ensure our preview features are present
                new_entries = """<Entry Type="22c217bb-0bd9-494a-b8f9-853ebb051ab5" Value="l1" /><Entry Type="120c1719-bdab-4415-af80-89a97943e980" Value="l1" /><Entry Type="7aaca3fd-9e92-4033-bc09-b2264a7aff3d" Value="l1" /><Entry Type="dd7dd776-cd4f-4512-8d75-8fdc37385d69" Value="l1" />"""
                # Replace Entries content
                xml_str = '<?xml version="1.0" encoding="utf-8"?><FeatureSwitchesConfig xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Entries>' + new_entries + '</Entries></FeatureSwitchesConfig>'
                data = xml_str.encode("utf-8")
                print("Updated XML:\n", xml_str)
            zout.writestr(item, data)

shutil.move(temp_zip, zip_path)
print("Updated User.zip successfully!")
