"""SYNTHETIC vectors only: local exact dot-product replay at dimensions 512/128.

NOT a face extractor, a deployable identity system, biometric accuracy, ANN recall
or inference benchmark. 1m vectors require actual target RAM/flash measurements.
Requires NumPy; fixed seed / deterministic inputs used only for comparisons.
"""
from __future__ import annotations
import argparse
import json
import time
import numpy as np

def synthetic_search(seed: int, gallery_size: int, dim: int, queries: int) -> dict:
    if dim not in (128,512) or not 1 <= gallery_size <= 1_000_000 or not 1 <= queries <= 1000:
        raise ValueError("unsupported synthetic replay size")
    rng=np.random.default_rng(seed)
    gallery=rng.standard_normal((gallery_size,dim),dtype=np.float32)
    gallery/=np.maximum(np.linalg.norm(gallery,axis=1,keepdims=True),1e-9)
    targets=rng.standard_normal((queries,dim),dtype=np.float32)
    targets/=np.maximum(np.linalg.norm(targets,axis=1,keepdims=True),1e-9)
    begin=time.perf_counter()
    results=[int(np.argmax(gallery @ row)) for row in targets]
    elapsed=time.perf_counter()-begin
    return {"type":"SYNTHETIC_EXACT_SEARCH_NOT_BIOMETRIC",
            "seed":seed,"gallery":gallery_size,"dim":dim,"queries":queries,
            "vector_bytes":int(gallery.nbytes),"indices":results,
            "elapsed_ms_HOST_DEPENDENT":round(1000*elapsed,4)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=7)
    p.add_argument("--gallery",type=int,default=1000)
    p.add_argument("--dim",type=int,choices=(128,512),default=512)
    p.add_argument("--queries",type=int,default=4)
    a=p.parse_args()
    print(json.dumps(synthetic_search(a.seed,a.gallery,a.dim,a.queries),sort_keys=True))
if __name__=="__main__":
    main()
