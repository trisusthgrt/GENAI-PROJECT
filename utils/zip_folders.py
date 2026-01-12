import os
import zipfile

def zip_folder(folder_path: str, zip_path: str) -> None:
    """
    Zips the contents of folder_path into zip_path.
    """
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, folder_path)
                zipf.write(abs_file, rel_path)
