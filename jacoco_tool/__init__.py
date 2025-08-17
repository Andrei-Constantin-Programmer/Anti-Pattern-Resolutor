"""
JaCoCo Tool - Clean Coverage Analysis
=====================================

This module provides streamlined JaCoCo coverage analysis functionality.
"""

from .core import JaCoCoAnalyzer, analyze_repositories, export_results

__all__ = ['JaCoCoAnalyzer', 'analyze_repositories', 'export_results']