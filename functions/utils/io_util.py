import glob
import os
import shutil
import tarfile
import zipfile


def cp(source_pattern, destination):
    # Expand the source pattern to match files and directories
    for source in glob.glob(source_pattern):
        # Determine the destination path
        if os.path.isdir(destination):
            dest_path = os.path.join(destination, os.path.basename(source))
        else:
            dest_path = destination

        # Copy file or directory
        if os.path.isdir(source):
            shutil.copytree(source, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source, dest_path)


def unzip(target_archive_path, dest_archive_path):
    # Find all files matching the pattern
    archive_files = glob.glob(target_archive_path)

    if not archive_files:
        raise FileNotFoundError(f"No files matching pattern: {target_archive_path}")

    for archive_file in archive_files:
        # Determine the archive type based on the file extension
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
