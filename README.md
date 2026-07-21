# STEP to Point Cloud

## Installation

- create a virutal environment with python 3.11.9 (other versions could also work) (Windows = "python -m venv .venv")
- activte the virtual environment (Windows = ".venv\scripts\activate")
- install the dependencies from requirements.txt (windows = "pip install requirements.txt")

## Use

- put a step assembly file in the input folder
- uses the newest file in the "input" folder
- run the main script: "python main.py"
- in the output folder a PLY, PCD and XYZ file with the clustered pointcloud are generated

## Optional

- If you want to get one subpointlcouds with some of the parts from the complete assembly use the create_combinations scripts
- "python create_combinations.py"

## Current Bugs/Issues
- problems with the placement of parts in subassemblies of the Step assembly file
- repeatable colors for the clusters

