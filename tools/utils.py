from os import path, listdir

def prepare_files_pathnames_for_directory(directory: str, file_extension: str = "") -> list[str]:
    return [path.join(directory, file) for file in listdir(directory) if file.endswith(file_extension)]

def get_filenames_from_directory(directory: str, file_extension: str = "") -> list[str]:
    return [filename for filename in listdir(directory) if filename.endswith(file_extension)]
