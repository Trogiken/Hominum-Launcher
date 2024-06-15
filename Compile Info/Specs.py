import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.txt",
    version="3.5.1.1",
    company_name="Noah Blaszak",
    file_description="Syncronize local files with remote server",
    internal_name="Hominum Updater",
    legal_copyright="© Noah Blaszak. All rights reserved.",
    original_filename="HominumUpdater.exe",
    product_name="Hominum Updater"
)