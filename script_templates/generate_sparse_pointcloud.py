import os
from pathlib import Path
import subprocess
import re
import numpy as np
import pandas as pd


def parse_campari_rap(fn_rap):
    matched_points = []
    with open(fn_rap, 'r') as f:
        for line in f:
            if re.match(r'^\*\d', line):
                split = line.replace('*', '').strip().split()
                if len(split) == 4:
                    matched_points.append(split)

    data = np.array(matched_points).astype(np.float32)
    pc_df = pd.DataFrame(data=data, columns=['x', 'y', 'z', 'pds'])

    return pc_df

# experiments needs to have: ori-name, experiment code, details
experiments_df = pd.read_csv("experiments.csv")


for ori in experiments_df.ori_final:
    print(ori)
    if Path(f"{ori}_rapport.txt").exists():
        print(f"converting campari report to {ori}_sparse.ply")
        pc_df = parse_campari_rap(f"{ori}_rapport.txt")
        pc_df[['x', 'y', 'z']].to_csv('tmp_pc.txt', sep=' ', index=False)

        p = subprocess.Popen(['pdal', 'translate', 'tmp_pc.txt', f"{ori}_sparse.ply"])
        p.wait()

        os.remove('tmp_pc.txt')
