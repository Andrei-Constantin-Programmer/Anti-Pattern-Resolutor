import json, os
from pathlib import Path
import lizard
import re
import javalang

def calculate_nesting_depth(code: str) -> int:
    """
    Calculate the maximum nesting depth for a function.
    """
    tree = javalang.parse.parse(code)

    max_depth = 0

    def walk(node, depth=0):
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        if isinstance(node, (javalang.tree.IfStatement,
                             javalang.tree.ForStatement,
                             javalang.tree.WhileStatement,
                             javalang.tree.TryStatement,
                             javalang.tree.SwitchStatement)):
            depth += 1
        for child in getattr(node, 'children', []):
            if isinstance(child, (list, tuple)):
                for c in child:
                    if isinstance(c, javalang.ast.Node):
                        walk(c, depth)
            elif isinstance(child, javalang.ast.Node):
                walk(child, depth)

    walk(tree)
    return max_depth


def _process_lizard_result(lizard_result, source_code: str, filename: str, source_type: str = "file"):
    """
    Helper function to process lizard analysis results and extract metrics.
    """
    functions = []
    
    for fn in lizard_result.function_list:        

        functions.append({
            "name": fn.long_name,                 
            "start_line": fn.start_line,
            "end_line": fn.end_line,
            "nloc": fn.nloc,                      # SLOC (non-comment LOC) for the function
            "cyclomatic_complexity": fn.cyclomatic_complexity    
            })
        
    # Calculate nesting depth using brace counting approach
    nesting_depth = calculate_nesting_depth(source_code)

    file_metrics = {
        "file": filename,
        "file_sloc_nloc": lizard_result.nloc,              # file-level SLOC (non-comment LOC)
        "total_functions": len(functions),
        "avg_cc": round(sum(f["cyclomatic_complexity"] for f in functions)/len(functions), 2) if functions else 0.0,
        "max_cc": max((f["cyclomatic_complexity"] for f in functions), default=0),
        "max_nd_in_file": nesting_depth,
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
    p.add_argument("--output", "-o", help="Output JSON file path", default="metrics_results.json")
    args = p.parse_args()

    results = []
    target = Path(args.target)
    if target.is_dir():
        for f in target.rglob("*.java"):
            results.append(analyze_file(f))
    else:
        results.append(analyze_file(target))

    # Save results to JSON file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Metrics analysis complete. Results saved to: {output_path}")
    print(f"Analyzed {len(results)} file(s)")
    
    # Print summary
    if results:
        total_functions = sum(r.get('total_functions', 0) for r in results)
        avg_complexity = sum(r.get('avg_cc', 0) for r in results) / len(results)
        print(f"Total functions analyzed: {total_functions}")
        print(f"Average complexity across files: {avg_complexity:.2f}")