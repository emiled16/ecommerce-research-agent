#! /bin/bash

## This script is used to install the prerequisites for the project
## It works only on MacOS with zsh
## Disclaimer: this script is very simple and not optimized for production
## It assumes that:
# - brew is installed
# - the user is using zsh
# - .python-version file is present in the root of the project

set -e

brew install pyenv
brew install direnv

echo "eval "$(direnv hook bash)"" >> ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc

source ~/.zshrc

pyenv install $(cat .python-version)

echo "pyenv installed"
echo "direnv installed"
echo "python installed"

