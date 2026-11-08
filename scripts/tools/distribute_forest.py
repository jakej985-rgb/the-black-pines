#!/usr/bin/env python3
"""
Procedural Forest Distribution Tool for The Black Pines (Issue #2).
Populates scenes/world/forest.tscn with:
- Multi-archetype trees (Douglas Fir, Tall Pine, Standard Pine, Dead Snag, Sapling)
- Preserved clearings and walking routes via geometric exclusion masks
- Dense perimeter horizon belts
- Rich undergrowth carpet (bracken ferns, wild grass, forest debris)
"""

import math
import random
import os

SEED = 42

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def point_to_segment_dist(p, a, b):
    # Shortest distance from 2D point p to line segment ab
    ab = (b[0] - a[0], b[1] - a[1])
    ab_len_sq = ab[0]**2 + ab[1]**2
    if ab_len_sq < 0.0001:
        return distance(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / ab_len_sq))
    proj = (a[0] + t * ab[0], a[1] + t * ab[1])
    return distance(p, proj)

def generate_forest():
    random.seed(SEED)

    # 1. Exclusion Zones: (x, z, radius)
    exclusion_circles = [
        (0.0, 10.0, 10.5),    # Ranger Station & Porch & Generator
        (0.0, 14.5, 6.0),     # Behind Cabin Generator
        (8.5, -8.5, 8.5),     # Abandoned Camp & Flare & Journal
        (-10.5, -18.0, 8.0),  # Elk Carcass & Gore Pool
        (-7.5, -14.0, 5.5),   # Clawed Tree
        (-8.5, -28.0, 7.0),   # Sasquatch Stalker Glade
        (-4.0, 3.0, 3.8),     # Footprint 1
        (-5.5, -3.2, 3.8),    # Footprint 2
        (-7.5, -10.5, 3.8),   # Footprint 3
        (3.8, 8.5, 3.5),      # Scrap Metal
        (-2.0, -1.0, 3.5),    # Sticks Bundle
        (4.5, 1.5, 3.5),      # Rock Craggy 1
        (-6.2, -6.8, 3.5),    # Rock Craggy 2
        (-11.5, -14.5, 4.0),  # Rock Craggy 3
        (11.0, 1.5, 4.5),     # Rock Outcrop 1
        (-13.5, -11.0, 4.5),  # Rock Outcrop 2
    ]

    # Path corridors: list of (p1, p2, width)
    path_corridors = [
        ((0.0, 6.0), (-4.0, 3.0), 3.8),     # Cabin to Footprint 1
        ((-4.0, 3.0), (-5.5, -3.2), 3.8),   # Footprint 1 to Footprint 2
        ((-5.5, -3.2), (-7.5, -10.5), 3.8), # Footprint 2 to Footprint 3
        ((-7.5, -10.5), (-7.5, -14.0), 3.8),# Footprint 3 to Clawed Tree
        ((-7.5, -14.0), (-10.5, -18.0), 3.8),# Clawed Tree to Carcass
        ((0.0, 6.0), (8.5, -8.5), 4.0),     # Cabin to Abandoned Camp
    ]

    def is_in_exclusion_zone(x, z, extra_padding=0.0):
        p = (x, z)
        for cx, cz, r in exclusion_circles:
            if distance(p, (cx, cz)) < (r + extra_padding):
                return True
        for a, b, w in path_corridors:
            if point_to_segment_dist(p, a, b) < (w * 0.5 + extra_padding):
                return True
        return False

    # 2. Place Trees
    trees = []
    # Bounds: -60 to +60 in X and Z
    tree_archetypes = [
        ("TreeDouglasFir", "24_douglas_fir", 0.28, 4.2), # (name, ext_res_id, weight, min_dist)
        ("PineTree",       "1_tree",         0.35, 3.4),
        ("TreePineTall",   "25_pine_tall",   0.20, 3.0),
        ("TreeSnagDead",   "26_snag_dead",   0.09, 3.2),
        ("TreeSapling",    "27_sapling",     0.08, 2.0)
    ]

    # Candidate grid with jitter for natural clustering
    attempts = 0
    max_trees = 115

    # A. Perimeter dense ring trees (X or Z between 35 and 62)
    while len(trees) < 65 and attempts < 2000:
        attempts += 1
        # Pick from perimeter boundary zone
        angle = random.uniform(0, math.pi * 2)
        r = random.uniform(38.0, 62.0)
        x = math.cos(angle) * r
        z = math.sin(angle) * r

        if abs(x) > 63.0 or abs(z) > 63.0:
            continue
        if is_in_exclusion_zone(x, z, extra_padding=1.0):
            continue

        # Choose archetype
        roll = random.random()
        cum = 0.0
        chosen = tree_archetypes[1]
        for arch in tree_archetypes:
            cum += arch[2]
            if roll <= cum:
                chosen = arch
                break

        # Check proximity to existing trees
        too_close = False
        for tx, tz, _, min_d, _ in trees:
            if distance((x, z), (tx, tz)) < max(chosen[3], min_d):
                too_close = True
                break
        if not too_close:
            rot_y = random.uniform(0, math.pi * 2)
            scale = random.uniform(0.88, 1.25)
            trees.append((x, z, chosen, chosen[3], (rot_y, scale)))

    # B. Interior groves and natural clusters
    attempts = 0
    while len(trees) < max_trees and attempts < 3000:
        attempts += 1
        x = random.uniform(-45.0, 45.0)
        z = random.uniform(-45.0, 45.0)

        if is_in_exclusion_zone(x, z, extra_padding=1.2):
            continue

        roll = random.random()
        cum = 0.0
        chosen = tree_archetypes[1]
        for arch in tree_archetypes:
            cum += arch[2]
            if roll <= cum:
                chosen = arch
                break

        too_close = False
        for tx, tz, _, min_d, _ in trees:
            if distance((x, z), (tx, tz)) < max(chosen[3], min_d):
                too_close = True
                break
        if not too_close:
            rot_y = random.uniform(0, math.pi * 2)
            scale = random.uniform(0.9, 1.2)
            trees.append((x, z, chosen, chosen[3], (rot_y, scale)))

    print(f"Generated {len(trees)} trees with organic distribution!")

    # 3. Undergrowth Elements (Ferns, Grass, Debris)
    undergrowth = []
    under_types = [
        ("Fern",   "14_fern",   0.45, 1.0, 1.35),
        ("Grass",  "15_grass",  0.35, 0.9, 1.3),
        ("Debris", "16_debris", 0.20, 0.9, 1.25)
    ]

    for tx, tz, _, _, _ in trees:
        # Cluster 1-2 undergrowth elements near tree base
        if random.random() < 0.75:
            u_angle = random.uniform(0, math.pi * 2)
            u_dist = random.uniform(1.2, 2.5)
            ux = tx + math.cos(u_angle) * u_dist
            uz = tz + math.sin(u_angle) * u_dist
            if abs(ux) < 63 and abs(uz) < 63 and not is_in_exclusion_zone(ux, uz):
                roll = random.random()
                chosen_u = under_types[0] if roll < 0.50 else (under_types[1] if roll < 0.85 else under_types[2])
                rot_y = random.uniform(0, math.pi * 2)
                scale = random.uniform(chosen_u[3], chosen_u[4])
                undergrowth.append((ux, uz, chosen_u, (rot_y, scale)))

    # Additional trail edge undergrowth
    for _ in range(35):
        ux = random.uniform(-40, 40)
        uz = random.uniform(-40, 40)
        if not is_in_exclusion_zone(ux, uz) and abs(ux) < 60 and abs(uz) < 60:
            roll = random.random()
            chosen_u = under_types[0] if roll < 0.45 else (under_types[1] if roll < 0.80 else under_types[2])
            rot_y = random.uniform(0, math.pi * 2)
            scale = random.uniform(chosen_u[3], chosen_u[4])
            undergrowth.append((ux, uz, chosen_u, (rot_y, scale)))

    print(f"Generated {len(undergrowth)} undergrowth instances!")

    # Format Godot 4 Transform3D matrix
    def make_transform(x, y, z, rot_y, scale):
        c = math.cos(rot_y) * scale
        s = math.sin(rot_y) * scale
        return f"Transform3D({c:.6f}, 0, {s:.6f}, 0, {scale:.6f}, 0, {-s:.6f}, 0, {c:.6f}, {x:.2f}, {y:.2f}, {z:.2f})"

    # Generate tree node strings
    tree_nodes = []
    for i, (x, z, arch, _, (rot_y, scale)) in enumerate(trees):
        node_name = f"{arch[0]}_{i+1:03d}"
        t_str = make_transform(x, 0.0, z, rot_y, scale)
        node_str = f'[node name="{node_name}" parent="Trees" instance=ExtResource("{arch[1]}")]\ntransform = {t_str}\n'
        tree_nodes.append(node_str)

    # Generate undergrowth node strings
    undergrowth_nodes = []
    for i, (x, z, u_type, (rot_y, scale)) in enumerate(undergrowth):
        node_name = f"{u_type[0]}_{i+1:03d}"
        t_str = make_transform(x, 0.0, z, rot_y, scale)
        node_str = f'[node name="{node_name}" parent="Undergrowth" instance=ExtResource("{u_type[1]}")]\ntransform = {t_str}\n'
        undergrowth_nodes.append(node_str)

    return "\n".join(tree_nodes), "\n".join(undergrowth_nodes)

if __name__ == "__main__":
    t_nodes, u_nodes = generate_forest()
    with open("assets/models/generated_trees.txt", "w") as f:
        f.write(t_nodes)
    with open("assets/models/generated_undergrowth.txt", "w") as f:
        f.write(u_nodes)
    print("Exported generated_trees.txt and generated_undergrowth.txt!")
