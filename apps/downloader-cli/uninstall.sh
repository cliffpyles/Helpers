#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")

# create a symlink to the script in the user scripts directory
unlink "$HOME_DIR/bin/downloader"
unlink "$HOME_DIR/bin/dl"

echo "The following applications were uninstalled:"
echo " - downloader-cli"
