"""
JaCoCo Core Module - Clean, Generalized Coverage Analysis

This module provides core functionality for JaCoCo coverage analysis.
"""

import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JaCoCoAnalyzer:
    """Main class for JaCoCo coverage analysis."""
    
    def __init__(self, timeout: int = 300, verbose: bool = False):
        """
        Initialize JaCoCo analyzer.
        
        Args:
            timeout: Build timeout in seconds
            verbose: Enable verbose logging
        """
        self.timeout = timeout
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
    
    
    def _find_modules(self, repo_path: Path) -> List[Path]:
        """Find all Maven/Gradle modules in the repository."""
        modules = []
        
        # Add root if it has build files
        if self._has_build_files(repo_path):
            modules.append(repo_path)
        
        # Find all subdirectory modules
        for pom_file in repo_path.rglob("pom.xml"):
            module_dir = pom_file.parent
            if module_dir != repo_path and self._has_java_files(module_dir):
                modules.append(module_dir)
        
        for gradle_file in repo_path.rglob("build.gradle*"):
            module_dir = gradle_file.parent
            if module_dir != repo_path and self._has_java_files(module_dir):
                modules.append(module_dir)
        
        return list(set(modules))  # Remove duplicates
    
    def _has_build_files(self, path: Path) -> bool:
        """Check if directory has build files."""
        return (path / "pom.xml").exists() or (path / "build.gradle").exists() or (path / "build.gradle.kts").exists()
    
    def _has_java_files(self, path: Path) -> bool:
        """Check if directory contains Java files."""
        return any(path.rglob("*.java"))
    
    def _get_module_name(self, repo_path: Path, module_path: Path) -> str:
        """Generate a readable module name."""
        if module_path == repo_path:
            return repo_path.name
        else:
            relative_path = module_path.relative_to(repo_path)
            return str(relative_path).replace(os.sep, "/")
    
    def _run_jacoco_for_module(self, module_path: Path, force: bool) -> bool:
        """Run JaCoCo analysis for a single module."""
        jacoco_xml = module_path / "target" / "site" / "jacoco" / "jacoco.xml"
        
        # Skip if report exists and not forcing
        if jacoco_xml.exists() and not force:
            logger.debug(f"JaCoCo report already exists for {module_path.name}")
            return True
        
        # Determine build system and setup JaCoCo if needed
        if (module_path / "pom.xml").exists():
            self._setup_jacoco_maven(module_path)
            return self._run_maven_jacoco(module_path)
        elif (module_path / "build.gradle").exists() or (module_path / "build.gradle.kts").exists():
            self._setup_jacoco_gradle(module_path)
            return self._run_gradle_jacoco(module_path)
        else:
            logger.warning(f"No build file found in {module_path}")
            return False
    
    def _setup_jacoco_maven(self, module_path: Path) -> bool:
        """Setup JaCoCo plugin in Maven pom.xml if not already configured."""
        pom_file = module_path / "pom.xml"
        
        try:
            content = pom_file.read_text(encoding='utf-8')
            
            # Check if JaCoCo is already configured
            if 'jacoco' in content:
                logger.debug(f"JaCoCo already configured in {module_path.name}")
                return True
            
            # JaCoCo plugin configuration
            jacoco_plugin = """
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.11</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>prepare-agent</goal>
                        </goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals>
                            <goal>report</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>"""
            
            # Look for <build><plugins> section specifically
            if '<build>' in content and '<plugins>' in content:
                # Find the build plugins section and add JaCoCo
                build_start = content.find('<build>')
                build_end = content.find('</build>', build_start)
                build_section = content[build_start:build_end + 8]
                
                if '<plugins>' in build_section:
                    # Insert into existing build plugins
                    plugins_start = content.find('<plugins>', build_start)
                    insertion_point = plugins_start + len('<plugins>')
                    content = content[:insertion_point] + jacoco_plugin + content[insertion_point:]
                else:
                    # Add plugins section to existing build
                    plugins_section = f"\n        <plugins>{jacoco_plugin}\n        </plugins>\n    "
                    build_close = content.find('</build>')
                    content = content[:build_close] + plugins_section + content[build_close:]
            else:
                # Add entire build section with JaCoCo plugin
                build_section = f"""
    <build>
        <plugins>{jacoco_plugin}
        </plugins>
    </build>"""
                # Insert before closing project tag
                project_close = content.rfind('</project>')
                content = content[:project_close] + build_section + '\n' + content[project_close:]
            
            # Write updated pom.xml
            pom_file.write_text(content, encoding='utf-8')
            logger.debug(f"JaCoCo plugin added to {module_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup JaCoCo in Maven: {e}")
            return False
    
    def _setup_jacoco_gradle(self, module_path: Path) -> bool:
        """Setup JaCoCo plugin in Gradle build file if not already configured."""
        # Try build.gradle first, then build.gradle.kts
        build_files = [module_path / "build.gradle", module_path / "build.gradle.kts"]
        build_file = next((f for f in build_files if f.exists()), None)
        
        if not build_file:
            logger.warning(f"No Gradle build file found in {module_path}")
            return False
        
        try:
            content = build_file.read_text(encoding='utf-8')
            
            # Check if JaCoCo is already configured
            if 'jacoco' in content.lower():
                logger.debug(f"JaCoCo already configured in {module_path.name}")
                return True
            
            # Add JaCoCo configuration
            jacoco_config = """
apply plugin: 'jacoco'

jacoco {
    toolVersion = "0.8.11"
}

jacocoTestReport {
    reports {
        xml.required = true
        html.required = true
    }
}

test.finalizedBy jacocoTestReport
"""
            
            # Append JaCoCo configuration to the file
            content = content + jacoco_config
            
            # Write updated build file
            build_file.write_text(content, encoding='utf-8')
            logger.debug(f"JaCoCo plugin added to {module_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup JaCoCo in Gradle: {e}")
            return False
    
    def _run_maven_jacoco(self, module_path: Path) -> bool:
        """Run Maven JaCoCo analysis."""
        # Use .cmd extension for Windows compatibility
        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"

        strategies = [
            f"{mvn_cmd} clean test jacoco:report -q",
            f"{mvn_cmd} clean compile test-compile jacoco:report -DskipTests=true -q",
            f"{mvn_cmd} clean test jacoco:report -DfailIfNoTests=false -q",
        ]
        
        for strategy in strategies:
            try:
                logger.debug(f"Trying: {strategy}")
                result = subprocess.run(
                    strategy.split(),
                    cwd=module_path,
                    timeout=self.timeout,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "MAVEN_OPTS": "-Xmx2g"}
                )
                
                if result.returncode == 0:
                    jacoco_xml = module_path / "target" / "site" / "jacoco" / "jacoco.xml"
                    if jacoco_xml.exists():
                        logger.debug(f"Maven JaCoCo successful for {module_path.name}")
                        return True
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Maven timeout for {module_path.name}")
            except Exception as e:
                logger.debug(f"Maven strategy failed: {e}")
                continue
        
        return False
    
    def _run_gradle_jacoco(self, module_path: Path) -> bool:
        """Run Gradle JaCoCo analysis."""
        # Use .bat extension for Windows compatibility
        gradlew_cmd = "./gradlew.bat" if os.name == "nt" else "./gradlew"
        gradle_cmd = "gradle.bat" if os.name == "nt" else "gradle"
        
        strategies = [
            f"{gradlew_cmd} test jacocoTestReport",
            f"{gradle_cmd} test jacocoTestReport",
        ]
        
        for strategy in strategies:
            try:
                logger.debug(f"Trying: {strategy}")
                result = subprocess.run(
                    strategy.split(),
                    cwd=module_path,
                    timeout=self.timeout,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Check for Gradle JaCoCo report
                    report_paths = [
                        module_path / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml",
                        module_path / "build" / "jacoco" / "jacoco.xml"
                    ]
                    
                    if any(path.exists() for path in report_paths):
                        logger.debug(f"Gradle JaCoCo successful for {module_path.name}")
                        return True
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Gradle timeout for {module_path.name}")
            except Exception as e:
                logger.debug(f"Gradle strategy failed: {e}")
                continue
        
        return False
    
    def _extract_100_percent_files(self, module_path: Path, repo_path: Path) -> List[str]:
        """Extract files with 100% line coverage from JaCoCo XML report."""
        # Check Maven location first
        jacoco_xml = module_path / "target" / "site" / "jacoco" / "jacoco.xml"
        if not jacoco_xml.exists():
            # Check Gradle locations
            gradle_paths = [
                module_path / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml",
                module_path / "build" / "jacoco" / "jacoco.xml"
            ]
            jacoco_xml = next((path for path in gradle_paths if path.exists()), None)
        
        if not jacoco_xml:
            return []
        
        try:
            tree = ET.parse(jacoco_xml)
            root = tree.getroot()
            
            fully_covered_files = []
            
            # Parse XML structure: report > package > sourcefile
            for package in root.findall('.//package'):
                package_name = package.get('name', '').replace('/', '.')
                
                for sourcefile in package.findall('sourcefile'):
                    filename = sourcefile.get('name')
                    
                    if not filename or not filename.endswith('.java'):
                        continue
                    
                    # Check line coverage
                    line_counter = sourcefile.find(".//counter[@type='LINE']")
                    if line_counter is not None:
                        missed = int(line_counter.get('missed', 0))
                        covered = int(line_counter.get('covered', 0))
                        
                        if covered > 0 and missed == 0:  # 100% coverage
                            # Construct full file path
                            java_file_path = self._find_java_file(
                                module_path, package_name, filename
                            )
                            
                            if java_file_path:
                                fully_covered_files.append(str(java_file_path))
            
            return fully_covered_files
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse JaCoCo XML {jacoco_xml}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting coverage data: {e}")
            return []
    
    def _find_java_file(self, module_path: Path, package_name: str, filename: str) -> Optional[Path]:
        """Find the actual Java file path given package and filename."""
        # Convert package name to directory path
        package_path = package_name.replace('.', os.sep)
        
        # Search in common Maven/Gradle source directories
        source_dirs = [
            module_path / "src" / "main" / "java",
            module_path / "src" / "test" / "java",
            module_path / "src",
        ]
        
        for src_dir in source_dirs:
            if package_path:
                full_path = src_dir / package_path / filename
            else:
                full_path = src_dir / filename
            
            if full_path.exists():
                return full_path
        
        # Fallback: search for filename in the entire module
        for java_file in module_path.rglob(filename):
            return java_file
        
        return None

    def analyze_repository(self, repo_path: str, force: bool = False) -> Dict[str, List[str]]:
        """
        Analyze a repository and return files with 100% coverage.
        
        Args:
            repo_path: Path to the repository
            force: Force re-analysis even if reports exist
            
        Returns:
            Dictionary mapping module names to lists of fully covered files
        """
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return {}
        
        if not self._has_java_files(repo_path):
            logger.info(f"No Java files found in {repo_path}")
            return {}
        
        # Find all modules with build files
        modules = self._find_modules(repo_path)
        logger.info(f"Found {len(modules)} modules in {repo_path.name}")
        
        results = {}
        
        for module_path in modules:
            module_name = self._get_module_name(repo_path, module_path)
            logger.info(f"Processing module: {module_name}")
            
            if self._run_jacoco_for_module(module_path, force):
                covered_files = self._extract_100_percent_files(module_path, repo_path)
                if covered_files:
                    results[module_name] = covered_files
                    logger.info(f"Found {len(covered_files)} files with 100% coverage in {module_name}")
            else:
                logger.warning(f"JaCoCo analysis failed for module: {module_name}")
        
        return results


def analyze_repositories(clone_root: str, **kwargs) -> Dict[str, Dict[str, List[str]]]:
    """
    Analyze all repositories in a clone directory.
    
    Args:
        clone_root: Root directory containing cloned repositories
        **kwargs: Additional arguments passed to JaCoCoAnalyzer
        
    Returns:
        Dictionary mapping repository names to their coverage results
    """
    clone_path = Path(clone_root)
    if not clone_path.exists():
        logger.error(f"Clone root does not exist: {clone_root}")
        return {}
    
    analyzer = JaCoCoAnalyzer(**kwargs)
    results = {}
    
    for repo_dir in clone_path.iterdir():
        if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
            logger.info(f"Analyzing repository: {repo_dir.name}")
            repo_results = analyzer.analyze_repository(str(repo_dir))
            if repo_results:
                results[repo_dir.name] = repo_results
    
    return results


def export_results(results: Dict[str, Dict[str, List[str]]], output_dir: str = "jacoco_results") -> str:
    """
    Export coverage analysis results.
    
    Args:
        results: Coverage analysis results
        output_dir: Output directory for results
        
    Returns:
        Path to the combined file list
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    all_files = []
    
    # Export individual repository results
    for repo_name, repo_results in results.items():
        repo_files = []
        for module_name, files in repo_results.items():
            repo_files.extend(files)
        
        if repo_files:
            repo_file = output_path / f"{repo_name}_100_percent_coverage.txt"
            with open(repo_file, 'w') as f:
                for file_path in sorted(repo_files):
                    f.write(f"{file_path}\n")
            
            all_files.extend(repo_files)
            logger.info(f"Exported {len(repo_files)} files for {repo_name}")
    
    # Export combined results
    if all_files:
        combined_file = output_path / "all_100_percent_coverage_files.txt"
        with open(combined_file, 'w') as f:
            for file_path in sorted(set(all_files)):  # Remove duplicates
                f.write(f"{file_path}\n")
        
        logger.info(f"Exported {len(set(all_files))} total files with 100% coverage")
        return str(combined_file)
    else:
        logger.info("No files with 100% coverage found across all repositories")
        return ""
