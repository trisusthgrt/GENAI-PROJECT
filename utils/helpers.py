# Helper utility functions

import os

def saveFile(dirname: str, filename: str, content: str) -> None:
    """
    Saves the file with the given content inside 'output/<dirname>/<filename>'.
    Creates directories as needed.
    """
    base_dir = "output"
    full_dir = os.path.join(base_dir, dirname)
    os.makedirs(full_dir, exist_ok=True)
    filepath = os.path.join(full_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)