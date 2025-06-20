#!/usr/bin/env python3
"""
Windows Filename Validator
Checks for filenames that violate Windows naming conventions
"""

import os
import re
import argparse

def check_for_updates_if_enabled():
    """Check for updates in a non-intrusive way"""
    try:
        from update_checker import UpdateChecker
        from version import __version__
        
        checker = UpdateChecker()
        update_info = checker.check_for_updates()
        
        if not 'error' in update_info and update_info.get('update_available', False):
            print(f"📢 Media Manager update available: v{update_info['current_version']} → v{update_info['latest_version']}")
            print(f"   View release: {update_info['release_url']}")
            print()
    except ImportError:
        # Update checker not available, skip silently
        pass
    except Exception:
        # Any error checking updates should be silent to not interfere with main operation
        pass


class WindowsFilenameValidator:
    """Validates filenames against Windows naming conventions"""
    
    # Characters not allowed in Windows filenames
    INVALID_CHARS = set('<>:"|?*\\/')
    
    # Reserved names in Windows (case-insensitive)
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Maximum filename length (without extension)
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 260
    
    def __init__(self):
        self.issues = []
    
    def validate_filename(self, filepath):
        """
        Validate a single filename against Windows conventions
        
        Args:
            filepath (str): Full path to the file
            
        Returns:
            list: List of issues found with the filename
        """
        issues = []
        filename = os.path.basename(filepath)
        
        # Check for invalid characters
        invalid_chars_found = [char for char in filename if char in self.INVALID_CHARS]
        if invalid_chars_found:
            issues.append(f"Contains invalid characters: {', '.join(set(invalid_chars_found))}")
        
        # Check for control characters (0-31)
        control_chars = [char for char in filename if ord(char) < 32]
        if control_chars:
            issues.append(f"Contains control characters (ASCII 0-31)")
        
        # Check for names ending with period or space
        name_without_ext = os.path.splitext(filename)[0]
        if filename.endswith('.') or filename.endswith(' ') or name_without_ext.endswith(' ') or name_without_ext.endswith('.'):
            issues.append("Filename ends with period or space")
        
        # Check for reserved names
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in self.RESERVED_NAMES:
            issues.append(f"Uses reserved Windows name: {name_without_ext}")
        
        # Check filename length
        if len(filename) > self.MAX_FILENAME_LENGTH:
            issues.append(f"Filename too long ({len(filename)} > {self.MAX_FILENAME_LENGTH} characters)")
        
        # Check full path length
        if len(filepath) > self.MAX_PATH_LENGTH:
            issues.append(f"Full path too long ({len(filepath)} > {self.MAX_PATH_LENGTH} characters)")
        
        # Check for leading/trailing spaces in any path component
        path_parts = filepath.split(os.sep)
        for i, part in enumerate(path_parts):
            if part != part.strip():
                issues.append(f"Path component has leading/trailing spaces: '{part}'")
        
        return issues
    
    def suggest_filename_fix(self, filepath):
        """
        Suggest a fixed filename for a problematic file
        
        Args:
            filepath (str): Full path to the file
            
        Returns:
            str or None: Suggested new filename, or None if no fix needed
        """
        filename = os.path.basename(filepath)
        original_filename = filename
        
        # Replace invalid characters with underscores
        for char in self.INVALID_CHARS:
            if char in filename:
                filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Remove trailing periods and spaces from name part (before extension)
        name_part, ext_part = os.path.splitext(filename)
        name_part = name_part.rstrip('. ')
        filename = name_part + ext_part
        
        # Handle reserved names by adding suffix
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in self.RESERVED_NAMES:
            name_part, ext_part = os.path.splitext(filename)
            filename = f"{name_part}_file{ext_part}"
        
        # Truncate if too long
        if len(filename) > self.MAX_FILENAME_LENGTH:
            name_part, ext_part = os.path.splitext(filename)
            max_name_length = self.MAX_FILENAME_LENGTH - len(ext_part)
            filename = name_part[:max_name_length] + ext_part
        
        # Clean up multiple underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Remove leading/trailing underscores
        name_part, ext_part = os.path.splitext(filename)
        name_part = name_part.strip('_')
        filename = name_part + ext_part
        
        # Return None if no changes were made
        return filename if filename != original_filename else None
    
    def validate_file_list(self, file_list):
        """
        Validate a list of file paths
        
        Args:
            file_list (list): List of file paths to validate
            
        Returns:
            dict: Dictionary mapping file paths to lists of issues
        """
        results = {}
        
        for filepath in file_list:
            issues = self.validate_filename(filepath)
            if issues:
                results[filepath] = issues
        
        return results
    
    def validate_from_file(self, input_file):
        """
        Validate filenames from a text file (like media list)
        
        Args:
            input_file (str): Path to file containing list of file paths
            
        Returns:
            dict: Dictionary mapping file paths to lists of issues
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_list = [line.strip() for line in f if line.strip()]
            
            return self.validate_file_list(file_list)
        
        except Exception as e:
            raise Exception(f"Error reading file {input_file}: {e}")
    
    def generate_report(self, validation_results, output_file=None):
        """
        Generate a human-readable report of validation issues
        
        Args:
            validation_results (dict): Results from validation
            output_file (str, optional): File to write report to
            
        Returns:
            str: The generated report
        """
        if not validation_results:
            report = "✅ No Windows filename compatibility issues found!\n"
        else:
            report = f"❌ Found {len(validation_results)} files with Windows naming issues:\n\n"
            
            for filepath, issues in validation_results.items():
                report += f"📁 {filepath}\n"
                for issue in issues:
                    report += f"   • {issue}\n"
                report += "\n"
            
            report += "\n📝 Common fixes:\n"
            report += "• Remove or replace invalid characters: < > : \" | ? * \\ /\n"
            report += "• Rename files that use reserved Windows names (CON, PRN, AUX, etc.)\n"
            report += "• Remove trailing periods and spaces from filenames\n"
            report += "• Shorten very long filenames or paths\n"
            report += "• Remove leading/trailing spaces from directory names\n"
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            except Exception as e:
                raise Exception(f"Error writing report to {output_file}: {e}")
        
        return report


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Validate filenames for Windows compatibility")
    parser.add_argument('-i', '--input', required=True, 
                       help='Input file containing list of file paths')
    parser.add_argument('-o', '--output', 
                       help='Output file for the validation report')
    parser.add_argument('--no-update-check', action='store_true', help='Skip checking for updates')
    
    args = parser.parse_args()
    
    # Check for updates unless disabled
    if not args.no_update_check:
        check_for_updates_if_enabled()
    
    try:
        validator = WindowsFilenameValidator()
        results = validator.validate_from_file(args.input)
        report = validator.generate_report(results, args.output)
        
        print(report)
        
        if args.output:
            print(f"\nReport saved to: {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
