"""
File I/O operations for AntiPattern Remediator

This module handles reading and writing files during the workflow process.
"""

from colorama import Fore, Style


def read_java_file(file_path: str) -> str:
    """Read the content of a Java file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(Fore.RED + f"Error reading file {file_path}: {e}" + Style.RESET_ALL)
        return None


def save_refactored_code(file_path: str, refactored_code: str, backup: bool = False) -> bool:
    """Save the refactored code back to the original file."""
    try:
        # Create backup if requested (disabled by default since we backup entire repos)
        if backup:
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup_file:
                    backup_file.write(original.read())
            print(Fore.YELLOW + f"Backup created: {backup_path}" + Style.RESET_ALL)
        
        # Write refactored code
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(refactored_code)
        
        print(Fore.GREEN + f"Refactored code saved to: {file_path}" + Style.RESET_ALL)
        return True
        
    except Exception as e:
        print(Fore.RED + f"Error saving refactored code to {file_path}: {e}" + Style.RESET_ALL)
        return False
