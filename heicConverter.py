import os
import argparse

from converter import convert_heic_to_jpeg, convert_heic_file


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
