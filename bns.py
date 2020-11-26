"""
This Python module is an interface to the software tool BNS for
the computation of attractors in synchronous Boolean Networks.
"""
import io
import subprocess
import pandas as pd
import sys

from colomoto.types import *
from colomoto_jupyter.sessionfiles import *

class BNSModel(object):
    def __init__(self, filename, names=None):
        self.filename = filename
        self.names = names
        # TODO: if names is None, try sniffing them from comments

def _get_model(obj):
    if isinstance(obj, BNSModel):
        return obj

    def biolqm_import(biolqm, obj):
        cnetfile = new_output_file(".cnet")
        assert biolqm.save(obj, cnetfile)
        names = [str(n) for n in obj.getComponents()]
        return BNSModel(cnetfile, names)

    if "biolqm" in sys.modules:
        biolqm = sys.modules["biolqm"]
        if biolqm.is_biolqm_object(obj):
            return biolqm_import(biolqm, obj)
    if "ginsim" in sys.modules:
        ginsim = sys.modules["ginsim"]
        if ginsim.is_ginsim_object(obj):
            biolqm = import_colomoto_tool("biolqm")
            obj = ginsim.to_biolqm(obj)
            return biolqm_import(biolqm, obj)
    assert isinstance(obj, str), "unsupported model input"
    return BNSModel(obj)


def load(filename):
    return _get_model(filename)

def fixpoints(model):
    """
    Compute the fixed points of the given Boolean network `bn`.

    `model` should be the path to a file in CNET format or a bioLQM or GINsim
    object

    Returns None or a list of ``colomoto.types.State``.
    """
    return attractors(model, length=1)


def attractors(model, length=None):
    """
    Compute the attractors of the given Boolean network `bn`.

    `model` should be the path to a file in CNET format or a bioLQM or GINsim
    object

    `length` enables to search only attractors of a specific length (or its factors)

    Returns None if no attractors are found (if a max length is specified), 
    or a list of ``colomoto.types.State`` if all attractors are fixed points,
    otherwise a list of ``colomoto.types.HypercubeCollection``.
    """

    model = _get_model(model)

    args = [ "bns" ]
    if length:
        args += [  "-l", str(length) ]
    args += [ model.filename ]

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

    return [ _as_states(cur, nvar, model.names) for cur in attractors ]


def _as_states(attr, nvar, names):
    widths = [ 1 for _ in range(nvar) ]
    with io.StringIO(attr) as stream:
        df = pd.read_fwf(stream, widths=widths, header=None)
        if names:
            df.columns = names
        if df.shape[0] == 1:
            return State(df.to_dict(orient="records")[0])
        return HypercubeCollection(df.to_dict(orient="records"))

