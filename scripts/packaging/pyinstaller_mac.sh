#!/bin/bash

# PyInstaller packaging script for Aetherflow on macOS
# Creates a standalone DMG bundle with proper macOS integration

set -e  # Exit on error

# Configuration
APP_NAME="Aetherflow"
APP_VERSION="0.1.0"
PYTHON_VERSION="3.9"
ARCH="x86_64"
MIN_MACOS_VERSION="10.12"
DMG_NAME="${APP_NAME}-${APP_VERSION}-macos-${ARCH}.dmg"
BUILD_DIR="dist"
SPEC_FILE="${APP_NAME}.spec"
ICON_FILE="resources/icon.icns"
ENTITLEMENTS="scripts/packaging/macos.entitlements"
CERTIFICATE_ID=""  # Set to your Developer ID for signing
NOTARIZE=false     # Set to true for App Store notarization

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if running on macOS
    if [[ "$(uname)" != "Darwin" ]]; then
        print_error "This script must be run on macOS"
        exit 1
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required"
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ "$PYTHON_VER" < "3.8" ]]; then
        print_error "Python 3.8 or higher is required (found $PYTHON_VER)"
        exit 1
    fi
    
    # Check PyInstaller
    if ! python3 -c "import pyinstaller" &> /dev/null; then
        print_info "Installing PyInstaller..."
        pip3 install pyinstaller
    fi
    
    # Check for required tools
    for tool in create-dmg codesign; do
        if ! command -v $tool &> /dev/null; then
            print_warning "$tool not found. Some features may be limited."
        fi
    done
    
    # Check for create-dmg (install if missing)
    if ! command -v create-dmg &> /dev/null; then
        print_info "Installing create-dmg..."
        brew install create-dmg || {
            print_warning "create-dmg not installed via brew. DMG creation may fail."
        }
    fi
    
    print_success "Prerequisites check passed"
}

# Create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    mkdir -p "${BUILD_DIR}"
    mkdir -p "resources"
    mkdir -p "scripts/packaging"
    
    print_success "Directory structure created"
}

# Create macOS entitlements file
create_entitlements() {
    print_info "Creating macOS entitlements file..."
    
    cat > "${ENTITLEMENTS}" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.files.downloads.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.device.usb</key>
    <true/>
</dict>
</plist>
EOF
    
    print_success "Entitlements file created at ${ENTITLEMENTS}"
}

# Create default icon if none exists
create_default_icon() {
    if [[ ! -f "${ICON_FILE}" ]]; then
        print_info "Creating default application icon..."
        
        # Create a simple icon using sips (macOS built-in)
        mkdir -p "resources"
        
        # Create a temporary PNG
        TEMP_ICON="resources/temp_icon.png"
        
        # Create a 1024x1024 blue icon with 'A' in the center
        cat > "resources/create_icon.py" << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 1024x1024 image
img = Image.new('RGBA', (1024, 1024), color=(52, 152, 219, 255))
draw = ImageDraw.Draw(img)

# Try to load a font
try:
    font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 400)
except:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 400)
    except:
        font = ImageFont.load_default()

