#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")

# create a symlink to the script in the user scripts directory
unlink "$HOME_DIR/bin/data"
unlink "$HOME_DIR/bin/infra"
unlink "$HOME_DIR/bin/sns"

echo "The following applications were uninstalled:"
echo " - data-cli"
echo " - infra-cli"
echo " - sns-cli"
