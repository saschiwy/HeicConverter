import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk
from converter import convert_heic_to_jpeg, convert_heic_file
import platform
import re
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Handle DPI awareness for Windows
if platform.system() == "Windows":
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class HEICConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("HEIC to JPEG Converter")
        master.geometry("800x600")  # More reasonable default size
        
        # Set background color for a professional look
        self.bg_color = "#f0f0f0"
        master.configure(bg=self.bg_color)
        
        self.selected_files = []  # Store selected files
        
        # Create a custom theme for widgets
        self.create_custom_theme()
        
        # Main content frame with padding
        main_frame = ttk.Frame(master, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)
        
        # Combined Input/Output section
        self.create_paths_section(main_frame)
        
        # Options section
        self.create_options_section(main_frame)
        
        # Convert button (centered)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill='x')
        
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor='center')
        
        self.convert_button = ttk.Button(
            button_container,
            text="Convert",
            command=self.convert,
            style="Action.TButton",
            width=15
        )
        self.convert_button.pack()
        
        # Console Output 
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="5 5 5 5")
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Console text widget with internal scrollbar
        self.console_output = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=10,  # Fixed height to ensure visibility
            borderwidth=1,
            relief="solid"
        )
        self.console_output.pack(fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Setup drag and drop if possible
        self.setup_drag_drop()

    def create_custom_theme(self):
        """Create a custom theme for the application"""
        style = ttk.Style()
        
        # Configure the base theme
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabelframe", background=self.bg_color)
        style.configure("TLabelframe.Label", background=self.bg_color, font=("Helvetica", 11, "bold"))
        
        # Button styles
        style.configure("TButton", font=("Helvetica", 11), padding=8)
        style.configure("Action.TButton", font=("Helvetica", 12, "bold"), padding=10)
        
        # Label styles
        style.configure("TLabel", background=self.bg_color, font=("Helvetica", 11), padding=5)
        
        # Entry styles
        style.configure("TEntry", font=("Helvetica", 11), padding=8)
        
        # Checkbox styles
        style.configure("TCheckbutton", background=self.bg_color, font=("Helvetica", 11), padding=5)

    def create_paths_section(self, parent):
        """Create the combined paths section for input and output selection"""
        paths_frame = ttk.LabelFrame(parent, text="File Paths", padding="10 5 10 10")
        paths_frame.pack(fill='x', padx=5, pady=5)
        
        # Input path row
        input_frame = ttk.Frame(paths_frame)
        input_frame.pack(fill='x', pady=5)
        
        input_label = ttk.Label(input_frame, text="Input:", width=10, anchor='w')
        input_label.pack(side='left')
        
        self.path_entry = ttk.Entry(input_frame)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Buttons and checkbox row
        buttons_frame = ttk.Frame(paths_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        spacer = ttk.Label(buttons_frame, text="", width=10)
        spacer.pack(side='left')
        
        self.select_file_button = ttk.Button(
            buttons_frame,
            text="Select File(s)",
            command=self.browse_files
        )
        self.select_file_button.pack(side='left')
        
        self.select_dir_button = ttk.Button(
            buttons_frame,
            text="Select Folder",
            command=self.browse_directory
        )
        self.select_dir_button.pack(side='left', padx=5)
        
        # Recursive checkbox to the right of the buttons
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(
            buttons_frame,
            text="Search subdirectories",
            variable=self.recursive_var
        )
        self.recursive_check.pack(side='left')
        
        # Target path row
        target_frame = ttk.Frame(paths_frame)
        target_frame.pack(fill='x', pady=5)
        
        target_label = ttk.Label(target_frame, text="Output:", width=10, anchor='w')
        target_label.pack(side='left')
        
        self.target_entry = ttk.Entry(target_frame)
        self.target_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        self.browse_target_button = ttk.Button(
            target_frame,
            text="Browse",
            command=self.browse_target
        )
        self.browse_target_button.pack(side='left')

    def create_options_section(self, parent):
        """Create the options section for conversion settings"""
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding="10 5 10 10")
        options_frame.pack(fill='x', padx=5, pady=5)
        
        # Checkboxes in a row
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.pack(fill='x', pady=5)
        
        self.remove_var = tk.BooleanVar()
        self.remove_check = ttk.Checkbutton(
            checkbox_frame,
            text="Remove converted HEIC Files",
            variable=self.remove_var
        )
        self.remove_check.pack(side='left', padx=(0, 20))
        
        self.overwrite_var = tk.BooleanVar()
        self.overwrite_check = ttk.Checkbutton(
            checkbox_frame,
            text="Overwrite existing JPEG files",
            variable=self.overwrite_var
        )
        self.overwrite_check.pack(side='left')
        
        # Quality slider
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill='x', pady=5)
        
        quality_label = ttk.Label(quality_frame, text="Quality (1-100):")
        quality_label.pack(side='left')
        
        self.quality_value = tk.StringVar(value="95")
        quality_display = ttk.Label(quality_frame, textvariable=self.quality_value, width=3)
        quality_display.pack(side='right')
        
        self.quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self.quality_value.set(str(int(float(v))))
        )
        self.quality_scale.set(95)  # Default value
        self.quality_scale.pack(side='left', fill='x', expand=True, padx=5)

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Mark the path entry as a drop target
        self.add_drop_target(self.path_entry)
        
        # Also make the main window a drop target
        self.add_drop_target(self.master)
        
        # Add appropriate messages to status bar
        self.console_output.insert(tk.END, "Drag and drop HEIC files or folders here to convert them.\n")
        self.status_var.set("Ready - Drag and drop supported")

    def add_drop_target(self, widget):
        """Add drop target capabilities to a widget"""
        # Different approach based on whether we have tkinterdnd2 available
        if hasattr(self.master, 'TkdndVersion'):
            # Using tkinterdnd2
            widget.drop_target_register('DND_Files')
            widget.dnd_bind('<<Drop>>', self.on_drop_files)
        else:
            # Fallback for platforms without tkinterdnd2
            widget.bind('<Drop>', self.on_drop_files)
            # Basic visual feedback
            widget.bind('<Enter>', lambda e: self.status_var.set("Drop files here"))
            widget.bind('<Leave>', lambda e: self.status_var.set("Ready"))

    def on_drop_files(self, event):
        """Handle files being dropped"""
        try:
            # Handle the dropped data
            data = event.data if hasattr(event, 'data') else event.widget.get()
            
            # Clean up file paths (different formats between systems)
            if platform.system() == "Windows":
                # Windows paths might be in {} or have file:/// prefix
                files = [f.strip('{}').replace('file:///', '') for f in data.split()]
            else:
                # Unix-like paths
                files = [f.replace('file://', '') for f in data.split()]
            
            self.process_dropped_files(files)
            
            return "break"  # Prevent default handling
        except Exception as e:
            self.status_var.set(f"Error processing dropped files: {str(e)}")
            self.console_output.insert(tk.END, f"Error: {str(e)}\n")
            return "break"

    def process_dropped_files(self, files):
        """Process a list of dropped files or directories"""
        valid_files = []
        directories = []
        
        for file_path in files:
            # Clean up the path
            file_path = file_path.strip('"\'')
            
            if os.path.isfile(file_path):
                if file_path.lower().endswith('.heic'):
                    valid_files.append(file_path)
            elif os.path.isdir(file_path):
                directories.append(file_path)
        
        # Handle directories first (prioritize directories over files)
        if directories:
            directory = directories[0]  # Take the first directory
            self.selected_files = []
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            
            # Set target directory if empty
            if self.target_entry.get() == "":
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, directory)
            
            # Enable recursive option
            self.recursive_check.state(['!disabled'])
            
            self.status_var.set(f"Directory selected: {directory}")
            if len(directories) > 1:
                self.console_output.insert(tk.END, f"Note: Multiple directories dropped. Using {directory}.\n")
            
            return
        
        # Handle HEIC files
        if valid_files:
            self.selected_files = valid_files
            self.path_entry.delete(0, tk.END)
            
            if len(valid_files) == 1:
                self.path_entry.insert(0, valid_files[0])
                self.status_var.set(f"1 file selected: {os.path.basename(valid_files[0])}")
            else:
                self.path_entry.insert(0, f"{len(valid_files)} files selected")
                self.status_var.set(f"{len(valid_files)} files selected")
            
            # Set target directory if empty
            if self.target_entry.get() == "":
                parent_dir = os.path.dirname(valid_files[0])
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, parent_dir)
            
            # Disable recursive option for file selection
            self.recursive_check.state(['disabled'])
            
            # Log the files found
            self.console_output.insert(tk.END, f"Added {len(valid_files)} HEIC files for conversion.\n")
            return
        
        # No valid files found
        self.status_var.set("No valid HEIC files found in the dropped items")
        self.console_output.insert(tk.END, "No valid HEIC files found in the dropped items.\n")

    def browse_files(self):
        """Browse for file(s)"""
        filetypes = [("HEIC files", "*.heic"), ("All files", "*.*")]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        
        if files:
            self.selected_files = files
            self.path_entry.delete(0, tk.END)
            if len(files) == 1:
                self.path_entry.insert(0, files[0])
                self.status_var.set(f"1 file selected: {os.path.basename(files[0])}")
            else:
                self.path_entry.insert(0, f"{len(files)} files selected")
                self.status_var.set(f"{len(files)} files selected")
            
            # Set target directory to parent of first file if empty
            if self.target_entry.get() == "":
                parent_dir = os.path.dirname(files[0])
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, parent_dir)
                
            # Disable recursive option as it's not applicable for file selection
            self.recursive_check.state(['disabled'])

    def browse_directory(self):
        """Browse for a directory"""
        file_path = filedialog.askdirectory()
        if file_path:
            self.selected_files = []  # Clear any previously selected files
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            self.status_var.set(f"Directory selected: {file_path}")
            
            # Set target directory to match source if empty
            if self.target_entry.get() == "":
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, file_path)
                
            # Enable recursive option for directory selection
            self.recursive_check.state(['!disabled'])

    def browse_target(self):
        """Browse for target directory"""
        file_path = filedialog.askdirectory()
        if file_path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, file_path)
            self.status_var.set(f"Target directory: {file_path}")

    def generate_unique_filename(self, target_file):
        """Generate a unique filename by adding (n) suffix if file exists"""
        if not os.path.exists(target_file):
            return target_file
        
        directory = os.path.dirname(target_file)
        filename, extension = os.path.splitext(os.path.basename(target_file))
        
        # Check if filename already has (n) pattern
        match = re.match(r"(.*)\((\d+)\)$", filename)
        if match:
            base_name = match.group(1).rstrip()
            counter = int(match.group(2))
        else:
            base_name = filename
            counter = 1
        
        # Find an available filename
        while True:
            new_filename = f"{base_name}({counter}){extension}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def convert(self):
        """Handle the conversion process"""
        target = self.target_entry.get()
        remove = self.remove_var.get()
        overwrite = self.overwrite_var.get()
        recursive = self.recursive_var.get()
        quality = int(self.quality_scale.get())

        # Clear previous output
        self.console_output.delete(1.0, tk.END)
        self.status_var.set("Converting...")
        self.master.update()  # Update the GUI to show status change

        # Ensure quality is within the range 1-100
        quality = max(1, min(100, quality))

        output_text = ""
        
        # Show selected conversion options
        output_text += "Conversion settings:\n"
        output_text += f"- Quality: {quality}%\n"
        output_text += f"- Remove originals: {'Yes' if remove else 'No'}\n"
        output_text += f"- Overwrite existing: {'Yes' if overwrite else 'No'}\n"
        if not self.selected_files:
            output_text += f"- Search subdirectories: {'Yes' if recursive else 'No'}\n"
        output_text += "\n"
        
        # Check if target directory exists, create if needed
        if not os.path.exists(target):
            os.makedirs(target)
            output_text += f"Created target directory: {target}\n"

        # Add the output to the console
        self.console_output.insert(tk.END, output_text)
        self.console_output.see(tk.END)
        self.master.update()  # Update the display

        # Use StringIO to capture console output 
        console_capture = io.StringIO()
        
        # Check if we have files selected or a directory path
        if self.selected_files:
            # File(s) mode
            successful_count = 0
            self.console_output.insert(tk.END, f'Converting {len(self.selected_files)} selected file(s):\n')
            self.master.update()  # Update display
            
            for source_file in self.selected_files:
                # Check if it's a valid HEIC file
                if not os.path.isfile(source_file) or not source_file.lower().endswith('.heic'):
                    self.console_output.insert(tk.END, f'Skipping invalid file: {source_file}\n')
                    self.master.update()
                    continue
                    
                target_filename = os.path.basename(source_file).split('.')[0] + ".jpg"
                target_file = os.path.join(target, target_filename)
                
                # Generate unique filename if not overwriting
                if not overwrite and os.path.exists(target_file):
                    target_file = self.generate_unique_filename(target_file)
                    target_filename = os.path.basename(target_file)
                
                self.console_output.insert(tk.END, f'Converting: {os.path.basename(source_file)} -> {target_filename}\n')
                self.master.update()
                
                # Capture stdout during conversion
                with redirect_stdout(console_capture), redirect_stderr(console_capture):
                    success = convert_heic_file(source_file, target_file, overwrite, remove, quality)
                
                # Get and display any captured output
                captured = console_capture.getvalue()
                if captured:
                    self.console_output.insert(tk.END, captured)
                    self.master.update()
                    console_capture.truncate(0)
                    console_capture.seek(0)
                
                if success:
                    successful_count += 1
            
            self.console_output.insert(tk.END, f'Successfully converted {successful_count} out of {len(self.selected_files)} files\n')
            self.status_var.set(f"Converted {successful_count} of {len(self.selected_files)} files")
        else:
            # Directory mode
            path = self.path_entry.get()
            if os.path.isdir(path):
                self.console_output.insert(tk.END, f'Converting HEIC files in directory {path} to {target}\n')
                self.master.update()
                
                # Capture stdout during conversion
                with redirect_stdout(console_capture), redirect_stderr(console_capture):
                    converted = convert_heic_to_jpeg(path, recursive, overwrite, remove, quality, target)
                
                # Get and display any captured output
                captured = console_capture.getvalue()
                if captured:
                    self.console_output.insert(tk.END, captured)
                
                self.console_output.insert(tk.END, f'Successfully converted {len(converted)} files\n')
                self.status_var.set(f"Converted {len(converted)} files")
            else:
                self.console_output.insert(tk.END, f'Invalid directory path: {path}\n')
                self.status_var.set("Error: Invalid directory path")

        # Make sure to see the end of the log
        self.console_output.see(tk.END)


def main():
    # Try to use tkinterdnd2 for drag and drop
    try:
        from tkinterdnd2 import TkinterDnD, DND_FILES
        root = TkinterDnD.Tk()
        print("Using tkinterdnd2 for drag and drop support")
    except ImportError:
        # Fall back to regular Tk
        root = tk.Tk()
        print("tkinterdnd2 not available, basic drag and drop support will be limited")
    
    root.configure(bg="#f0f0f0")  # Set background color
    gui = HEICConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
    