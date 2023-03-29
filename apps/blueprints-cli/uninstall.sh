#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")

# create a symlink to the script in the user scripts directory
unlink "$HOME_DIR/bin/blueprints"
unlink "$HOME_DIR/bin/bp"

echo "The following applications were uninstalled:"
echo " - blueprints-cli"
