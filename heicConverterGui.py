import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext  # Added for the console output
from converter import convert_heic_to_jpeg, convert_heic_file


class HEICConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("HEIC to JPEG Converter")

        self.path_label = tk.Label(master, text="File or Directory Path:")
        self.path_label.pack(anchor='w')

        self.path_entry = tk.Entry(master, width=50)
        self.path_entry.pack(anchor='w')

        self.browse_button = tk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack(anchor='w')

        self.remove_var = tk.BooleanVar()
        self.remove_check = tk.Checkbutton(master, text="Remove converted HEIC Files", variable=self.remove_var)
        self.remove_check.pack(anchor='w')

        self.overwrite_var = tk.BooleanVar()
        self.overwrite_check = tk.Checkbutton(master, text="Overwrite existing JPEG files", variable=self.overwrite_var)
        self.overwrite_check.pack(anchor='w')

        self.recursive_var = tk.BooleanVar(value=True)  # Set the default value to True
        self.recursive_check = tk.Checkbutton(master, text="Search subdirectories", variable=self.recursive_var)
        self.recursive_check.pack(anchor='w')

        self.convert_button = tk.Button(master, text="Convert", command=self.convert)
        self.convert_button.pack(anchor='w')

        # Console Output
        self.console_output = scrolledtext.ScrolledText(master, width=80, height=20, wrap=tk.WORD)
        self.console_output.pack(anchor='w')

    def browse(self):
        file_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

    def convert(self):
        path = self.path_entry.get()
        remove = self.remove_var.get()
        overwrite = self.overwrite_var.get()
        recursive = self.recursive_var.get()

        output_text = ""

        if os.path.isdir(path):
            output_text += f'Converting HEIC files in directory {path}\n'
            converted = convert_heic_to_jpeg(path, recursive, overwrite, remove)
            output_text += f'Successfully converted {len(converted)} files\n'

        elif os.path.isfile(path):
            output_text += f'Converting HEIC file {path}\n'
            convert_heic_file(path, os.path.splitext(path)[0] + ".jpg", overwrite, remove)
            output_text += 'Successfully converted file\n'

        else:
            output_text += f'Don\'t know what to do with {path}\n'

        self.console_output.insert(tk.END, output_text)
        self.console_output.see(tk.END)  # Scroll to the end

def main():
    root = tk.Tk()
    gui = HEICConverterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
