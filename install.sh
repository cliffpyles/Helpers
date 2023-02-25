#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")

# make a directory for user scripts if it doesn't exist
if [ ! -d "$HOME_DIR/bin" ]; then
  mkdir "$HOME_DIR/bin"
fi

# create a symlink to the script in the user scripts directory
ln -s "$PWD/data_cli.py" "$HOME_DIR/bin/data-cli"
ln -s "$PWD/infra_cli.py" "$HOME_DIR/bin/infra-cli"

# add the user scripts directory to the PATH
if ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.bashrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.bashrc"
fi

if [ -n "$ZSH_VERSION" ] && ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.zshrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.zshrc"
fi

echo "Installations complete."
echo "Type 'data-cli' to use the data_cli app."
echo "Type 'infra-cli' to use the infra_cli app."
