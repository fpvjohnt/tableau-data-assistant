"""Utility modules for Tableau Data Assistant."""

from importlib import import_module
from typing import Dict, Tuple

from .cache_manager import cached, get_cache_manager
from .data_quality import DataQualityScorer, calculate_quality_score
from .logger import get_logger, log_execution_time, log_function_call

_LAZY_IMPORTS: Dict[str, Tuple[str, str]] = {
    'get_security_manager': ('utils.security', 'get_security_manager'),
    'validate_file': ('utils.security', 'validate_file'),
    'sanitize_filename': ('utils.security', 'sanitize_filename'),
    'perform_statistical_analysis': ('utils.statistics', 'perform_statistical_analysis'),
    'StatisticalAnalyzer': ('utils.statistics', 'StatisticalAnalyzer'),
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_name, attribute = _LAZY_IMPORTS[name]
        module = import_module(module_name)
        value = getattr(module, attribute)
        globals()[name] = value
        return value
    raise AttributeError(name)


__all__ = [
    'cached',
    'calculate_quality_score',
    'DataQualityScorer',
    'get_cache_manager',
    'get_logger',
    'log_execution_time',
    'log_function_call',
    'perform_statistical_analysis',
    'sanitize_filename',
    'StatisticalAnalyzer',
    'validate_file',
    'get_security_manager',
]
