"""
Repository backup management for AntiPattern Remediator

This module handles creating backups of repositories before processing.
"""

import shutil
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style


def create_repository_backup(repo_paths: set, backup_base_dir: str = "../backups") -> dict:
    """Create backups of repositories before processing."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(backup_base_dir) / f"repo_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_info = {
        'timestamp': timestamp,
        'backup_dir': str(backup_dir),
        'backed_up_repos': [],
        'failed_backups': []
    }
    
    print(Fore.BLUE + f"\nCreating repository backups in: {backup_dir}" + Style.RESET_ALL)
    
    for repo_path in repo_paths:
        try:
            repo_path_obj = Path(repo_path)
            repo_name = repo_path_obj.name
            backup_repo_path = backup_dir / repo_name
            
            print(Fore.CYAN + f"Backing up repository: {repo_name}..." + Style.RESET_ALL)
            
            # Copy the entire repository
            shutil.copytree(repo_path, backup_repo_path, dirs_exist_ok=True)
            
            backup_info['backed_up_repos'].append({
                'original_path': repo_path,
                'backup_path': str(backup_repo_path),
                'repo_name': repo_name
            })
            
            print(Fore.GREEN + f"Successfully backed up: {repo_name}" + Style.RESET_ALL)
            
        except Exception as e:
            print(Fore.RED + f"Failed to backup {repo_path}: {e}" + Style.RESET_ALL)
            backup_info['failed_backups'].append({
                'repo_path': repo_path,
                'error': str(e)
            })
    
    return backup_info
