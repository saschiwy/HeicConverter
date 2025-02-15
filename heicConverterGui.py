import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk  # ttk for modern themed widgets
from converter import convert_heic_to_jpeg, convert_heic_file
import platform

# Handle DPI awareness for Windows
if platform.system() == "Windows":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class HEICConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("HEIC to JPEG Converter")
        master.geometry("800x700")  # Set a default size for the window

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TCheckbutton", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)

        self.path_label = ttk.Label(master, text="File or Directory Path:")
        self.path_label.pack(anchor='w', padx=10, pady=5)

        path_frame = ttk.Frame(master)
        path_frame.pack(anchor='w', padx=10, pady=5, fill='x')

        self.path_entry = ttk.Entry(path_frame, width=50)
        self.path_entry.pack(side='left', padx=(0, 5))

        self.browse_button = ttk.Button(path_frame, text="Browse", command=self.browse)
        self.browse_button.pack(side='left')

        self.target_label = ttk.Label(master, text="Target Path:")
        self.target_label.pack(anchor='w', padx=10, pady=5)

        target_frame = ttk.Frame(master)
        target_frame.pack(anchor='w', padx=10, pady=5, fill='x')

        self.target_entry = ttk.Entry(target_frame, width=50)
        self.target_entry.pack(side='left', padx=(0, 5))

        self.browse_button = ttk.Button(target_frame, text="Browse", command=self.browse_target)
        self.browse_button.pack(side='left')

        self.remove_var = tk.BooleanVar()
        self.remove_check = ttk.Checkbutton(master, text="Remove converted HEIC Files", variable=self.remove_var)
        self.remove_check.pack(anchor='w', padx=10, pady=5)

        self.overwrite_var = tk.BooleanVar()
        self.overwrite_check = ttk.Checkbutton(master, text="Overwrite existing JPEG files",
                                               variable=self.overwrite_var)
        self.overwrite_check.pack(anchor='w', padx=10, pady=5)

        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(master, text="Search subdirectories", variable=self.recursive_var)
        self.recursive_check.pack(anchor='w', padx=10, pady=5)

        self.quality_label = ttk.Label(master, text="Quality (1-100):")
        self.quality_label.pack(anchor='w', padx=10, pady=5)

        self.quality_scale = tk.Scale(master, from_=1, to=100, orient=tk.HORIZONTAL)
        self.quality_scale.set(95)  # Default value
        self.quality_scale.pack(anchor='w', padx=10, pady=5)

        self.convert_button = ttk.Button(master, text="Convert", command=self.convert)
        self.convert_button.pack(anchor='w', padx=10, pady=5)

        # Console Output
        self.console_output = scrolledtext.ScrolledText(master, width=80, height=20, wrap=tk.WORD)
        self.console_output.pack(anchor='w', padx=10, pady=10)

    def browse(self):
        file_path = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

        if self.target_entry.get() == "":
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, file_path)

    def browse_target(self):
        file_path = filedialog.askdirectory()
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, file_path)

    def convert(self):
        path = self.path_entry.get()
        target = self.target_entry.get()
        remove = self.remove_var.get()
        overwrite = self.overwrite_var.get()
        recursive = self.recursive_var.get()
        quality = int(self.quality_entry.get())

        # Ensure quality is within the range 1-100
        if quality > 100:
            quality = 100
        elif quality < 1:
            quality = 1

        output_text = ""

        if os.path.isdir(path):
            output_text += f'Converting HEIC files in directory {path} to {target}\n'
            converted = convert_heic_to_jpeg(path, recursive, overwrite, remove, quality, target)
            output_text += f'Successfully converted {len(converted)} files\n'

        elif os.path.isfile(path):
            t_file = os.path.join(target, os.path.basename(path).split('.')[0]) + ".jpg"
            output_text += f'Converting HEIC file {path} to {t_file}\n'
            convert_heic_file(path, t_file, overwrite, remove, quality)
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
