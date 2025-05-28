#!/usr/bin/env python3
"""
Create a better icon design with clipboard and magnifying glass with checkmark
"""

from PIL import Image, ImageDraw
import os
import math

def create_clipboard_magnifier_icon(size=256):
    """Create a professional icon with clipboard and magnifying glass with checkmark"""
    
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors for a modern, professional look
    bg_color = (45, 52, 75)  # Dark blue-gray background
    accent_color = (74, 144, 226)  # Modern blue
    clipboard_color = (240, 240, 240)  # Light gray for clipboard
    paper_color = (255, 255, 255)  # White for paper
    checkmark_color = (40, 167, 69)  # Green for checkmark
    glass_color = (255, 255, 255, 200)  # Semi-transparent white for glass
    
    # Draw background circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw clipboard
    clipboard_width = size // 2
    clipboard_height = int(size * 0.6)
    clipboard_x = size // 4
    clipboard_y = size // 4
    
    # Clipboard base (rectangle with rounded corners)
    try:
        draw.rounded_rectangle(
            [clipboard_x, clipboard_y, clipboard_x + clipboard_width, clipboard_y + clipboard_height],
            radius=size//20, fill=clipboard_color, outline=(200, 200, 200), width=2
        )
    except AttributeError:
        # Fallback for older PIL versions
        draw.rectangle([clipboard_x, clipboard_y, clipboard_x + clipboard_width, clipboard_y + clipboard_height],
                      fill=clipboard_color, outline=(200, 200, 200), width=2)
    
    # Paper on clipboard
    paper_margin = size // 20
    paper_x = clipboard_x + paper_margin
    paper_y = clipboard_y + paper_margin * 2
    paper_width = clipboard_width - paper_margin * 2
    paper_height = clipboard_height - paper_margin * 3
    
    draw.rectangle([paper_x, paper_y, paper_x + paper_width, paper_y + paper_height],
                  fill=paper_color, outline=(220, 220, 220), width=1)
    
    # Draw clipboard clip at the top
    clip_width = size // 8
    clip_height = size // 12
    clip_x = clipboard_x + clipboard_width // 2 - clip_width // 2
    clip_y = clipboard_y - clip_height // 2
    
    try:
        draw.rounded_rectangle([clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
                              radius=size//40, fill=(180, 180, 180), outline=(150, 150, 150), width=1)
    except AttributeError:
        draw.rectangle([clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
                      fill=(180, 180, 180), outline=(150, 150, 150), width=1)
    
    # Draw some list lines on the paper
    line_spacing = size // 20
    line_start_x = paper_x + size // 25
    line_end_x = paper_x + paper_width - size // 25
    
    for i in range(4):
        line_y = paper_y + size // 15 + (i * line_spacing)
        if line_y < paper_y + paper_height - size // 20:
            draw.line([line_start_x, line_y, line_end_x, line_y], 
                     fill=(200, 200, 200), width=2)
    
    # Draw magnifying glass
    glass_center_x = size - size // 3
    glass_center_y = size - size // 3
    glass_radius = size // 6
    
    # Glass circle background
    draw.ellipse([glass_center_x - glass_radius, glass_center_y - glass_radius,
                 glass_center_x + glass_radius, glass_center_y + glass_radius],
                fill=glass_color, outline=accent_color, width=4)
    
    # Checkmark inside the magnifying glass
    check_size = glass_radius // 2
    check_x = glass_center_x
    check_y = glass_center_y
    
    # Draw checkmark (✓)
    check_stroke = max(2, size // 40)
    draw.line([check_x - check_size//2, check_y, 
              check_x - check_size//6, check_y + check_size//2], 
             fill=checkmark_color, width=check_stroke)
    draw.line([check_x - check_size//6, check_y + check_size//2, 
              check_x + check_size//2, check_y - check_size//3], 
             fill=checkmark_color, width=check_stroke)
    
    # Magnifying glass handle
    handle_length = size // 7
    handle_angle = 45  # degrees
    handle_rad = math.radians(handle_angle)
    
    handle_start_x = glass_center_x + int(glass_radius * 0.7 * math.cos(handle_rad))
    handle_start_y = glass_center_y + int(glass_radius * 0.7 * math.sin(handle_rad))
    handle_end_x = handle_start_x + int(handle_length * math.cos(handle_rad))
    handle_end_y = handle_start_y + int(handle_length * math.sin(handle_rad))
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=accent_color, width=max(4, size//30))
    
    # Add a subtle border to the main circle
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=None, outline=accent_color, width=3)
    
    return img

def create_simple_clipboard_icon(size=64):
    """Create a simpler version for Linux compatibility"""
    
    # Create a new image with solid background for better compatibility
    img = Image.new('RGBA', (size, size), (45, 52, 75, 255))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    clipboard_color = (240, 240, 240, 255)
    paper_color = (255, 255, 255, 255)
    accent_color = (74, 144, 226, 255)
    checkmark_color = (40, 167, 69, 255)
    
    # Draw clipboard (simpler design)
    clipboard_width = max(10, size // 2)
    clipboard_height = max(10, int(size * 0.5))
    clipboard_x = size // 6
    clipboard_y = size // 6
    
    # Clipboard base
    draw.rectangle([clipboard_x, clipboard_y, clipboard_x + clipboard_width, clipboard_y + clipboard_height],
                  fill=clipboard_color, outline=(200, 200, 200, 255), width=1)
    
    # Paper
    paper_margin = max(2, size // 20)
    paper_x = clipboard_x + paper_margin
    paper_y = clipboard_y + paper_margin * 2
    paper_width = max(5, clipboard_width - paper_margin * 2)
    paper_height = max(5, clipboard_height - paper_margin * 3)
    
    draw.rectangle([paper_x, paper_y, paper_x + paper_width, paper_y + paper_height],
                  fill=paper_color, outline=(220, 220, 220, 255), width=1)
    
    # Simple lines on paper
    for i in range(3):
        line_y = paper_y + 5 + (i * 6)
        if line_y < paper_y + paper_height - 3:
            draw.line([paper_x + 2, line_y, paper_x + paper_width - 2, line_y], 
                     fill=(200, 200, 200, 255), width=1)
    
    # Simple magnifying glass
    glass_center_x = size - size // 4
    glass_center_y = size - size // 4
    glass_radius = size // 8
    
    # Glass circle
    draw.ellipse([glass_center_x - glass_radius, glass_center_y - glass_radius,
                 glass_center_x + glass_radius, glass_center_y + glass_radius],
                fill=(255, 255, 255, 200), outline=accent_color, width=2)
    
    # Simple checkmark
    check_size = glass_radius // 2
    draw.line([glass_center_x - check_size//2, glass_center_y, 
              glass_center_x - check_size//6, glass_center_y + check_size//2], 
             fill=checkmark_color, width=2)
    draw.line([glass_center_x - check_size//6, glass_center_y + check_size//2, 
              glass_center_x + check_size//2, glass_center_y - check_size//3], 
             fill=checkmark_color, width=2)
    
    # Handle
    handle_start_x = glass_center_x + int(glass_radius * 0.7)
    handle_start_y = glass_center_y + int(glass_radius * 0.7)
    handle_end_x = handle_start_x + glass_radius//2
    handle_end_y = handle_start_y + glass_radius//2
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=accent_color, width=2)
    
    return img

def create_xmp_clipboard_icon():
    """Create an XMP icon with clipboard and magnifying glass"""
    xmp_content = '''/* XPM */
static char * media_manager_clipboard_xpm[] = {
"32 32 8 1",
" 	c None",
".	c #2D344B",
"+	c #4A90E2",
"@	c #F0F0F0",
"#	c #FFFFFF",
"$	c #28A745",
"%	c #DCDCDC",
"&	c #C8C8C8",
"                                ",
"                                ",
"    ......................      ",
"   .                      .     ",
"  .   @@@@@@@@@@@@@@@@     .    ",
" .   @@@@@@@@@@@@@@@@@@     .   ",
" .   @&#############@@@     .   ",
" .   @###############@@     .   ",
" .   @#%%%%%%%%%%%%%#@@     .   ",
" .   @#%%%%%%%%%%%%%#@@     .   ",
" .   @#%%%%%%%%%%%%%#@@     .   ",
" .   @#%%%%%%%%%%%%%#@@     .   ",
" .   @###############@@     .   ",
" .   @@@@@@@@@@@@@@@@@@     .   ",
"  .   @@@@@@@@@@@@@@@@     .    ",
"   .                      .     ",
"    ......................      ",
"                                ",
"                      ....      ",
"                     .++++.     ",
"                    .+++$++.    ",
"                   .++$$$++.    ",
"                  .++$$$$$+.    ",
"                 .+++$$$++.     ",
"                .++++$++.       ",
"               .+++++.          ",
"              .+++.             ",
"             .++.               ",
"            .+.                 ",
"           .                    ",
"                                ",
"                                "};'''
    
    with open('media_manager_clipboard.xpm', 'w') as f:
        f.write(xmp_content)
    print("Created media_manager_clipboard.xpm")

def main():
    """Create the new clipboard + magnifying glass icons"""
    
    # Create high-quality icons
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        if size <= 64:
            # Use simpler design for smaller sizes
            icon = create_simple_clipboard_icon(size)
        else:
            # Use detailed design for larger sizes
            icon = create_clipboard_magnifier_icon(size)
        
        icon.save(f"media_manager_new_{size}.png")
        print(f"Created media_manager_new_{size}.png")
    
    # Create ICO file with multiple sizes
    icons = []
    for size in [16, 32, 48, 64]:
        if size <= 64:
            icons.append(create_simple_clipboard_icon(size))
        else:
            icons.append(create_clipboard_magnifier_icon(size))
    
    # Save as ICO file
    icons[0].save("media_manager_new.ico", format='ICO', sizes=[(s, s) for s in [16, 32, 48, 64]])
    print("Created media_manager_new.ico")
    
    # Create XMP version
    create_xmp_clipboard_icon()
    
    print("\nNew clipboard + magnifying glass icons created successfully!")

if __name__ == "__main__":
    main()
