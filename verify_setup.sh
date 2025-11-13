#!/bin/bash

echo "=========================================="
echo "Tableau Data Assistant - Setup Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo "   $PYTHON_VERSION"

# Check virtual environment
echo ""
echo "2. Checking virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "   ${GREEN}✓${NC} Virtual environment active: $VIRTUAL_ENV"
else
    echo -e "   ${YELLOW}⚠${NC} Virtual environment not active"
    echo "   Run: source venv/bin/activate"
fi

# Check directory structure
echo ""
echo "3. Checking project structure..."
REQUIRED_DIRS=("config" "utils" "tests" "cache" "sessions" "exports" "logs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "   ${GREEN}✓${NC} $dir/"
    else
        echo -e "   ${RED}✗${NC} $dir/ (missing)"
    fi
done

# Check utility modules
echo ""
echo "4. Checking utility modules..."
UTIL_MODULES=("logger.py" "cache_manager.py" "security.py" "data_quality.py" "statistics.py" "session_manager.py" "report_generator.py" "visualizations.py")
for module in "${UTIL_MODULES[@]}"; do
    if [ -f "utils/$module" ]; then
        SIZE=$(ls -lh "utils/$module" | awk '{print $5}')
        echo -e "   ${GREEN}✓${NC} utils/$module ($SIZE)"
    else
        echo -e "   ${RED}✗${NC} utils/$module (missing)"
    fi
done

# Check documentation
echo ""
echo "5. Checking documentation..."
DOCS=("IMPLEMENTATION_GUIDE.md" "QUICK_START.md" "README_ENHANCEMENTS.md" "PROJECT_SUMMARY.txt")
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "   ${GREEN}✓${NC} $doc"
    else
        echo -e "   ${RED}✗${NC} $doc (missing)"
    fi
done

# Try importing modules
echo ""
echo "6. Testing module imports..."
python -c "
try:
    from utils import get_logger
    print('   ✓ logger')
except Exception as e:
    print(f'   ✗ logger: {e}')

try:
    from utils import get_cache_manager
    print('   ✓ cache_manager')
except Exception as e:
    print(f'   ✗ cache_manager: {e}')

try:
    from utils import calculate_quality_score
    print('   ✓ data_quality')
except Exception as e:
    print(f'   ✗ data_quality: {e}')

try:
    from utils import perform_statistical_analysis
    print('   ✓ statistics')
except Exception as e:
    print(f'   ✗ statistics: {e}')

try:
    from utils import get_session_manager
    print('   ✓ session_manager')
except Exception as e:
    print(f'   ✗ session_manager: {e}')

try:
    from utils import get_report_generator
    print('   ✓ report_generator')
except Exception as e:
    print(f'   ✗ report_generator: {e}')

try:
    from utils.visualizations import create_visualizations
    print('   ✓ visualizations')
except Exception as e:
    print(f'   ✗ visualizations: {e}')

try:
    from config import settings
    print('   ✓ config.settings')
except Exception as e:
    print(f'   ✗ config.settings: {e}')
" 2>&1

# Summary
echo ""
echo "=========================================="
echo "Setup verification complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If any checks failed, run: pip install -r requirements.txt"
echo "2. Read: IMPLEMENTATION_GUIDE.md for integration instructions"
echo "3. Try: QUICK_START.md for usage examples"
echo "4. Test: pytest tests/ -v"
echo ""
