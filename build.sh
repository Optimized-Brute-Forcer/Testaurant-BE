#!/bin/bash
set -e

echo "Starting build process..."

# Define directories
FUNCTIONS_DIR="serverless_functions"

# Clean previous build artifacts if any (though we want to keep the source files)
# In this manual bundling approach, serverless_functions IS the source + build dir.
# But we should be careful not to delete the handler itself if it's there.

echo "Installing dependencies to $FUNCTIONS_DIR..."
# Install dependencies directly into the functions directory
python3 -m pip install -r requirements.txt --target $FUNCTIONS_DIR --upgrade

echo "Copying application code to $FUNCTIONS_DIR/app..."
# Create app directory in functions if it doesn't exist
mkdir -p $FUNCTIONS_DIR/app

# Copy app code
cp -r app/* $FUNCTIONS_DIR/app/

# Copy .env if it exists
# cp .env $FUNCTIONS_DIR/ || true

# Copy runtime.txt AND requirements.txt to specify Python version strongly
cp runtime.txt $FUNCTIONS_DIR/
cp requirements.txt $FUNCTIONS_DIR/

# Remove bin directory which might contain conflicting binaries or confuse the scanner
rm -rf $FUNCTIONS_DIR/bin

echo "Preparing function directory..."
# Create directory for the final function
# Netlify treats a subdirectory in 'functions' as a function if it contains a handler.
# Function name = subdirectory name = app_handler
OUTPUT_DIR="ready_functions/app_handler"
# Clean up previous artifacts
rm -rf ready_functions
mkdir -p $OUTPUT_DIR

# Copy contents (dependencies + app code + runtime + requirements)
cp -r $FUNCTIONS_DIR/* $OUTPUT_DIR/

echo "Build complete. Artifact directory: $OUTPUT_DIR"
ls -F $OUTPUT_DIR | head -n 10
