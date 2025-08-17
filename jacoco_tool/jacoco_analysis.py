"""
JaCoCo Integration
==================

Clean, generalized workflow for:
1. Cloning Java repositories
2. Running JaCoCo coverage analysis  
3. Filtering files with 100% test coverage
4. Preparing filtered files for anti-pattern analysis

Usage:
    python jacoco_analysis.py --repos repos.txt
    python jacoco_analysis.py --repos repos.txt --force-jacoco
    python jacoco_analysis.py --single-repo https://github.com/user/repo
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# Add project modules to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_handler.clone_repos import clone_repo, clone_repos_from_file
from jacoco_tool.core import JaCoCoAnalyzer, analyze_repositories, export_results
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clone_repositories(args) -> Tuple[List[str], Path]:
    """
    Clone repositories based on command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Tuple of (list of repo names to analyze, clone directory path)
    """
    logger.info("Step 1: Cloning repositories...")
    # Handle clone directory relative to current working directory
    clone_dir = Path(args.clone_dir)
    if not clone_dir.is_absolute():
        clone_dir = Path.cwd() / clone_dir
    clone_dir.mkdir(exist_ok=True)
    
    # Track which repositories to analyze (only the ones cloned in this run)
    repos_to_analyze = []
    
    try:
        if args.single_repo:
            # Extract repo name from URL
            repo_name = args.single_repo.split('/')[-1].replace('.git', '')
            repos_to_analyze.append(repo_name)
            
            clone_repo(args.single_repo, str(clone_dir))
            logger.info(f"Cloned repository: {args.single_repo}")
            
        else:
            # Use repos file (either explicitly provided or default)
            repos_file = Path(args.repos)
            if not repos_file.is_absolute():
                repos_file = Path.cwd() / repos_file
            
            if not repos_file.exists():
                logger.error(f"Repository list file not found: {repos_file}")
                raise FileNotFoundError(f"Repository list file not found: {repos_file}")
            
            # Read repository URLs from file to get repo names
            with open(repos_file, 'r') as f:
                repo_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Extract repo names from URLs
            for url in repo_urls:
                repo_name = url.split('/')[-1].replace('.git', '')
                repos_to_analyze.append(repo_name)
            
            clone_repos_from_file(str(repos_file), str(clone_dir))
            logger.info(f"Cloned repositories from {repos_file}")
            
    except Exception as e:
        logger.error(f"Repository cloning failed: {e}")
        raise
    
    return repos_to_analyze, clone_dir


def run_jacoco_analysis(repos_to_analyze: List[str], clone_dir: Path, args) -> Dict[str, Dict[str, List[str]]]:
    """
    Run JaCoCo coverage analysis on specified repositories.
    
    Args:
        repos_to_analyze: List of repository names to analyze
        clone_dir: Directory containing cloned repositories
        args: Parsed command line arguments
        
    Returns:
        Dictionary mapping repository names to their coverage results
    """
    logger.info("Step 2: Running JaCoCo coverage analysis...")
    
    analyzer = JaCoCoAnalyzer(timeout=args.timeout, verbose=args.verbose)
    results = {}
    
    # Only analyze the repositories that were specified for this run
    for repo_name in repos_to_analyze:
        repo_dir = clone_dir / repo_name
        if repo_dir.is_dir():
            logger.info(f"Analyzing repository: {repo_name}")
            repo_results = analyzer.analyze_repository(str(repo_dir), force=args.force_jacoco)
            if repo_results:
                results[repo_name] = repo_results
        else:
            logger.warning(f"Repository directory not found: {repo_dir}")
    
    if not results:
        logger.warning("No coverage results found. Ensure repositories contain Java projects with tests.")
        raise ValueError("No coverage results found")
    
    # Count total files
    total_files = sum(
        len(files) for repo_results in results.values() 
        for files in repo_results.values()
    )
    
    logger.info(f"Found {total_files} files with 100% coverage across {len(results)} repositories")
    return results


def export_coverage_results(results: Dict[str, Dict[str, List[str]]], args) -> None:
    """
    Export coverage analysis results to files.
    
    Args:
        results: Coverage analysis results
        args: Parsed command line arguments
        
    Returns:
        Path to the combined file list
    """
    logger.info("Step 3: Exporting results...")
    
    # Handle output directory relative to current working directory
    output_dir = args.output_dir
    if not Path(output_dir).is_absolute():
        output_dir = str(Path.cwd() / output_dir)
    
    combined_file = export_results(results, output_dir)
    
    if not combined_file:
        logger.warning("No files with 100% coverage found")
        raise ValueError("No files with 100% coverage found")
    
    logger.info(f"Results exported to: {args.output_dir}")
    logger.info(f"Combined file list: {combined_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for repo_name, repo_results in results.items():
        repo_total = sum(len(files) for files in repo_results.values())
        print(f"{repo_name}: {repo_total} files with 100% coverage")
        
        for module_name, files in repo_results.items():
            if len(repo_results) > 1:  # Only show modules if multi-module
                print(f"  {module_name}: {len(files)} files")
    
    # Count total files
    total_files = sum(
        len(files) for repo_results in results.values() 
        for files in repo_results.values()
    )
    
    print(f"\nTotal files ready for analysis: {total_files}")
    print(f"File list: {combined_file}")
    print("\nNext steps:")
    print("1. Review the file list to understand coverage scope")
    print("2. Use these files for anti-pattern analysis")
    print("3. Apply refactoring recommendations to well-tested code")
    

def main():
    """Main workflow function."""
    parser = argparse.ArgumentParser(
        description="Analyze Java repositories with JaCoCo coverage filtering"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--repos",
        default="repos.txt",
        help="Text file containing GitHub repository URLs (one per line) (default: repos.txt)"
    )
    input_group.add_argument(
        "--single-repo",
        help="Single GitHub repository URL to analyze"
    )
    
    # Configuration options
    parser.add_argument(
        "--clone-dir",
        default="clones",
        help="Directory to clone repositories into (default: clones)"
    )
    parser.add_argument(
        "--output-dir", 
        default="jacoco_results",
        help="Directory for output files (default: jacoco_results)"
    )
    parser.add_argument(
        "--force-jacoco",
        action="store_true",
        help="Force JaCoCo analysis even if reports already exist"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Build timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== JaCoCo Tool Analysis ===")
    
    try:
        # Step 1: Clone repositories
        repos_to_analyze, clone_dir = clone_repositories(args)
        
        # Step 2: Run JaCoCo analysis
        results = run_jacoco_analysis(repos_to_analyze, clone_dir, args)
        
        # Step 3: Export results
        export_coverage_results(results, args)
        
        logger.info("Workflow completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
