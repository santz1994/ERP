#!/usr/bin/env bash
# Quick Setup & Test Script for QA Infrastructure
# Usage: ./qa-setup.sh

set -e

echo "======================================================================"
echo "ERP 2026 - QA Infrastructure Quick Setup"
echo "======================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")"

echo -e "${YELLOW}1. Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

echo -e "${YELLOW}2. Installing QA dependencies...${NC}"
cd erp-softtoys
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt 2>&1 | tail -5
echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "${YELLOW}3. Checking pytest configuration...${NC}"
if [ -f "../tests/conftest.py" ]; then
    echo -e "${GREEN}✅ conftest.py found${NC}"
else
    echo -e "${RED}❌ conftest.py missing${NC}"
    exit 1
fi

echo -e "${YELLOW}4. Running pytest smoke test...${NC}"
pytest ../tests/ --collect-only -q | head -20
echo -e "${GREEN}✅ Tests collected successfully${NC}"

echo -e "${YELLOW}5. Checking code quality tools...${NC}"
tools=("black" "ruff" "mypy" "bandit")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo -e "${GREEN}✅ $tool${NC}"
    else
        echo -e "${YELLOW}⚠️  $tool not in PATH (but installed)${NC}"
    fi
done

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start backend:"
echo "     uvicorn app.main:app --reload --port 8000"
echo ""
echo "  2. Run all tests:"
echo "     pytest ../tests/ -v"
echo ""
echo "  3. Run specific suite:"
echo "     pytest ../tests/test_boundary_value_analysis.py -v"
echo ""
echo "  4. Run with coverage:"
echo "     pytest ../tests/ --cov=app --cov-report=html"
echo ""
echo "  5. Run load tests:"
echo "     locust -f ../tests/locustfile.py --headless -u 5 -r 1 -t 20s --host http://localhost:8000"
echo ""
echo "  6. Security scan:"
echo "     bandit -r app -f txt"
echo ""
echo "======================================================================"
