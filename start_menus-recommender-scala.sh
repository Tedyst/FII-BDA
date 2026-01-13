#!/bin/bash
# Startup script for menus-recommender-scala.ipynb
# Usage: ./start_menus-recommender-scala.sh [lab|notebook] [port] [--no-browser]
#
# Note: This script assumes you have a Scala kernel installed (e.g., Almond kernel)
# To install Almond kernel: coursier launch --fork almond:0.14.0-SNAPSHOT --scala 2.12.12 -- --install

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists (for Jupyter)
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo "Please create it first with: python3 -m venv venv"
    exit 1
fi

# Set Java 11 for Spark 3.5.0 - MUST BE BEFORE ACTIVATING VENV
JAVA_11_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
if [ -d "$JAVA_11_HOME" ]; then
    export JAVA_HOME="$JAVA_11_HOME"
    export PATH="$JAVA_HOME/bin:$PATH"
    echo -e "${GREEN}JAVA_HOME set to: $JAVA_HOME${NC}"
else
    # Try to find Java 11
    if command -v update-alternatives >/dev/null 2>&1; then
        JAVA_PATH=$(update-alternatives --list java 2>/dev/null | grep java-11 | head -1)
        if [ -n "$JAVA_PATH" ]; then
            JAVA_11_HOME=$(dirname $(dirname "$JAVA_PATH"))
            export JAVA_HOME="$JAVA_11_HOME"
            export PATH="$JAVA_HOME/bin:$PATH"
            echo -e "${GREEN}Found Java 11 at: $JAVA_HOME${NC}"
        else
            echo -e "${YELLOW}Java 11 not found via update-alternatives${NC}"
            echo -e "${YELLOW}Please install Java 11: sudo apt install openjdk-11-jdk${NC}"
        fi
    fi
fi

# Verify Java
if command -v java >/dev/null 2>&1; then
    JAVA_VERSION=$(java -version 2>&1 | head -1)
    echo -e "${GREEN}Java: $JAVA_VERSION${NC}"
else
    echo -e "${RED}Error: Java not found!${NC}"
    echo "Please install Java 11: sudo apt install openjdk-11-jdk"
    exit 1
fi

# Check Scala installation
if command -v scala >/dev/null 2>&1; then
    SCALA_VERSION=$(scala -version 2>&1 | head -1)
    echo -e "${GREEN}Scala: $SCALA_VERSION${NC}"
else
    echo -e "${YELLOW}Warning: Scala not found in PATH${NC}"
    echo -e "${YELLOW}Scala kernel (Almond) may still work if installed via coursier${NC}"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check for Scala kernel (Almond)
echo -e "${GREEN}Checking for Scala kernel (Almond)...${NC}"
SCALA_KERNEL_FOUND=false
if command -v jupyter >/dev/null 2>&1; then
    KERNELS=$(jupyter kernelspec list 2>/dev/null | grep -i scala || true)
    if [ -n "$KERNELS" ]; then
        SCALA_KERNEL_FOUND=true
        echo -e "${GREEN}Scala kernel found!${NC}"
        echo "$KERNELS"
    else
        echo -e "${YELLOW}Scala kernel not found in Jupyter kernelspec list${NC}"
        echo -e "${YELLOW}To install Almond kernel (Scala 2.12), run:${NC}"
        echo -e "${CYAN}coursier launch --fork almond:0.14.0-SNAPSHOT --scala 2.12.12 -- --install${NC}"
        echo ""
        echo -e "${YELLOW}Or install stable version:${NC}"
        echo -e "${CYAN}coursier launch --fork almond:0.13.2 --scala 2.12.12 -- --install${NC}"
        echo ""
        echo -e "${YELLOW}Note: The notebook will still open, but you may need to manually select the Scala kernel${NC}"
    fi
fi

# Check if notebook exists
NOTEBOOK_FILE="menus-recommender-scala.ipynb"
if [ ! -f "$NOTEBOOK_FILE" ]; then
    echo -e "${RED}Error: Notebook file not found: $NOTEBOOK_FILE${NC}"
    exit 1
fi

# Parse arguments
JUPYTER_TYPE="${1:-lab}"
PORT="${2:-8889}"
NO_BROWSER=false

# Check for --no-browser flag
for arg in "$@"; do
    if [ "$arg" = "--no-browser" ]; then
        NO_BROWSER=true
    fi
done

# Validate Jupyter type
if [ "$JUPYTER_TYPE" != "lab" ] && [ "$JUPYTER_TYPE" != "notebook" ]; then
    if [ "$JUPYTER_TYPE" != "--no-browser" ]; then
        echo -e "${YELLOW}Invalid option: $JUPYTER_TYPE${NC}"
        echo "Usage: ./start_menus-recommender-scala.sh [lab|notebook] [port] [--no-browser]"
        echo "Default: lab on port 8889"
    fi
    JUPYTER_TYPE="lab"
fi

# Detect WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
    echo -e "${CYAN}WSL detected${NC}"
else
    IS_WSL=false
fi

# Get hostname/IP for URL
if [ "$IS_WSL" = true ]; then
    # In WSL, use localhost (accessible from Windows browser)
    HOST="localhost"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Jupyter will be accessible from Windows browser at:${NC}"
    if [ "$JUPYTER_TYPE" = "lab" ]; then
        echo -e "${CYAN}http://localhost:$PORT/lab${NC}"
    else
        echo -e "${CYAN}http://localhost:$PORT${NC}"
    fi
    echo -e "${BLUE}========================================${NC}"
else
    HOST="localhost"
fi

# Build Jupyter command
BROWSER_FLAG=""
if [ "$NO_BROWSER" = true ]; then
    BROWSER_FLAG="--no-browser"
    echo -e "${YELLOW}Browser will not open automatically${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}After Jupyter starts, open in your browser:${NC}"
    if [ "$JUPYTER_TYPE" = "lab" ]; then
        echo -e "${CYAN}http://localhost:$PORT/lab${NC}"
    else
        echo -e "${CYAN}http://localhost:$PORT${NC}"
    fi
    echo -e "${BLUE}========================================${NC}"
else
    # Try to detect if we can open browser automatically
    if command -v wslview >/dev/null 2>&1; then
        echo -e "${GREEN}Will try to open browser automatically (WSL)${NC}"
    elif command -v xdg-open >/dev/null 2>&1 && [ -n "$DISPLAY" ]; then
        echo -e "${GREEN}Will try to open browser automatically (X11)${NC}"
    else
        echo -e "${YELLOW}Browser auto-open not available. Copy the URL from output below.${NC}"
        BROWSER_FLAG="--no-browser"
    fi
fi

# Set Spark environment variables
export SPARK_HOME="${SPARK_HOME:-$(python3 -c 'import findspark; findspark.init(); import os; print(os.environ.get("SPARK_HOME", ""))' 2>/dev/null || echo '')}"
if [ -n "$SPARK_HOME" ]; then
    echo -e "${GREEN}SPARK_HOME: $SPARK_HOME${NC}"
fi

# Start Jupyter
if [ "$JUPYTER_TYPE" = "lab" ]; then
    echo -e "${GREEN}Starting Jupyter Lab on port $PORT...${NC}"
    echo -e "${YELLOW}Opening notebook: $NOTEBOOK_FILE${NC}"
    echo -e "${BLUE}Notebook: Menu Recommender System - Scala (SparkML)${NC}"
    if [ "$SCALA_KERNEL_FOUND" = false ]; then
        echo -e "${YELLOW}Warning: Make sure to select the Scala kernel when the notebook opens!${NC}"
    fi
    echo ""
    jupyter lab --port="$PORT" "$NOTEBOOK_FILE" $BROWSER_FLAG --ip="$HOST"
else
    echo -e "${GREEN}Starting Jupyter Notebook on port $PORT...${NC}"
    echo -e "${YELLOW}Opening notebook: $NOTEBOOK_FILE${NC}"
    echo -e "${BLUE}Notebook: Menu Recommender System - Scala (SparkML)${NC}"
    if [ "$SCALA_KERNEL_FOUND" = false ]; then
        echo -e "${YELLOW}Warning: Make sure to select the Scala kernel when the notebook opens!${NC}"
    fi
    echo ""
    jupyter notebook --port="$PORT" "$NOTEBOOK_FILE" $BROWSER_FLAG --ip="$HOST"
fi
