import os
import argparse
import re
from typing import List, Optional

from converter import (
    convert_heic_to_jpeg,
    convert_heic_file,
    convert_multiple_heic_files,
    generate_unique_filename
)


def parse_args():
    """
    Parse command line arguments

    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Convert HEIC files to JPEG')

    # Input selection options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--path', help='Path to directory or file to convert')
    input_group.add_argument('--files', nargs='+', help='List of specific HEIC files to convert')

    # Conversion options
    parser.add_argument('-r', '--remove', help='Remove converted HEIC Files', action='store_true')
    parser.add_argument('-o', '--overwrite', help='Overwrite existing JPEG files', action='store_true')
    parser.add_argument('--not-recursive', help='Do not search subdirectories', action='store_true')
    parser.add_argument('--skip-prompt', help='Skip the prompt at the end', action='store_true')
    parser.add_argument('-q', '--quality', help='Quality of the JPG Files, default: 95', type=int,
                        default=95)
    parser.add_argument('-t', '--target',
                        help='The target directory for the converted files')
    parser.add_argument('--unique', help='Generate unique filenames when target exists', action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')

    return parser.parse_args()


def main():
    """Main function for CLI operation"""
    args = parse_args()
    current_path = os.path.abspath(os.getcwd())

    # Validate quality value
    quality = max(1, min(100, args.quality))

    # Process file or directory path
    if args.path:
        path = os.path.abspath(args.path)

        # Determine target directory
        if args.target:
            target = args.target
        elif os.path.isdir(path):
            target = path
        else:
            target = os.path.dirname(path)
    else:
        # If using --files option
        path = None
        target = args.target or current_path

    # Ensure target directory exists
    if not os.path.exists(target):
        os.makedirs(target)
        print(f"Created target directory: {target}")

    # Handle conversion based on input type
    if args.files:
        print(f'Converting {len(args.files)} specified HEIC files to {target}')
        converted = convert_multiple_heic_files(
            args.files,
            args.overwrite,
            args.remove,
            quality,
            target,
            generate_unique=args.unique,
            verbose=args.verbose
        )
        print(f'\nSuccessfully converted {len(converted)} files')
    elif os.path.isdir(path):
        print(f'Converting HEIC files in directory {path} to {target}')
        converted = convert_heic_to_jpeg(
            path,
            not args.not_recursive,
            args.overwrite,
            args.remove,
            quality,
            target,
            generate_unique=args.unique,
            verbose=args.verbose
        )
        print(f'\nSuccessfully converted {len(converted)} files')
    elif os.path.isfile(path):
        t_file = os.path.join(target, os.path.basename(path).split('.')[0]) + ".jpg"
        if args.unique and os.path.exists(t_file) and not args.overwrite:
            t_file = generate_unique_filename(t_file)

        print(f'Converting HEIC file {path} to {t_file}')
        success = convert_heic_file(path, t_file, args.overwrite, args.remove, quality, verbose=args.verbose)
        print(f'\nSuccessfully converted file: {"Yes" if success else "No"}')
    else:
        print(f'Don\'t know what to do with {path}')

    if not args.skip_prompt:
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()
