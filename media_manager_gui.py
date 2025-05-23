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
from email_utils import send_missing_media_email, load_email_config_from_file
from pathlib import Path

# Import functions from existing scripts
from generate_media_list import generate_media_list
from generate_missing_media_list import find_two_most_recent_media_lists

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
            "email": {
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
        
        # Configuration tab
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="Configuration")
        
        # Logs tab
        self.logs_frame = ttk.Frame(notebook)
        notebook.add(self.logs_frame, text="Logs & Results")
        
        self.create_main_tab()
        self.create_config_tab()
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
        """Create the configuration tab"""
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
        
        # Email configuration
        email_frame = ttk.LabelFrame(self.config_frame, text="Email Configuration", padding="10")
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
        
        # File retention
        retention_frame = ttk.LabelFrame(self.config_frame, text="File Retention", padding="10")
        retention_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(retention_frame, text="Keep latest files:").pack(side='left')
        self.retention_var = tk.StringVar()
        ttk.Entry(retention_frame, textvariable=self.retention_var, width=10).pack(side='left', padx=5)
        
        # Save button
        ttk.Button(self.config_frame, text="Save Configuration", 
                  command=self.save_settings).pack(pady=10)
    
    def create_logs_tab(self):
        """Create the logs and results tab"""
        # Recent files frame
        files_frame = ttk.LabelFrame(self.logs_frame, text="Recent Media Lists", padding="10")
        files_frame.pack(fill='x', padx=10, pady=5)
        
        self.files_listbox = tk.Listbox(files_frame, height=8)
        files_scrollbar = ttk.Scrollbar(files_frame, orient='vertical')
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)
        files_scrollbar.config(command=self.files_listbox.yview)
        
        self.files_listbox.pack(side='left', fill='both', expand=True)
        files_scrollbar.pack(side='right', fill='y')
        
        # File buttons
        file_btn_frame = ttk.Frame(files_frame)
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
        
        # Load email settings
        for key, var in self.email_vars.items():
            var.set(self.config["email"].get(key, ""))
        
        # Load retention setting
        self.retention_var.set(str(self.config["file_retention_count"]))
        
        # Refresh file list
        self.refresh_file_list()
    
    def save_settings(self):
        """Save settings from GUI controls"""
        # Save directories
        self.config["scan_directories"] = list(self.dir_listbox.get(0, tk.END))
        
        # Save output directory
        self.config["output_directory"] = self.output_var.get()
        
        # Save email settings
        for key, var in self.email_vars.items():
            self.config["email"][key] = var.get()
        
        # Save retention setting
        try:
            self.config["file_retention_count"] = int(self.retention_var.get())
        except ValueError:
            messagebox.showerror("Error", "File retention count must be a number")
            return
        
        self.save_config()
        
        # Validate email configuration and provide feedback
        email_config = load_email_config_from_file(self.config_file)
        if email_config and email_config.is_valid():
            messagebox.showinfo("Success", "Configuration saved successfully!\n\nEmail configuration is valid and ready to use.")
        elif any(self.config["email"].get(field) for field in ["sender_email", "receiver_email", "password", "smtp_server"]):
            # Some email fields are filled but configuration is invalid
            messagebox.showwarning("Configuration Saved", 
                "Configuration saved, but email setup has issues:\n\n" +
                "• Check email address formats (must be valid email addresses)\n" +
                "• Verify SMTP port is a number between 1-65535\n" +
                "• Ensure all required fields are filled\n" +
                "• For Gmail: use app passwords, not regular passwords\n\n" +
                "Email notifications will not work until these are fixed.")
        else:
            messagebox.showinfo("Success", "Configuration saved successfully!")
    
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
            
            # Ensure output directory exists
            output_dir = self.output_var.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"media_list_{timestamp}.txt")
            
            # Generate the list
            generate_media_list(directories, output_file)
            
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
            
            # Find the two most recent media lists
            most_recent, second_recent = find_two_most_recent_media_lists(output_dir, 'media_list_*.txt')
            
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
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                missing_file = os.path.join(output_dir, f"missing_media_{timestamp}.txt")
                
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
                    self.log_message("Email not configured - skipping email notification")
                
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
            
            # Get all text files sorted by modification time
            pattern = os.path.join(output_dir, "*.txt")
            files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
            
            if len(files) > retention_count:
                files_to_delete = files[retention_count:]
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        self.log_message(f"Deleted old file: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.log_message(f"Error deleting {file_path}: {e}")
                
                self.log_message(f"Kept {retention_count} most recent files, deleted {len(files_to_delete)} old files")
            else:
                self.log_message(f"Only {len(files)} files found, no cleanup needed")
            
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
        """Run a complete check (generate list, check missing, manage files)"""
        self.log_message("Starting complete check...")
        self.generate_media_list()
        self.check_missing_media()
        self.manage_files()
        self.log_message("Complete check finished")
    
    def is_email_configured(self):
        """Check if email is properly configured"""
        # Use the shared module's validation logic for consistency
        email_config = load_email_config_from_file(self.config_file)
        return email_config is not None and email_config.is_valid()
    
    
    def refresh_file_list(self):
        """Refresh the list of files in the logs tab"""
        try:
            self.files_listbox.delete(0, tk.END)
            output_dir = self.output_var.get()
            
            if os.path.exists(output_dir):
                pattern = os.path.join(output_dir, "*.txt")
                files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
                
                for file_path in files:
                    filename = os.path.basename(file_path)
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    display_name = f"{filename} ({mod_time.strftime('%Y-%m-%d %H:%M:%S')})"
                    self.files_listbox.insert(tk.END, display_name)
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
