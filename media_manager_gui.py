#!/usr/bin/env python3
"""
Windows GUI for Missing Media Scripts
A tkinter-based GUI to simplify the process of managing media file monitoring on Windows.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import datetime
import glob
import re
from email_utils import send_missing_media_email, load_email_config_from_file
from pathlib import Path

# Import functions from existing scripts
from generate_media_list import generate_media_list
from generate_missing_media_list import find_two_most_recent_media_lists
from windows_filename_validator import WindowsFilenameValidator

class FilenameFixDialog:
    def __init__(self, parent, validation_results, validator, log_function):
        self.validation_results = validation_results
        self.validator = validator
        self.log_function = log_function
        self.fixes_to_apply = {}  # filepath -> new_filename
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Fix Filename Issues")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_dialog_widgets()
        self.populate_fixes()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_dialog_widgets(self):
        """Create the dialog widgets"""
        # Header
        header_frame = ttk.Frame(self.dialog)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Filename Issues Found", 
                 font=("Arial", 14, "bold")).pack()
        ttk.Label(header_frame, text="Review suggested fixes and select which ones to apply:", 
                 font=("Arial", 10)).pack()
        
        # Main content frame with scrollbar
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply Selected Fixes", 
                  command=self.apply_fixes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=self.deselect_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side='right', padx=5)
    
    def populate_fixes(self):
        """Populate the dialog with file issues and suggested fixes"""
        self.checkboxes = {}
        
        for i, (filepath, issues) in enumerate(self.validation_results.items()):
            # Get suggested fix
            suggested_fix = self.validator.suggest_filename_fix(filepath)
            
            if not suggested_fix:
                continue  # Skip if no fix can be suggested
            
            # Create frame for this file
            file_frame = ttk.LabelFrame(self.scrollable_frame, text=f"File {i+1}", padding="5")
            file_frame.pack(fill='x', padx=5, pady=5)
            
            # Original filename
            orig_frame = ttk.Frame(file_frame)
            orig_frame.pack(fill='x', pady=2)
            ttk.Label(orig_frame, text="Original:", font=("Arial", 9, "bold")).pack(side='left')
            ttk.Label(orig_frame, text=os.path.basename(filepath), 
                     font=("Arial", 9), wraplength=600).pack(side='left', padx=5)
            
            # Issues
            issues_frame = ttk.Frame(file_frame)
            issues_frame.pack(fill='x', pady=2)
            ttk.Label(issues_frame, text="Issues:", font=("Arial", 9, "bold")).pack(side='left')
            issues_text = "; ".join(issues)
            ttk.Label(issues_frame, text=issues_text, font=("Arial", 9), 
                     foreground="red", wraplength=600).pack(side='left', padx=5)
            
            # Suggested fix
            fix_frame = ttk.Frame(file_frame)
            fix_frame.pack(fill='x', pady=2)
            ttk.Label(fix_frame, text="Suggested:", font=("Arial", 9, "bold")).pack(side='left')
            ttk.Label(fix_frame, text=suggested_fix, font=("Arial", 9), 
                     foreground="green", wraplength=600).pack(side='left', padx=5)
            
            # Checkbox to apply fix
            checkbox_frame = ttk.Frame(file_frame)
            checkbox_frame.pack(fill='x', pady=2)
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(checkbox_frame, text="Apply this fix", variable=var)
            checkbox.pack(side='left')
            
            self.checkboxes[filepath] = (var, suggested_fix)
    
    def select_all(self):
        """Select all checkboxes"""
        for var, _ in self.checkboxes.values():
            var.set(True)
    
    def deselect_all(self):
        """Deselect all checkboxes"""
        for var, _ in self.checkboxes.values():
            var.set(False)
    
    def apply_fixes(self):
        """Apply the selected filename fixes"""
        selected_fixes = []
        
        for filepath, (var, suggested_fix) in self.checkboxes.items():
            if var.get():
                selected_fixes.append((filepath, suggested_fix))
        
        if not selected_fixes:
            messagebox.showinfo("No Fixes Selected", "Please select at least one fix to apply.")
            return
        
        # Confirm with user
        count = len(selected_fixes)
        if not messagebox.askyesno("Confirm Fixes", 
                                  f"Apply {count} filename fix(es)?\n\nThis will rename the selected files."):
            return
        
        # Apply fixes
        success_count = 0
        error_count = 0
        
        for filepath, new_filename in selected_fixes:
            try:
                directory = os.path.dirname(filepath)
                new_filepath = os.path.join(directory, new_filename)
                
                # Check if target file already exists
                if os.path.exists(new_filepath):
                    self.log_function(f"Skipped {os.path.basename(filepath)}: Target filename already exists")
                    error_count += 1
                    continue
                
                # Rename the file
                os.rename(filepath, new_filepath)
                self.log_function(f"Renamed: {os.path.basename(filepath)} → {new_filename}")
                success_count += 1
                
            except Exception as e:
                self.log_function(f"Error renaming {os.path.basename(filepath)}: {e}")
                error_count += 1
        
        # Show results
        if success_count > 0:
            messagebox.showinfo("Fixes Applied", 
                               f"Successfully renamed {success_count} file(s).\n"
                               f"Errors: {error_count}\n\n"
                               f"Check the Status log for details.")
        else:
            messagebox.showwarning("No Fixes Applied", 
                                  f"No files were renamed due to errors.\n"
                                  f"Check the Status log for details.")
        
        # Close dialog
        self.dialog.destroy()

class MediaManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Manager - Windows GUI")
        self.root.geometry("800x650")
        
        # Configuration file path
        self.config_file = "media_manager_config.json"
        self.config = self.load_config()
        
        # Create the GUI
        self.create_widgets()
        self.load_settings()
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "scan_directories": [],
            "output_directory": os.path.join(os.getcwd(), "lists"),
            "file_extensions": {
                "media": [".mp4", ".mkv", ".avi"],
                "additional": []
            },
            "email": {
                "enabled": False,
                "sender_name": "",
                "sender_email": "",
                "receiver_email": "",
                "password": "",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            },
            "file_retention_count": 100
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    
                    # Handle nested dictionaries (email, file_extensions)
                    for nested_key in ["email", "file_extensions"]:
                        if nested_key in config and isinstance(config[nested_key], dict):
                            for sub_key in default_config[nested_key]:
                                if sub_key not in config[nested_key]:
                                    config[nested_key][sub_key] = default_config[nested_key][sub_key]
                    
                    # Backward compatibility: if email.enabled doesn't exist, default to False
                    if "enabled" not in config.get("email", {}):
                        config["email"]["enabled"] = False
                    
                    return config
        except Exception as e:
            messagebox.showerror("Config Error", f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Config Error", f"Error saving config: {e}")
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_frame = ttk.Frame(notebook)
        notebook.add(self.main_frame, text="Main")
        
        # Main Configuration tab
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="Main Configuration")
        
        # Email Configuration tab
        self.email_frame = ttk.Frame(notebook)
        notebook.add(self.email_frame, text="Email Configuration")
        
        # Logs tab
        self.logs_frame = ttk.Frame(notebook)
        notebook.add(self.logs_frame, text="Logs & Results")
        
        self.create_main_tab()
        self.create_config_tab()
        self.create_email_tab()
        self.create_logs_tab()
    
    def create_main_tab(self):
        """Create the main operations tab"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Media Manager", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Operations frame
        ops_frame = ttk.LabelFrame(self.main_frame, text="Operations", padding="10")
        ops_frame.pack(fill='x', padx=10, pady=5)
        
        # Generate media list button
        ttk.Button(ops_frame, text="Generate Media List", 
                  command=self.generate_media_list_threaded,
                  width=25).pack(pady=5)
        
        # Check for missing media button
        ttk.Button(ops_frame, text="Check for Missing Media", 
                  command=self.check_missing_media_threaded,
                  width=25).pack(pady=5)
        
        # Manage files button
        ttk.Button(ops_frame, text="Manage File Retention", 
                  command=self.manage_files_threaded,
                  width=25).pack(pady=5)
        
        # Windows filename validation button
        ttk.Button(ops_frame, text="Check Windows Filename Compatibility", 
                  command=self.check_windows_filenames_threaded,
                  width=35).pack(pady=5)
        
        # Filename fixing button
        ttk.Button(ops_frame, text="View & Fix Filename Issues", 
                  command=self.view_and_fix_filenames,
                  width=25).pack(pady=5)
        
        # Run all button
        ttk.Button(ops_frame, text="Run Complete Check", 
                  command=self.run_complete_check_threaded,
                  width=25).pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        status_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, state='disabled')
        self.status_text.pack(fill='both', expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)
    
    def create_config_tab(self):
        """Create the main configuration tab"""
        # Directories section
        dir_frame = ttk.LabelFrame(self.config_frame, text="Scan Directories", padding="10")
        dir_frame.pack(fill='x', padx=10, pady=5)
        
        # Directory listbox with scrollbar
        list_frame = ttk.Frame(dir_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.dir_listbox = tk.Listbox(list_frame, height=6)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        self.dir_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.dir_listbox.yview)
        
        self.dir_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Directory buttons
        dir_btn_frame = ttk.Frame(dir_frame)
        dir_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(dir_btn_frame, text="Add Directory", 
                  command=self.add_directory).pack(side='left', padx=5)
        ttk.Button(dir_btn_frame, text="Remove Selected", 
                  command=self.remove_directory).pack(side='left', padx=5)
        
        # Output directory
        output_frame = ttk.LabelFrame(self.config_frame, text="Output Directory", padding="10")
        output_frame.pack(fill='x', padx=10, pady=5)
        
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output_directory).pack(side='right', padx=5)
        
        # File Extensions section
        ext_frame = ttk.LabelFrame(self.config_frame, text="File Extensions", padding="10")
        ext_frame.pack(fill='x', padx=10, pady=5)
        
        # Media Extensions
        media_frame = ttk.Frame(ext_frame)
        media_frame.pack(fill='x', pady=5)
        ttk.Label(media_frame, text="Media Extensions:", width=20).pack(side='left')
        self.media_ext_var = tk.StringVar()
        ttk.Entry(media_frame, textvariable=self.media_ext_var, width=60).pack(side='left', fill='x', expand=True, padx=5)
        
        # Additional Extensions
        additional_frame = ttk.Frame(ext_frame)
        additional_frame.pack(fill='x', pady=5)
        ttk.Label(additional_frame, text="Additional Extensions:", width=20).pack(side='left')
        self.additional_ext_var = tk.StringVar()
        ttk.Entry(additional_frame, textvariable=self.additional_ext_var, width=60).pack(side='left', fill='x', expand=True, padx=5)
        
        # Extension help text
        help_frame = ttk.Frame(ext_frame)
        help_frame.pack(fill='x', pady=2)
        help_text = "Enter extensions separated by commas (e.g., .mp4, .mkv, .avi)"
        ttk.Label(help_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(side='left')
        
        # File retention
        retention_frame = ttk.LabelFrame(self.config_frame, text="File Retention", padding="10")
        retention_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(retention_frame, text="Keep latest files:").pack(side='left')
        self.retention_var = tk.StringVar()
        ttk.Entry(retention_frame, textvariable=self.retention_var, width=10).pack(side='left', padx=5)
        
        # Save button
        ttk.Button(self.config_frame, text="Save Main Configuration", 
                  command=self.save_main_settings).pack(pady=10)
    
    def create_email_tab(self):
        """Create the email configuration tab"""
        # Email Enable/Disable section
        enable_frame = ttk.LabelFrame(self.email_frame, text="Email Notifications", padding="10")
        enable_frame.pack(fill='x', padx=10, pady=5)
        
        self.email_enabled_var = tk.BooleanVar()
        self.email_enabled_checkbox = ttk.Checkbutton(
            enable_frame, 
            text="Enable email notifications for missing media", 
            variable=self.email_enabled_var,
            command=self.toggle_email_fields
        )
        self.email_enabled_checkbox.pack(anchor='w')
        
        # Email configuration
        email_frame = ttk.LabelFrame(self.email_frame, text="Email Settings", padding="10")
        email_frame.pack(fill='x', padx=10, pady=5)
        
        # Email fields
        email_fields = [
            ("Sender Name:", "sender_name"),
            ("Sender Email:", "sender_email"),
            ("Receiver Email:", "receiver_email"),
            ("Password:", "password"),
            ("SMTP Server:", "smtp_server"),
            ("SMTP Port:", "smtp_port")
        ]
        
        self.email_vars = {}
        self.email_entries = {}
        for i, (label, key) in enumerate(email_fields):
            row_frame = ttk.Frame(email_frame)
            row_frame.pack(fill='x', pady=2)
            
            ttk.Label(row_frame, text=label, width=15).pack(side='left')
            self.email_vars[key] = tk.StringVar()
            
            if key == "password":
                entry = ttk.Entry(row_frame, textvariable=self.email_vars[key], show="*")
            else:
                entry = ttk.Entry(row_frame, textvariable=self.email_vars[key])
            
            entry.pack(side='left', fill='x', expand=True, padx=5)
            self.email_entries[key] = entry
        
        # Email help text
        email_help_frame = ttk.Frame(self.email_frame)
        email_help_frame.pack(fill='x', padx=10, pady=5)
        
        help_text = ("For Gmail: Use app passwords instead of your regular password.\n"
                    "Go to Google Account Settings → Security → 2-Step Verification → App passwords")
        ttk.Label(email_help_frame, text=help_text, font=("Arial", 8), 
                 foreground="gray", wraplength=600, justify='left').pack(anchor='w')
        
        # Save button
        ttk.Button(self.email_frame, text="Save Email Configuration", 
                  command=self.save_email_settings).pack(pady=10)
    
    def toggle_email_fields(self):
        """Enable/disable email fields based on checkbox state"""
        state = 'normal' if self.email_enabled_var.get() else 'disabled'
        for entry in self.email_entries.values():
            entry.config(state=state)
    
    def create_logs_tab(self):
        """Create the logs and results tab"""
        # Filter frame
        filter_frame = ttk.LabelFrame(self.logs_frame, text="File Type Filter", padding="10")
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        # Filter radio buttons
        self.file_filter = tk.StringVar(value="all")
        filter_options = [
            ("All Files", "all"),
            ("Media Lists", "media_lists"),
            ("Missing Media", "missing_media"), 
            ("Filename Issues", "filename_issues"),
            ("Legacy Files", "root")
        ]
        
        filter_btn_frame = ttk.Frame(filter_frame)
        filter_btn_frame.pack(fill='x')
        
        for text, value in filter_options:
            ttk.Radiobutton(filter_btn_frame, text=text, variable=self.file_filter, 
                           value=value, command=self.refresh_file_list).pack(side='left', padx=10)
        
        # Recent files frame
        self.files_frame = ttk.LabelFrame(self.logs_frame, text="Recent Files", padding="10")
        self.files_frame.pack(fill='x', padx=10, pady=5)
        
        self.files_listbox = tk.Listbox(self.files_frame, height=8)
        files_scrollbar = ttk.Scrollbar(self.files_frame, orient='vertical')
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)
        files_scrollbar.config(command=self.files_listbox.yview)
        
        self.files_listbox.pack(side='left', fill='both', expand=True)
        files_scrollbar.pack(side='right', fill='y')
        
        # File buttons
        file_btn_frame = ttk.Frame(self.files_frame)
        file_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(file_btn_frame, text="View Selected", 
                  command=self.view_selected_file).pack(side='left', padx=5)
        ttk.Button(file_btn_frame, text="Refresh List", 
                  command=self.refresh_file_list).pack(side='left', padx=5)
        ttk.Button(file_btn_frame, text="Open Output Folder", 
                  command=self.open_output_folder).pack(side='left', padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self.logs_frame, text="File Content", padding="10")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_text.pack(fill='both', expand=True)
    
    def load_settings(self):
        """Load settings into GUI controls"""
        # Load directories
        self.dir_listbox.delete(0, tk.END)
        for directory in self.config["scan_directories"]:
            self.dir_listbox.insert(tk.END, directory)
        
        # Load output directory
        self.output_var.set(self.config["output_directory"])
        
        # Load file extensions
        media_exts = ", ".join(self.config["file_extensions"]["media"])
        self.media_ext_var.set(media_exts)
        
        additional_exts = ", ".join(self.config["file_extensions"]["additional"])
        self.additional_ext_var.set(additional_exts)
        
        # Load email settings
        self.email_enabled_var.set(self.config["email"].get("enabled", False))
        for key, var in self.email_vars.items():
            var.set(self.config["email"].get(key, ""))
        
        # Load retention setting
        self.retention_var.set(str(self.config["file_retention_count"]))
        
        # Update email field states based on enabled checkbox
        self.toggle_email_fields()
        
        # Refresh file list
        self.refresh_file_list()
    
    def save_main_settings(self):
        """Save main configuration settings"""
        try:
            # Save directories
            self.config["scan_directories"] = list(self.dir_listbox.get(0, tk.END))
            
            # Save output directory
            self.config["output_directory"] = self.output_var.get()
            
            # Save file extensions
            def parse_extensions(ext_string):
                if not ext_string.strip():
                    return []
                extensions = [ext.strip() for ext in ext_string.split(',') if ext.strip()]
                # Ensure extensions start with dot
                return [ext if ext.startswith('.') else '.' + ext for ext in extensions]
            
            self.config["file_extensions"]["media"] = parse_extensions(self.media_ext_var.get())
            self.config["file_extensions"]["additional"] = parse_extensions(self.additional_ext_var.get())
            
            # Validate that we have at least some file extensions
            all_extensions = self.config["file_extensions"]["media"] + self.config["file_extensions"]["additional"]
            if not all_extensions:
                messagebox.showwarning("Warning", "No file extensions specified. Adding default media extensions.")
                self.config["file_extensions"]["media"] = [".mp4", ".mkv", ".avi"]
            
            # Save retention setting
            try:
                self.config["file_retention_count"] = int(self.retention_var.get())
            except ValueError:
                messagebox.showerror("Error", "File retention count must be a number")
                return
            
            self.save_config()
            messagebox.showinfo("Success", "Main configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving main configuration: {e}")
    
    def save_email_settings(self):
        """Save email configuration settings"""
        try:
            # Save email enabled state
            self.config["email"]["enabled"] = self.email_enabled_var.get()
            
            # Save email settings
            for key, var in self.email_vars.items():
                self.config["email"][key] = var.get()
            
            self.save_config()
            
            # Validate email configuration if enabled
            if self.email_enabled_var.get():
                email_config = load_email_config_from_file(self.config_file)
                if email_config and email_config.is_valid():
                    messagebox.showinfo("Success", "Email configuration saved successfully!\n\nEmail configuration is valid and ready to use.")
                else:
                    messagebox.showwarning("Configuration Saved", 
                        "Email configuration saved, but has issues:\n\n" +
                        "• Check email address formats (must be valid email addresses)\n" +
                        "• Verify SMTP port is a number between 1-65535\n" +
                        "• Ensure all required fields are filled\n" +
                        "• For Gmail: use app passwords, not regular passwords\n\n" +
                        "Email notifications will not work until these are fixed.")
            else:
                messagebox.showinfo("Success", "Email configuration saved successfully!\n\nEmail notifications are disabled.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving email configuration: {e}")
    
    def add_directory(self):
        """Add a directory to scan"""
        directory = filedialog.askdirectory()
        if directory and directory not in self.dir_listbox.get(0, tk.END):
            self.dir_listbox.insert(tk.END, directory)
    
    def remove_directory(self):
        """Remove selected directory"""
        selected = self.dir_listbox.curselection()
        if selected:
            self.dir_listbox.delete(selected[0])
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_var.set(directory)
    
    def log_message(self, message):
        """Add a message to the status log"""
        self.status_text.config(state='normal')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()
    
    def start_operation(self):
        """Start an operation (show progress bar)"""
        self.progress.start()
    
    def stop_operation(self):
        """Stop an operation (hide progress bar)"""
        self.progress.stop()
    
    def generate_media_list_threaded(self):
        """Generate media list in a separate thread"""
        thread = threading.Thread(target=self.generate_media_list)
        thread.start()
    
    def generate_media_list(self):
        """Generate a media list"""
        try:
            self.start_operation()
            self.log_message("Starting media list generation...")
            
            directories = list(self.dir_listbox.get(0, tk.END))
            if not directories:
                self.log_message("Error: No directories configured for scanning")
                return
            
            # Ensure output directories exist
            output_dir = self.output_var.get()
            media_lists_dir = os.path.join(output_dir, "media_lists")
            os.makedirs(media_lists_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(media_lists_dir, f"media_list_{timestamp}.txt")
            
            # Get configured file extensions
            all_extensions = (self.config["file_extensions"]["media"] + 
                            self.config["file_extensions"]["additional"])
            if not all_extensions:
                all_extensions = ['.mp4', '.mkv', '.avi']  # Fallback to defaults
            
            self.log_message(f"Scanning for extensions: {', '.join(all_extensions)}")
            
            # Generate the list
            generate_media_list(directories, output_file, all_extensions)
            
            self.log_message(f"Media list generated: {output_file}")
            self.refresh_file_list()
            
        except Exception as e:
            self.log_message(f"Error generating media list: {e}")
        finally:
            self.stop_operation()
    
    def check_missing_media_threaded(self):
        """Check for missing media in a separate thread"""
        thread = threading.Thread(target=self.check_missing_media)
        thread.start()
    
    def check_missing_media(self):
        """Check for missing media files"""
        try:
            self.start_operation()
            self.log_message("Checking for missing media...")
            
            output_dir = self.output_var.get()
            media_lists_dir = os.path.join(output_dir, "media_lists")
            
            # Find the two most recent media lists
            most_recent, second_recent = find_two_most_recent_media_lists(media_lists_dir, 'media_list_*.txt')
            
            if not most_recent or not second_recent:
                self.log_message("Error: Need at least 2 media lists to compare")
                return
            
            # Load titles from both files
            def load_titles_from_file(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return set(f.read().splitlines())
            
            most_recent_titles = load_titles_from_file(most_recent)
            second_recent_titles = load_titles_from_file(second_recent)
            
            # Find missing titles
            missing_titles = second_recent_titles - most_recent_titles
            
            if missing_titles:
                # Save missing titles
                missing_media_dir = os.path.join(output_dir, "missing_media")
                os.makedirs(missing_media_dir, exist_ok=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                missing_file = os.path.join(missing_media_dir, f"missing_media_{timestamp}.txt")
                
                with open(missing_file, 'w', encoding='utf-8') as f:
                    for title in sorted(missing_titles):
                        f.write(f"{title}\n")
                
                self.log_message(f"Found {len(missing_titles)} missing media files")
                self.log_message(f"Missing media list saved: {missing_file}")
                
                # Send email if configured
                if self.is_email_configured():
                    self.log_message("Attempting to send email notification...")
                    success = send_missing_media_email(
                        missing_titles, 
                        config_file="media_manager_config.json",
                        log_function=self.log_message
                    )
                else:
                    # Check if email is disabled vs not configured
                    if not self.config.get("email", {}).get("enabled", False):
                        self.log_message("Email notifications are disabled. Enable and configure via Email Configuration tab - skipping email notification")
                    else:
                        self.log_message("Email not properly configured. Configure via Email Configuration tab - skipping email notification")
                
            else:
                self.log_message("No missing media files found")
            
            self.refresh_file_list()
            
        except Exception as e:
            self.log_message(f"Error checking for missing media: {e}")
        finally:
            self.stop_operation()
    
    def manage_files_threaded(self):
        """Manage file retention in a separate thread"""
        thread = threading.Thread(target=self.manage_files)
        thread.start()
    
    def manage_files(self):
        """Manage file retention (equivalent to manage_txt_files.sh)"""
        try:
            self.start_operation()
            self.log_message("Managing file retention...")
            
            output_dir = self.output_var.get()
            retention_count = self.config["file_retention_count"]
            
            # Subdirectories to manage
            subdirs = ["media_lists", "missing_media", "filename_issues"]
            total_deleted = 0
            
            for subdir in subdirs:
                subdir_path = os.path.join(output_dir, subdir)
                if os.path.exists(subdir_path):
                    # Get all text files in this subdirectory sorted by modification time
                    pattern = os.path.join(subdir_path, "*.txt")
                    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
                    
                    if len(files) > retention_count:
                        files_to_delete = files[retention_count:]
                        for file_path in files_to_delete:
                            try:
                                os.remove(file_path)
                                self.log_message(f"Deleted old file from {subdir}: {os.path.basename(file_path)}")
                                total_deleted += 1
                            except Exception as e:
                                self.log_message(f"Error deleting {file_path}: {e}")
                        
                        self.log_message(f"{subdir}: Kept {retention_count} most recent files, deleted {len(files_to_delete)} old files")
                    else:
                        self.log_message(f"{subdir}: Only {len(files)} files found, no cleanup needed")
            
            if total_deleted == 0:
                self.log_message("No files needed cleanup")
            else:
                self.log_message(f"Total files deleted: {total_deleted}")
            
            self.refresh_file_list()
            
        except Exception as e:
            self.log_message(f"Error managing files: {e}")
        finally:
            self.stop_operation()
    
    def run_complete_check_threaded(self):
        """Run complete check in a separate thread"""
        thread = threading.Thread(target=self.run_complete_check)
        thread.start()
    
    def run_complete_check(self):
        """Run a complete check (generate list, check missing, manage files, validate Windows filenames)"""
        self.log_message("Starting complete check...")
        self.generate_media_list()
        self.check_missing_media()
        self.manage_files()
        self.check_windows_filenames()
        self.log_message("Complete check finished")
    
    def check_windows_filenames_threaded(self):
        """Check Windows filename compatibility in a separate thread"""
        thread = threading.Thread(target=self.check_windows_filenames)
        thread.start()
    
    def check_windows_filenames(self):
        """Check the most recent media list for Windows filename compatibility issues"""
        try:
            self.start_operation()
            self.log_message("Checking Windows filename compatibility...")
            
            output_dir = self.output_var.get()
            media_lists_dir = os.path.join(output_dir, "media_lists")
            
            # Find the most recent media list
            pattern = os.path.join(media_lists_dir, 'media_list_*.txt')
            files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
            
            if not files:
                self.log_message("Error: No media list files found. Please generate a media list first.")
                return
            
            most_recent_file = files[0]
            self.log_message(f"Analyzing: {os.path.basename(most_recent_file)}")
            
            # Validate filenames
            validator = WindowsFilenameValidator()
            validation_results = validator.validate_from_file(most_recent_file)
            
            if validation_results:
                # Save the report
                filename_issues_dir = os.path.join(output_dir, "filename_issues")
                os.makedirs(filename_issues_dir, exist_ok=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = os.path.join(filename_issues_dir, f"windows_filename_issues_{timestamp}.txt")
                
                report = validator.generate_report(validation_results, report_file)
                
                self.log_message(f"Found {len(validation_results)} files with Windows naming issues")
                self.log_message(f"Report saved: {report_file}")
                
                # Show a summary in the log
                self.log_message("\nSample issues found:")
                count = 0
                for filepath, issues in validation_results.items():
                    if count >= 5:  # Show only first 5 for brevity
                        self.log_message(f"... and {len(validation_results) - 5} more (see report file)")
                        break
                    self.log_message(f"  • {os.path.basename(filepath)}: {issues[0]}")
                    count += 1
                
            else:
                self.log_message("✅ All filenames are Windows compatible!")
            
            self.refresh_file_list()
            
        except Exception as e:
            self.log_message(f"Error checking Windows filenames: {e}")
        finally:
            self.stop_operation()
    
    def view_and_fix_filenames(self):
        """Open dialog to view and fix filename issues"""
        try:
            output_dir = self.output_var.get()
            filename_issues_dir = os.path.join(output_dir, "filename_issues")
            
            if not os.path.exists(filename_issues_dir):
                messagebox.showinfo("No Issues Found", 
                    "No filename issues directory found. Run 'Check Windows Filename Compatibility' first.")
                return
            
            # Find the most recent filename issues report
            pattern = os.path.join(filename_issues_dir, 'windows_filename_issues_*.txt')
            files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
            
            if not files:
                messagebox.showinfo("No Issues Found", 
                    "No filename issues reports found. Run 'Check Windows Filename Compatibility' first.")
                return
            
            # Load the most recent media list to get current files
            media_lists_dir = os.path.join(output_dir, "media_lists")
            media_pattern = os.path.join(media_lists_dir, 'media_list_*.txt')
            media_files = sorted(glob.glob(media_pattern), key=os.path.getmtime, reverse=True)
            
            if not media_files:
                messagebox.showwarning("No Media List", 
                    "No media list found. Generate a media list first.")
                return
            
            # Validate current files and get suggestions
            validator = WindowsFilenameValidator()
            validation_results = validator.validate_from_file(media_files[0])
            
            if not validation_results:
                messagebox.showinfo("No Issues", "No filename issues found in the current media list!")
                return
            
            # Open the filename fixing dialog
            dialog = FilenameFixDialog(self.root, validation_results, validator, self.log_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening filename fix dialog: {e}")
    
    def is_email_configured(self):
        """Check if email is enabled and properly configured"""
        # First check if email is enabled
        if not self.config.get("email", {}).get("enabled", False):
            return False
        
        # Use the shared module's validation logic for consistency
        email_config = load_email_config_from_file(self.config_file)
        return email_config is not None and email_config.is_valid()
    
    
    def refresh_file_list(self):
        """Refresh the list of files in the logs tab with filtering"""
        try:
            self.files_listbox.delete(0, tk.END)
            output_dir = self.output_var.get()
            
            if os.path.exists(output_dir):
                # Get current filter
                current_filter = getattr(self, 'file_filter', None)
                if current_filter is None:
                    # Initialize filter if not exists (for backward compatibility)
                    self.file_filter = tk.StringVar(value="all")
                    current_filter = self.file_filter
                
                filter_value = current_filter.get()
                
                # Subdirectories to check
                subdirs = ["media_lists", "missing_media", "filename_issues"]
                all_files = []
                
                for subdir in subdirs:
                    # Skip subdirectory if filtering and it doesn't match
                    if filter_value != "all" and filter_value != subdir:
                        continue
                    
                    subdir_path = os.path.join(output_dir, subdir)
                    if os.path.exists(subdir_path):
                        pattern = os.path.join(subdir_path, "*.txt")
                        files = glob.glob(pattern)
                        for file_path in files:
                            all_files.append((file_path, subdir))
                
                # Also check root directory for any legacy files
                if filter_value == "all" or filter_value == "root":
                    root_pattern = os.path.join(output_dir, "*.txt")
                    root_files = glob.glob(root_pattern)
                    for file_path in root_files:
                        all_files.append((file_path, "root"))
                
                # Sort all files by modification time (newest first)
                all_files.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
                
                for file_path, subdir in all_files:
                    filename = os.path.basename(file_path)
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if subdir == "root":
                        display_name = f"{filename} ({mod_time.strftime('%Y-%m-%d %H:%M:%S')})"
                    else:
                        display_name = f"[{subdir}] {filename} ({mod_time.strftime('%Y-%m-%d %H:%M:%S')})"
                    self.files_listbox.insert(tk.END, display_name)
                
                # Update frame title with file count and filter info
                file_count = len(all_files)
                if filter_value == "all":
                    filter_text = "all files"
                else:
                    filter_map = {
                        "media_lists": "media lists",
                        "missing_media": "missing media reports", 
                        "filename_issues": "filename issue reports",
                        "root": "legacy files"
                    }
                    filter_text = filter_map.get(filter_value, filter_value)
                
                self.files_frame.config(text=f"Recent Files ({file_count} {filter_text})")
                        
        except Exception as e:
            self.log_message(f"Error refreshing file list: {e}")
    
    def view_selected_file(self):
        """View the content of the selected file"""
        selected = self.files_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file to view")
            return
        
        try:
            # Get the filename from the display name
            display_name = self.files_listbox.get(selected[0])
            
            # Handle both old format and new format with subdirectory
            if display_name.startswith("["):
                # New format: [subdir] filename (timestamp)
                parts = display_name.split("] ", 1)
                subdir = parts[0][1:]  # Remove the opening bracket
                filename = parts[1].split(" (")[0]  # Remove timestamp part
                file_path = os.path.join(self.output_var.get(), subdir, filename)
            else:
                # Old format or root: filename (timestamp)
                filename = display_name.split(" (")[0]  # Remove timestamp part
                file_path = os.path.join(self.output_var.get(), filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(1.0, f"=== {filename} ===\n\n{content}")
            self.log_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
    
    def open_output_folder(self):
        """Open the output folder in Windows Explorer"""
        try:
            output_dir = self.output_var.get()
            if os.path.exists(output_dir):
                os.startfile(output_dir)
            else:
                messagebox.showwarning("Folder Not Found", "Output directory does not exist")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening folder: {e}")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = MediaManagerGUI(root)
    
    # Set window icon if available
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # Icon file not found, continue without it
    
    root.mainloop()

if __name__ == "__main__":
    main()
