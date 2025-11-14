"""Utility modules for Tableau Data Assistant"""

# Legacy utilities (if they exist)
try:
    from .logger import get_logger, log_function_call, log_execution_time
except ImportError:
    pass

try:
    from .cache_manager import get_cache_manager, cached
except ImportError:
    pass

try:
    from .security import get_security_manager, validate_file, sanitize_filename
except ImportError:
    pass

try:
    from .data_quality import calculate_quality_score, DataQualityScorer
except ImportError:
    pass

try:
    from .statistics import perform_statistical_analysis, StatisticalAnalyzer
except ImportError:
    pass

# New responsible AI modules
from .validation import (
    DataValidator,
    ValidationResult,
    validate_for_tableau,
    generate_validation_report
)

from .cleaning import (
    DataCleaner,
    CleaningReport,
    generate_cleaning_summary
)

from .privacy import (
    PIIDetector,
    PIIMasker,
    DataMinimizer,
    PIIReport,
    mask_pii_dataframe
)

from .anomaly_detection import (
    IQRAnomalyDetector,
    ZScoreAnomalyDetector,
    IsolationForestDetector,
    AnomalyDetectorEnsemble,
    AnomalyReport,
    detect_anomalies
)

from .logging_utils import (
    AuditLogger,
    SessionLogger,
    PIISafeFormatter,
    setup_application_logging,
    generate_session_id
)

from .screenshot_analysis import (
    DashboardScreenshotAnalyzer,
    ScreenshotAnalysis,
    analyze_dashboard_screenshot
)

from .sql_utils import (
    TableauSQLGenerator,
    SQLOptimizer,
    TableauCustomSQLHelper,
    SQLOptimizationReport,
    optimize_sql_for_tableau,
    generate_tableau_sql
)

from .trust_scoring import (
    TrustScore,
    DatasetTrustReport,
    TrustScoreCalculator,
    TrustScoreStore,
    TrustHeatmapGenerator,
    calculate_trust_scores,
    export_trust_scores_for_tableau
)

from .data_contract import (
    FieldContract,
    DataContract,
    DataContractAnalyzer,
    DataContractGenerator,
    generate_data_contract,
    export_data_contract_proposal
)

from .story_coach import (
    StoryElement,
    StoryArc,
    StoryRecommendation,
    NarrativeReport,
    DashboardStoryCoach,
    analyze_dashboard_story,
    export_story_report
)

__all__ = [
    # Validation
    'DataValidator',
    'ValidationResult',
    'validate_for_tableau',
    'generate_validation_report',

    # Cleaning
    'DataCleaner',
    'CleaningReport',
    'generate_cleaning_summary',

    # Privacy
    'PIIDetector',
    'PIIMasker',
    'DataMinimizer',
    'PIIReport',
    'mask_pii_dataframe',

    # Anomaly Detection
    'IQRAnomalyDetector',
    'ZScoreAnomalyDetector',
    'IsolationForestDetector',
    'AnomalyDetectorEnsemble',
    'AnomalyReport',
    'detect_anomalies',

    # Logging
    'AuditLogger',
    'SessionLogger',
    'PIISafeFormatter',
    'setup_application_logging',
    'generate_session_id',

    # Screenshot Analysis
    'DashboardScreenshotAnalyzer',
    'ScreenshotAnalysis',
    'analyze_dashboard_screenshot',

    # SQL Utilities
    'TableauSQLGenerator',
    'SQLOptimizer',
    'TableauCustomSQLHelper',
    'SQLOptimizationReport',
    'optimize_sql_for_tableau',
    'generate_tableau_sql',

    # Trust Scoring
    'TrustScore',
    'DatasetTrustReport',
    'TrustScoreCalculator',
    'TrustScoreStore',
    'TrustHeatmapGenerator',
    'calculate_trust_scores',
    'export_trust_scores_for_tableau',

    # Data Contract
    'FieldContract',
    'DataContract',
    'DataContractAnalyzer',
    'DataContractGenerator',
    'generate_data_contract',
    'export_data_contract_proposal',

    # Story Coach
    'StoryElement',
    'StoryArc',
    'StoryRecommendation',
    'NarrativeReport',
    'DashboardStoryCoach',
    'analyze_dashboard_story',
    'export_story_report',
]
