from pathlib import Path


def get_file_name(file):

    if isinstance(file, (str, Path)):
        return str(file)

    return file.name