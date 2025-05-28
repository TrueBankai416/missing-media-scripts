#!/usr/bin/env python3
"""
Create a simpler, more compatible icon for Linux systems
"""

from PIL import Image, ImageDraw
import os

def create_simple_icon(size=64):
    """Create a simple, high-contrast icon that works well on Linux"""
    
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors - simpler, high contrast
    bg_color = (45, 52, 75, 255)  # Dark blue background, fully opaque
    primary_color = (74, 144, 226, 255)  # Blue
    missing_color = (220, 53, 69, 255)  # Red
    present_color = (40, 167, 69, 255)  # Green
    
    # Draw solid background circle (no transparency issues)
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw a simple grid of files (3x2)
    file_size = size // 8
    spacing = size // 5
    start_x = size // 4
    start_y = size // 3
    
    # File positions in a grid
    positions = [
        (start_x, start_y),
        (start_x + spacing, start_y),
        (start_x + spacing*2, start_y),
        (start_x, start_y + spacing),
        (start_x + spacing, start_y + spacing),
        (start_x + spacing*2, start_y + spacing),
    ]
    
    # Draw files - some present (green), some missing (red)
    for i, (x, y) in enumerate(positions):
        if i in [1, 4]:  # Files 2 and 5 are missing
            color = missing_color
            # Draw X for missing
            draw.line([x-file_size//3, y-file_size//3, x+file_size//3, y+file_size//3], 
                     fill=(255, 255, 255, 255), width=2)
            draw.line([x-file_size//3, y+file_size//3, x+file_size//3, y-file_size//3], 
                     fill=(255, 255, 255, 255), width=2)
        else:
            color = present_color
            # Draw checkmark for present
            draw.line([x-file_size//3, y, x-file_size//6, y+file_size//4], 
                     fill=(255, 255, 255, 255), width=2)
            draw.line([x-file_size//6, y+file_size//4, x+file_size//3, y-file_size//4], 
                     fill=(255, 255, 255, 255), width=2)
        
        # Draw file rectangle
        draw.rectangle([x-file_size//2, y-file_size//2, 
                       x+file_size//2, y+file_size//2], 
                      fill=color, outline=(255, 255, 255, 255), width=1)
    
    # Draw simple magnifying glass in corner
    glass_x = size - size//3
    glass_y = size//4
    glass_radius = size//8
    
    # Glass circle
    draw.ellipse([glass_x - glass_radius, glass_y - glass_radius,
                 glass_x + glass_radius, glass_y + glass_radius],
                fill=None, outline=primary_color, width=3)
    
    # Handle
    handle_start_x = glass_x + int(glass_radius * 0.7)
    handle_start_y = glass_y + int(glass_radius * 0.7)
    handle_end_x = handle_start_x + glass_radius//2
    handle_end_y = handle_start_y + glass_radius//2
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=primary_color, width=3)
    
    return img

def create_xpm_icon():
    """Create an XPM icon for maximum Linux compatibility"""
    xpm_content = '''/* XPM */
static char * media_manager_xpm[] = {
"32 32 8 1",
" 	c None",
".	c #2D344B",
"+	c #4A90E2",
"@	c #DC3545",
"#	c #28A745",
"$	c #FFFFFF",
"%	c #343A40",
"&	c #F8F9FA",
"                                ",
"                                ",
"    ......................      ",
"   .++++++++++++++++++++++.     ",
"  .++##################++.     ",
" .++#$$#  @$$@  #$$#  ##+.     ",
" .++#$$#  @$$@  #$$#  ##+.     ",
" .++#$$#  @$$@  #$$#  ##+.     ",
" .++##################++.     ",
" .++  @$$@  #$$#  @$$@  ++.     ",
" .++  @$$@  #$$#  @$$@  ++.     ",
" .++  @$$@  #$$#  @$$@  ++.     ",
" .++##################++.     ",
"  .++++++++++++++++++++.      ",
"   ...................       ",
"              ....             ",
"             .++++.            ",
"            .++++++.           ",
"           .++....++.          ",
"          .++.    .++.         ",
"         .++.      .++.        ",
"        .++.        .++        ",
"       .++.          .+        ",
"      .++.                     ",
"     .++.                      ",
"    .++.                       ",
"   .++.                        ",
"  .++.                         ",
" .++.                          ",
".++.                           ",
"++.                            ",
"                                "};'''
    
    with open('media_manager_icon.xpm', 'w') as f:
        f.write(xpm_content)
    print("Created media_manager_icon.xpm")

def main():
    """Create multiple icon formats for maximum compatibility"""
    
    # Create simpler PNG icons
    sizes = [16, 24, 32, 48, 64]
    for size in sizes:
        icon = create_simple_icon(size)
        filename = f"media_manager_simple_{size}.png"
        icon.save(filename)
        print(f"Created {filename}")
    
    # Create XPM for Linux
    create_xpm_icon()
    
    # Also create a simple 32x32 version without transparency
    simple_icon = create_simple_icon(32)
    # Convert to RGB (remove alpha channel)
    rgb_icon = Image.new('RGB', simple_icon.size, (240, 240, 240))  # Light gray background
    rgb_icon.paste(simple_icon, mask=simple_icon.split()[-1])  # Use alpha as mask
    rgb_icon.save("media_manager_simple.png")
    print("Created media_manager_simple.png (no transparency)")

if __name__ == "__main__":
    main()
