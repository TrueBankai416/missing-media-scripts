#!/usr/bin/env python3
"""
Create a completely solid icon for Windows with no transparency at all
"""

from PIL import Image, ImageDraw
import os

def create_solid_windows_icon(size=32):
    """Create a completely solid icon with white background for Windows"""
    
    # Create image with solid white background
    img = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Simple, high-contrast design with no transparency
    bg_color = (70, 130, 200)  # Blue background
    clipboard_color = (220, 220, 220)  # Light gray
    paper_color = (255, 255, 255)  # White
    line_color = (180, 180, 180)  # Gray lines
    glass_bg = (240, 240, 240)  # Light gray for glass
    glass_border = (50, 50, 50)  # Dark border
    check_color = (0, 150, 0)  # Green checkmark
    handle_color = (100, 100, 100)  # Gray handle
    
    # Draw background (rounded square)
    margin = 2
    draw.rectangle([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw clipboard (simplified)
    cb_width = size // 3
    cb_height = int(size * 0.6)
    cb_x = size // 8
    cb_y = size // 6
    
    # Clipboard rectangle
    draw.rectangle([cb_x, cb_y, cb_x + cb_width, cb_y + cb_height], 
                  fill=clipboard_color, outline=(150, 150, 150))
    
    # Paper on clipboard
    paper_margin = 2
    paper_x = cb_x + paper_margin
    paper_y = cb_y + paper_margin + 2
    paper_width = cb_width - paper_margin * 2
    paper_height = cb_height - paper_margin * 2 - 4
    
    if paper_width > 0 and paper_height > 0:
        draw.rectangle([paper_x, paper_y, paper_x + paper_width, paper_y + paper_height],
                      fill=paper_color, outline=line_color)
        
        # Simple lines on paper
        line_spacing = max(2, paper_height // 4)
        for i in range(3):
            line_y = paper_y + 2 + (i * line_spacing)
            if line_y < paper_y + paper_height - 1:
                draw.line([paper_x + 1, line_y, paper_x + paper_width - 1, line_y], 
                         fill=line_color)
    
    # Clipboard clip
    clip_w = max(3, cb_width // 3)
    clip_h = 2
    clip_x = cb_x + cb_width // 2 - clip_w // 2
    clip_y = cb_y - 1
    draw.rectangle([clip_x, clip_y, clip_x + clip_w, clip_y + clip_h],
                  fill=(160, 160, 160), outline=(120, 120, 120))
    
    # Magnifying glass (simple circle)
    glass_x = size - size // 3
    glass_y = size - size // 3
    glass_radius = max(4, size // 8)
    
    # Glass circle
    draw.ellipse([glass_x - glass_radius, glass_y - glass_radius,
                 glass_x + glass_radius, glass_y + glass_radius],
                fill=glass_bg, outline=glass_border, width=1)
    
    # Checkmark inside glass (very simple)
    check_size = glass_radius // 2
    if check_size >= 2:
        # Simple checkmark - just two lines
        draw.line([glass_x - check_size//2, glass_y, 
                  glass_x, glass_y + check_size//2], 
                 fill=check_color, width=1)
        draw.line([glass_x, glass_y + check_size//2, 
                  glass_x + check_size//2, glass_y - check_size//2], 
                 fill=check_color, width=1)
    
    # Handle (simple line)
    handle_start_x = glass_x + glass_radius - 1
    handle_start_y = glass_y + glass_radius - 1
    handle_end_x = min(size - 1, handle_start_x + glass_radius//2)
    handle_end_y = min(size - 1, handle_start_y + glass_radius//2)
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=handle_color, width=2)
    
    return img

def main():
    """Create completely solid Windows icons"""
    
    # Create multiple sizes for ICO
    sizes = [16, 24, 32, 48]
    icons = []
    
    for size in sizes:
        icon = create_solid_windows_icon(size)
        filename = f"media_manager_solid_{size}.png"
        icon.save(filename)
        icons.append(icon)
        print(f"Created {filename}")
    
    # Create ICO file with solid backgrounds only
    icons[0].save("media_manager_solid.ico", 
                 format='ICO', 
                 sizes=[(16, 16), (24, 24), (32, 32), (48, 48)])
    print("Created media_manager_solid.ico")
    
    # Create a test single-size ICO
    test_icon = create_solid_windows_icon(32)
    test_icon.save("media_manager_simple_solid.ico", format='ICO', sizes=[(32, 32)])
    print("Created media_manager_simple_solid.ico")

if __name__ == "__main__":
    main()
