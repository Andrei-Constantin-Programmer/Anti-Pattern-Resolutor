"""
Core workflow utilities for AntiPattern Remediator

This module contains utility functions for parsing results and extracting repository paths.
"""

import json
import re
from pathlib import Path
from colorama import Fore, Style


def parse_antipattern_results(antipatterns_scanner_results):
    """Parse anti-pattern scanner results to determine if patterns were found and count them."""

    if not antipatterns_scanner_results:
        return False, 0
    
    # Try to parse as JSON first
    try:
        if isinstance(antipatterns_scanner_results, str):
            print(type(antipatterns_scanner_results))
            # Try to extract JSON from the string - improved regex pattern
            # Look for JSON objects containing total_antipatterns_found
            json_pattern = r'\{\s*[^}]*?"total_antipatterns_found"\s*:\s*(\d+)[^}]*?\}'
            json_match = re.search(json_pattern, antipatterns_scanner_results, re.DOTALL)
            
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    total_found = json_data.get('total_antipatterns_found', 0)
                    return total_found > 0, total_found
                except json.JSONDecodeError:
                    # If full JSON parsing fails, extract just the number
                    total_found = int(json_match.group(1))
                    return total_found > 0, total_found
            
            return False, 0
        
        elif isinstance(antipatterns_scanner_results, dict):
            total_found = antipatterns_scanner_results.get('total_antipatterns_found', 0)
            return total_found > 0, total_found
            
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error parsing antipattern results: {e}")
        pass
    
    # Default: if we have results but can't parse them, assume no anti-patterns
    return False, 0


def get_repository_paths_from_files(file_paths: list) -> set:
    """Extract unique repository paths from the list of file paths."""
    repo_paths = set()
    
    for file_path in file_paths:
        path = Path(file_path)
        
        # Find the clones directory in the path
        for i, part in enumerate(path.parts):
            if part == 'clones' and i + 1 < len(path.parts):
                # The next part after 'clones' is the repository name
                repo_name = path.parts[i + 1]
                # Reconstruct the full repository path
                clones_path = Path(*path.parts[:i+1])  # Path up to 'clones'
                repo_path = clones_path / repo_name
                repo_paths.add(str(repo_path))
                break
    
    return repo_paths
