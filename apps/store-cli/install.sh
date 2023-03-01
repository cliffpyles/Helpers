#!/bin/bash

# get the current user's home directory
HOME_DIR=$(eval echo "~$USER")
HELPERS_DIR=$(eval echo "$PWD")
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo $HOME_DIR
echo $HELPERS_DIR
echo $SCRIPT_DIR

# make a directory for user scripts if it doesn't exist
if [ ! -d "$HOME_DIR/bin" ]; then
  mkdir "$HOME_DIR/bin"
fi

# create a symlink to the script in the user scripts directory
ln -s "$SCRIPT_DIR/store_cli.py" "$HOME_DIR/bin/store"

# add a default store
if [ ! -d "$HOME_DIR/.store-cli/stores/default" ]; then
  mkdir -p "$HOME_DIR/.store-cli/stores/default"
fi

if [ ! -f "$HOME_DIR/.store-cli/stores/default/data.json" ]; then
  touch ~/.store-cli/stores/default/data.json
  echo "[]" > ~/.store-cli/stores/default/data.json
fi

# add a config file
if [ ! -f "$HOME_DIR/.store-cli/config.yaml" ]; then
  cp $SCRIPT_DIR/config.yaml $HOME_DIR/.store-cli/config.yaml
fi

# add the user scripts directory to the PATH
if ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.bashrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.bashrc"
fi

if [ -n "$ZSH_VERSION" ] && ! grep -q "$HOME_DIR/bin" "$HOME_DIR/.zshrc"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME_DIR/.zshrc"
fi


echo "Installations complete."
echo "Type 'store' to use the store-cli app."
