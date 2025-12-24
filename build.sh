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
# Copy runtime.txt AND requirements.txt
cp runtime.txt $FUNCTIONS_DIR/
cp requirements.txt $FUNCTIONS_DIR/
# Create __init__.py to help detection
touch $FUNCTIONS_DIR/__init__.py

# Remove bin directory
rm -rf $FUNCTIONS_DIR/bin

echo "Zipping function artifact..."
# Create directory for the final zip
mkdir -p ready_functions
rm -f ready_functions/app_handler.zip

# Zip the contents of serverless_functions into app_handler.zip
cd $FUNCTIONS_DIR
zip -r ../ready_functions/app_handler.zip .
cd ..

echo "Build complete. Artifact: ready_functions/app_handler.zip"
ls -l ready_functions/app_handler.zip
