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

# Add project modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_handler.clone_repos import clone_repo, clone_repos_from_file
from jacoco_tool.core import JaCoCoAnalyzer, analyze_repositories, export_results
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main workflow function."""
    parser = argparse.ArgumentParser(
        description="Analyze Java repositories with JaCoCo coverage filtering"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--repos",
        help="Text file containing GitHub repository URLs (one per line)"
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
    
    # Step 1: Clone repositories
    logger.info("Step 1: Cloning repositories...")
    clone_dir = Path(args.clone_dir)
    clone_dir.mkdir(exist_ok=True)
    
    try:
        if args.repos:
            if not os.path.exists(args.repos):
                logger.error(f"Repository list file not found: {args.repos}")
                return 1
            
            clone_repos_from_file(args.repos, str(clone_dir))
            logger.info(f"Cloned repositories from {args.repos}")
            
        elif args.single_repo:
            clone_repo(args.single_repo, str(clone_dir))
            logger.info(f"Cloned repository: {args.single_repo}")
            
    except Exception as e:
        logger.error(f"Repository cloning failed: {e}")
        return 1
    
    # Step 2: Run JaCoCo Analysis
    logger.info("Step 2: Running JaCoCo coverage analysis...")
    try:
        analyzer = JaCoCoAnalyzer(timeout=args.timeout, verbose=args.verbose)
        results = {}
        
        for repo_dir in clone_dir.iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
                logger.info(f"Analyzing repository: {repo_dir.name}")
                repo_results = analyzer.analyze_repository(str(repo_dir), force=args.force_jacoco)
                if repo_results:
                    results[repo_dir.name] = repo_results
        
        if not results:
            logger.warning("No coverage results found. Ensure repositories contain Java projects with tests.")
            return 1
            
        # Count total files
        total_files = sum(
            len(files) for repo_results in results.values() 
            for files in repo_results.values()
        )
        
        logger.info(f"Found {total_files} files with 100% coverage across {len(results)} repositories")
        
    except Exception as e:
        logger.error(f"JaCoCo analysis failed: {e}")
        return 1
    
    # Step 3: Export Results
    logger.info("Step 3: Exporting results...")
    try:
        combined_file = export_results(results, args.output_dir)
        
        if combined_file:
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
            
            print(f"\nTotal files ready for analysis: {total_files}")
            print(f"File list: {combined_file}")
            print("\nNext steps:")
            print("1. Review the file list to understand coverage scope")
            print("2. Use these files for anti-pattern analysis")
            print("3. Apply refactoring recommendations to well-tested code")
            
        else:
            logger.warning("No files with 100% coverage found")
            return 1
            
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1
    
    logger.info("Workflow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
