#!/bin/bash

###############################################################################
# EMAP Server Installation Script
# This script clones/updates the EMAP repository and sets up the server
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/PandorasBox-Byte/EMAP.git"
INSTALL_DIR="$HOME/EMAP-Server"
SERVER_DIR="$INSTALL_DIR/Server"

# Print colored messages
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

print_header() {
    echo -e "\n${GREEN}================================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}================================================================${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    local os=$(detect_os)
    
    if [ "$os" == "linux" ]; then
        print_info "Detected Linux system"
        
        # Check if running as root or with sudo
        if [ "$EUID" -ne 0 ]; then
            print_warning "Some dependencies may require sudo privileges"
            SUDO="sudo"
        else
            SUDO=""
        fi
        
        # Update package list
        print_info "Updating package list..."
        $SUDO apt-get update -qq
        
        # Install Python3 and pip
        if ! command_exists python3; then
            print_info "Installing Python3..."
            $SUDO apt-get install -y python3
        else
            print_success "Python3 is already installed"
        fi
        
        if ! command_exists pip3; then
            print_info "Installing pip3..."
            $SUDO apt-get install -y python3-pip
        else
            print_success "pip3 is already installed"
        fi
        
        # Install python3-venv
        print_info "Installing python3-venv..."
        $SUDO apt-get install -y python3-venv
        
        # Install git
        if ! command_exists git; then
            print_info "Installing git..."
            $SUDO apt-get install -y git
        else
            print_success "git is already installed"
        fi
        
    elif [ "$os" == "macos" ]; then
        print_info "Detected macOS system"
        
        # Check for Homebrew
        if ! command_exists brew; then
            print_warning "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            print_success "Homebrew is already installed"
        fi
        
        # Install Python3
        if ! command_exists python3; then
            print_info "Installing Python3 via Homebrew..."
            brew install python3
        else
            print_success "Python3 is already installed"
        fi
        
        # Install git
        if ! command_exists git; then
            print_info "Installing git via Homebrew..."
            brew install git
        else
            print_success "git is already installed"
        fi
        
    else
        print_error "Unsupported operating system"
        exit 1
    fi
    
    print_success "System dependencies installed"
}

# Clone or update repository
setup_repository() {
    print_header "Setting Up Repository"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Repository directory exists. Updating..."
        cd "$INSTALL_DIR"
        git pull origin main
        print_success "Repository updated"
    else
        print_info "Cloning repository to $INSTALL_DIR..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        print_success "Repository cloned"
    fi
}

# Setup Python virtual environment
setup_venv() {
    print_header "Setting Up Python Virtual Environment"
    
    cd "$SERVER_DIR"
    
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    cd "$SERVER_DIR"
    
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    print_info "Upgrading pip..."
    pip install --upgrade pip -q
    
    if [ -f "requirements.txt" ]; then
        print_info "Installing Python packages from requirements.txt..."
        pip install -r requirements.txt -q
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found"
    fi
    
    deactivate
}

# Setup environment file
setup_env_file() {
    print_header "Setting Up Environment File"
    
    cd "$SERVER_DIR"
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists. Skipping creation."
    else
        if [ -f ".env.example" ]; then
            print_info "Creating .env file from .env.example..."
            cp .env.example .env
            print_success ".env file created"
            print_warning "Please edit .env file to configure your settings"
        else
            print_info "Creating default .env file..."
            cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this

# Database
DATABASE_URL=sqlite:///ema.db

# Server
HOST=0.0.0.0
PORT=5000

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
EOF
            print_success ".env file created with defaults"
            print_warning "Please edit .env file to set your SECRET_KEY and ADMIN_PASSWORD"
        fi
    fi
}

# Initialize database
init_database() {
    print_header "Initializing Database"
    
    cd "$SERVER_DIR"
    
    source venv/bin/activate
    
    if [ -f "app.py" ]; then
        print_info "Running database initialization..."
        python3 -c "from app import db; db.create_all()" 2>/dev/null || print_warning "Database may already be initialized"
        print_success "Database initialized"
    fi
    
    deactivate
}

# Make scripts executable
make_scripts_executable() {
    print_header "Making Scripts Executable"
    
    cd "$SERVER_DIR"
    
    for script in setup.sh setup_dev.sh Start.sh Stop.sh deploy_to_linux.sh; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_success "Made $script executable"
        fi
    done
}

# Display completion message
display_completion() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}EMAP Server has been successfully installed!${NC}\n"
    echo -e "Installation directory: ${BLUE}$INSTALL_DIR${NC}"
    echo -e "Server directory: ${BLUE}$SERVER_DIR${NC}\n"
    
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. Edit the configuration file:"
    echo -e "   ${BLUE}nano $SERVER_DIR/.env${NC}\n"
    echo -e "2. Start the server:"
    echo -e "   ${BLUE}cd $SERVER_DIR${NC}"
    echo -e "   ${BLUE}./Start.sh${NC}\n"
    echo -e "3. Stop the server:"
    echo -e "   ${BLUE}./Stop.sh${NC}\n"
    
    echo -e "${YELLOW}Admin Panel:${NC}"
    echo -e "   URL: ${BLUE}http://localhost:5000/admin${NC}"
    echo -e "   Default credentials in .env file\n"
    
    echo -e "${GREEN}For more information, check:${NC}"
    echo -e "   ${BLUE}$SERVER_DIR/README.md${NC}"
    echo -e "   ${BLUE}$SERVER_DIR/ADMIN_PANEL_GUIDE.md${NC}\n"
}

# Main installation flow
main() {
    clear
    print_header "EMAP Server Installation Script"
    
    print_info "This script will install the EMAP server on your system"
    print_info "Installation directory: $INSTALL_DIR"
    echo ""
    
    read -p "Continue with installation? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    # Run installation steps
    install_system_deps
    setup_repository
    setup_venv
    install_python_deps
    setup_env_file
    init_database
    make_scripts_executable
    display_completion
}

# Run main function
main
