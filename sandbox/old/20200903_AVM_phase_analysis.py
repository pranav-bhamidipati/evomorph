import sys
import os
import numpy as np
import pandas as pd
import tqdm
import datetime
import numba
from glob import glob

########################

os.chdir("/home/ubuntu/git/evomorph/data/2020-09-03_avm_phase_sims/")

@numba.njit
def get_D_eff(X0, Xmax, L, tmax, v0, Dr, n=19):
    
    X0_norm = X0 - L/2
    center_cells = np.argsort(np.sqrt(X0_norm[:, 0]**2 + X0_norm[:, 1]**2))[:n]
    
    dX = np.fmod(Xmax[center_cells] - X0[center_cells], L/2)
    dr2 = np.zeros(n, dtype=np.float32)
    for i in range(n):
        dr2[i] = dX[i, 0] ** 2 + dX[i, 1] ** 2
    
    Ds = dr2.mean() / (4*tmax)
    D0 = v0**2/(2*Dr)
    return Ds / D0

def npy_to_D_eff(fname, metadata, n=7):
    
    X = np.load(fname)
#     X = X[:X.shape[0]//2]
    n_t = X.shape[0]
    X0, Xmax = X[0], X[-1]
    kwargs = metadata.loc[metadata["filename"] == fname, :].to_dict()
    kwargs = {k: tuple(v.values())[0] for k, v in kwargs.items()}

    return get_D_eff(
        X0,
        Xmax,
        kwargs["L"],
        n_t * kwargs["dt"],
        kwargs["v0"],
        kwargs["Dr"],
        n=n
    )

metadata = pd.read_csv("metadata.csv", index_col=0)
files = list(metadata["filename"])
# files = [os.path.abspath(file) for file in files]

iterator = enumerate(files)
iterator = tqdm.tqdm(iterator)

D_eff = np.empty(metadata.shape[0])
for i, file in iterator:
    D_eff[i] = npy_to_D_eff(file, metadata)

metadata["D_eff"] = D_eff
metadata.to_csv("metadata_Deff2.csv", index="filename")
