#!/bin/bash
# This script updates a PythonAnywhere web app from a GitHub repository and reloads the web app.
# Environment variables should be set in ~/.env:
# GITHUB_USERNAME: Your GitHub username
# GITHUB_PAT: Your GitHub Personal Access Token
# REPOSITORY_NAME: The name of your GitHub repository
# PYTHONANYWHERE_USERNAME: Your PythonAnywhere username
# Usage: ./update_and_reload.sh

# load environment variables
set -a
source ~/.env
set +a

# go to the repository directory
cd ~/${REPOSITORY_NAME}

# pull the latest changes from GitHub
git remote set-url origin https://${GITHUB_USERNAME}:${GITHUB_PAT}@github.com/${GITHUB_USERNAME}/${REPOSITORY_NAME}.git
git fetch --all
git pull https://${GITHUB_USERNAME}:${GITHUB_PAT}@github.com/${GITHUB_USERNAME}/${REPOSITORY_NAME}.git $(git rev-parse --abbrev-ref HEAD)

# install or update the virtual environment
source ./env/bin/activate
pip install -r requirements.txt