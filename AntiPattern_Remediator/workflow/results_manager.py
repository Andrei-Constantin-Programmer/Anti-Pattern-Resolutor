"""
Results processing and reporting for AntiPattern Remediator

This module handles saving intermediate results and creating processing summaries.
"""

import json
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style


def save_intermediate_results(file_path: str, final_state: dict, settings, results_dir: str = "../processing_results") -> bool:
    """Save intermediate results from the agentic workflow for analysis in markdown format."""
    try:
        if file_path != 'java_code_snippet' and not None:
            # Create results directory if it doesn't exist
            results_path = Path(results_dir)
            results_path.mkdir(parents=True, exist_ok=True)
            
            # Create a unique filename based on the original file path
            file_path_obj = Path(file_path)
            
            # Extract the meaningful part of the path starting from the repository name
            # Find the 'clones' directory and take everything after it
            meaningful_path = None
            for i, part in enumerate(file_path_obj.parts):
                if part == 'clones' and i + 1 < len(file_path_obj.parts):
                    # Take from the repo name onwards
                    meaningful_path = Path(*file_path_obj.parts[i+1:])
                    break
            
            if meaningful_path is None:
                # Fallback: use just the filename if 'clones' not found
                meaningful_path = file_path_obj.name
            
            # Create a safe filename by replacing path separators and other problematic characters
            safe_filename = str(meaningful_path).replace('/', '_').replace('\\', '_').replace(':', '_')
            
            # Replace .java extension with .md and add results suffix
            if safe_filename.endswith('.java'):
                safe_filename = safe_filename[:-5]  # Remove .java
            results_filename = f"{safe_filename}_results.md"
            results_file_path = results_path / results_filename
        else: 
            results_filename = f"java_code_snippet_results.md"
            results_file_path = results_filename

        # Generate markdown content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        markdown_content = f"""# Processing Results: {file_path_obj.name if file_path != 'java_code_snippet' else 'Java Code Snippet'}

## File Information
- **Original File Path**: `{file_path}`
- **Processing Timestamp**: {timestamp}
- **Code Refactored**: {'Yes' if final_state.get('refactored_code') else 'No'}

---

## Anti-Pattern Scanner Results

"""
        
        antipatterns_results = final_state.get('antipatterns_scanner_results')
        if antipatterns_results:
            if isinstance(antipatterns_results, str):
                markdown_content += f"\n{antipatterns_results}\n\n\n"
            elif isinstance(antipatterns_results, dict):
                for key, value in antipatterns_results.items():
                    markdown_content += f"### {key.replace('_', ' ').title()}\n"
                    if isinstance(value, (list, dict)):
                        markdown_content += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                    else:
                        markdown_content += f"{value}\n\n"
            else:
                markdown_content += f"```json\n{json.dumps(antipatterns_results, indent=2, default=str)}\n```\n\n"
        else:
            markdown_content += "No anti-patterns detected or scanner did not run.\n\n"
        
        markdown_content += "---\n\n## Refactoring Strategy Results\n\n"
        
        refactoring_results = final_state.get('refactoring_strategy_results')
        if refactoring_results:
            if isinstance(refactoring_results, str):
                markdown_content += f"\n{refactoring_results}\n\n\n"
            elif isinstance(refactoring_results, dict):
                for key, value in refactoring_results.items():
                    markdown_content += f"### {key.replace('_', ' ').title()}\n"
                    if isinstance(value, (list, dict)):
                        markdown_content += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                    else:
                        markdown_content += f"{value}\n\n"
            else:
                markdown_content += f"```json\n{json.dumps(refactoring_results, indent=2, default=str)}\n```\n\n"
        else:
            markdown_content += "No refactoring strategy generated.\n\n"
        
        if final_state.get("explanation_json"):
            explanation_results = final_state.get('explanation_json')
            markdown_content += "---\n\n## Explanation Results\n\n"
            
            # Parse and format the explanation JSON
            if isinstance(explanation_results, dict):
                # Handle individual anti-patterns
                items = explanation_results.get('items', [])
                if items:
                    markdown_content += "### Anti-Patterns Addressed\n\n"
                    
                    for i, item in enumerate(items, 1):
                        antipattern_name = item.get('antipattern_name', 'Unknown Pattern')
                        markdown_content += f"#### {i}. {antipattern_name}\n\n"
                        
                        # Loop through all keys in the item (except refactored_code and antipattern_name)
                        for key, value in item.items():
                            if key not in ['antipattern_name', 'refactored_code'] and value:
                                # Convert snake_case to Title Case for heading
                                heading = key.replace('_', ' ').title()
                                markdown_content += f"**{heading}:** {value}\n\n"
                        
                        markdown_content += "---\n\n"
                
                # Handle all other sections dynamically
                for key, value in explanation_results.items():
                    if key != 'items' and value:  # Skip items (already processed) and empty values
                        # Convert snake_case to Title Case for section heading
                        section_title = key.replace('_', ' ').title()
                        markdown_content += f"### {section_title}\n\n"
                        
                        if isinstance(value, list):
                            # Handle list items
                            for item in value:
                                markdown_content += f"- {item}\n"
                            markdown_content += "\n"
                        else:
                            # Handle single values
                            markdown_content += f"{value}\n\n"
            else:
                # Fallback to JSON if format is unexpected
                markdown_content += f"```json\n{json.dumps(explanation_results, indent=2, default=str)}\n```\n\n"
        else:
            markdown_content += "No explanation generated.\n\n"
        
        # Add side-by-side code comparison
        markdown_content += "---\n\n## Code Comparison\n\n"
        
        original_code = final_state.get('code', '')
        refactored_code = final_state.get('refactored_code', '')
        
        if original_code or refactored_code:
            markdown_content += "### Original Code vs Refactored Code\n\n"
            markdown_content += '<div style="display: flex; gap: 20px;">\n\n'
            
            # Original code column
            markdown_content += '<div style="flex: 1;">\n\n'
            markdown_content += "**Original Code:**\n\n"
            if original_code:
                markdown_content += f"```java\n{original_code}\n```\n\n"
            else:
                markdown_content += "*No original code available*\n\n"
            markdown_content += '</div>\n\n'
            
            # Refactored code column
            markdown_content += '<div style="flex: 1;">\n\n'
            markdown_content += "**Refactored Code:**\n\n"
            if refactored_code:
                markdown_content += f"```java\n{refactored_code}\n```\n\n"
            else:
                markdown_content += "*No refactored code generated*\n\n"
            markdown_content += '</div>\n\n'
            
            markdown_content += '</div>\n\n'
            
            # Add code comparison summary
            if original_code and refactored_code:
                original_lines = len(original_code.splitlines())
                refactored_lines = len(refactored_code.splitlines())
                line_change = refactored_lines - original_lines
                line_change_str = f"+{line_change}" if line_change > 0 else str(line_change)
                
                markdown_content += f"**Code Metrics:**\n"
                markdown_content += f"- Original Loc: {original_lines}\n"
                markdown_content += f"- Refactored Loc: {refactored_lines}\n"
                markdown_content += f"- LoC change: {line_change_str}\n\n"
        else:
            markdown_content += "No code available for comparison.\n\n"
        
        markdown_content += f"---\n\n*Generated by AntiPattern Remediator Tool using {settings.LLM_MODEL}*\n"        
        # Save to markdown file
        with open(results_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(Fore.CYAN + f"Intermediate results saved: {results_file_path}" + Style.RESET_ALL)
        return True
        
    except Exception as e:
        print(Fore.RED + f"Error saving intermediate results for {file_path}: {e}" + Style.RESET_ALL)
        return False


def create_processing_summary(processed_files: list, backup_info: dict, results_dir: str = "../processing_results") -> str:
    """Create a comprehensive summary report of the processing session."""
    try:
        results_path = Path(results_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = results_path / f"processing_summary_{timestamp}.json"
        
        # Categorize results
        successful_refactoring = [f for f in processed_files if f['status'] == 'success']
        no_refactoring_needed = [f for f in processed_files if f['status'] == 'no_refactoring']
        files_with_antipatterns = [f for f in processed_files if f.get('antipatterns_found', False)]
        total_antipatterns = sum(f.get('antipatterns_count', 0) for f in processed_files)
        
        summary_data = {
            'processing_session': {
                'timestamp': timestamp,
                'backup_info': backup_info,
                'total_files_processed': len(processed_files),
                'successful_refactoring': len(successful_refactoring),
                'no_refactoring_needed': len(no_refactoring_needed),
                'files_with_antipatterns_detected': len(files_with_antipatterns),
                'total_antipatterns_found': total_antipatterns
            },
            'detailed_results': {
                'successful_refactoring': successful_refactoring,
                'no_refactoring_needed': no_refactoring_needed,
            },
            'statistics': {
                'refactoring_success_rate': len(successful_refactoring) / len(processed_files) * 100 if processed_files else 0,
                'antipattern_detection_rate': len(files_with_antipatterns) / len(processed_files) * 100 if processed_files else 0,
                'average_code_reviews': sum(f.get('code_review_times', 0) for f in processed_files) / len(processed_files) if processed_files else 0,
                'total_antipatterns_found': total_antipatterns,
                'average_antipatterns_per_file': total_antipatterns / len(processed_files) if processed_files else 0
            }
        }
        
        # Save summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(Fore.CYAN + f"Processing summary saved: {summary_file}" + Style.RESET_ALL)
        return str(summary_file)
        
    except Exception as e:
        print(Fore.RED + f"Error creating processing summary: {e}" + Style.RESET_ALL)
        return None
