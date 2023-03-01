#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")

# make a directory for user scripts if it doesn't exist
if [ ! -d "$HOME_DIR/bin" ]; then
  mkdir "$HOME_DIR/bin"
fi

# create a symlink to the script in the user scripts directory
ln -s "$PWD/apps/data-cli/data_cli.py" "$HOME_DIR/bin/data"
ln -s "$PWD/apps/infra-cli/infra_cli.py" "$HOME_DIR/bin/infra"
ln -s "$PWD/apps/sns-cli/sns-cli.mjs" "$HOME_DIR/bin/sns"

# add the user scripts directory to the PATH
if ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.bashrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.bashrc"
fi

if [ -n "$ZSH_VERSION" ] && ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.zshrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.zshrc"
fi

# install dependencies for sns-cli
cd $HELPERS_DIR/apps/sns-cli
npm install
cd $HELPERS_DIR

echo "Installations complete."
echo "Type 'data' to use the data-cli app."
echo "Type 'infra' to use the infra-cli app."
echo "Type 'sns' to use the sns-cli app."
