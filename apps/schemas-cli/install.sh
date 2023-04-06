#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Home Directory: $HOME_DIR"
echo "Helpers Directory: $HELPERS_DIR"
echo "Script Directory: $SCRIPT_DIR"


# make a directory for user scripts if it doesn't exist
if [ ! -d "$HOME_DIR/bin" ]; then
  mkdir "$HOME_DIR/bin"
fi

# Install dependencies
npm install
npm link

echo "Installations complete."
echo "Type 'schema' to use the schemas-cli app."