import re
from colorama import Fore, Style

class ConditionalEdges:
    def __init__(self):
        pass

    def code_review_condition(self, state):
        """
        Determine the next step based on code review results.
        Uses regex to match the first line decision with flexibility.
        """
        if state["code_review_times"] > 2:
            print(Fore.GREEN + "Code has been reviewed twice, defaulting to pass" + Style.RESET_ALL)
            return "pass"
        review_results = state.get("code_review_results", "")
        
        if not review_results:
            print(Fore.YELLOW + "Warning: No code review results found, defaulting to transform_code" + Style.RESET_ALL)
            return "transform_code"
        
        # Extract the first line which contains the decision
        lines = review_results.strip().split('\n')
        if not lines:
            print(Fore.YELLOW + "Warning: Empty code review results, defaulting to transform_code" + Style.RESET_ALL)
            return "transform_code"
            
        first_line = lines[0].strip()
        print(f"Code review first line: '{first_line}'")
        
        # Use regex patterns to match decisions
        if re.search(r'\*?pass\*?', first_line, re.IGNORECASE):
            print(Fore.GREEN + "Decision: pass" + Style.RESET_ALL)
            return "pass"
        elif re.search(r'\*?fail\*?', first_line, re.IGNORECASE):
            print(Fore.RED + "Decision: code_reviewer -> code_transformer" + Style.RESET_ALL)
            return "transform_code"
        else:
            print(Fore.YELLOW + "Decision: defaulting to transform_code" + Style.RESET_ALL)
            return "transform_code"