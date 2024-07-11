import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.txt",
    version="1.0.1.0",
    company_name="Noah Blaszak",
    file_description="Hominum Minecraft Launcher",
    internal_name="Hominum Client",
    legal_copyright="© Noah Blaszak. All rights reserved.",
    original_filename="Hominum.exe",
    product_name="Hominum"
)