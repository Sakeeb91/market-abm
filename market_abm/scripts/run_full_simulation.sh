#!/bin/bash
# Run a full market ABM simulation with optimal parameters
# Run from project root with: ./scripts/run_full_simulation.sh

# Navigate to the project directory
cd "$(dirname "$0")/.." || exit

# Create necessary directories
mkdir -p results

# Make sure Python path is correctly set
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Set arguments for the simulation
STEPS=500
DEBUG=false
SAVE_PLOTS=true
SHOW_PLOTS=true

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-show) SHOW_PLOTS=false ;;
        --debug) DEBUG=true ;;
        --steps) STEPS="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Display simulation parameters
echo "=== Running Market ABM Simulation ==="
echo "Steps: $STEPS"
echo "Debug mode: $DEBUG"
echo "Save plots: $SAVE_PLOTS"
echo "Show plots: $SHOW_PLOTS"
echo "====================================="

# Build the command
CMD="python run.py"

# Add arguments
if [ "$DEBUG" = true ]; then
    CMD="$CMD --debug"
fi

CMD="$CMD --steps $STEPS"

if [ "$SAVE_PLOTS" = false ]; then
    CMD="$CMD --no-save"
fi

if [ "$SHOW_PLOTS" = false ]; then
    CMD="$CMD --no-show"
fi

# Run the simulation
echo "Running command: $CMD"
$CMD

echo "Simulation complete." 