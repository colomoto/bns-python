"""
This Python module is an interface to the software tool BNS for
the computation of attractors in synchronous Boolean Networks.
"""
import io
import subprocess
import pandas as pd

from colomoto.types import *


def fixpoints(filename):
    """
    Compute the fixed points of the given Boolean network `bn`.

    `filename` should be the path to a file in CNET format.

    Returns None or a list of ``colomoto.types.State``.
    """
    return attractors(filename, length=1)


def attractors(filename, length=None):
    """
    Compute the attractors of the given Boolean network `bn`.

    `filename` should be the path to a file in CNET format.

    `length` enables to search only attractors of a specific length (or its factors)

    Returns None if no attractors are found (if a max length is specified), 
    or a list of ``colomoto.types.State`` if all attractors are fixed points,
    otherwise a list of ``colomoto.types.HypercubeCollection``.
    """

    # TODO: automagic conversion for some foreign models
    
    args = [ "bns" ]
    if length:
        args += [  "-l", str(length) ]
    args += [ filename ]

    cmd = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    max_len = 0
    attractors = []
    current = []
    nvar = 0
    for line in cmd.stdout:
        if line.startswith(b"0") or line.startswith(b"1"):
            current.append(line.strip().decode("utf-8"))
        elif line .startswith(b"Attractor"):
            if len(current) > max_len:
                max_len = len(current)
                nvar = len(current[0])
            attractors.append("\n".join(current))
            current = []

    if max_len == 0:
        return None
    
    return [ _as_states(cur, nvar) for cur in attractors ]


def _as_states(attr, nvar):
    widths = [ 1 for _ in range(nvar) ]
    with io.StringIO(attr) as stream:
        df = pd.read_fwf(stream, widths=widths, header=None)
        if df.shape[0] == 1:
            return State(df.to_dict(orient="records")[0])
        return HypercubeCollection(df.to_dict(orient="records"))

