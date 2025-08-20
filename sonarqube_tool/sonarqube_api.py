import os
import json
import requests
from typing import Optional, Dict

SONARQUBE_URL = "http://localhost:9000"
PAGE_SIZE = 500

class SonarQubeAPI:
    def __init__(self, base_url: str = SONARQUBE_URL, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token or os.getenv('SONARQUBE_TOKEN')
        
        if not self.token:
            raise ValueError("SonarQube token is required. Provide it as parameter or set SONARQUBE_TOKEN environment variable.")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _get_issues(self, component_key: str) -> Dict:
        url = f"{self.base_url}/api/issues/search"
        all_issues = []
        page = 1
        
        while True:
            params = {
                'componentKeys': component_key,
                'ps': PAGE_SIZE,
                'p': page
            }
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                page_issues = data.get('issues', [])
                all_issues.extend(page_issues)
                
                if len(page_issues) == 0:
                    break    
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error calling SonarQube API: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response text: {e.response.text}")
                raise
        return {
            'total': len(all_issues),
            'issues': all_issues
        }
    
    def _get_rule_details(self, rule_key: str) -> Dict:
        url = f"{self.base_url}/api/rules/show"
        params = {
           'key': rule_key
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling SonarQube API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
        return data
    
    def is_scan_successful(self, project_key: str) -> bool:
        url = f"{self.base_url}/api/ce/component"
        params = {
            'component': project_key
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            info = data.get('current', {})
            result = info.get('status', '') == 'SUCCESS'
            return result
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def get_issues_for_file(self, project_key: str, file_path: str) -> Dict:
        component_key = f"{project_key}:{file_path}"
        return self._get_issues(component_key)
    
    def get_all_issues(self, project_key: str) -> Dict:
        return self._get_issues(project_key)

    def get_rules_and_fix_method(self, rule_key: str) -> Dict:
        data = self._get_rule_details(rule_key)
        result = {}
        rule = data.get('rule', {})
        if rule:
            result['rule_key'] = rule.get('key', '')
            result['rule_name'] = rule.get('name', '')
            result['severity'] = rule.get('severity', '')
            result['type'] = rule.get('type', '')
            
            description_sections = rule.get('descriptionSections', [])
            for section in description_sections:
                section_key = section.get('key', '')
                section_content = section.get('content', '')
                result[section_key] = section_content
        return result

    def print_all_issues(self, project_key: str) -> None:
        try:
            issues_data = self.get_all_issues(project_key)
            issues = issues_data.get('issues', [])
            total = issues_data.get('total', 0)
            
            severity_count = {}
            for issue in issues:
                impacts = issue.get('impacts', [])
                if impacts and len(impacts) > 0:
                    severity = impacts[0].get('severity', 'UNKNOWN')
                    severity_count[severity] = severity_count.get(severity, 0) + 1
            print(f"Total issues: {total}")
            for severity, count in sorted(severity_count.items()):
                print(f"{severity}: {count}")
        except Exception as e:
            print(f"Error: {e}")

    def print_file_issues(self, project_key: str, file_path: str) -> None:
        try:
            issues_data = self.get_issues_for_file(project_key, file_path)
            issues = issues_data.get('issues', [])
            
            if issues:
                # Show only first 3 issues
                for i, issue in enumerate(issues[:3], 1):
                    print(f"{i}. {issue.get('message', 'No message')}")
                    print(f"   Rule: {issue.get('rule', 'Unknown')}")
                    
                    impacts = issue.get('impacts', [])
                    severity = 'Unknown'
                    if impacts and len(impacts) > 0:
                        severity = impacts[0].get('severity', 'Unknown')
                    
                    print(f"   Severity: {severity}")
                    print(f"   Type: {issue.get('type', 'Unknown')}")
                    
                    if 'textRange' in issue:
                        line = issue['textRange'].get('startLine', 'Unknown')
                        print(f"   Line: {line}")
                    print()
                # Show remaining count if there are more than 3 issues
                if len(issues) > 3:
                    remaining = len(issues) - 3
                    print(f"... and {remaining} more issues not shown")
            else:
                print("No issues found")
        except Exception as e:
            print(f"Error: {e}")

    def save_all_issues(self, project_key: str, file_path: str) -> None:
        try:
            issues_data = self.get_all_issues(project_key)
            with open(file_path, 'w') as f:
                json.dump(issues_data, f, indent=4)
            print(f"All issues saved to {file_path}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    api = SonarQubeAPI()
    project_key = "commons-collections"
    file_path = "src/main/java/org/apache/commons/collections4/map/AbstractHashedMap.java"
    rule_key_1 = "java:S2160"
    rule_key_2 = "java:S1117"
    rule_key_3 = "java:S5993"
    print(f"Checking scan success for project {project_key}: {api.is_scan_successful(project_key)}")

    print("Project issues summary:")
    api.print_all_issues(project_key)
    
    print(f"\nFile issues details:")
    api.print_file_issues(project_key, file_path)

    print(f"\nRule details:")
    print(api.get_rules_and_fix_method(rule_key_3))
