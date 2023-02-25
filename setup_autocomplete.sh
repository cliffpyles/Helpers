#!/bin/bash

# Install argcomplete package
pip install argcomplete

# Add argcomplete code to infra_cli.py script
echo "" >> infra_cli.py
echo "try:" >> infra_cli.py
echo "    import argcomplete" >> infra_cli.py
echo "except ImportError:" >> infra_cli.py
echo "    pass" >> infra_cli.py
echo "" >> infra_cli.py
echo "try:" >> infra_cli.py
echo "    argcomplete.autocomplete(parser)" >> infra_cli.py
echo "except Exception:" >> infra_cli.py
echo "    pass" >> infra_cli.py

# Install bash-completion package (Mac only)
if [[ "$OSTYPE" == "darwin"* ]]; then
  brew install bash-completion
fi

# Activate global argcomplete
sudo activate-global-python-argcomplete --user
# activate-global-python-argcomplete --user

# Add register-python-argcomplete command to bashrc and zshrc
echo 'eval "$(register-python-argcomplete infra_cli.py)"' >> ~/.bashrc
echo 'eval "$(register-python-argcomplete infra_cli.py)"' >> ~/.zshrc

# Create infra_cli_completion.sh script for Bash
echo '_infra_cli_completion()
{
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "${prev}" in
        deploy|delete|create|view)
            COMPREPLY=( $(compgen -f ${cur}) )
            return 0
            ;;
        --parameters-file)
            COMPREPLY=( $(compgen -f ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
}
complete -F _infra_cli_completion infra_cli.py' | sudo tee /etc/bash_completion.d/infra_cli_completion.sh > /dev/null

# Create _infra_cli script for Zsh
echo '#compdef infra_cli.py

# Infra CLI command completion
# Options:
#   --parameters-file   Path to a JSON file containing template parameters

_arguments \
  "1: :->commands" \
  "--parameters-file=[Path to a JSON file containing template parameters]" \
  ": :->args"

case "$state" in
  commands)
    case $line[1] in
      deploy)
        _arguments \
          "1: :_files" \
          "2: :_files" \
          "--parameters" \
          "--parameters-file=[Path to a JSON file containing template parameters]" \
          "*: :_files"
        ;;
      delete)
        _arguments \
          "1: :_files"
        ;;
      create)
        _arguments \
          "1: :_files" \
          "2: :_files" \
          "--template-type=[Format of the CloudFormation template]: :(json yaml)"
        ;;
      view)
        _arguments \
          "1: :_files" \
          "--show-outputs" \
          "--show-events" \
          "--show-resources"
        ;;
    esac
    ;;
  args)
    case $line[1] in
      --parameters-file)
        _files
        ;;
    esac
    ;;
esac' | sudo tee /etc/zsh_completion.d/_infra_cli > /dev/null
