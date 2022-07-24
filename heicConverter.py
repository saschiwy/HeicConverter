import os
import sys
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import piexif
import fnmatch

register_heif_opener()


def get_file_list(dir_of_interest):
    file_list = []

    for root, dirs, files in os.walk(dir_of_interest):
        for file in files:
            if fnmatch.fnmatch(file.lower(), '*.heic'):
                file_list.append([root.replace('\\', '/').replace('//', '/'), file])

    return file_list


def convert_heic_to_jpeg(dir_of_interest):
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

        image = Image.open(root + "/" + filename)
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
            image.save(target_file, "jpeg", exif = exif_bytes)
            print(f'Converted image: {filename}')

            success_files.append(filename)
        else:
            print(f"Unable to get exif data for {filename}")

    return success_files


if __name__ == '__main__':
    path = os.path.abspath(os.getcwd())

    if len(sys.argv) > 1:
        path = sys.argv[1]

    converted = convert_heic_to_jpeg(path)
    print(f'\nSuccessfully converted {len(converted)} files')

    input("Press Enter to continue...")
