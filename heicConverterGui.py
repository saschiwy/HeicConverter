import locale
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk
import platform
import io
import sys
import json
import subprocess
from contextlib import redirect_stdout, redirect_stderr

from converter import (
    convert_heic_to_jpeg,
    convert_heic_file,
    convert_multiple_heic_files,
    generate_unique_filename
)

# Handle DPI awareness for Windows
if platform.system() == "Windows":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


def get_system_language():
    lang, _ = locale.getlocale()
    if lang:
        return lang.split('_')[0]
    return "en"


en = {
    "title": "HEIC to JPEG Converter",
    "convert_button": "Convert",
    "open_folder_button": "Open Destination",
    "conversion_log": "Conversion Log",
    "status_ready": "Ready",
    "log_initial": "HEIC to JPEG Converter ready.\nDrag and drop HEIC files or folders here to convert them.",
    "file_paths": "File Paths",
    "input_path": "Input Path",
    "select_file_button": "Select File(s)",
    "select_directory_button": "Select Folder",
    "output_path": "Output:",
    "recursive": "Search Subdirectories",
    "preserve": "Preserve subfolder structure",
    "browse_button": "Browse",
    "conversion_options": "Conversion Options",
    "remove_converted": "Remove converted HEIC Files",
    "overwrite_existing": "Overwrite existing JPEG files",
    "quality_label": "Quality (1-100):",
    "drag_drop_enabled": "Drag and drop support enabled.",
    "drag_drop_limited": "Limited drag and drop support (tkinterdnd2 not available).",
    "drop_files_here": "Drop files here",
    "destination_not_exist": "Destination folder doesn't exist.",
    "opened_destination": "Opened destination folder: {path}",
    "error_opening_folder": "Error opening folder: {error}",
    "directory_selected": "Directory selected: {path}",
    "multiple_directories": "Note: Multiple directories dropped. Using {path}.",
    "file_selected": "1 file selected: {filename}",
    "files_selected": "{count} files selected",
    "added_files": "Added {count} HEIC files for conversion.",
    "no_valid_files": "No valid HEIC files found in the dropped items.",
    "target_directory": "Target directory: {path}",
    "converting": "Converting...",
    "conversion_settings": "Conversion settings:",
    "quality_percent": "- Quality: {quality}%",
    "remove_originals": "- Remove originals: {value}",
    "overwrite_existing_option": "- Overwrite existing: {value}",
    "generate_unique_filenames": "- Generate unique filenames: Yes",
    "search_subdirectories": "- Search subdirectories: {value}",
    "preserve_structure_option": "- Preserve structure: {value}",
    "created_target_directory": "Created target directory: {path}",
    "converting_selected_files": "Converting {count} selected file(s)...",
    "successfully_converted": "Successfully converted {converted} out of {total} files",
    "converted_files": "Converted {count} files",
    "converting_directory": "Converting HEIC files in directory {path} to {target}",
    "converting_file": "Converting HEIC file {path} to {target_file}",
    "conversion_successful": "Conversion successful",
    "conversion_failed": "Conversion failed",
    "invalid_path": "Invalid path: {path}",
    "error_invalid_path": "Error: Invalid path",
    "error_processing_drop": "Error processing dropped files: {error}",
    "select_language": "Select Language",
}

gui_settings = {
    "language": get_system_language(),
    "last_input_path": "",
    "last_output_path": "",
    "remove_converted": False,
    "overwrite_existing": False,
    "quality": 95,
    "search_subdirectories": True,
    "preserve_structure": True
}


class HEICConverterGUI:
    @staticmethod
    def load_language(lang_code):
        try:
            with open(os.path.join("lang", f"{lang_code}.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            if lang_code != "en":
                print(f"Language file for '{lang_code}' not found. Falling back to English.")
            return en

    @staticmethod
    def get_supported_languages():
        lang_dir = os.path.join("lang")
        if not os.path.exists(lang_dir):
            return ["en"]
        languages = ["en"]
        for filename in os.listdir(lang_dir):
            if filename.endswith(".json"):
                lang_code = os.path.splitext(filename)[0]
                languages.append(lang_code)
        return languages

    def get_text(self, key):
        try:
            return self.language[key]
        except KeyError:
            print(f"Key '{key}' not found in language file. Using English fallback.")
            return en.get(key, key)

    def load_settings(self):
        settings_file = os.path.join("heic_gui_settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.settings = settings
            except json.JSONDecodeError:
                print("No valid settings found, using default settings.")
        else:
            print("Settings file not found, using default settings.")

    def save_settings(self):
        settings_file = os.path.join("heic_gui_settings.json")

        # Update settings with current values
        self.settings["language"] = self.language_var.get()
        self.settings["last_input_path"] = self.path_entry.get()
        self.settings["last_output_path"] = self.target_entry.get()
        self.settings["remove_converted"] = self.remove_var.get()
        self.settings["overwrite_existing"] = self.overwrite_var.get()
        self.settings["quality"] = int(self.quality_value.get())
        self.settings["search_subdirectories"] = self.recursive_var.get()
        self.settings["preserve_structure"] = self.preserve_structure_var.get()

        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved successfully.")
        except IOError as e:
            print(f"Error saving settings: {e}")

    def on_close(self):
        self.save_settings()
        self.master.destroy()

    def create_language_selector(self, parent):
        """Create a dropdown for language selection"""
        lang_frame = ttk.Frame(parent)
        lang_frame.pack(fill='x', pady=5)

        self.label_text = self.get_text("select_language")
        self.lang_label = ttk.Label(lang_frame, text=self.label_text, width=len(self.label_text), anchor='w')
        self.lang_label.pack(side='left')

        self.language_var = tk.StringVar(value=self.settings.get("language", get_system_language()))
        self.language_selector = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=self.get_supported_languages(),
            state="readonly"
        )
        self.language_selector.pack(side='left', padx=5)
        # Bind selection change to immediately apply language
        self.language_selector.bind('<<ComboboxSelected>>', self.on_language_change)

    def on_language_change(self, event=None):
        """Reload language file and update visible texts immediately."""
        new_lang = event.widget.get() if (event is not None and hasattr(event, "widget")) else self.language_var.get()
        self.language = self.load_language(new_lang)
        self.settings["language"] = new_lang

        # Update window title and status text
        self.master.title(self.get_text("title"))
        self.status_var.set(self.get_text("status_ready"))
        self.convert_button.config(text=self.get_text("convert_button"))
        self.open_folder_button.config(text=self.get_text("open_folder_button"))

        # Update paths section texts
        if hasattr(self, "paths_frame"):
            self.paths_frame.config(text=self.get_text("file_paths"))
        if hasattr(self, "input_label"):
            self.input_label.config(text=self.get_text("input_path"))
        if hasattr(self, "select_file_button"):
            self.select_file_button.config(text=self.get_text("select_file_button"))
        if hasattr(self, "select_dir_button"):
            self.select_dir_button.config(text=self.get_text("select_directory_button"))
        if hasattr(self, "recursive_check"):
            self.recursive_check.config(text=self.get_text("recursive"))
        if hasattr(self, "preserve_structure_check"):
            self.preserve_structure_check.config(text=self.get_text("preserve"))
        if hasattr(self, "target_label"):
            self.target_label.config(text=self.get_text("output_path"))
        if hasattr(self, "browse_target_button"):
            self.browse_target_button.config(text=self.get_text("browse_button"))

        # Update options section texts
        if hasattr(self, "options_frame"):
            self.options_frame.config(text=self.get_text("conversion_options"))
        if hasattr(self, "remove_check"):
            self.remove_check.config(text=self.get_text("remove_converted"))
        if hasattr(self, "overwrite_check"):
            self.overwrite_check.config(text=self.get_text("overwrite_existing"))
        if hasattr(self, "quality_label"):
            self.quality_label.config(text=self.get_text("quality_label"))

        # Update language selector label if present
        if hasattr(self, "lang_label"):
            self.lang_label.config(text=self.get_text("select_language"))

        # Update log frame title if present
        if hasattr(self, "log_frame"):
           self.log_frame.config(text=self.get_text("conversion_log"))

        # Update log frame title and initial log text
        if hasattr(self, "console_output"):
            self.log(self.get_text("log_initial"))
        # Optionally save the setting immediately
        self.save_settings()

    def __init__(self, master):
        self.settings = gui_settings.copy()
        self.load_settings()

        self.language = self.load_language(self.settings.get("language", get_system_language()))

        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        master.title(self.get_text("title"))
        master.geometry("1000x800")
        self.bg_color = "#f0f0f0"
        master.configure(bg=self.bg_color)
        self.selected_files = []
        self.create_custom_theme()
        main_frame = ttk.Frame(master, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)
        self.create_paths_section(main_frame)
        self.create_options_section(main_frame)
        self.create_language_selector(master)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill='x')
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor='center')
        self.convert_button = ttk.Button(
            button_container,
            text=self.get_text('convert_button'),
            command=self.convert,
            style="Action.TButton",
            width=15
        )
        self.convert_button.pack(side=tk.LEFT, padx=5)
        self.open_folder_button = ttk.Button(
            button_container,
            text=self.get_text('open_folder_button'),
            command=self.open_destination_folder,
            width=15
        )
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        self.log_frame = ttk.LabelFrame(main_frame, text=self.get_text('conversion_log'), padding="5 5 5 5")
        self.log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.console_output = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=10,
            borderwidth=1,
            relief="solid"
        )
        self.console_output.pack(fill='both', expand=True)
        self.status_var = tk.StringVar(value=self.get_text("status_ready"))
        status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.setup_drag_drop()
        self.log(self.get_text("log_initial"))

    def create_custom_theme(self):
        style = ttk.Style()
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabelframe", background=self.bg_color)
        style.configure("TLabelframe.Label", background=self.bg_color, font=("Helvetica", 11, "bold"))
        style.configure("TButton", font=("Helvetica", 11), padding=8)
        style.configure("Action.TButton", font=("Helvetica", 12, "bold"), padding=10)
        style.configure("TLabel", background=self.bg_color, font=("Helvetica", 11), padding=5)
        style.configure("TEntry", font=("Helvetica", 11), padding=8)
        style.configure("TCheckbutton", background=self.bg_color, font=("Helvetica", 11), padding=5)

    def create_paths_section(self, parent):
        self.paths_frame = ttk.LabelFrame(parent, text=self.get_text("file_paths"), padding="10 5 10 10")
        self.paths_frame.pack(fill='x', padx=5, pady=5)
        input_frame = ttk.Frame(self.paths_frame)
        input_frame.pack(fill='x', pady=5)
        self.input_label = ttk.Label(input_frame, text=self.get_text("input_path"), width=10, anchor='w')
        self.input_label.pack(side='left')
        self.path_entry = ttk.Entry(input_frame)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.path_entry.insert(0, self.settings.get("last_input_path", ""))
        buttons_frame = ttk.Frame(self.paths_frame)
        buttons_frame.pack(fill='x', pady=5)
        spacer = ttk.Label(buttons_frame, text="", width=10)
        spacer.pack(side='left')
        self.select_file_button = ttk.Button(
            buttons_frame,
            text=self.get_text("select_file_button"),
            command=self.browse_files
        )
        self.select_file_button.pack(side='left')
        self.select_dir_button = ttk.Button(
            buttons_frame,
            text=self.get_text("select_directory_button"),
            command=self.browse_directory
        )
        self.select_dir_button.pack(side='left', padx=5)
        self.recursive_var = tk.BooleanVar(value=self.settings.get("search_subdirectories", True))
        self.recursive_check = ttk.Checkbutton(
            buttons_frame,
            text=self.get_text("recursive"),
            variable=self.recursive_var
        )
        self.recursive_check.pack(side='left')
        self.preserve_structure_var = tk.BooleanVar(value=self.settings.get("preserve_structure", True))
        self.preserve_structure_check = ttk.Checkbutton(
            buttons_frame,
            text=self.get_text("preserve"),
            variable=self.preserve_structure_var
        )
        self.preserve_structure_check.pack(side='left', padx=(20, 0))
        target_frame = ttk.Frame(self.paths_frame)
        target_frame.pack(fill='x', pady=5)
        self.target_label = ttk.Label(target_frame, text=self.get_text("output_path"), width=10, anchor='w')
        self.target_label.pack(side='left')
        self.target_entry = ttk.Entry(target_frame)
        self.target_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.browse_target_button = ttk.Button(
            target_frame,
            text=self.get_text("browse_button"),
            command=self.browse_target
        )
        self.browse_target_button.pack(side='left')
        self.target_entry.insert(0, self.settings.get("last_output_path", ""))

    def create_options_section(self, parent):
        self.options_frame = ttk.LabelFrame(parent, text=self.get_text("conversion_options"), padding="10 5 10 10")
        self.options_frame.pack(fill='x', padx=5, pady=5)
        checkbox_frame = ttk.Frame(self.options_frame)
        checkbox_frame.pack(fill='x', pady=5)
        self.remove_var = tk.BooleanVar(value=self.settings.get("remove_converted", False))
        self.remove_check = ttk.Checkbutton(
            checkbox_frame,
            text=self.get_text("remove_converted"),
            variable=self.remove_var
        )
        self.remove_check.pack(side='left', padx=(0, 20))
        self.overwrite_var = tk.BooleanVar(value=self.settings.get("overwrite_existing", False))
        self.overwrite_check = ttk.Checkbutton(
            checkbox_frame,
            text=self.get_text("overwrite_existing"),
            variable=self.overwrite_var
        )
        self.overwrite_check.pack(side='left')
        quality_frame = ttk.Frame(self.options_frame)
        quality_frame.pack(fill='x', pady=5)
        self.quality_label = ttk.Label(quality_frame, text=self.get_text("quality_label"))
        self.quality_label.pack(side='left')
        self.quality_value = tk.StringVar(value=str(self.settings.get("quality", 95)))
        quality_display = ttk.Label(quality_frame, textvariable=self.quality_value, width=3)
        quality_display.pack(side='right')
        self.quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self.quality_value.set(str(int(float(v))))
        )
        self.quality_scale.set(self.settings.get("quality", 95))
        self.quality_scale.pack(side='left', fill='x', expand=True, padx=5)

    def setup_drag_drop(self):
        try:
            from tkinterdnd2 import TkinterDnD, DND_FILES
            if isinstance(self.master, TkinterDnD.Tk):
                self.path_entry.drop_target_register('DND_Files')
                self.path_entry.dnd_bind('<<Drop>>', self.on_drop_files)
                self.master.drop_target_register('DND_Files')
                self.master.dnd_bind('<<Drop>>', self.on_drop_files)
                self.log(self.get_text("drag_drop_enabled"))
        except ImportError:
            self.log(self.get_text("drag_drop_limited"))
            self.path_entry.bind('<Enter>', lambda e: self.status_var.set(self.get_text("drop_files_here")))
            self.path_entry.bind('<Leave>', lambda e: self.status_var.set(self.get_text("status_ready")))

    def log(self, message):
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.see(tk.END)
        self.master.update_idletasks()

    def update_progress(self, message):
        self.log(message)
        self.status_var.set(message)

    def open_destination_folder(self):
        target_path = self.target_entry.get()
        if not target_path or not os.path.exists(target_path):
            self.log(self.get_text("destination_not_exist"))
            return
        try:
            if platform.system() == "Windows":
                os.startfile(target_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", target_path])
            else:
                subprocess.run(["xdg-open", target_path])
            self.log(self.get_text("opened_destination").format(path=target_path))
        except Exception as e:
            self.log(self.get_text("error_opening_folder").format(error=str(e)))

    def on_drop_files(self, event):
        try:
            data = event.data if hasattr(event, 'data') else event.widget.get()
            if platform.system() == "Windows":
                files = [f.strip('{}').replace('file:///', '') for f in data.split()]
            else:
                files = [f.replace('file://', '') for f in data.split()]
            self.process_dropped_files(files)
            return "break"
        except Exception as e:
            self.status_var.set(self.get_text("error_processing_drop").format(error=str(e)))
            self.log(f"Error: {str(e)}")
            return "break"

    def process_dropped_files(self, files):
        valid_files = []
        directories = []
        for file_path in files:
            file_path = file_path.strip('"\'')

            if os.path.isfile(file_path):
                if file_path.lower().endswith('.heic'):
                    valid_files.append(file_path)
            elif os.path.isdir(file_path):
                directories.append(file_path)
        if directories:
            directory = directories[0]
            self.selected_files = []
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            if self.target_entry.get() == "":
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, directory)
            self.recursive_check.state(['!disabled'])
            self.status_var.set(self.get_text("directory_selected").format(path=directory))
            if len(directories) > 1:
                self.log(self.get_text("multiple_directories").format(path=directory))
            return
        if valid_files:
            self.selected_files = valid_files
            self.path_entry.delete(0, tk.END)
            if len(valid_files) == 1:
                self.path_entry.insert(0, valid_files[0])
                self.status_var.set(self.get_text("file_selected").format(filename=os.path.basename(valid_files[0])))
            else:
                self.path_entry.insert(0, self.get_text("files_selected").format(count=len(valid_files)))
                self.status_var.set(self.get_text("files_selected").format(count=len(valid_files)))
            if self.target_entry.get() == "":
                parent_dir = os.path.dirname(valid_files[0])
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, parent_dir)
            self.recursive_check.state(['disabled'])
            self.log(self.get_text("added_files").format(count=len(valid_files)))
            return
        self.status_var.set(self.get_text("no_valid_files"))
        self.log(self.get_text("no_valid_files"))

    def browse_files(self):
        filetypes = [("HEIC files", "*.heic"), ("All files", "*.*")]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        if files:
            self.selected_files = files
            self.path_entry.delete(0, tk.END)
            if len(files) == 1:
                self.path_entry.insert(0, files[0])
                self.status_var.set(self.get_text("file_selected").format(filename=os.path.basename(files[0])))
            else:
                self.path_entry.insert(0, self.get_text("files_selected").format(count=len(files)))
                self.status_var.set(self.get_text("files_selected").format(count=len(files)))
            if self.target_entry.get() == "":
                parent_dir = os.path.dirname(files[0])
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, parent_dir)
            self.recursive_check.state(['disabled'])

    def browse_directory(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.selected_files = []
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            self.status_var.set(self.get_text("directory_selected").format(path=file_path))
            if self.target_entry.get() == "":
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, file_path)
            self.recursive_check.state(['!disabled'])

    def browse_target(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, file_path)
            self.status_var.set(self.get_text("target_directory").format(path=file_path))

    def convert(self):
        target = self.target_entry.get()
        remove = self.remove_var.get()
        overwrite = self.overwrite_var.get()
        recursive = self.recursive_var.get()
        quality = int(self.quality_scale.get())
        preserve_structure = self.preserve_structure_var.get()
        generate_unique = True
        verbose = True
        self.console_output.delete(1.0, tk.END)
        self.status_var.set(self.get_text("converting"))
        self.master.update()
        self.log(self.get_text("conversion_settings"))
        self.log(self.get_text("quality_percent").format(quality=quality))
        self.log(self.get_text("remove_originals").format(value="Yes" if remove else "No"))
        self.log(self.get_text("overwrite_existing_option").format(value="Yes" if overwrite else "No"))
        self.log(self.get_text("generate_unique_filenames"))
        if not self.selected_files:
            self.log(self.get_text("search_subdirectories").format(value="Yes" if recursive else "No"))
        self.log(self.get_text("preserve_structure_option").format(value="Yes" if preserve_structure else "No"))
        self.log("")
        if not os.path.exists(target):
            os.makedirs(target)
            self.log(self.get_text("created_target_directory").format(path=target))
        console_capture = io.StringIO()
        if self.selected_files:
            self.log(self.get_text("converting_selected_files").format(count=len(self.selected_files)))
            with redirect_stdout(console_capture), redirect_stderr(console_capture):
                converted = convert_multiple_heic_files(
                    self.selected_files,
                    overwrite,
                    remove,
                    quality,
                    target,
                    self.update_progress,
                    generate_unique,
                    verbose
                )
            captured = console_capture.getvalue()
            if captured:
                self.log(captured)
            self.log(self.get_text("successfully_converted").format(converted=len(converted), total=len(self.selected_files)))
            self.status_var.set(self.get_text("converted_files").format(count=len(converted)))
        else:
            path = self.path_entry.get()
            if os.path.isdir(path):
                self.log(self.get_text("converting_directory").format(path=path, target=target))
                with redirect_stdout(console_capture), redirect_stderr(console_capture):
                    converted = convert_heic_to_jpeg(
                        path,
                        recursive,
                        overwrite,
                        remove,
                        quality,
                        target,
                        preserve_structure,
                        self.update_progress,
                        generate_unique,
                        verbose
                    )
                captured = console_capture.getvalue()
                if captured:
                    self.log(captured)
                self.log(self.get_text("successfully_converted").format(converted=len(converted), total=len(converted)))
                self.status_var.set(self.get_text("converted_files").format(count=len(converted)))
            elif os.path.isfile(path):
                t_file = os.path.join(target, os.path.basename(path).split('.')[0]) + ".jpg"
                if generate_unique and os.path.exists(t_file) and not overwrite:
                    t_file = generate_unique_filename(t_file)
                self.log(self.get_text("converting_file").format(path=path, target_file=t_file))
                with redirect_stdout(console_capture), redirect_stderr(console_capture):
                    success = convert_heic_file(
                        path,
                        t_file,
                        overwrite,
                        remove,
                        quality,
                        self.update_progress,
                        verbose
                    )
                captured = console_capture.getvalue()
                if captured:
                    self.log(captured)
                self.log(self.get_text("conversion_successful") if success else self.get_text("conversion_failed"))
                self.status_var.set(self.get_text("conversion_successful") if success else self.get_text("conversion_failed"))
            else:
                self.log(self.get_text("invalid_path").format(path=path))
                self.status_var.set(self.get_text("error_invalid_path"))
        self.console_output.see(tk.END)


def main():
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        print("Using tkinterdnd2 for drag and drop support")
    except ImportError:
        root = tk.Tk()
        print("tkinterdnd2 not available, basic drag and drop support will be limited")
    root.configure(bg="#f0f0f0")
    gui = HEICConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
