import json, os
from pathlib import Path
import lizard
import re

def calculate_nesting_depth(source_code: str, start_line: int, end_line: int) -> int:
    """
    Calculate the maximum nesting depth for a function by counting braces and control structures.
    """
    lines = source_code.split('\n')
    function_lines = lines[start_line-1:end_line]
    
    max_depth = 0
    current_depth = 0
    
    for line in function_lines:
        # Remove string literals and comments to avoid false positives
        cleaned_line = re.sub(r'\".*?\"', '', line)  # Remove string literals
        cleaned_line = re.sub(r'//.*', '', cleaned_line)  # Remove line comments
        
        # Count opening braces and control structures that increase nesting
        # Note: This is a simplified approach and might not catch all cases
        for char in cleaned_line:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
    
    return max_depth

def _process_lizard_result(lizard_result, source_code: str, filename: str, source_type: str = "file"):
    """
    Helper function to process lizard analysis results and extract metrics.
    """
    functions = []
    for fn in lizard_result.function_list:
        
        # Calculate nesting depth
        nesting_depth = calculate_nesting_depth(source_code, fn.start_line, fn.end_line)
        
        functions.append({
            "name": fn.long_name,                 
            "start_line": fn.start_line,
            "end_line": fn.end_line,
            "nloc": fn.nloc,                      # SLOC (non-comment LOC) for the function
            "cyclomatic_complexity": fn.cyclomatic_complexity,
            # Store all nesting metrics for debugging/analysis
            "max_nesting_depth": nesting_depth        
            })
    
    file_metrics = {
        "file": filename,
        "file_sloc_nloc": lizard_result.nloc,              # file-level SLOC (non-comment LOC)
        "total_functions": len(functions),
        "avg_cc": round(sum(f["cyclomatic_complexity"] for f in functions)/len(functions), 2) if functions else 0.0,
        "max_cc": max((f["cyclomatic_complexity"] for f in functions), default=0),
        "max_nd_in_file": max((f["effective_nesting_depth"] for f in functions), default=0),
        "functions": functions,
    }
    
    # Add source type indicator for string analysis
    if source_type == "string":
        file_metrics["source_type"] = "string"
    
    return file_metrics

def analyze_file(path: Path):
    """Analyze a Java file from file path."""
    # Read the source code for custom nesting analysis
    with open(path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Analyze with lizard
    lizard_result = lizard.analyze_file(str(path))
    
    # Process the results using shared helper
    return _process_lizard_result(lizard_result, source_code, str(path), "file")

def analyze_source_code(source_code: str, filename: str = "AnalyzedCode.java"):
    """Analyze Java source code directly from string."""
    # Analyze with lizard
    lizard_result = lizard.analyze_file.analyze_source_code(filename, source_code)
    
    # Process the results using shared helper
    return _process_lizard_result(lizard_result, source_code, filename, "string")

def compare_code_metrics(original_metrics, refactored_metrics, filename_prefix: str = "Code"):
    """Compare metrics between original and refactored code."""

    comparison = {
        "improvements": {
            "sloc_reduction": original_metrics["file_sloc_nloc"] - refactored_metrics["file_sloc_nloc"],
            "function_count_change": refactored_metrics["total_functions"] - original_metrics["total_functions"],
            "avg_cc_improvement": original_metrics["avg_cc"] - refactored_metrics["avg_cc"],
            "max_cc_reduction": original_metrics["max_cc"] - refactored_metrics["max_cc"],
            "max_nesting_reduction": original_metrics["max_nd_in_file"] - refactored_metrics["max_nd_in_file"]
        }
    }
    return comparison

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("target", help="Path to a .java file or a directory")
    p.add_argument("--json", action="store_true", help="Print JSON")
    args = p.parse_args()

    results = []
    target = Path(args.target)
    if target.is_dir():
        for f in target.rglob("*.java"):
            results.append(analyze_file(f))
    else:
        results.append(analyze_file(target))

    print(json.dumps(results, indent=2) if args.json else results)