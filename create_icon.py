#!/usr/bin/env python3
"""
Create a custom icon for the Media Manager GUI
Represents missing media detection with a magnifying glass and file symbols
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_media_manager_icon(size=256):
    """Create a custom icon for the Media Manager application"""
    
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors for a modern look
    bg_color = (45, 52, 75)  # Dark blue-gray background
    accent_color = (74, 144, 226)  # Modern blue
    missing_color = (220, 53, 69)  # Red for missing items
    present_color = (40, 167, 69)  # Green for present items
    glass_color = (255, 255, 255, 180)  # Semi-transparent white
    
    # Draw background circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw file icons in background (representing media files)
    file_width = size // 8
    file_height = size // 6
    
    # File positions (3x2 grid)
    file_positions = [
        (size//4, size//3),      # Top left
        (size//2, size//3),      # Top center  
        (3*size//4, size//3),    # Top right
        (size//4, 2*size//3),    # Bottom left
        (size//2, 2*size//3),    # Bottom center
        (3*size//4, 2*size//3),  # Bottom right
    ]
    
    # Draw files with different states (present, missing)
    for i, (x, y) in enumerate(file_positions):
        # Some files are present (green), some missing (red)
        if i in [1, 4]:  # Files 2 and 5 are missing
            color = missing_color
            # Draw X mark for missing
            x_size = file_width // 3
            draw.line([x-x_size//2, y-x_size//2, x+x_size//2, y+x_size//2], 
                     fill=(255, 255, 255), width=3)
            draw.line([x-x_size//2, y+x_size//2, x+x_size//2, y-x_size//2], 
                     fill=(255, 255, 255), width=3)
        else:
            color = present_color
            # Draw checkmark for present
            check_size = file_width // 3
            draw.line([x-check_size//2, y, x-check_size//4, y+check_size//3], 
                     fill=(255, 255, 255), width=3)
            draw.line([x-check_size//4, y+check_size//3, x+check_size//2, y-check_size//3], 
                     fill=(255, 255, 255), width=3)
        
        # Draw file rectangle
        draw.rectangle([x-file_width//2, y-file_height//2, 
                       x+file_width//2, y+file_height//2], 
                      fill=color, outline=(255, 255, 255, 200), width=2)
    
    # Draw magnifying glass
    glass_center_x = 3 * size // 4
    glass_center_y = size // 4
    glass_radius = size // 6
    handle_length = size // 8
    
    # Glass circle (semi-transparent)
    draw.ellipse([glass_center_x - glass_radius, glass_center_y - glass_radius,
                 glass_center_x + glass_radius, glass_center_y + glass_radius],
                fill=glass_color, outline=accent_color, width=4)
    
    # Handle
    handle_x = glass_center_x + int(glass_radius * 0.7)
    handle_y = glass_center_y + int(glass_radius * 0.7)
    handle_end_x = handle_x + int(handle_length * 0.7)
    handle_end_y = handle_y + int(handle_length * 0.7)
    
    draw.line([handle_x, handle_y, handle_end_x, handle_end_y], 
             fill=accent_color, width=6)
    
    # Add a subtle border to the main circle
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=None, outline=accent_color, width=3)
    
    return img

def main():
    """Create icons in multiple sizes"""
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        icon = create_media_manager_icon(size)
        icon.save(f"media_manager_icon_{size}.png")
        print(f"Created media_manager_icon_{size}.png")
    
    # Create Windows ICO file with multiple sizes
    icons = []
    for size in [16, 32, 48, 64, 128, 256]:
        icons.append(create_media_manager_icon(size))
    
    # Save as ICO file
    icons[0].save("media_manager_icon.ico", format='ICO', sizes=[(s, s) for s in sizes])
    print("Created media_manager_icon.ico")

if __name__ == "__main__":
    main()
