#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")

npm uninstall
npm unlink

echo "The following applications were uninstalled:"
echo "- schemas-cli"
