#!/bin/bash

# Aetherflow Universal Installer
# Works on macOS, Linux, and Windows (Git Bash/WSL)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            OS="macOS"
            ;;
        Linux*)
            # Check if it's WSL
            if grep -q Microsoft /proc/version 2>/dev/null; then
                OS="WSL"
            else
                OS="Linux"
            fi
            ;;
        MINGW*|CYGWIN*|MSYS*)
            OS="Windows"
            ;;
        *)
            OS="UNKNOWN"
            ;;
    esac
    log_info "Detected OS: $OS"
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    log_info "Found Python $PYTHON_VERSION"
    
    if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 9 ]); then
        log_error "Python 3.9 or higher is required. Found version $PYTHON_VERSION"
        exit 1
    fi
    
    # Check pip
    if ! $PYTHON_CMD -m pip --version &>/dev/null; then
        log_warning "pip not found. Installing pip..."
        if [ "$OS" = "Linux" ] || [ "$OS" = "WSL" ]; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif [ "$OS" = "macOS" ]; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            $PYTHON_CMD get-pip.py
            rm get-pip.py
        fi
    fi
    
    PIP_CMD="$PYTHON_CMD -m pip"
    log_success "Python $PYTHON_VERSION and pip are ready"
}

# Check for virtual environment
check_venv() {
    log_info "Checking for virtual environment..."
    
    if [ -n "$VIRTUAL_ENV" ]; then
        log_success "Already in a virtual environment: $VIRTUAL_ENV"
        return 0
    fi
    
    if [ -d "venv" ] || [ -d ".venv" ]; then
        log_info "Found existing virtual environment"
        return 1
    fi
    
    return 2
}

# Create virtual environment
create_venv() {
    log_info "Creating virtual environment..."
    
    if [ "$OS" = "Windows" ]; then
        $PYTHON_CMD -m venv venv
        ACTIVATE_CMD="venv/Scripts/activate"
    else
        $PYTHON_CMD -m venv venv
        ACTIVATE_CMD="venv/bin/activate"
    fi
    
    if [ ! -f "$ACTIVATE_CMD" ]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi
    
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    log_info "Activating virtual environment..."
    
    if [ "$OS" = "Windows" ]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    if [ -n "$VIRTUAL_ENV" ]; then
        log_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        log_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
