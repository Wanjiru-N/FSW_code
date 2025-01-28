#!/bin/bash

# Define the virtual environment directory
VENV_DIR=~/FSW_Test

# Check if the virtual environment exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment."
    exit 1
fi

echo "Virtual environment activated."

# Install required dependencies (optional, add packages if needed)
# pip install -r requirements.txt

# List of Python scripts to run simultaneously
SCRIPTS=(
    ~/Desktop/Code/analog_plots_logs_2.py
    ~/Desktop/Code/open-loop_digital-control.py
    ~/Desktop/Code/Tachogen.py
)

# Run each script in the background
for script in "${SCRIPTS[@]}"
do
    if [ -f "$script" ]; then
        echo "Running $script in background..."
        python "$script" &
    else
        echo "Script $script not found!"
    fi
done

# Wait for all background processes to finish
wait

# Deactivate the virtual environment
deactivate

echo "All scripts executed. Virtual environment deactivated."
