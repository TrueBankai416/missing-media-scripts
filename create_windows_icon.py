#!/usr/bin/env python3
"""
Create a Windows-compatible ICO file without transparency issues
"""

from PIL import Image, ImageDraw
import os

def create_windows_compatible_icon(size=64):
    """Create a solid background icon for Windows compatibility"""
    
    # Create image with solid white background (no transparency)
    img = Image.new('RGB', (size, size), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Define colors (all solid, no alpha)
    bg_color = (45, 52, 75)  # Dark blue background
    clipboard_color = (240, 240, 240)  # Light gray for clipboard
    paper_color = (255, 255, 255)  # White for paper
    accent_color = (74, 144, 226)  # Modern blue
    checkmark_color = (40, 167, 69)  # Green for checkmark
    border_color = (200, 200, 200)  # Gray for borders
    
    # Draw background circle with solid color
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw clipboard
    clipboard_width = max(10, size // 2)
    clipboard_height = max(10, int(size * 0.5))
    clipboard_x = size // 6
    clipboard_y = size // 4
    
    # Clipboard base
    draw.rectangle([clipboard_x, clipboard_y, clipboard_x + clipboard_width, clipboard_y + clipboard_height],
                  fill=clipboard_color, outline=border_color, width=1)
    
    # Paper on clipboard
    paper_margin = max(2, size // 20)
    paper_x = clipboard_x + paper_margin
    paper_y = clipboard_y + paper_margin * 2
    paper_width = max(5, clipboard_width - paper_margin * 2)
    paper_height = max(5, clipboard_height - paper_margin * 3)
    
    if paper_width > 0 and paper_height > 0:
        draw.rectangle([paper_x, paper_y, paper_x + paper_width, paper_y + paper_height],
                      fill=paper_color, outline=(220, 220, 220), width=1)
        
        # Draw lines on paper
        line_spacing = max(3, size // 15)
        for i in range(min(4, paper_height // line_spacing)):
            line_y = paper_y + line_spacing + (i * line_spacing)
            if line_y < paper_y + paper_height - 2:
                draw.line([paper_x + 2, line_y, paper_x + paper_width - 2, line_y], 
                         fill=(200, 200, 200), width=1)
    
    # Draw clipboard clip at top
    clip_width = max(4, size // 10)
    clip_height = max(2, size // 20)
    clip_x = clipboard_x + clipboard_width // 2 - clip_width // 2
    clip_y = clipboard_y - clip_height // 2
    
    draw.rectangle([clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
                  fill=(180, 180, 180), outline=(150, 150, 150), width=1)
    
    # Draw magnifying glass
    glass_center_x = size - size // 3
    glass_center_y = size - size // 3
    glass_radius = max(6, size // 7)
    
    # Glass circle with solid background
    draw.ellipse([glass_center_x - glass_radius, glass_center_y - glass_radius,
                 glass_center_x + glass_radius, glass_center_y + glass_radius],
                fill=(245, 245, 245), outline=accent_color, width=max(2, size//20))
    
    # Checkmark inside magnifying glass
    check_size = max(3, glass_radius // 2)
    check_stroke = max(2, size // 25)
    
    # Draw checkmark
    draw.line([glass_center_x - check_size//2, glass_center_y, 
              glass_center_x - check_size//6, glass_center_y + check_size//2], 
             fill=checkmark_color, width=check_stroke)
    draw.line([glass_center_x - check_size//6, glass_center_y + check_size//2, 
              glass_center_x + check_size//2, glass_center_y - check_size//3], 
             fill=checkmark_color, width=check_stroke)
    
    # Magnifying glass handle
    handle_length = max(4, glass_radius)
    handle_start_x = glass_center_x + int(glass_radius * 0.7)
    handle_start_y = glass_center_y + int(glass_radius * 0.7)
    handle_end_x = handle_start_x + handle_length//2
    handle_end_y = handle_start_y + handle_length//2
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=accent_color, width=max(3, size//15))
    
    return img

def main():
    """Create Windows-compatible icons"""
    
    # Create icons in standard Windows sizes
    sizes = [16, 24, 32, 48, 64]
    icons = []
    
    for size in sizes:
        icon = create_windows_compatible_icon(size)
        filename = f"media_manager_windows_{size}.png"
        icon.save(filename)
        icons.append(icon)
        print(f"Created {filename}")
    
    # Create a high-quality ICO file specifically for Windows
    # Use only the most important sizes to avoid issues
    ico_icons = []
    for size in [16, 24, 32, 48]:
        ico_icons.append(create_windows_compatible_icon(size))
    
    # Save as ICO with specific Windows compatibility
    ico_icons[0].save("media_manager_windows.ico", 
                     format='ICO', 
                     sizes=[(16, 16), (24, 24), (32, 32), (48, 48)])
    print("Created media_manager_windows.ico")
    
    # Also create a simple 32x32 version for testing
    simple_icon = create_windows_compatible_icon(32)
    simple_icon.save("media_manager_test.ico", format='ICO', sizes=[(32, 32)])
    print("Created media_manager_test.ico")

if __name__ == "__main__":
    main()
