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

# Copy .env if it exists (optional, Netlify usually handles env vars via UI, but good for completeness if needed)
# cp .env $FUNCTIONS_DIR/ || true

echo "Build complete. Contents of $FUNCTIONS_DIR:"
ls -F $FUNCTIONS_DIR
