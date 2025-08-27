"""
Full Repository Workflow - Process files with 100% test coverage from JaCoCo results
"""
from colorama import Fore, Style
from pathlib import Path
import os

# Import workflow utilities
from workflow.workflow_utils import parse_antipattern_results, get_repository_paths_from_files
from workflow.backup_manager import create_repository_backup
from workflow.results_manager import save_intermediate_results, create_processing_summary
from workflow.file_operations import read_java_file, save_refactored_code



def read_jacoco_results(jacoco_results_dir: str = "../jacoco_results") -> list:
    """Read the list of files with 100% coverage from JaCoCo results."""
    results_path = Path(jacoco_results_dir)
    
    if not results_path.exists():
        print(Fore.RED + f"JaCoCo results directory not found: {results_path}" + Style.RESET_ALL)
        return []
    
    # Find all result files
    all_files = list(results_path.glob("*.txt"))
    if not all_files:
        print(Fore.RED + f"No JaCoCo result files found in: {results_path}" + Style.RESET_ALL)
        return []
    
    # Separate combined file from individual repo files
    combined_file = results_path / "all_100_percent_coverage_files.txt"
    repo_files = [f for f in all_files if f.name != "all_100_percent_coverage_files.txt"]
    
    print(Fore.CYAN + "\nAvailable JaCoCo result files:" + Style.RESET_ALL)
    print("0) All repositories (combined)")
    
    # Show individual repository options
    for i, repo_file in enumerate(repo_files, 1):
        # Extract repo name from filename (remove _100_percent_coverage.txt suffix)
        repo_name = repo_file.stem.replace("_100_percent_coverage", "")
        print(f"{i}) {repo_name}")
    
    # Get user choice
    while True:
        try:
            choice = input(f"\nSelect repository to process (0-{len(repo_files)}): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                # Use combined file
                selected_file = combined_file
                repo_name = "All repositories"
                break
            elif 1 <= choice_num <= len(repo_files):
                # Use specific repo file
                selected_file = repo_files[choice_num - 1]
                repo_name = selected_file.stem.replace("_100_percent_coverage", "")
                break
            else:
                print(Fore.RED + f"Invalid choice. Please enter a number between 0 and {len(repo_files)}" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
    
    # Read the selected file
    if not selected_file.exists():
        print(Fore.RED + f"Selected file not found: {selected_file}" + Style.RESET_ALL)
        return []
    
    try:
        with open(selected_file, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]
        
        print(Fore.GREEN + f"Selected: {repo_name}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Found {len(file_paths)} files with 100% test coverage" + Style.RESET_ALL)
        return file_paths
        
    except Exception as e:
        print(Fore.RED + f"Error reading file {selected_file}: {e}" + Style.RESET_ALL)
        return []



def process_java_files_with_workflow(file_paths: list, settings, db_manager, prompt_manager, langgraph):
    """Process each Java file through the agentic workflow."""
    processed_files = []
    failed_files = []
    
    for i, file_path in enumerate(file_paths, 1):
        print(Fore.BLUE + f"\n{'='*60}" + Style.RESET_ALL)
        print(Fore.BLUE + f"Processing file {i}/{len(file_paths)}: {file_path}" + Style.RESET_ALL)
        print(Fore.BLUE + f"{'='*60}" + Style.RESET_ALL)
        
        # Read the Java file content
        java_code = read_java_file(file_path)
        if java_code is None:
            failed_files.append(file_path)
            continue
        
        # Create initial state for this file
        initial_state = {
            "code": java_code,
            "context": None,
            "trove_context": None,
            "antipatterns_scanner_results": None,
            "refactoring_strategy_results": None,
            "refactored_code": None,
            "code_review_results": None,
            "code_review_times": 0,
            "msgs": [],
            "answer": None,
            "current_file_path": file_path  # Track current file being processed
        }
        
        try:
            # Run the agentic workflow
            print(Fore.CYAN + "Running agentic workflow..." + Style.RESET_ALL)
            final_state = langgraph.invoke(initial_state)
            
            # Save intermediate results for analysis
            save_intermediate_results(file_path, final_state, settings)
            
            # Check if refactoring was successful
            if final_state.get('refactored_code'):
                # Parse anti-pattern results
                antipatterns_found, antipatterns_count = parse_antipattern_results(final_state.get('antipatterns_scanner_results'))
                
                # Save the refactored code back to the file
                if save_refactored_code(file_path, final_state['refactored_code']):
                    processed_files.append({
                        'file_path': file_path,
                        'status': 'success',
                        'antipatterns_found': antipatterns_found,
                        'antipatterns_count': antipatterns_count,
                        'code_review_times': final_state.get('code_review_times', 0),
                        'has_intermediate_results': True
                    })
                    print(Fore.GREEN + f"Successfully processed: {file_path}" + Style.RESET_ALL)
                else:
                    failed_files.append(file_path)
            else:
                # Parse anti-pattern results
                antipatterns_found, antipatterns_count = parse_antipattern_results(final_state.get('antipatterns_scanner_results'))
                
                print(Fore.YELLOW + f"No refactored code generated for: {file_path}" + Style.RESET_ALL)
                processed_files.append({
                    'file_path': file_path,
                    'status': 'no_refactoring',
                    'antipatterns_found': antipatterns_found,
                    'antipatterns_count': antipatterns_count,
                    'code_review_times': final_state.get('code_review_times', 0),
                    'has_intermediate_results': True
                })
                
        except Exception as e:
            print(Fore.RED + f"Error processing {file_path}: {e}" + Style.RESET_ALL)
            failed_files.append(file_path)
    
    return processed_files, failed_files


def run_full_repo_workflow(settings, db_manager, prompt_manager, langgraph):
    """Run the full repository workflow for files with 100% test coverage."""
    print(Fore.BLUE + "\n=== Full Repository Workflow ===" + Style.RESET_ALL)
    print("Process Java files with 100% test coverage from JaCoCo results...")
    
    # Read JaCoCo results to get files with 100% test coverage
    print(Fore.CYAN + "\nReading JaCoCo results..." + Style.RESET_ALL)
    file_paths = read_jacoco_results()
    
    if not file_paths:
        print(Fore.RED + "No files found in JaCoCo results. Please run JaCoCo analysis first." + Style.RESET_ALL)
        print("Run: python jacoco_tool/jacoco_analysis.py")
        return False

    # Extract repository paths from file paths
    print(Fore.CYAN + "\nIdentifying repositories to backup..." + Style.RESET_ALL)
    repo_paths = get_repository_paths_from_files(file_paths)
    
    if not repo_paths:
        print(Fore.RED + "No repository paths could be identified from the file paths." + Style.RESET_ALL)
        return False
    
    print(f"Found {len(repo_paths)} repositories to backup:")
    for repo_path in sorted(repo_paths):
        repo_name = Path(repo_path).name
        print(f"  • {repo_name} ({repo_path})")

    # Ask user for confirmation to proceed with backup and processing
    print(f"\nFiles to process ({len(file_paths)} total):")
    for i, path in enumerate(file_paths[:5], 1):  # Show first 5 files
        print(f"  {i}. {path}")
    if len(file_paths) > 5:
        print(f"  ... and {len(file_paths) - 5} more files")
    
    proceed = input(f"\nProceed with backing up {len(repo_paths)} repositories and processing {len(file_paths)} files? (Y/N): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled.")
        return False

    # Create repository backups
    print(Fore.BLUE + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.BLUE + "CREATING REPOSITORY BACKUPS" + Style.RESET_ALL)
    print(Fore.BLUE + f"{'='*60}" + Style.RESET_ALL)
    
    backup_info = create_repository_backup(repo_paths)
    
    if backup_info['failed_backups']:
        print(Fore.RED + f"\nWarning: {len(backup_info['failed_backups'])} repositories failed to backup:" + Style.RESET_ALL)
        for failed in backup_info['failed_backups']:
            print(Fore.RED + f" {failed['repo_path']}: {failed['error']}" + Style.RESET_ALL)
        
        continue_anyway = input("\nContinue processing despite backup failures? (Y/N): ").strip().lower()
        if continue_anyway != 'y':
            print("Operation cancelled due to backup failures.")
            return False
    
    print(Fore.GREEN + f"\nSuccessfully backed up {len(backup_info['backed_up_repos'])} repositories" + Style.RESET_ALL)
    print(Fore.GREEN + f"Backup location: {backup_info['backup_dir']}" + Style.RESET_ALL)

    # Process each file through the agentic workflow
    print(Fore.BLUE + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.BLUE + "STARTING FILE PROCESSING" + Style.RESET_ALL)
    print(Fore.BLUE + f"{'='*60}" + Style.RESET_ALL)
    
    processed_files, failed_files = process_java_files_with_workflow(
        file_paths, settings, db_manager, prompt_manager, langgraph
    )

    # Create comprehensive processing summary
    summary_file = create_processing_summary(processed_files, backup_info)

    # Generate summary report
    print(Fore.BLUE + "\n" + "="*80 + Style.RESET_ALL)
    print(Fore.BLUE + "BATCH PROCESSING SUMMARY" + Style.RESET_ALL)
    print(Fore.BLUE + "="*80 + Style.RESET_ALL)
    
    # Backup summary
    print(Fore.CYAN + "Repository Backup Summary:" + Style.RESET_ALL)
    print(f"  Backup timestamp: {backup_info['timestamp']}")
    print(f"  Backup location: {backup_info['backup_dir']}")
    print(f"  Repositories backed up: {len(backup_info['backed_up_repos'])}")
    if backup_info['failed_backups']:
        print(f"  Failed backups: {len(backup_info['failed_backups'])}")
    
    # Processing summary
    print(Fore.CYAN + "\nFile Processing Summary:" + Style.RESET_ALL)
    print(f"  Total files processed: {len(processed_files)}")
    print(f"  Failed files: {len(failed_files)}")
    
    # Categorize results
    successful_refactoring = [f for f in processed_files if f['status'] == 'success']
    no_refactoring_needed = [f for f in processed_files if f['status'] == 'no_refactoring']
    files_with_antipatterns = [f for f in processed_files if f.get('antipatterns_found', False)]
    total_antipatterns = sum(f.get('antipatterns_count', 0) for f in processed_files)
    
    print(Fore.GREEN + f"  Successfully refactored: {len(successful_refactoring)}" + Style.RESET_ALL)
    print(Fore.YELLOW + f"  No refactoring needed: {len(no_refactoring_needed)}" + Style.RESET_ALL)
    print(Fore.RED + f"  Failed: {len(failed_files)}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"  Files with anti-patterns: {len(files_with_antipatterns)}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"  Total anti-patterns found: {total_antipatterns}" + Style.RESET_ALL)
    
    # Statistics
    if processed_files:
        refactor_rate = len(successful_refactoring) / len(processed_files) * 100
        antipattern_rate = len(files_with_antipatterns) / len(processed_files) * 100

        
        print(Fore.CYAN + "\nProcessing Statistics:" + Style.RESET_ALL)
        print(f"  Refactoring success rate: {refactor_rate:.1f}%")
        print(f"  Anti-pattern detection rate: {antipattern_rate:.1f}%")
        print(f"  Total anti-patterns found: {total_antipatterns}")
    
    # Show detailed results
    if successful_refactoring:
        print(Fore.GREEN + "\nSuccessfully refactored files:" + Style.RESET_ALL)
        for file_info in successful_refactoring:
            antipatterns_info = f" (antipatterns: {file_info.get('antipatterns_count', 0)})" if file_info.get('antipatterns_count', 0) > 0 else ""
            print(f"{file_info['file_path']} (reviews: {file_info['code_review_times']}){antipatterns_info}")
    
    if failed_files:
        print(Fore.RED + "\nFailed files:" + Style.RESET_ALL)
        for file_path in failed_files:
            print(f"{file_path}")
    
    print(Fore.GREEN + f"\nBatch processing complete!" + Style.RESET_ALL)
    print(Fore.CYAN + f"Repository backups available at: {backup_info['backup_dir']}" + Style.RESET_ALL)
    print(f"To restore a repository, copy from backup directory back to original location.")
    
    # Intermediate results information
    print(Fore.MAGENTA + f"\nIntermediate Results:" + Style.RESET_ALL)
    print(f"  Individual file analysis results saved in: ../processing_results/")
    if summary_file:
        print(f"  Comprehensive summary saved: {Path(summary_file).name}")
