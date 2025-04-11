#!/bin/bash

# URL of the file to download
FILE_URL="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"

# Path to the target directory
TARGET_DIR="models"

# Create the target directory if it does not exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating directory $TARGET_DIR..."
    mkdir -p "$TARGET_DIR"
fi

# Download the file with progress bar
echo "Downloading file from $FILE_URL..."
wget --show-progress "$FILE_URL" -O /tmp/vosk-model.zip

# Extract the file
echo "Extracting the file..."
unzip -q /tmp/vosk-model.zip -d "$TARGET_DIR"

# Remove the downloaded ZIP file
echo "Cleaning up temporary files..."
rm /tmp/vosk-model.zip

# Detect the operating system
OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == "Linux" ]]; then
    # Check if the system is Ubuntu
    if [ -f /etc/os-release ] && grep -qi "ubuntu" /etc/os-release; then
        echo "Detected Ubuntu. Installing required Python libraries..."
        
        # Ensure pip is installed
        if ! command -v pip &> /dev/null; then
            echo "pip not found. Installing pip..."
            sudo apt update && sudo apt install -y python3-pip
        fi
        python3 -m pip install vosk pyaudio
    else
        echo "Non-Ubuntu Linux detected. Please install dependencies manually."
    fi
elif [[ "$OS_TYPE" == "MINGW"* || "$OS_TYPE" == "CYGWIN"* ]]; then
    echo "Detected Windows with Bash. Installing required Python libraries..."
    
    # Ensure pip is installed
    if ! command -v pip &> /dev/null; then
        echo "pip not found. Installing pip..."
        python3 -m ensurepip --upgrade || curl https://bootstrap.pypa.io/get-pip.py | python3
    fi
    python3 -m pip install vosk pyaudio
else
    echo "Unsupported operating system. Please install dependencies manually."
fi

echo "Done! The file has been extracted to the $TARGET_DIR directory."