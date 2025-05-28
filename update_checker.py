#!/usr/bin/env python3
"""
Update checker for Media Manager
Checks GitHub releases for updates
"""

import json
import urllib.request
import urllib.error
from version import __version__, __repository__

class UpdateChecker:
    def __init__(self, repository=__repository__, current_version=__version__):
        self.repository = repository
        self.current_version = current_version
        self.github_api_url = f"https://api.github.com/repos/{repository}/releases"
    
    def check_for_updates(self):
        """
        Check for updates from GitHub releases
        
        Returns:
            dict: Update information with keys:
                - 'update_available': bool
                - 'latest_version': str
                - 'current_version': str
                - 'release_url': str (if update available)
                - 'release_notes': str (if update available)
                - 'error': str (if error occurred)
        """
        try:
            # Fetch latest release from GitHub API
            latest_release = self._get_latest_release()
            
            if latest_release is None:
                return {
                    'update_available': False,
                    'current_version': self.current_version,
                    'latest_version': self.current_version,
                    'error': 'Unable to fetch release information'
                }
            
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            release_url = latest_release.get('html_url', '')
            release_notes = latest_release.get('body', '')
            
            # Compare versions
            update_available = self._is_newer_version(latest_version, self.current_version)
            
            result = {
                'update_available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'release_url': release_url,
                'release_notes': release_notes
            }
            
            return result
            
        except Exception as e:
            return {
                'update_available': False,
                'current_version': self.current_version,
                'latest_version': self.current_version,
                'error': f'Error checking for updates: {str(e)}'
            }
    
    def _get_latest_release(self):
        """Fetch the latest release from GitHub API"""
        try:
            # Create request with User-Agent header (required by GitHub API)
            request = urllib.request.Request(
                f"{self.github_api_url}/latest",
                headers={'User-Agent': 'MediaManager-UpdateChecker'}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No releases found
                return None
            raise
        except Exception:
            raise
    
    def _is_newer_version(self, latest, current):
        """
        Compare version strings to determine if latest is newer than current
        Supports semantic versioning (major.minor.patch)
        """
        try:
            # Clean version strings (remove 'v' prefix if present)
            latest = latest.lstrip('v')
            current = current.lstrip('v')
            
            # Split version parts
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Normalize to same length (pad with zeros)
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            # Compare versions
            for i in range(max_len):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False
            
            return False  # Versions are equal
            
        except (ValueError, AttributeError):
            # If version parsing fails, assume no update needed
            return False
    
    def get_current_version_info(self):
        """Get current version information"""
        from version import __author__, __description__
        
        return {
            'version': self.current_version,
            'repository': self.repository,
            'author': __author__,
            'description': __description__
        }

def main():
    """Test the update checker"""
    checker = UpdateChecker()
    print("Checking for updates...")
    
    update_info = checker.check_for_updates()
    
    if 'error' in update_info:
        print(f"Error: {update_info['error']}")
    else:
        print(f"Current version: {update_info['current_version']}")
        print(f"Latest version: {update_info['latest_version']}")
        
        if update_info['update_available']:
            print("🎉 Update available!")
            print(f"Release URL: {update_info['release_url']}")
            if update_info['release_notes']:
                print(f"Release notes: {update_info['release_notes'][:200]}...")
        else:
            print("✅ You're up to date!")

if __name__ == "__main__":
    main()
