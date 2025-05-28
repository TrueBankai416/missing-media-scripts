#!/usr/bin/env python3
"""
Debug script to test Windows icon loading
"""

import tkinter as tk
import os
import platform

def test_icon_loading():
    """Test different icon loading methods"""
    root = tk.Tk()
    root.title("Icon Test")
    root.geometry("300x200")
    
    print(f"Platform: {platform.system()}")
    print("Available icon files:")
    
    # List all icon files
    icon_files = []
    for f in os.listdir('.'):
        if f.endswith(('.ico', '.png', '.bmp')):
            icon_files.append(f)
            print(f"  {f}: {os.path.getsize(f)} bytes")
    
    # Test different methods
    methods_tried = []
    
    # Method 1: Try iconbitmap with ICO
    for ico_file in ['media_manager_final.ico', 'debug_test.ico', 'media_manager_solid.ico']:
        if os.path.exists(ico_file):
            try:
                root.iconbitmap(ico_file)
                methods_tried.append(f"iconbitmap({ico_file}) - SUCCESS")
                break
            except Exception as e:
                methods_tried.append(f"iconbitmap({ico_file}) - FAILED: {e}")
    
    # Method 2: Try iconphoto with PNG
    for png_file in ['windows_solid_32.png', 'media_manager_solid_32.png']:
        if os.path.exists(png_file):
            try:
                img = tk.PhotoImage(file=png_file)
                root.iconphoto(True, img)
                methods_tried.append(f"iconphoto({png_file}) - SUCCESS")
                # Keep reference
                root.icon_img = img
                break
            except Exception as e:
                methods_tried.append(f"iconphoto({png_file}) - FAILED: {e}")
    
    # Display results
    text_widget = tk.Text(root, wrap=tk.WORD)
    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    
    results = "Icon Loading Test Results:\n\n"
    for method in methods_tried:
        results += method + "\n"
    
    results += f"\nWindow should show custom icon in:\n"
    results += f"- Title bar (top-left)\n"  
    results += f"- Taskbar\n"
    results += f"- Alt+Tab switcher\n"
    
    text_widget.insert('1.0', results)
    text_widget.config(state='disabled')
    
    # Keep window open
    root.mainloop()

if __name__ == "__main__":
    test_icon_loading()
