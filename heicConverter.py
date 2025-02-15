import os
import argparse

from converter import convert_heic_to_jpeg, convert_heic_file


def parse_args():
    """
    Parse command line arguments

    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Convert HEIC files to JPEG')
    parser.add_argument('path', help='the path to the file or directory to convert', default='./', nargs='?')
    parser.add_argument('-r', '--remove', help='Remove converted HEIC Files', action='store_true')
    parser.add_argument('-o', '--overwrite', help='Overwrite existing JPEG files', action='store_true')
    parser.add_argument('--not-recursive', help='Do not search subdirectories', action='store_true')
    parser.add_argument('--skip-prompt', help='Skip the prompt at the end', action='store_true')
    parser.add_argument('-q', '--quality', help='Quality of the JPG Files, default: 95', type=int,
                        default=95)
    parser.add_argument('-t', '--target',
                        help='The target directory for the converted files if not given, the source directory is used')

    return parser.parse_args()


if __name__ == '__main__':
    path = os.path.abspath(os.getcwd())

    args = parse_args()
    if args.path:
        path = args.path

    path = os.path.abspath(path)

    if args.target:
        target = args.target
    elif os.path.isdir(path):
        target = path
    else:
        target = os.path.dirname(path)

    if os.path.isdir(path):
        print(f'Converting HEIC files in directory {path} to {target}')
        converted = convert_heic_to_jpeg(path,
                                         not args.not_recursive,
                                         args.overwrite,
                                         args.remove,
                                         args.quality,
                                         target)

        print(f'\nSuccessfully converted {len(converted)} files')

    elif os.path.isfile(path):
        t_file = os.path.join(target, os.path.basename(path).split('.')[0]) + ".jpg"
        print(f'Converting HEIC file {path} to {t_file}')
        convert_heic_file(path, t_file, args.overwrite, args.remove, args.quality)
        print(f'\nSuccessfully converted file')

    else:
        print(f'Dont know what to do with {path}')

    if not args.skip_prompt:
        input("Press Enter to continue...")
