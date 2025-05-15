#!/usr/bin/env bash

set -e

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/mauro/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/mauro/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/mauro/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/mauro/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<


# Define constants
REPO_URL="https://github.com/MauroAbidalCarrer/automatic_video_editing.git"
REPO_DIR="$HOME/repos/automatic_video_editing"
ENV_NAME="DOM"
ENV_YAML="$REPO_DIR/conda-env.yaml"
MAIN_SCRIPT="$REPO_DIR/src/main.py"

# Ensure ~/repos directory exists
mkdir -p "$HOME/repos"

# Step 1: Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Installing Miniconda..."

    # Choose installer based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        INSTALLER=Miniconda3-latest-Linux-x86_64.sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        INSTALLER=Miniconda3-latest-MacOSX-x86_64.sh
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi

    curl -fsSL "https://repo.anaconda.com/miniconda/$INSTALLER" -o "/tmp/$INSTALLER"
    bash "/tmp/$INSTALLER" -b -p "$HOME/miniconda"
    rm "/tmp/$INSTALLER"

    # Initialize conda
    export PATH="$HOME/miniconda/bin:$PATH"
fi
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# Ensure Conda is available in this shell
export PATH="$HOME/miniconda/bin:$PATH"
eval "$(conda shell.bash hook)"

# Step 2: Clone the repo if it doesn't exist, and checkout MVP branch
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning repository into $REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
    git checkout MVP
else
    cd "$REPO_DIR"
    git fetch origin
    git checkout MVP
    git pull origin MVP
fi

# Step 3: Create Conda environment if it doesn't exist
if ! conda info --envs | grep -q "^$ENV_NAME[[:space:]]"; then
    echo "Creating conda environment $ENV_NAME"
    conda env create -n "$ENV_NAME" -f "$ENV_YAML"
fi

# Step 4: Activate environment and run the script
echo "Activating environment and running script..."
conda activate "$ENV_NAME"

# Step 5: Run the main script
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Main script not found at $MAIN_SCRIPT"
    exit 1
fi

python "$MAIN_SCRIPT"