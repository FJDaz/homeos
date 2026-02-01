#!/bin/bash

# Aetherflow Portability Test Suite
# Tests installation and functionality across macOS, Linux, and Windows (Git Bash/WSL)
# Generates compatibility reports for CI/CD integration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results tracking
declare -A TEST_RESULTS
declare -A TEST_DETAILS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0
REPORT_FILE="portability_report_$(date +%Y%m%d_%H%M%S).json"
HTML_REPORT_FILE="portability_report_$(date +%Y%m%d_%H%M%S).html"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

log_debug() {
    if [ "$DEBUG" = "true" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

# Test result tracking
record_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    local platform="$4"
    
    TEST_RESULTS["$test_name"]="$result"
    TEST_DETAILS["$test_name"]="$details"
    
    case $result in
        "PASS")
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo -e "${GREEN}✓ PASS${NC}: $test_name"
            ;;
        "FAIL")
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo -e "${RED}✗ FAIL${NC}: $test_name - $details"
            ;;
        "SKIP")
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            echo -e "${YELLOW}↷ SKIP${NC}: $test_name - $details"
            ;;
    esac
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

# Detect OS and architecture
detect_environment() {
    log_info "Detecting environment..."
    
    # OS detection
    case "$(uname -s)" in
        Darwin*)
            OS="macOS"
            OS_VERSION="$(sw_vers -productVersion)"
            ;;
        Linux*)
            if grep -q Microsoft /proc/version 2>/dev/null; then
                OS="WSL"
                OS_VERSION="$(cat /proc/version | grep -o 'Microsoft@[^ ]*' || echo 'Unknown')"
            else
                OS="Linux"
                if [ -f /etc/os-release ]; then
                    . /etc/os-release
                    OS_VERSION="$NAME $VERSION"
                else
                    OS_VERSION="Unknown"
                fi
            fi
            ;;
        MINGW*|CYGWIN*|MSYS*)
            OS="Windows"
            OS_VERSION="$(cmd.exe /c ver 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo 'Unknown')"
            ;;
        *)
            OS="UNKNOWN"
            OS_VERSION="Unknown"
            ;;
    esac
    
    # Architecture detection
    ARCH="$(uname -m)"
    
    # Shell detection
    SHELL_NAME="$(basename "$SHELL")"
    
    # Python detection
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION="$(python3 --version 2>&1)"
    elif command -v python &>/dev/null; then
        PYTHON_VERSION="$(python --version 2>&1)"
    else
        PYTHON_VERSION="Not found"
    fi
    
    log_info "Environment detected:"
    log_info "  OS: $OS $OS_VERSION"
    log_info "  Architecture: $ARCH"
    log_info "  Shell: $SHELL_NAME"
    log_info "  Python: $PYTHON_VERSION"
    
    # Export for use in tests
    export DETECTED_OS="$OS"
    export DETECTED_ARCH="$ARCH"
}

# Test 1: Python availability and version
test_python_installation() {
    local test_name="python_installation"
    log_test "Testing Python installation..."
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
