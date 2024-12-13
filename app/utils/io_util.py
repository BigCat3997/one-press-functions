import glob
import os
import shutil
import tarfile
import zipfile


def cp(source_pattern, destination):
    for source in glob.glob(source_pattern):
        if os.path.isdir(destination):
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            dest_path = destination

        if os.path.isdir(source):
            shutil.copytree(source, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source, dest_path)


def unzip(target_archive_path, dest_archive_path):
    archive_files = glob.glob(target_archive_path)

    if not archive_files:
        raise FileNotFoundError(f"No files matching pattern: {target_archive_path}")

    for archive_file in archive_files:
        if archive_file.endswith(".zip"):
            with zipfile.ZipFile(archive_file, "r") as zip_ref:
                zip_ref.extractall(dest_archive_path)
                print(f"Extracted {archive_file} to {dest_archive_path}")
        elif (
            archive_file.endswith(".tar")
            or archive_file.endswith(".tar.gz")
            or archive_file.endswith(".tar.bz2")
        ):
            with tarfile.open(archive_file, "r:*") as tar_ref:
                tar_ref.extractall(dest_archive_path)
                print(f"Extracted {archive_file} to {dest_archive_path}")
        else:
            raise ValueError(
                f"The file {archive_file} is not a supported archive format"
            )

    print("> Verify content of at current directory.")
    for item in os.listdir(dest_archive_path):
        path = os.path.join(dest_archive_path, item)
        print(path)


def delete_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    else:
        raise FileNotFoundError(f"Path not found: {path}")
