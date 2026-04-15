import locale
import os
import platform
import io
import json
import subprocess
import threading
from contextlib import redirect_stdout, redirect_stderr

import customtkinter as ctk
from tkinter import filedialog

from converter import (
    convert_heic_to_jpeg,
    convert_heic_file,
    convert_multiple_heic_files,
    generate_unique_filename
)

# Configure CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Define consistent fonts
FONT_MAIN = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 13, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BUTTON = ("Segoe UI", 14)
FONT_LOG = ("Consolas", 11)

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
    "quality_label": "Quality",
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
    "select_language": "Language",
}

zh_CN = {
  "title": "HEIC / HEIF 转 JPEG 工具",
  "convert_button": "开始转换",
  "open_folder_button": "打开文件夹",
  "conversion_log": "转换记录",
  "status_ready": "就绪",
  "log_initial": "HEIC 转 JPEG 工具已就绪。\n将 HEIC 文件或包含 HEIC 的文件夹拖放到此处开始转换。",
  "file_paths": "文件路径",
  "input_path": "输入路径",
  "select_file_button": "选择文件",
  "select_directory_button": "选择文件夹",
  "output_path": "输出路径",
  "recursive": "包含子目录",
  "preserve": "保留目录结构",
  "browse_button": "浏览...",
  "conversion_options": "转换选项",
  "remove_converted": "转换后删除原 HEIC 文件",
  "overwrite_existing": "覆盖已存在的 JPEG 文件",
  "quality_label": "输出质量 (1-100)：",
  "drag_drop_enabled": "已启用拖放支持。",
  "drag_drop_limited": "拖放支持有限（tkinterdnd2 不可用）。",
  "drop_files_here": "将文件或文件夹拖到此处",
  "destination_not_exist": "目标文件夹不存在。",
  "opened_destination": "已打开目标文件夹：{path}",
  "error_opening_folder": "打开文件夹失败：{error}",
  "directory_selected": "已选择文件夹：{path}",
  "multiple_directories": "注意：放入了多个文件夹。将使用：{path}",
  "file_selected": "已选择 1 个文件：{filename}",
  "files_selected": "已选择 {count} 个文件",
  "added_files": "已添加 {count} 个 HEIC 文件到转换队列。",
  "no_valid_files": "放入的项目中未找到有效的 HEIC 文件。",
  "target_directory": "目标文件夹：{path}",
  "converting": "正在转换…",
  "conversion_settings": "转换设置：",
  "quality_percent": "- 质量：{quality}%",
  "remove_originals": "- 删除原文件：{value}",
  "overwrite_existing_option": "- 覆盖已存在文件：{value}",
  "generate_unique_filenames": "- 生成唯一文件名：是",
  "search_subdirectories": "- 搜索子目录：{value}",
  "preserve_structure_option": "- 保留目录结构：{value}",
  "created_target_directory": "已创建目标文件夹：{path}",
  "converting_selected_files": "正在转换所选的 {count} 个文件…",
  "successfully_converted": "已成功转换 {converted} / {total} 个文件",
  "converted_files": "已转换 {count} 个文件",
  "converting_directory": "正在将文件夹 {path} 内的 HEIC 文件转换到 {target}",
  "converting_file": "正在将 HEIC 文件 {path} 转为 {target_file}",
  "conversion_successful": "转换成功",
  "conversion_failed": "转换失败",
  "invalid_path": "无效路径：{path}",
  "error_invalid_path": "错误：无效路径",
  "error_processing_drop": "处理拖放项目时出错：{error}",
  "select_language": "选择语言"
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
        # Check built-in languages first
        if lang_code == "Chinese (Simplified)" or lang_code == "zh_CN":
            return zh_CN
        if lang_code == "en":
            return en
        # Fallback to English
        return en

    @staticmethod
    def get_supported_languages():
        # Built-in languages
        return ["en", "zh-CN"]

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
        self.settings["language"] = self.settings.get("language", "en")  # Keep existing language setting
        self.settings["last_input_path"] = self.path_entry.get()
        self.settings["last_output_path"] = self.target_entry.get()
        self.settings["remove_converted"] = self.remove_var.get()
        self.settings["overwrite_existing"] = self.overwrite_var.get()
        self.settings["quality"] = int(self.quality_slider.get())
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
        self.app.destroy()

    def on_language_change(self, event=None):
        new_lang = self.language_var.get()
        self.language = self.load_language(new_lang)
        self.settings["language"] = new_lang
        self.app.title(self.get_text("title"))
        self.status_label.configure(text=self.get_text("status_ready"))
        self.update_ui_texts()
        self.save_settings()

    def update_ui_texts(self):
        # Update section titles
        self.paths_frame.configure(title=self.get_text("file_paths"))
        self.options_frame.configure(title=self.get_text("conversion_options"))
        self.log_frame.configure(title=self.get_text("conversion_log"))
        
        # Update labels
        self.input_label.configure(text=self.get_text("input_path"))
        self.target_label.configure(text=self.get_text("output_path"))
        self.quality_label.configure(text=self.get_text("quality_label"))
        
        # Update buttons
        self.select_file_button.configure(text=self.get_text("select_file_button"))
        self.select_dir_button.configure(text=self.get_text("select_directory_button"))
        self.browse_target_button.configure(text=self.get_text("browse_button"))
        self.convert_button.configure(text=self.get_text("convert_button"))
        self.open_folder_button.configure(text=self.get_text("open_folder_button"))
        
        # Update checkboxes
        self.recursive_check.configure(text=self.get_text("recursive"))
        self.preserve_structure_check.configure(text=self.get_text("preserve"))
        self.remove_check.configure(text=self.get_text("remove_converted"))
        self.overwrite_check.configure(text=self.get_text("overwrite_existing"))
        
        # [Language label hidden]
        
        # Update initial log
        self.log_text.insert("1.0", self.get_text("log_initial"))
        self.log_text.see("end")

    def __init__(self, app):
        self.app = app
        self.settings = gui_settings.copy()
        self.load_settings()
        self.language = self.load_language(self.settings.get("language", get_system_language()))

        app.protocol("WM_DELETE_WINDOW", self.on_close)
        app.title(self.get_text("title"))
        app.geometry("600x700")
        app.resizable(False, False)

        # Configure grid
        app.columnconfigure(0, weight=1)
        
        # Main container with rounded corners
        self.main_container = ctk.CTkFrame(app, corner_radius=0, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # File Paths Section
        self.paths_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.paths_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            self.paths_frame,
            text=self.get_text("file_paths"),
            font=FONT_TITLE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Input row
        input_row = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=15, pady=(0, 8))
        
        self.input_label = ctk.CTkLabel(input_row, text=self.get_text("input_path"), width=80, anchor="w", font=FONT_MAIN)
        self.input_label.pack(side="left")
        
        self.path_entry = ctk.CTkEntry(input_row, placeholder_text="Select file or folder...", font=FONT_MAIN)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.path_entry.insert(0, self.settings.get("last_input_path", ""))
        
        # Buttons row
        buttons_row = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        buttons_row.pack(fill="x", padx=15, pady=(0, 10))
        
        self.select_file_button = ctk.CTkButton(
            buttons_row,
            text=self.get_text("select_file_button"),
            command=self.browse_files,
            width=100,
            height=28,
            font=FONT_BUTTON
        )
        self.select_file_button.pack(side="left")
        
        self.select_dir_button = ctk.CTkButton(
            buttons_row,
            text=self.get_text("select_directory_button"),
            command=self.browse_directory,
            width=100,
            height=28,
            font=FONT_BUTTON
        )
        self.select_dir_button.pack(side="left", padx=8)
        
        # Checkboxes
        self.recursive_var = ctk.BooleanVar(value=self.settings.get("search_subdirectories", True))
        self.recursive_check = ctk.CTkCheckBox(
            buttons_row,
            text=self.get_text("recursive"),
            variable=self.recursive_var,
            command=self.on_checkbox_change,
            font=FONT_MAIN
        )
        self.recursive_check.pack(side="left", padx=(20, 0))
        
        self.preserve_structure_var = ctk.BooleanVar(value=self.settings.get("preserve_structure", True))
        self.preserve_structure_check = ctk.CTkCheckBox(
            buttons_row,
            text=self.get_text("preserve"),
            variable=self.preserve_structure_var,
            command=self.on_checkbox_change,
            font=FONT_MAIN
        )
        self.preserve_structure_check.pack(side="left", padx=(15, 0))
        
        # Target row
        target_row = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        target_row.pack(fill="x", padx=15, pady=(0, 15))
        
        self.target_label = ctk.CTkLabel(target_row, text=self.get_text("output_path"), width=80, anchor="w", font=FONT_MAIN)
        self.target_label.pack(side="left")
        
        self.target_entry = ctk.CTkEntry(target_row, placeholder_text="Output folder...", font=FONT_MAIN)
        self.target_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.target_entry.insert(0, self.settings.get("last_output_path", ""))
        
        self.browse_target_button = ctk.CTkButton(
            target_row,
            text=self.get_text("browse_button"),
            command=self.browse_target,
            width=80,
            height=28,
            font=FONT_BUTTON
        )
        self.browse_target_button.pack(side="left")
        
        # Options Section
        self.options_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.options_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            self.options_frame,
            text=self.get_text("conversion_options"),
            font=FONT_TITLE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Checkboxes row
        checkbox_row = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        checkbox_row.pack(fill="x", padx=15, pady=(0, 10))
        
        self.remove_var = ctk.BooleanVar(value=self.settings.get("remove_converted", False))
        self.remove_check = ctk.CTkCheckBox(
            checkbox_row,
            text=self.get_text("remove_converted"),
            variable=self.remove_var,
            command=self.on_checkbox_change,
            font=FONT_MAIN
        )
        self.remove_check.pack(side="left", padx=(0, 25))
        
        self.overwrite_var = ctk.BooleanVar(value=self.settings.get("overwrite_existing", False))
        self.overwrite_check = ctk.CTkCheckBox(
            checkbox_row,
            text=self.get_text("overwrite_existing"),
            variable=self.overwrite_var,
            command=self.on_checkbox_change,
            font=FONT_MAIN
        )
        self.overwrite_check.pack(side="left")
        
        # Quality slider
        quality_row = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        quality_row.pack(fill="x", padx=15, pady=(0, 15))
        
        self.quality_label = ctk.CTkLabel(quality_row, text=self.get_text("quality_label"), font=FONT_MAIN)
        self.quality_label.pack(side="left")
        
        self.quality_slider = ctk.CTkSlider(
            quality_row,
            from_=1,
            to=100,
            number_of_steps=99,
            command=self.on_quality_change
        )
        self.quality_slider.set(self.settings.get("quality", 95))
        self.quality_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.quality_value_label = ctk.CTkLabel(
            quality_row,
            text=f"{int(self.quality_slider.get())}%",
            width=40,
            font=FONT_BOLD
        )
        self.quality_value_label.pack(side="left")
        
        # Language selector and buttons row
        bottom_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(0, 10))
        
        # [Language selector hidden for now]
        # lang_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
        # lang_frame.pack(side="left")
        # self.lang_label = ctk.CTkLabel(lang_frame, text=self.get_text("select_language"))
        # self.lang_label.pack(side="left", padx=(0, 5))
        # self.language_var = ctk.StringVar(value=self.settings.get("language", get_system_language()))
        # self.language_selector = ctk.CTkComboBox(
        #     lang_frame,
        #     values=self.get_supported_languages(),
        #     variable=self.language_var,
        #     state="readonly",
        #     width=80,
        #     command=self.on_language_change
        # )
        # self.language_selector.pack(side="left")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        self.convert_button = ctk.CTkButton(
            buttons_frame,
            text=self.get_text("convert_button"),
            command=self.convert,
            width=140,
            height=36,
            font=FONT_BUTTON
        )
        self.convert_button.pack(side="left", padx=8)
        
        self.open_folder_button = ctk.CTkButton(
            buttons_frame,
            text=self.get_text("open_folder_button"),
            command=self.open_destination_folder,
            width=140,
            height=36,
            font=FONT_BUTTON
        )
        self.open_folder_button.pack(side="left")
        
        # Log Section
        self.log_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            self.log_frame,
            text=self.get_text("conversion_log"),
            font=FONT_TITLE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            font=FONT_LOG,
            wrap="word",
            border_width=0,
            fg_color=("gray95", "gray90")
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_text.insert("1.0", self.get_text("log_initial"))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            app,
            text=self.get_text("status_ready"),
            anchor="w",
            padx=20,
            pady=8,
            text_color="gray",
            font=FONT_MAIN
        )
        self.status_label.pack(fill="x")

    def on_checkbox_change(self):
        self.save_settings()

    def on_quality_change(self, value):
        self.quality_value_label.configure(text=f"{int(value)}%")
        self.save_settings()

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.app.update_idletasks()

    def update_progress(self, message):
        self.log(message)
        self.status_label.configure(text=message)

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

    def browse_files(self):
        filetypes = [("HEIC/HEIF files", "*.heic;*.heif"), ("All files", "*.*")]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        if files:
            self.selected_files = files
            self.path_entry.delete(0, "end")
            if len(files) == 1:
                self.path_entry.insert(0, files[0])
                self.status_label.configure(text=self.get_text("file_selected").format(filename=os.path.basename(files[0])))
            else:
                self.path_entry.insert(0, self.get_text("files_selected").format(count=len(files)))
                self.status_label.configure(text=self.get_text("files_selected").format(count=len(files)))
            if self.target_entry.get() == "":
                parent_dir = os.path.dirname(files[0])
                self.target_entry.delete(0, "end")
                self.target_entry.insert(0, parent_dir)
            self.recursive_check.configure(state="disabled")
            self.log(self.get_text("added_files").format(count=len(files)))

    def browse_directory(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.selected_files = []
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)
            self.status_label.configure(text=self.get_text("directory_selected").format(path=file_path))
            if self.target_entry.get() == "":
                self.target_entry.delete(0, "end")
                self.target_entry.insert(0, file_path)
            self.recursive_check.configure(state="normal")

    def browse_target(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, file_path)
            self.status_label.configure(text=self.get_text("target_directory").format(path=file_path))

    def convert(self):
        # Disable button during conversion
        self.convert_button.configure(state="disabled")
        self.open_folder_button.configure(state="disabled")
        
        target = self.target_entry.get()
        remove = self.remove_var.get()
        overwrite = self.overwrite_var.get()
        recursive = self.recursive_var.get()
        quality = int(self.quality_slider.get())
        preserve_structure = self.preserve_structure_var.get()
        generate_unique = True
        verbose = True
        
        self.log_text.delete("1.0", "end")
        self.status_label.configure(text=self.get_text("converting"))
        
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
        
        # Run conversion in a separate thread to keep UI responsive
        thread = threading.Thread(
            target=self._run_conversion,
            args=(target, remove, overwrite, recursive, quality, preserve_structure, generate_unique, verbose)
        )
        thread.daemon = True
        thread.start()
    
    def _run_conversion(self, target, remove, overwrite, recursive, quality, preserve_structure, generate_unique, verbose):
        console_capture = io.StringIO()
        
        try:
            if self.selected_files:
                self.log(self.get_text("converting_selected_files").format(count=len(self.selected_files)))
                with redirect_stdout(console_capture), redirect_stderr(console_capture):
                    converted = convert_multiple_heic_files(
                        self.selected_files, overwrite, remove, quality, target,
                        self.update_progress, generate_unique, verbose
                    )
                captured = console_capture.getvalue()
                if captured:
                    self.log(captured)
                self.log(self.get_text("successfully_converted").format(converted=len(converted), total=len(self.selected_files)))
                self.status_label.configure(text=self.get_text("converted_files").format(count=len(converted)))
            else:
                path = self.path_entry.get()
                if os.path.isdir(path):
                    self.log(self.get_text("converting_directory").format(path=path, target=target))
                    with redirect_stdout(console_capture), redirect_stderr(console_capture):
                        converted = convert_heic_to_jpeg(
                            path, recursive, overwrite, remove, quality, target,
                            preserve_structure, self.update_progress, generate_unique, verbose
                        )
                    captured = console_capture.getvalue()
                    if captured:
                        self.log(captured)
                    self.log(self.get_text("successfully_converted").format(converted=len(converted), total=len(converted)))
                    self.status_label.configure(text=self.get_text("converted_files").format(count=len(converted)))
                elif os.path.isfile(path):
                    t_file = os.path.join(target, os.path.basename(path).split('.')[0]) + ".jpg"
                    if generate_unique and os.path.exists(t_file) and not overwrite:
                        t_file = generate_unique_filename(t_file)
                    self.log(self.get_text("converting_file").format(path=path, target_file=t_file))
                    with redirect_stdout(console_capture), redirect_stderr(console_capture):
                        success = convert_heic_file(
                            path, t_file, overwrite, remove, quality,
                            self.update_progress, verbose
                        )
                    captured = console_capture.getvalue()
                    if captured:
                        self.log(captured)
                    result_text = self.get_text("conversion_successful") if success else self.get_text("conversion_failed")
                    self.log(result_text)
                    self.status_label.configure(text=result_text)
                else:
                    self.log(self.get_text("invalid_path").format(path=path))
                    self.status_label.configure(text=self.get_text("error_invalid_path"))
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.status_label.configure(text=self.get_text("conversion_failed"))
        finally:
            # Re-enable buttons after conversion completes
            self.app.after(0, lambda: self.convert_button.configure(state="normal"))
            self.app.after(0, lambda: self.open_folder_button.configure(state="normal"))


def main():
    app = ctk.CTk()
    
    # Set window icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon3.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    
    gui = HEICConverterGUI(app)
    app.mainloop()


if __name__ == '__main__':
    main()