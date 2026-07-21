#!/usr/bin/env python3

import json
from pathlib import Path
from itertools import combinations

import open3d as o3d

from exporter import save_cloud


# --------------------------------------------------------
# JSON laden
# --------------------------------------------------------

with open("config_combinations.json", "r") as f:
    config = json.load(f)

input_folder = Path(config["input_folder"])
output_folder = Path(config["output_folder"])
output_folder.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------
# Alle Punktwolken laden
# --------------------------------------------------------

clouds = {}

for file in input_folder.glob("*.pcd"):

    name = file.stem

    cloud = o3d.io.read_point_cloud(str(file))

    clouds[name] = cloud


print(f"{len(clouds)} Punktwolken gefunden.")


# --------------------------------------------------------
# Hilfsfunktion
# --------------------------------------------------------

def save_combination(names):

    combined = o3d.geometry.PointCloud()

    for name in names:
        combined += clouds[name]

    filename = output_folder / "__".join(names)

    save_cloud(combined, filename)


# --------------------------------------------------------
# Jobs ausführen
# --------------------------------------------------------

all_names = sorted(clouds.keys())

for job in config["jobs"]:

    mode = job["mode"]

    # ----------------------------
    # alle Kombinationen
    # ----------------------------

    if mode == "all":

        for r in range(2, len(all_names)+1):

            for combo in combinations(all_names, r):

                save_combination(combo)

print("Fertig.")