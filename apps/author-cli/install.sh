#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Home Directory: $HOME_DIR"
echo "Helpers Directory: $HELPERS_DIR"
echo "Script Directory: $SCRIPT_DIR"

# install dependencies
pip install -r $SCRIPT_DIR/requirements.txt

# create a config file for the app if it doesn't exist
if [ ! -f "$HOME_DIR/.author/config.yaml" ]; then
  mkdir "$HOME_DIR/.author"
  touch "$HOME_DIR/.author/config.yaml"
fi

# make a directory for user scripts if it doesn't exist
if [ ! -d "$HOME_DIR/bin" ]; then
  mkdir "$HOME_DIR/bin"
fi

# create symlinks to the script in the user scripts directory
ln -s "$SCRIPT_DIR/author_cli.py" "$HOME_DIR/bin/author"

# add the user scripts directory to the PATH
if ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.bashrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.bashrc"
fi

if [ -n "$ZSH_VERSION" ] && ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.zshrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.zshrc"
fi


echo "Installations complete."
echo "Type 'author' to use the author-cli app."