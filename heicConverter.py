import os
import sys
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import piexif
import fnmatch
import argparse

register_heif_opener()


def get_file_list(dir_of_interest, recursive):
    """
    Get a list of all files in the directory of interest

    :param dir_of_interest: the directory to search
    :param recursive: search subdirectories

    :return: a list of files
    """
    file_list = []

    for root, dirs, files in os.walk(dir_of_interest):
        if not recursive:
            dirs.clear()

        for file in files:
            if fnmatch.fnmatch(file.lower(), '*.heic'):
                file_list.append([root.replace('\\', '/').replace('//', '/'), file])

    return file_list


def convert_heic_file(source_file, target_file, overwrite, remove):
    """
    Convert a single heic file to jpeg

    :param source_file: the source file
    :param target_file: the target file
    :param overwrite: overwrite existing jpeg files
    :param remove: remove converted heic files

    :return: True if successful, False otherwise
    """

    if os.path.exists(target_file):
        if overwrite:
            os.remove(target_file)
        else:
            print(f'File {target_file} already exists, skip')
            if remove:
                os.remove(source_file)
            return False

    success = False

    try:
        image = Image.open(source_file)
        image_exif = image.getexif()
        if image_exif:
            # Make a map with tag names and grab the datetime
            exif = {ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes}
            if 'DateTime' in exif:
                date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
            else:
                date = datetime.now()

            # Load exif data via piexif
            exif_dict = piexif.load(image.info["exif"])

            # Update exif data with orientation and datetime
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
            exif_bytes = piexif.dump(exif_dict)

            # Save image as jpeg
            image.save(target_file, "jpeg", exif=exif_bytes)
            print(f'Converted image: {source_file}')

            success = True
        else:
            print(f"Unable to get exif data for {source_file}")

    except Exception as e:
        print(f"Unable to convert {source_file}: {e}")

    if success and remove:
        os.remove(source_file)

    return success


def convert_heic_to_jpeg(dir_of_interest, recursive, overwrite, remove):
    """
    Convert all heic files in the directory of interest to jpeg

    :param dir_of_interest: The directory to search
    :param recursive: search subdirectories
    :param overwrite: overwrite existing jpeg files
    :param remove: remove converted heic files

    :return: a list of successfully converted files
    """
    heic_files = get_file_list(dir_of_interest, recursive)

    # Extract files of interest
    success_files = []

    print(f'Found {len(heic_files)} files to convert in folder {dir_of_interest}')

    # Convert files to jpg while keeping the timestamp
    for root, filename in heic_files:

        target_filename = os.path.splitext(filename)[0] + ".jpg"
        target_file = root + "/" + target_filename

        if convert_heic_file(f'{root}/{filename}', target_file, overwrite, remove):
            success_files.append(target_filename)

    return success_files


def parse_args():
    """
    Parse command line arguments

    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Convert HEIC files to JPEG')
    parser.add_argument('path', help='the path to the file or directory to convert')
    parser.add_argument('-r', '--remove', help='Remove converted HEIC Files', action='store_true')
    parser.add_argument('-o', '--overwrite', help='Overwrite existing JPEG files', action='store_true')
    parser.add_argument('--not-recursive', help='Do not search subdirectories', action='store_true')
    parser.add_argument('--skip-prompt', help='Skip the prompt at the end', action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    path = os.path.abspath(os.getcwd())

    args = parse_args()
    if args.path:
        path = args.path

    if os.path.isdir(path):
        print(f'Converting HEIC files in directory {path}')
        converted = convert_heic_to_jpeg(path, not args.not_recursive, args.overwrite, args.remove)
        print(f'\nSuccessfully converted {len(converted)} files')

    elif os.path.isfile(path):
        print(f'Converting HEIC file {path}')
        convert_heic_file(path, os.path.splitext(path)[0] + ".jpg", args.overwrite, args.remove)
        print(f'\nSuccessfully converted file')

    else:
        print(f'Dont know what to do with {path}')

    if not args.skip_prompt:
        input("Press Enter to continue...")
