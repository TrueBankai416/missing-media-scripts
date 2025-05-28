#!/usr/bin/env python3
"""
GUI for Missing Media Scripts
A tkinter-based GUI to simplify the process of managing media file monitoring on Windows and Linux.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import datetime
import glob
import re
import platform
import subprocess
import sys
import argparse
import webbrowser
from email_utils import send_missing_media_email, load_email_config_from_file
from pathlib import Path

# Import functions from existing scripts
from generate_media_list import generate_media_list
from generate_missing_media_list import find_two_most_recent_media_lists
from windows_filename_validator import WindowsFilenameValidator

# Import version and update checking
from version import __version__, __author__, __description__, __repository__
from update_checker import UpdateChecker

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
        self.root.title("Media Manager - Professional")
        
        # Set custom icon if available
        try:
            if os.path.exists("media_manager_icon.ico"):
                self.root.iconbitmap("media_manager_icon.ico")
            elif os.path.exists("media_manager_icon_64.png"):
                # Fallback to PNG icon
                icon_img = tk.PhotoImage(file="media_manager_icon_64.png")
                self.root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"Could not set icon: {e}")
        
        # Apply modern styling
        self.setup_modern_style()
        
        # Start maximized to show all buttons properly
        try:
            # Try zoomed state first (Windows)
            self.root.state('zoomed')
        except tk.TclError:
            try:
                # Alternative for other platforms
                self.root.attributes('-zoomed', True)
            except tk.TclError:
                # Fallback to manual maximization
                self.root.geometry("1200x800")
                self.root.update_idletasks()
                width = self.root.winfo_screenwidth()
                height = self.root.winfo_screenheight()
                self.root.geometry(f"{width}x{height}+0+0")
        
        # Configuration file path
        self.config_file = "media_manager_config.json"
        self.config = self.load_config()
        
        # Create the GUI
        self.create_widgets()
        self.load_settings()
    
    def setup_modern_style(self):
        """Apply modern styling to the GUI"""
        style = ttk.Style()
        
        # Try to use a more modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Configure modern colors
        bg_color = "#f8f9fa"  # Light gray background
        accent_color = "#4a90e2"  # Modern blue
        dark_bg = "#343a40"  # Dark background for contrast
        light_text = "#ffffff"  # White text
        dark_text = "#212529"  # Dark text
        success_color = "#28a745"  # Green for success
        danger_color = "#dc3545"  # Red for errors
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure ttk styles
        style.configure('Modern.TLabel', 
                       background=bg_color, 
                       foreground=dark_text,
                       font=('Segoe UI', 9))
        
        style.configure('Title.TLabel',
                       background=bg_color,
                       foreground=dark_text,
                       font=('Segoe UI', 14, 'bold'))
        
        style.configure('Modern.TButton',
                       background=accent_color,
                       foreground=light_text,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map('Modern.TButton',
                 background=[('active', '#357abd'),
                           ('pressed', '#2968a3')])
        
        style.configure('Success.TButton',
                       background=success_color,
                       foreground=light_text,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map('Success.TButton',
                 background=[('active', '#218838'),
                           ('pressed', '#1e7e34')])
        
        style.configure('Modern.TFrame',
                       background=bg_color,
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TLabelFrame',
                       background=bg_color,
                       borderwidth=2,
                       relief='raised',
                       labelmargins=(10, 5, 5, 5))
        
        style.configure('Modern.TLabelFrame.Label',
                       background=bg_color,
                       foreground=dark_text,
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Modern.TNotebook',
                       background=bg_color,
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       background='#e9ecef',
                       foreground=dark_text,
                       padding=[20, 8],
                       font=('Segoe UI', 9))
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', accent_color),
                           ('active', '#dee2e6')],
                 foreground=[('selected', light_text)])
        
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       insertcolor=dark_text,
                       font=('Segoe UI', 9))
        
        style.configure('Modern.TCheckbutton',
                       background=bg_color,
                       foreground=dark_text,
                       font=('Segoe UI', 9))
        
        style.configure('Modern.TProgressbar',
                       background=accent_color,
                       borderwidth=0,
                       lightcolor=accent_color,
                       darkcolor=accent_color)
        
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
            "file_retention_count": 100,
            "automation": {
                "enabled": False,
                "tasks": {
                    "generate_media_list": {
                        "enabled": False,
                        "time": "05:00",
                        "frequency": "daily"
                    },
                    "check_missing_media": {
                        "enabled": False,
                        "time": "05:30",
                        "frequency": "daily"
                    },
                    "manage_file_retention": {
                        "enabled": False,
                        "time": "06:00",
                        "frequency": "daily"
                    },
                    "check_windows_filenames": {
                        "enabled": False,
                        "time": "06:30",
                        "frequency": "daily"
                    },
                    "complete_check": {
                        "enabled": False,
                        "time": "05:00",
                        "frequency": "daily"
                    }
                }
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    
                    # Handle nested dictionaries (email, file_extensions, automation)
                    for nested_key in ["email", "file_extensions", "automation"]:
                        if nested_key in config and isinstance(config[nested_key], dict):
                            for sub_key in default_config[nested_key]:
                                if sub_key not in config[nested_key]:
                                    config[nested_key][sub_key] = default_config[nested_key][sub_key]
                        
                        # Special handling for automation tasks
                        if nested_key == "automation" and "tasks" in default_config[nested_key]:
                            if "tasks" not in config.get(nested_key, {}):
                                config.setdefault(nested_key, {})["tasks"] = default_config[nested_key]["tasks"]
                            else:
                                # Merge individual task configurations
                                for task_id, task_config in default_config[nested_key]["tasks"].items():
                                    if task_id not in config[nested_key]["tasks"]:
                                        config[nested_key]["tasks"][task_id] = task_config
                    
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
        # Create notebook for tabs with modern styling
        notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.main_frame, text="Main")
        
        # Main Configuration tab
        self.config_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.config_frame, text="Main Configuration")
        
        # Email Configuration tab
        self.email_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.email_frame, text="Email Configuration")
        
        # Automation tab
        self.automation_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.automation_frame, text="Automation")
        
        # Logs tab
        self.logs_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.logs_frame, text="Logs & Results")
        
        # Help tab (moved after Logs & Results as requested)
        self.help_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.help_frame, text="Help")
        
        # Info tab
        self.info_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.info_frame, text="Info")
        
        # Support tab
        self.support_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.support_frame, text="Support")
        
        # Issues tab
        self.issues_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(self.issues_frame, text="Issues")
        
        self.create_main_tab()
        self.create_config_tab()
        self.create_email_tab()
        self.create_automation_tab()
        self.create_logs_tab()
        self.create_help_tab()
        self.create_info_tab()
        self.create_support_tab()
        self.create_issues_tab()
    
    def create_main_tab(self):
        """Create the main operations tab"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Media Manager", style="Title.TLabel")
        title_label.pack(pady=15)
        
        # Operations frame
        ops_frame = ttk.LabelFrame(self.main_frame, text="Operations", padding="15", style="Modern.TLabelFrame")
        ops_frame.pack(fill='x', padx=15, pady=10)
        
        # Generate media list button
        ttk.Button(ops_frame, text="📁 Generate Media List", 
                  command=self.generate_media_list_threaded,
                  width=30, style="Modern.TButton").pack(pady=8)
        
        # Check for missing media button
        ttk.Button(ops_frame, text="🔍 Check for Missing Media", 
                  command=self.check_missing_media_threaded,
                  width=30, style="Modern.TButton").pack(pady=8)
        
        # Manage files button
        ttk.Button(ops_frame, text="🗂️ Manage File Retention", 
                  command=self.manage_files_threaded,
                  width=30, style="Modern.TButton").pack(pady=8)
        
        # Windows filename validation button
        ttk.Button(ops_frame, text="✅ Check Windows Filename Compatibility", 
                  command=self.check_windows_filenames_threaded,
                  width=40, style="Modern.TButton").pack(pady=8)
        
        # Filename fixing button
        ttk.Button(ops_frame, text="🔧 View & Fix Filename Issues", 
                  command=self.view_and_fix_filenames,
                  width=30, style="Modern.TButton").pack(pady=8)
        
        # Run all button
        ttk.Button(ops_frame, text="⚡ Run Complete Check", 
                  command=self.run_complete_check_threaded,
                  width=30, style="Success.TButton").pack(pady=15)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="15", style="Modern.TLabelFrame")
        status_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, state='disabled',
                                                    font=('Consolas', 9), 
                                                    bg='#ffffff', fg='#212529',
                                                    insertbackground='#212529')
        self.status_text.pack(fill='both', expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate', style="Modern.TProgressbar")
        self.progress.pack(fill='x', padx=15, pady=10)
    
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
    
    def create_automation_tab(self):
        """Create the automation configuration tab"""
        # Enable/Disable Automation section
        enable_frame = ttk.LabelFrame(self.automation_frame, text="Task Automation", padding="10")
        enable_frame.pack(fill='x', padx=10, pady=5)
        
        self.automation_enabled_var = tk.BooleanVar()
        self.automation_enabled_checkbox = ttk.Checkbutton(
            enable_frame, 
            text="Enable task automation", 
            variable=self.automation_enabled_var,
            command=self.toggle_automation_fields
        )
        self.automation_enabled_checkbox.pack(anchor='w')
        
        # Platform info
        platform_info = ttk.Frame(enable_frame)
        platform_info.pack(fill='x', pady=5)
        
        current_platform = platform.system()
        platform_text = f"Detected platform: {current_platform}"
        if current_platform == "Windows":
            platform_text += " (will use Windows Task Scheduler)"
        elif current_platform == "Linux":
            platform_text += " (will use cron)"
        else:
            platform_text += " (may not be fully supported)"
        
        ttk.Label(platform_info, text=platform_text, font=("Arial", 9), 
                 foreground="gray").pack(anchor='w')
        
        # Automated Tasks section
        tasks_frame = ttk.LabelFrame(self.automation_frame, text="Automated Tasks", padding="10")
        tasks_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create a scrollable frame for tasks
        canvas = tk.Canvas(tasks_frame)
        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=canvas.yview)
        self.tasks_scrollable_frame = ttk.Frame(canvas)
        
        self.tasks_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.tasks_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Task definitions
        self.task_definitions = {
            "generate_media_list": {
                "name": "Generate Media List",
                "description": "Scan directories and create a new media list file"
            },
            "check_missing_media": {
                "name": "Check for Missing Media",
                "description": "Compare recent lists and identify missing files"
            },
            "manage_file_retention": {
                "name": "Manage File Retention",
                "description": "Clean up old list files (keep only latest N files)"
            },
            "check_windows_filenames": {
                "name": "Check Windows Filename Compatibility",
                "description": "Validate filenames for Windows compatibility"
            },
            "complete_check": {
                "name": "Run Complete Check",
                "description": "Run all operations in sequence: generate lists, check missing media, manage files, detect filename issues (does not auto-fix)"
            }
        }
        
        self.task_vars = {}
        self.task_time_vars = {}
        self.task_freq_vars = {}
        self.task_widgets = {}
        
        for task_id, task_info in self.task_definitions.items():
            self.create_task_configuration(task_id, task_info)
        
        # Warning for complete check
        warning_frame = ttk.Frame(self.tasks_scrollable_frame)
        warning_frame.pack(fill='x', pady=10)
        
        warning_text = ("⚠️ Note: If 'Run Complete Check' is enabled, it will override individual task settings. "
                       "All operations will run in sequence at the specified time. "
                       "Filename checking only detects issues and creates reports - it does NOT automatically rename files.")
        ttk.Label(warning_frame, text=warning_text, font=("Arial", 9), 
                 foreground="orange", wraplength=700, justify='left').pack(anchor='w')
        
        # Control buttons
        button_frame = ttk.Frame(self.automation_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Automation Settings", 
                  command=self.save_automation_settings).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Apply Scheduled Tasks", 
                  command=self.apply_scheduled_tasks).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove All Scheduled Tasks", 
                  command=self.remove_scheduled_tasks).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Test Task Creation", 
                  command=self.test_task_creation).pack(side='left', padx=5)
    
    def create_task_configuration(self, task_id, task_info):
        """Create configuration widgets for a single task"""
        task_frame = ttk.LabelFrame(self.tasks_scrollable_frame, text=task_info["name"], padding="10")
        task_frame.pack(fill='x', pady=5)
        
        # Description
        desc_frame = ttk.Frame(task_frame)
        desc_frame.pack(fill='x', pady=2)
        ttk.Label(desc_frame, text=task_info["description"], font=("Arial", 9), 
                 foreground="gray").pack(anchor='w')
        
        # Controls frame
        controls_frame = ttk.Frame(task_frame)
        controls_frame.pack(fill='x', pady=5)
        
        # Enable checkbox
        self.task_vars[task_id] = tk.BooleanVar()
        enable_cb = ttk.Checkbutton(controls_frame, text="Enable", 
                                   variable=self.task_vars[task_id])
        enable_cb.pack(side='left', padx=5)
        
        # Time setting
        ttk.Label(controls_frame, text="Time:").pack(side='left', padx=(20, 5))
        self.task_time_vars[task_id] = tk.StringVar()
        time_entry = ttk.Entry(controls_frame, textvariable=self.task_time_vars[task_id], width=8)
        time_entry.pack(side='left', padx=5)
        ttk.Label(controls_frame, text="(HH:MM 24-hour format)", font=("Arial", 8), 
                 foreground="gray").pack(side='left', padx=5)
        
        # Frequency setting
        ttk.Label(controls_frame, text="Frequency:").pack(side='left', padx=(20, 5))
        self.task_freq_vars[task_id] = tk.StringVar()
        freq_combo = ttk.Combobox(controls_frame, textvariable=self.task_freq_vars[task_id], 
                                 values=["daily", "weekly"], state="readonly", width=10)
        freq_combo.pack(side='left', padx=5)
        
        # Store widgets for later access
        self.task_widgets[task_id] = {
            'frame': task_frame,
            'enable_cb': enable_cb,
            'time_entry': time_entry,
            'freq_combo': freq_combo
        }
    
    def toggle_automation_fields(self):
        """Enable/disable automation fields based on checkbox state"""
        state = 'normal' if self.automation_enabled_var.get() else 'disabled'
        
        for task_widgets in self.task_widgets.values():
            task_widgets['enable_cb'].config(state=state)
            task_widgets['time_entry'].config(state=state)
            task_widgets['freq_combo'].config(state=state)
    
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
    
    def create_info_tab(self):
        """Create the info tab with version information and update checking"""
        # Version Information section
        version_frame = ttk.LabelFrame(self.info_frame, text="Version Information", padding="10")
        version_frame.pack(fill='x', padx=10, pady=5)
        
        # Current version info
        current_frame = ttk.Frame(version_frame)
        current_frame.pack(fill='x', pady=5)
        
        ttk.Label(current_frame, text="Application:", font=("Arial", 10, "bold")).pack(anchor='w')
        ttk.Label(current_frame, text=__description__, font=("Arial", 9)).pack(anchor='w', padx=20)
        
        ttk.Label(current_frame, text="Current Version:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10,0))
        ttk.Label(current_frame, text=__version__, font=("Arial", 9)).pack(anchor='w', padx=20)
        
        ttk.Label(current_frame, text="Author:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10,0))
        ttk.Label(current_frame, text=__author__, font=("Arial", 9)).pack(anchor='w', padx=20)
        
        ttk.Label(current_frame, text="Repository:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10,0))
        ttk.Label(current_frame, text=f"github.com/{__repository__}", font=("Arial", 9)).pack(anchor='w', padx=20)
        
        # Update Information section
        update_frame = ttk.LabelFrame(self.info_frame, text="Update Information", padding="10")
        update_frame.pack(fill='x', padx=10, pady=5)
        
        # Latest version display
        latest_frame = ttk.Frame(update_frame)
        latest_frame.pack(fill='x', pady=5)
        
        ttk.Label(latest_frame, text="Latest Version:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.latest_version_label = ttk.Label(latest_frame, text="Checking...", font=("Arial", 9))
        self.latest_version_label.pack(anchor='w', padx=20)
        
        # Update status
        self.update_status_label = ttk.Label(latest_frame, text="", font=("Arial", 9))
        self.update_status_label.pack(anchor='w', padx=20, pady=(5,0))
        
        # Update buttons
        button_frame = ttk.Frame(update_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Check for Updates", 
                  command=self.check_for_updates_threaded).pack(side='left', padx=5)
        
        self.view_release_button = ttk.Button(button_frame, text="View Latest Release", 
                                             command=self.view_latest_release, state='disabled')
        self.view_release_button.pack(side='left', padx=5)
        
        self.download_button = ttk.Button(button_frame, text="Download Update", 
                                         command=self.download_update, state='disabled')
        self.download_button.pack(side='left', padx=5)
        
        # Release Notes section
        notes_frame = ttk.LabelFrame(self.info_frame, text="Latest Release Notes", padding="10")
        notes_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.release_notes_text = scrolledtext.ScrolledText(notes_frame, height=10, state='disabled')
        self.release_notes_text.pack(fill='both', expand=True)
        
        # Initialize update checker
        self.update_checker = UpdateChecker()
        self.update_info = None
        
        # Start initial update check
        self.check_for_updates_threaded()
    
    def create_help_tab(self):
        """Create the help tab explaining what each button does"""
        # Title
        title_label = ttk.Label(self.help_frame, text="Help & Button Guide", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main container frame to center content
        main_container = ttk.Frame(self.help_frame)
        main_container.pack(fill='both', expand=True, padx=50, pady=10)
        
        # Main scrollable frame
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Store canvas window id for centering
        self.help_canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure scrollable frame to update scroll region
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the content horizontally
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x_center = (canvas_width - frame_width) // 2
                canvas.coords(self.help_canvas_window, x_center, 0)
            else:
                canvas.coords(self.help_canvas_window, 0, 0)
        
        # Configure canvas to center content when resized
        def on_canvas_configure(event):
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x_center = (canvas_width - frame_width) // 2
                canvas.coords(self.help_canvas_window, x_center, 0)
            else:
                canvas.coords(self.help_canvas_window, 0, 0)
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button explanations
        button_explanations = [
            ("Generate Media List", 
             "Scans your configured directories for media files and creates a timestamped list. "
             "This is the first step in tracking your media collection. The list includes all "
             "video files found in your scan directories. Can optionally include addistional extensions"
             " for different file types"),
            
            ("Check for Missing Media", 
             "Compares the two most recent media lists to identify files that have gone missing. "
             "Creates a report showing which files were present before but are no longer found. "
             "Useful for detecting deleted, moved, or corrupted media files."),
            
            ("Manage File Retention", 
             "Cleans up old list files to prevent disk space buildup. Keeps only the most recent "
             "N files (configured in settings). Helps maintain your lists directory by removing "
             "outdated media lists and reports."),
            
            ("Check Windows Filename Compatibility", 
             "Validates filenames for Windows compatibility issues. Detects problems like invalid "
             "characters, reserved names, or names that are too long. Creates a detailed report "
             "of any issues found. Does NOT automatically fix files."),
            
            ("View & Fix Filename Issues", 
             "Opens an interactive dialog to review and selectively fix filename issues found by "
             "the compatibility check. Allows you to preview suggested fixes and choose which "
             "ones to apply. Actually renames files when you approve the changes."),
            
            ("Run Complete Check", 
             "Executes all operations in sequence: generates a new media list, checks for missing "
             "media, manages file retention, and checks filename compatibility. This is the most "
             "comprehensive option and is recommended for regular monitoring.")
        ]
        
        for button_name, explanation in button_explanations:
            # Create frame for each button explanation
            btn_frame = ttk.LabelFrame(scrollable_frame, text=button_name, padding="10")
            btn_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(btn_frame, text=explanation, font=("Arial", 9), 
                     wraplength=700, justify='left').pack(anchor='w')
        
        # Additional help section
        tips_frame = ttk.LabelFrame(scrollable_frame, text="Tips & Best Practices", padding="10")
        tips_frame.pack(fill='x', padx=10, pady=10)
        
        tips_text = """• Configure your scan directories in 'Main Configuration' before running operations
• Set up email notifications to get alerts when media goes missing
• Use automation to schedule regular checks without manual intervention
• Review the 'Logs & Results' tab to see detailed output from operations
• The 'Run Complete Check' is perfect for daily automated monitoring
• Always backup important media files - this tool helps detect issues but doesn't prevent data loss"""
        
        ttk.Label(tips_frame, text=tips_text, font=("Arial", 9), 
                 wraplength=700, justify='left').pack(anchor='w')
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def check_for_updates_threaded(self):
        """Check for updates in a separate thread"""
        thread = threading.Thread(target=self.check_for_updates)
        thread.start()
    
    def check_for_updates(self):
        """Check for updates and update the GUI"""
        try:
            self.latest_version_label.config(text="Checking...")
            self.update_status_label.config(text="", foreground="black")
            self.view_release_button.config(state='disabled')
            self.download_button.config(state='disabled')
            
            # Clear release notes
            self.release_notes_text.config(state='normal')
            self.release_notes_text.delete(1.0, tk.END)
            self.release_notes_text.config(state='disabled')
            
            # Check for updates
            self.update_info = self.update_checker.check_for_updates()
            
            # Update GUI with results
            if 'error' in self.update_info:
                self.latest_version_label.config(text="Error checking for updates")
                self.update_status_label.config(text=self.update_info['error'], foreground="red")
            else:
                latest_version = self.update_info['latest_version']
                self.latest_version_label.config(text=latest_version)
                
                if self.update_info['update_available']:
                    self.update_status_label.config(text="🎉 Update available!", foreground="green")
                    self.view_release_button.config(state='normal')
                    self.download_button.config(state='normal')
                    
                    # Show release notes if available
                    if self.update_info.get('release_notes'):
                        self.release_notes_text.config(state='normal')
                        self.release_notes_text.insert(1.0, self.update_info['release_notes'])
                        self.release_notes_text.config(state='disabled')
                    
                    # Show update popup
                    self.show_update_popup()
                else:
                    self.update_status_label.config(text="✅ You're up to date!", foreground="blue")
                    
                # Enable view release button even if no update (to see latest release)
                self.view_release_button.config(state='normal')
                
        except Exception as e:
            self.latest_version_label.config(text="Error")
            self.update_status_label.config(text=f"Error checking for updates: {e}", foreground="red")
    
    def show_update_popup(self):
        """Show update available popup"""
        if not self.update_info or not self.update_info.get('update_available'):
            return
        
        latest_version = self.update_info['latest_version']
        current_version = self.update_info['current_version']
        
        result = messagebox.askyesno(
            "Update Available",
            f"A new version of Media Manager is available!\n\n"
            f"Current Version: {current_version}\n"
            f"Latest Version: {latest_version}\n\n"
            f"Would you like to view the release page?",
            icon='info'
        )
        
        if result:
            self.view_latest_release()
    
    def view_latest_release(self):
        """Open the latest release page in browser"""
        if self.update_info and self.update_info.get('release_url'):
            try:
                webbrowser.open(self.update_info['release_url'])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {e}")
        else:
            # Fallback to releases page
            try:
                webbrowser.open(f"https://github.com/{__repository__}/releases")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def download_update(self):
        """Direct user to download the update"""
        if self.update_info and self.update_info.get('release_url'):
            try:
                webbrowser.open(self.update_info['release_url'])
                messagebox.showinfo("Download Update", 
                    "The release page has been opened in your browser.\n\n"
                    "Look for download links or assets on the release page.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {e}")
        else:
            messagebox.showinfo("Download Update", 
                "Please visit the GitHub repository releases page to download the latest version:\n\n"
                f"https://github.com/{__repository__}/releases")
    
    def create_support_tab(self):
        """Create the support tab with repo and buymeacoffee links"""
        # Title
        title_label = ttk.Label(self.support_frame, text="Support & Community", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Repository section
        repo_frame = ttk.LabelFrame(self.support_frame, text="GitHub Repository", padding="20")
        repo_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(repo_frame, text="Visit our GitHub repository for:", font=("Arial", 10, "bold")).pack(anchor='w')
        
        repo_features = """• Latest releases and updates
• Source code and documentation
• Bug reports and feature requests
• Installation instructions
• Community discussions"""
        
        ttk.Label(repo_frame, text=repo_features, font=("Arial", 9), 
                 justify='left').pack(anchor='w', padx=20, pady=5)
        
        ttk.Button(repo_frame, text="Open GitHub Repository", 
                  command=self.open_github_repo).pack(pady=10)
        
        # Discord section
        discord_frame = ttk.LabelFrame(self.support_frame, text="Community Discord", padding="20")
        discord_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(discord_frame, text="Join our Discord community for:", font=("Arial", 10, "bold")).pack(anchor='w')
        
        discord_features = """• Real-time support and help
• Feature discussions and suggestions
• Share your setup and tips
• Connect with other users"""
        
        ttk.Label(discord_frame, text=discord_features, font=("Arial", 9), 
                 justify='left').pack(anchor='w', padx=20, pady=5)
        
        ttk.Button(discord_frame, text="Join Discord Server", 
                  command=self.open_discord).pack(pady=10)
        
        # Support development section
        support_frame = ttk.LabelFrame(self.support_frame, text="Support Development", padding="20")
        support_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(support_frame, text="Enjoying Media Manager? Support continued development:", 
                 font=("Arial", 10, "bold")).pack(anchor='w')
        
        support_text = """This project is developed and maintained in my spare time. 
Your support helps keep the project active and enables new features!"""
        
        ttk.Label(support_frame, text=support_text, font=("Arial", 9), 
                 wraplength=600, justify='left').pack(anchor='w', pady=5)
        
        ttk.Button(support_frame, text="☕ Buy Me a Coffee", 
                  command=self.open_buymeacoffee).pack(pady=10)
    
    def create_issues_tab(self):
        """Create the issues tab with template examples and GitHub link"""
        # Title
        title_label = ttk.Label(self.issues_frame, text="Report Issues & Bugs", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Introduction
        intro_frame = ttk.Frame(self.issues_frame)
        intro_frame.pack(fill='x', padx=20, pady=10)
        
        intro_text = """Found a bug or have a feature request? We'd love to hear from you! 
Use the templates below to help us understand and resolve issues quickly."""
        
        ttk.Label(intro_frame, text=intro_text, font=("Arial", 10), 
                 wraplength=700, justify='center').pack()
        
        # Bug report template
        bug_frame = ttk.LabelFrame(self.issues_frame, text="Bug Report Template", padding="15")
        bug_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        bug_template = """**Bug Description:**
A clear description of what the bug is.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Environment:**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.9.0]
- Media Manager Version: [e.g., 1.0.0]

**Additional Context:**
Any other relevant information, error messages, or screenshots."""
        
        bug_text = scrolledtext.ScrolledText(bug_frame, height=12, wrap=tk.WORD)
        bug_text.pack(fill='both', expand=True)
        bug_text.insert(1.0, bug_template)
        
        # Feature request template
        feature_frame = ttk.LabelFrame(self.issues_frame, text="Feature Request Template", padding="15")
        feature_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        feature_template = """**Feature Description:**
A clear description of the feature you'd like to see.

**Use Case:**
Describe the problem this feature would solve or the workflow it would improve.

**Proposed Solution:**
How you think this feature should work.

**Alternatives Considered:**
Any alternative solutions or features you've considered.

**Additional Context:**
Any other context, mockups, or examples that would help."""
        
        feature_text = scrolledtext.ScrolledText(feature_frame, height=8, wrap=tk.WORD)
        feature_text.pack(fill='both', expand=True)
        feature_text.insert(1.0, feature_template)
        
        # Action buttons
        button_frame = ttk.Frame(self.issues_frame)
        button_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Button(button_frame, text="🐛 Report Bug on GitHub", 
                  command=self.open_bug_report).pack(side='left', padx=10)
        ttk.Button(button_frame, text="💡 Request Feature on GitHub", 
                  command=self.open_feature_request).pack(side='left', padx=10)
        ttk.Button(button_frame, text="📋 Copy Bug Template", 
                  command=lambda: self.copy_to_clipboard(bug_template)).pack(side='left', padx=10)
        ttk.Button(button_frame, text="📋 Copy Feature Template", 
                  command=lambda: self.copy_to_clipboard(feature_template)).pack(side='left', padx=10)
    
    def open_github_repo(self):
        """Open the GitHub repository in browser"""
        try:
            webbrowser.open(f"https://github.com/{__repository__}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def open_discord(self):
        """Open Discord server in browser"""
        try:
            webbrowser.open("https://discord.com/channels/1217932881301737523/1217933464955785297")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def open_buymeacoffee(self):
        """Open Buy Me a Coffee page in browser"""
        try:
            webbrowser.open("https://www.buymeacoffee.com/BankaiTech")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def open_bug_report(self):
        """Open GitHub issues page for bug reports"""
        try:
            webbrowser.open(f"https://github.com/{__repository__}/issues/new?template=bug_report.md")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def open_feature_request(self):
        """Open GitHub issues page for feature requests"""
        try:
            webbrowser.open(f"https://github.com/{__repository__}/issues/new?template=feature_request.md")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Template copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard: {e}")
    
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
        
        # Load automation settings
        automation_config = self.config.get("automation", {})
        self.automation_enabled_var.set(automation_config.get("enabled", False))
        
        tasks_config = automation_config.get("tasks", {})
        for task_id in self.task_definitions.keys():
            task_config = tasks_config.get(task_id, {})
            self.task_vars[task_id].set(task_config.get("enabled", False))
            self.task_time_vars[task_id].set(task_config.get("time", "05:00"))
            self.task_freq_vars[task_id].set(task_config.get("frequency", "daily"))
        
        # Update field states based on enabled checkboxes
        self.toggle_email_fields()
        self.toggle_automation_fields()
        
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
    
    def save_automation_settings(self):
        """Save automation configuration settings"""
        try:
            # Validate time formats first
            for task_id, time_var in self.task_time_vars.items():
                time_str = time_var.get().strip()
                if time_str and self.task_vars[task_id].get():
                    if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                        messagebox.showerror("Invalid Time Format", 
                            f"Task '{self.task_definitions[task_id]['name']}' has invalid time format.\n"
                            f"Please use HH:MM format (24-hour), e.g., 05:30")
                        return
            
            # Save automation enabled state
            self.config["automation"]["enabled"] = self.automation_enabled_var.get()
            
            # Save task settings
            for task_id in self.task_definitions.keys():
                task_config = {
                    "enabled": self.task_vars[task_id].get(),
                    "time": self.task_time_vars[task_id].get().strip() or "05:00",
                    "frequency": self.task_freq_vars[task_id].get() or "daily"
                }
                self.config["automation"]["tasks"][task_id] = task_config
            
            self.save_config()
            messagebox.showinfo("Success", "Automation configuration saved successfully!\n\n"
                              "Use 'Apply Scheduled Tasks' to create the actual scheduled tasks on your system.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving automation configuration: {e}")
    
    def apply_scheduled_tasks(self):
        """Apply the scheduled tasks to the system"""
        if not self.automation_enabled_var.get():
            messagebox.showwarning("Automation Disabled", 
                "Automation is disabled. Enable it first and save the configuration.")
            return
        
        try:
            current_platform = platform.system()
            
            # Check if any tasks are enabled
            enabled_tasks = [task_id for task_id in self.task_definitions.keys() 
                           if self.task_vars[task_id].get()]
            
            if not enabled_tasks:
                messagebox.showwarning("No Tasks Enabled", 
                    "No tasks are enabled. Please enable at least one task.")
                return
            
            # Get the path to the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            python_executable = sys.executable
            
            success_count = 0
            error_count = 0
            
            # Handle complete check override
            if self.task_vars["complete_check"].get():
                self.log_message("Complete check is enabled - creating single scheduled task")
                task_config = self.config["automation"]["tasks"]["complete_check"]
                
                success = self.create_scheduled_task(
                    "MediaManager_CompleteCheck",
                    "Media Manager - Complete Check",
                    python_executable,
                    os.path.join(script_dir, "media_manager_gui.py"),
                    "--automated-complete-check",
                    task_config["time"],
                    task_config["frequency"]
                )
                
                if success:
                    success_count += 1
                    self.log_message("✓ Complete check task scheduled successfully")
                else:
                    error_count += 1
                    self.log_message("✗ Failed to schedule complete check task")
            else:
                # Create individual tasks
                for task_id in enabled_tasks:
                    if task_id == "complete_check":
                        continue  # Skip if not the complete check override
                    
                    task_config = self.config["automation"]["tasks"][task_id]
                    task_name = f"MediaManager_{task_id}"
                    task_description = f"Media Manager - {self.task_definitions[task_id]['name']}"
                    
                    success = self.create_scheduled_task(
                        task_name,
                        task_description,
                        python_executable,
                        os.path.join(script_dir, "media_manager_gui.py"),
                        f"--automated-{task_id.replace('_', '-')}",
                        task_config["time"],
                        task_config["frequency"]
                    )
                    
                    if success:
                        success_count += 1
                        self.log_message(f"✓ {self.task_definitions[task_id]['name']} scheduled successfully")
                    else:
                        error_count += 1
                        self.log_message(f"✗ Failed to schedule {self.task_definitions[task_id]['name']}")
            
            # Show results
            if success_count > 0:
                messagebox.showinfo("Tasks Applied", 
                    f"Successfully created {success_count} scheduled task(s).\n"
                    f"Errors: {error_count}\n\n"
                    f"Check the Status log for details.")
            else:
                messagebox.showerror("Failed", 
                    f"Failed to create any scheduled tasks.\n"
                    f"Check the Status log for details.")
                
        except Exception as e:
            self.log_message(f"Error applying scheduled tasks: {e}")
            messagebox.showerror("Error", f"Error applying scheduled tasks: {e}")
    
    def create_scheduled_task(self, task_name, description, executable, script_path, args, time_str, frequency):
        """Create a platform-specific scheduled task"""
        try:
            current_platform = platform.system()
            
            if current_platform == "Windows":
                return self.create_windows_task(task_name, description, executable, script_path, args, time_str, frequency)
            elif current_platform == "Linux":
                return self.create_linux_cron_job(task_name, description, executable, script_path, args, time_str, frequency)
            else:
                self.log_message(f"Platform {current_platform} is not supported for automation")
                return False
                
        except Exception as e:
            self.log_message(f"Error creating scheduled task {task_name}: {e}")
            return False
    
    def create_windows_task(self, task_name, description, executable, script_path, args, time_str, frequency):
        """Create a Windows Task Scheduler task"""
        try:
            # Build schtasks command
            cmd = [
                "schtasks", "/Create",
                "/TN", task_name,
                "/TR", f'"{executable}" "{script_path}" {args}',
                "/ST", time_str,
                "/F"  # Force overwrite if exists
            ]
            
            if frequency == "daily":
                cmd.extend(["/SC", "DAILY"])
            elif frequency == "weekly":
                cmd.extend(["/SC", "WEEKLY"])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                return True
            else:
                self.log_message(f"Windows task creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_message(f"Error creating Windows task: {e}")
            return False
    
    def create_linux_cron_job(self, task_name, description, executable, script_path, args, time_str, frequency):
        """Create a Linux cron job"""
        try:
            # Parse time string
            hour, minute = time_str.split(':')
            
            # Build cron expression
            if frequency == "daily":
                cron_time = f"{minute} {hour} * * *"
            elif frequency == "weekly":
                cron_time = f"{minute} {hour} * * 0"  # Sunday
            else:
                cron_time = f"{minute} {hour} * * *"  # Default to daily
            
            # Create cron entry
            cron_entry = f'{cron_time} "{executable}" "{script_path}" {args} # MediaManager: {task_name}\n'
            
            # Get current crontab
            try:
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                current_crontab = result.stdout if result.returncode == 0 else ""
            except:
                current_crontab = ""
            
            # Remove existing MediaManager entries for this task
            lines = current_crontab.split('\n')
            filtered_lines = [line for line in lines if f"# MediaManager: {task_name}" not in line]
            
            # Add new entry
            filtered_lines.append(cron_entry.strip())
            new_crontab = '\n'.join([line for line in filtered_lines if line.strip()]) + '\n'
            
            # Apply new crontab
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            if process.returncode == 0:
                return True
            else:
                self.log_message("Failed to update crontab")
                return False
                
        except Exception as e:
            self.log_message(f"Error creating Linux cron job: {e}")
            return False
    
    def remove_scheduled_tasks(self):
        """Remove all MediaManager scheduled tasks"""
        try:
            current_platform = platform.system()
            
            if current_platform == "Windows":
                success = self.remove_windows_tasks()
            elif current_platform == "Linux":
                success = self.remove_linux_cron_jobs()
            else:
                messagebox.showerror("Unsupported Platform", 
                    f"Platform {current_platform} is not supported for automation")
                return
            
            if success:
                messagebox.showinfo("Tasks Removed", 
                    "All MediaManager scheduled tasks have been removed successfully.")
                self.log_message("All scheduled tasks removed successfully")
            else:
                messagebox.showwarning("Partial Success", 
                    "Some tasks may not have been removed. Check the Status log for details.")
                
        except Exception as e:
            self.log_message(f"Error removing scheduled tasks: {e}")
            messagebox.showerror("Error", f"Error removing scheduled tasks: {e}")
    
    def remove_windows_tasks(self):
        """Remove Windows Task Scheduler tasks"""
        try:
            success = True
            task_names = [f"MediaManager_{task_id}" for task_id in self.task_definitions.keys()]
            
            for task_name in task_names:
                try:
                    cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]
                    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if result.returncode == 0:
                        self.log_message(f"✓ Removed task: {task_name}")
                    else:
                        # Task might not exist, which is fine
                        if "cannot find the file" not in result.stderr.lower():
                            self.log_message(f"✗ Failed to remove task {task_name}: {result.stderr}")
                            success = False
                except Exception as e:
                    self.log_message(f"✗ Error removing task {task_name}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_message(f"Error removing Windows tasks: {e}")
            return False
    
    def remove_linux_cron_jobs(self):
        """Remove Linux cron jobs"""
        try:
            # Get current crontab
            try:
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                current_crontab = result.stdout if result.returncode == 0 else ""
            except:
                current_crontab = ""
            
            if not current_crontab:
                self.log_message("No crontab entries found")
                return True
            
            # Remove MediaManager entries
            lines = current_crontab.split('\n')
            filtered_lines = [line for line in lines if "# MediaManager:" not in line]
            
            # Apply new crontab
            new_crontab = '\n'.join([line for line in filtered_lines if line.strip()]) + '\n'
            
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            if process.returncode == 0:
                self.log_message("✓ Removed all MediaManager cron jobs")
                return True
            else:
                self.log_message("✗ Failed to update crontab")
                return False
                
        except Exception as e:
            self.log_message(f"Error removing Linux cron jobs: {e}")
            return False
    
    def test_task_creation(self):
        """Test the task creation functionality without actually scheduling"""
        try:
            current_platform = platform.system()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            python_executable = sys.executable
            
            self.log_message(f"Testing task creation on {current_platform}...")
            self.log_message(f"Python executable: {python_executable}")
            self.log_message(f"Script directory: {script_dir}")
            
            # Test command that would be created
            if current_platform == "Windows":
                test_cmd = f'"{python_executable}" "{os.path.join(script_dir, "media_manager_gui.py")}" --automated-test'
                self.log_message(f"Test Windows command: {test_cmd}")
                
                # Test if schtasks is available
                try:
                    result = subprocess.run(["schtasks", "/?"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.returncode == 0:
                        self.log_message("✓ Windows Task Scheduler (schtasks) is available")
                    else:
                        self.log_message("✗ Windows Task Scheduler (schtasks) not available")
                except Exception as e:
                    self.log_message(f"✗ Error testing schtasks: {e}")
                    
            elif current_platform == "Linux":
                test_cmd = f'"{python_executable}" "{os.path.join(script_dir, "media_manager_gui.py")}" --automated-test'
                self.log_message(f"Test Linux command: {test_cmd}")
                
                # Test if crontab is available
                try:
                    result = subprocess.run(["which", "crontab"], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.log_message("✓ crontab is available")
                    else:
                        self.log_message("✗ crontab not available")
                except Exception as e:
                    self.log_message(f"✗ Error testing crontab: {e}")
            else:
                self.log_message(f"✗ Platform {current_platform} is not supported")
            
            messagebox.showinfo("Test Complete", 
                "Task creation test completed. Check the Status log for details.")
            
        except Exception as e:
            self.log_message(f"Error during test: {e}")
            messagebox.showerror("Test Error", f"Error during test: {e}")
    
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
        """Run a complete check (generate list, check missing, manage files, detect filename issues)"""
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

def run_headless_operation(operation, config_file="media_manager_config.json"):
    """Run an operation headlessly (without GUI) for automation"""
    try:
        # Load configuration
        if not os.path.exists(config_file):
            print(f"Error: Configuration file {config_file} not found")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Create a simple logger function
        def log_print(message):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
        
        log_print(f"Starting automated operation: {operation}")
        
        if operation == "generate-media-list":
            return run_headless_generate_media_list(config, log_print)
        elif operation == "check-missing-media":
            return run_headless_check_missing_media(config, log_print)
        elif operation == "manage-file-retention":
            return run_headless_manage_files(config, log_print)
        elif operation == "check-windows-filenames":
            return run_headless_check_windows_filenames(config, log_print)
        elif operation == "complete-check":
            return run_headless_complete_check(config, log_print)
        else:
            log_print(f"Unknown operation: {operation}")
            return False
            
    except Exception as e:
        print(f"Error in headless operation {operation}: {e}")
        return False

def run_headless_generate_media_list(config, log_function):
    """Generate media list headlessly"""
    try:
        from generate_media_list import generate_media_list
        
        directories = config.get("scan_directories", [])
        if not directories:
            log_function("Error: No directories configured for scanning")
            return False
        
        # Ensure output directories exist
        output_dir = config.get("output_directory", "lists")
        media_lists_dir = os.path.join(output_dir, "media_lists")
        os.makedirs(media_lists_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(media_lists_dir, f"media_list_{timestamp}.txt")
        
        # Get configured file extensions
        file_extensions = config.get("file_extensions", {})
        all_extensions = file_extensions.get("media", []) + file_extensions.get("additional", [])
        if not all_extensions:
            all_extensions = ['.mp4', '.mkv', '.avi']
        
        log_function(f"Scanning directories: {', '.join(directories)}")
        log_function(f"Looking for extensions: {', '.join(all_extensions)}")
        
        generate_media_list(directories, output_file, all_extensions)
        log_function(f"Media list generated: {output_file}")
        return True
        
    except Exception as e:
        log_function(f"Error generating media list: {e}")
        return False

def run_headless_check_missing_media(config, log_function):
    """Check for missing media headlessly"""
    try:
        from generate_missing_media_list import find_two_most_recent_media_lists
        
        output_dir = config.get("output_directory", "lists")
        media_lists_dir = os.path.join(output_dir, "media_lists")
        
        # Find the two most recent media lists
        most_recent, second_recent = find_two_most_recent_media_lists(media_lists_dir, 'media_list_*.txt')
        
        if not most_recent or not second_recent:
            log_function("Error: Need at least 2 media lists to compare")
            return False
        
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
            
            log_function(f"Found {len(missing_titles)} missing media files")
            log_function(f"Missing media list saved: {missing_file}")
            
            # Send email if configured
            email_config = config.get("email", {})
            if email_config.get("enabled", False):
                log_function("Sending email notification...")
                success = send_missing_media_email(
                    missing_titles, 
                    config_file="media_manager_config.json",
                    log_function=log_function
                )
            else:
                log_function("Email notifications disabled, skipping email")
        else:
            log_function("No missing media files found")
        
        return True
        
    except Exception as e:
        log_function(f"Error checking for missing media: {e}")
        return False

def run_headless_manage_files(config, log_function):
    """Manage file retention headlessly"""
    try:
        from manage_files import manage_files
        
        output_dir = config.get("output_directory", "lists")
        retention_count = config.get("file_retention_count", 100)
        
        subdirs = ["media_lists", "missing_media", "filename_issues"]
        total_deleted = 0
        
        for subdir in subdirs:
            subdir_path = os.path.join(output_dir, subdir)
            if os.path.exists(subdir_path):
                kept, deleted, error = manage_files(subdir_path, retention_count)
                if error:
                    log_function(f"Error managing {subdir}: {error}")
                else:
                    log_function(f"{subdir}: Kept {kept} files, deleted {deleted} files")
                    total_deleted += deleted
        
        log_function(f"File retention complete - total files deleted: {total_deleted}")
        return True
        
    except Exception as e:
        log_function(f"Error managing files: {e}")
        return False

def run_headless_check_windows_filenames(config, log_function):
    """Check Windows filename compatibility headlessly"""
    try:
        from windows_filename_validator import WindowsFilenameValidator
        
        output_dir = config.get("output_directory", "lists")
        media_lists_dir = os.path.join(output_dir, "media_lists")
        
        # Find the most recent media list
        pattern = os.path.join(media_lists_dir, 'media_list_*.txt')
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        
        if not files:
            log_function("Error: No media list files found")
            return False
        
        most_recent_file = files[0]
        log_function(f"Analyzing: {os.path.basename(most_recent_file)}")
        
        # Validate filenames
        validator = WindowsFilenameValidator()
        validation_results = validator.validate_from_file(most_recent_file)
        
        if validation_results:
            # Save the report
            filename_issues_dir = os.path.join(output_dir, "filename_issues")
            os.makedirs(filename_issues_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(filename_issues_dir, f"windows_filename_issues_{timestamp}.txt")
            
            validator.generate_report(validation_results, report_file)
            log_function(f"Found {len(validation_results)} files with Windows naming issues")
            log_function(f"Report saved: {report_file}")
        else:
            log_function("All filenames are Windows compatible")
        
        return True
        
    except Exception as e:
        log_function(f"Error checking Windows filenames: {e}")
        return False

def run_headless_complete_check(config, log_function):
    """Run complete check headlessly (detects filename issues but does not fix them)"""
    try:
        log_function("Starting complete check...")
        
        success = True
        success &= run_headless_generate_media_list(config, log_function)
        success &= run_headless_check_missing_media(config, log_function)
        success &= run_headless_manage_files(config, log_function)
        success &= run_headless_check_windows_filenames(config, log_function)
        
        log_function("Complete check finished")
        return success
        
    except Exception as e:
        log_function(f"Error in complete check: {e}")
        return False

def main():
    """Main function to run the GUI application or handle command-line automation"""
    parser = argparse.ArgumentParser(description="Media Manager GUI", add_help=False)
    parser.add_argument('--automated-generate-media-list', action='store_true',
                       help='Run generate media list automation (headless)')
    parser.add_argument('--automated-check-missing-media', action='store_true',
                       help='Run check missing media automation (headless)')
    parser.add_argument('--automated-manage-file-retention', action='store_true',
                       help='Run manage file retention automation (headless)')
    parser.add_argument('--automated-check-windows-filenames', action='store_true',
                       help='Run check Windows filenames automation (headless)')
    parser.add_argument('--automated-complete-check', action='store_true',
                       help='Run complete check automation (headless)')
    parser.add_argument('--automated-test', action='store_true',
                       help='Test automation (does nothing)')
    
    args, unknown = parser.parse_known_args()
    
    # Check if any automation flags are set
    automation_flags = [
        args.automated_generate_media_list,
        args.automated_check_missing_media,
        args.automated_manage_file_retention,
        args.automated_check_windows_filenames,
        args.automated_complete_check,
        args.automated_test
    ]
    
    if any(automation_flags):
        # Running in automation mode (headless)
        if args.automated_test:
            print("Automation test - script is working correctly")
            return 0
        
        operation = None
        if args.automated_generate_media_list:
            operation = "generate-media-list"
        elif args.automated_check_missing_media:
            operation = "check-missing-media"
        elif args.automated_manage_file_retention:
            operation = "manage-file-retention"
        elif args.automated_check_windows_filenames:
            operation = "check-windows-filenames"
        elif args.automated_complete_check:
            operation = "complete-check"
        
        if operation:
            success = run_headless_operation(operation)
            return 0 if success else 1
        else:
            print("Error: Unknown automation operation")
            return 1
    else:
        # Running in GUI mode
        root = tk.Tk()
        app = MediaManagerGUI(root)
        
        # Set window icon if available
        try:
            root.iconbitmap('icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        root.mainloop()
        return 0

if __name__ == "__main__":
    sys.exit(main())
