import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk  # ttk for modern themed widgets
from converter import convert_heic_to_jpeg, convert_heic_file
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

class HEICConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("HEIC to JPEG Converter")
        master.geometry("600x500")  # Set a default size for the window

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TCheckbutton", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)

        self.path_label = ttk.Label(master, text="File or Directory Path:")
        self.path_label.pack(anchor='w', padx=10, pady=5)

        self.path_entry = ttk.Entry(master, width=50)
        self.path_entry.pack(anchor='w', padx=10, pady=5)

        self.browse_button = ttk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack(anchor='w', padx=10, pady=5)

        self.remove_var = tk.BooleanVar()
        self.remove_check = ttk.Checkbutton(master, text="Remove converted HEIC Files", variable=self.remove_var)
        self.remove_check.pack(anchor='w', padx=10, pady=5)

        self.overwrite_var = tk.BooleanVar()
        self.overwrite_check = ttk.Checkbutton(master, text="Overwrite existing JPEG files", variable=self.overwrite_var)
        self.overwrite_check.pack(anchor='w', padx=10, pady=5)

        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(master, text="Search subdirectories", variable=self.recursive_var)
        self.recursive_check.pack(anchor='w', padx=10, pady=5)

        self.convert_button = ttk.Button(master, text="Convert", command=self.convert)
        self.convert_button.pack(anchor='w', padx=10, pady=5)

        # Console Output
        self.console_output = scrolledtext.ScrolledText(master, width=80, height=20, wrap=tk.WORD)
        self.console_output.pack(anchor='w', padx=10, pady=10)

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
        self.console_output.see(tk.END)

def main():
    root = tk.Tk()
    gui = HEICConverterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
