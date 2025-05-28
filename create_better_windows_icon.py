#!/usr/bin/env python3
"""
Create a better Windows ICO file with proper multi-size support and debug icon loading
"""

from PIL import Image, ImageDraw
import os

def create_simple_solid_icon(size):
    """Create a very simple, solid icon that should work on Windows"""
    
    # Create RGB image (no alpha channel at all)
    img = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Very simple design with high contrast
    # Background
    padding = max(1, size // 16)
    draw.rectangle([padding, padding, size-padding-1, size-padding-1], 
                  fill=(50, 100, 150))  # Dark blue
    
    # Simple clipboard rectangle
    cb_w = size // 3
    cb_h = size // 2
    cb_x = size // 8
    cb_y = size // 6
    
    # Clipboard
    draw.rectangle([cb_x, cb_y, cb_x + cb_w, cb_y + cb_h], 
                  fill=(220, 220, 220), outline=(100, 100, 100))
    
    # Paper
    paper_margin = max(1, size // 20)
    paper_x = cb_x + paper_margin
    paper_y = cb_y + paper_margin * 2
    paper_w = cb_w - paper_margin * 2
    paper_h = cb_h - paper_margin * 3
    
    if paper_w > 2 and paper_h > 2:
        draw.rectangle([paper_x, paper_y, paper_x + paper_w, paper_y + paper_h],
                      fill=(255, 255, 255), outline=(150, 150, 150))
        
        # Lines on paper
        if size >= 24:
            line_spacing = max(2, paper_h // 4)
            for i in range(min(3, paper_h // line_spacing)):
                line_y = paper_y + 2 + (i * line_spacing)
                if line_y < paper_y + paper_h - 1:
                    draw.line([paper_x + 1, line_y, paper_x + paper_w - 1, line_y], 
                             fill=(180, 180, 180))
    
    # Simple magnifying glass
    glass_x = size - size // 3
    glass_y = size - size // 3
    glass_r = max(3, size // 10)
    
    # Glass circle
    draw.ellipse([glass_x - glass_r, glass_y - glass_r,
                 glass_x + glass_r, glass_y + glass_r],
                fill=(240, 240, 240), outline=(80, 80, 80), width=1)
    
    # Simple checkmark if size allows
    if size >= 20:
        check_size = glass_r // 2
        draw.line([glass_x - check_size//2, glass_y, 
                  glass_x, glass_y + check_size//2], 
                 fill=(0, 120, 0), width=max(1, size//20))
        draw.line([glass_x, glass_y + check_size//2, 
                  glass_x + check_size//2, glass_y - check_size//2], 
                 fill=(0, 120, 0), width=max(1, size//20))
    
    # Handle
    if size >= 16:
        handle_len = glass_r
        handle_x1 = glass_x + glass_r - 1
        handle_y1 = glass_y + glass_r - 1
        handle_x2 = min(size-1, handle_x1 + handle_len//2)
        handle_y2 = min(size-1, handle_y1 + handle_len//2)
        
        draw.line([handle_x1, handle_y1, handle_x2, handle_y2], 
                 fill=(60, 60, 60), width=max(1, size//16))
    
    return img

def create_debug_icon(size):
    """Create a debug icon to test if it's loading at all"""
    img = Image.new('RGB', (size, size), (255, 0, 0))  # Red background
    draw = ImageDraw.Draw(img)
    
    # Draw the size number for debugging
    if size >= 16:
        # Simple text representation
        draw.rectangle([2, 2, size-3, size-3], fill=(255, 255, 255))
        
        # Draw size indicator
        center = size // 2
        if size == 16:
            draw.rectangle([center-2, center-2, center+2, center+2], fill=(0, 0, 255))
        elif size == 24:
            draw.rectangle([center-3, center-3, center+3, center+3], fill=(0, 255, 0))
        elif size == 32:
            draw.rectangle([center-4, center-4, center+4, center+4], fill=(255, 0, 255))
        elif size == 48:
            draw.rectangle([center-6, center-6, center+6, center+6], fill=(255, 255, 0))
    
    return img

def create_windows_ico_properly():
    """Create a Windows ICO file with proper format"""
    
    # Standard Windows icon sizes
    sizes = [16, 20, 24, 32, 40, 48, 64]
    
    # Create icons for each size
    icons = []
    for size in sizes:
        icon = create_simple_solid_icon(size)
        icons.append(icon)
        # Also save individual PNGs for testing
        icon.save(f"windows_solid_{size}.png")
        print(f"Created windows_solid_{size}.png")
    
    # Create the ICO file with all sizes
    icons[0].save("media_manager_final.ico", 
                 format='ICO', 
                 sizes=[(s, s) for s in sizes])
    print(f"Created media_manager_final.ico with sizes: {sizes}")
    
    # Create debug versions
    debug_icons = []
    for size in [16, 24, 32, 48]:
        debug_icon = create_debug_icon(size)
        debug_icons.append(debug_icon)
        debug_icon.save(f"debug_{size}.png")
    
    debug_icons[0].save("debug_test.ico", 
                       format='ICO', 
                       sizes=[(16, 16), (24, 24), (32, 32), (48, 48)])
    print("Created debug_test.ico")

def create_bmp_icons():
    """Create BMP versions for maximum Windows compatibility"""
    for size in [16, 24, 32, 48]:
        icon = create_simple_solid_icon(size)
        icon.save(f"media_manager_{size}.bmp")
        print(f"Created media_manager_{size}.bmp")

def main():
    create_windows_ico_properly()
    create_bmp_icons()
    print("\nCreated Windows-optimized icons with proper multi-size support")

if __name__ == "__main__":
    main()
