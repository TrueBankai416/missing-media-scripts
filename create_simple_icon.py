#!/usr/bin/env python3
"""
Create a simpler, more compatible icon for Linux systems
"""

from PIL import Image, ImageDraw
import os

def create_simple_icon(size=64):
    """Create a simple clipboard + magnifying glass icon for Linux compatibility"""
    
    # Create a new image with solid background for better compatibility
    img = Image.new('RGBA', (size, size), (45, 52, 75, 255))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    clipboard_color = (240, 240, 240, 255)
    paper_color = (255, 255, 255, 255)
    accent_color = (74, 144, 226, 255)
    checkmark_color = (40, 167, 69, 255)
    
    # Draw clipboard (simple design)
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
    line_spacing = max(3, size // 12)
    for i in range(3):
        line_y = paper_y + line_spacing + (i * line_spacing)
        if line_y < paper_y + paper_height - 3:
            draw.line([paper_x + 2, line_y, paper_x + paper_width - 2, line_y], 
                     fill=(200, 200, 200, 255), width=1)
    
    # Simple magnifying glass
    glass_center_x = size - size // 4
    glass_center_y = size - size // 4
    glass_radius = max(4, size // 8)
    
    # Glass circle
    draw.ellipse([glass_center_x - glass_radius, glass_center_y - glass_radius,
                 glass_center_x + glass_radius, glass_center_y + glass_radius],
                fill=(255, 255, 255, 200), outline=accent_color, width=2)
    
    # Simple checkmark inside
    check_size = max(2, glass_radius // 2)
    draw.line([glass_center_x - check_size//2, glass_center_y, 
              glass_center_x - check_size//6, glass_center_y + check_size//2], 
             fill=checkmark_color, width=2)
    draw.line([glass_center_x - check_size//6, glass_center_y + check_size//2, 
              glass_center_x + check_size//2, glass_center_y - check_size//3], 
             fill=checkmark_color, width=2)
    
    # Handle
    handle_start_x = glass_center_x + int(glass_radius * 0.7)
    handle_start_y = glass_center_y + int(glass_radius * 0.7)
    handle_end_x = handle_start_x + max(3, glass_radius//2)
    handle_end_y = handle_start_y + max(3, glass_radius//2)
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
             fill=accent_color, width=2)
    
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
