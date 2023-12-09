import os
import sys
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import piexif
import fnmatch

register_heif_opener()


def get_file_list(dir_of_interest):
    """
    Get a list of all files in the directory of interest

    :param dir_of_interest: the directory to search

    :return: a list of files
    """
    file_list = []

    for root, dirs, files in os.walk(dir_of_interest):
        for file in files:
            if fnmatch.fnmatch(file.lower(), '*.heic'):
                file_list.append([root.replace('\\', '/').replace('//', '/'), file])

    return file_list


def convert_heic_file(source_file, target_file):
    """"
    Convert a single heic file to jpeg

    :param source_file: the source file
    :param target_file: the target file

    :return: True if successful, False otherwise
    """
    image = Image.open(source_file)
    image_exif = image.getexif()
    if image_exif:
        # Make a map with tag names and grab the datetime
        exif = {ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes}
        date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')

        # Load exif data via piexif
        exif_dict = piexif.load(image.info["exif"])

        # Update exif data with orientation and datetime
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
        exif_bytes = piexif.dump(exif_dict)

        # Save image as jpeg
        image.save(target_file, "jpeg", exif=exif_bytes)
        print(f'Converted image: {source_file}')

        return True
    else:
        print(f"Unable to get exif data for {source_file}")
        return False


def convert_heic_to_jpeg(dir_of_interest):
    """
    Convert all heic files in the directory of interest to jpeg

    :param dir_of_interest: The directory to search

    :return: a list of successfully converted files
    """
    heic_files = get_file_list(dir_of_interest)

    # Extract files of interest
    success_files = []

    print(f'Found {len(heic_files)} files to convert in folder {dir_of_interest}')

    # Convert files to jpg while keeping the timestamp
    for root, filename in heic_files:

        target_filename = os.path.splitext(filename)[0] + ".jpg"
        target_file = root + "/" + target_filename
        if os.path.exists(target_file):
            print(f'File {target_filename} already exists, skip')
            continue

        if convert_heic_file(f'{root}/{filename}', target_file):
            success_files.append(target_filename)

    return success_files


if __name__ == '__main__':
    path = os.path.abspath(os.getcwd())

    if len(sys.argv) > 1:
        path = sys.argv[1]

    if os.path.isdir(path):
        print(f'Converting HEIC files in directory {path}')
        converted = convert_heic_to_jpeg(path)
        print(f'\nSuccessfully converted {len(converted)} files')

    elif os.path.isfile(path):
        print(f'Converting HEIC file {path}')
        convert_heic_file(path, os.path.splitext(path)[0] + ".jpg")
        print(f'\nSuccessfully converted file')

    else:
        print(f'Dont know what to do with {path}')

    input("Press Enter to continue...")
