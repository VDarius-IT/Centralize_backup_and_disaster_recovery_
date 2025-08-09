#!/usr/bin/env python3
"""
Quick verification of backup manifests in the local backup root.
"""
import os
import json
import argparse

def verify(manifests_dir):
    ok = True
    for fname in os.listdir(manifests_dir):
        if not fname.endswith(".manifest.json"):
            continue
        path = os.path.join(manifests_dir, fname)
        try:
            with open(path) as f:
                m = json.load(f)
            if "target" not in m or "timestamp" not in m:
                print("Invalid manifest:", path)
                ok = False
        except Exception as e:
            print("Error reading manifest:", path, e)
            ok = False
    if ok:
        print("All manifests look valid.")
        return 0
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifests-dir", default="./backups/manifests")
    args = parser.parse_args()
    os.makedirs(args.manifests_dir, exist_ok=True)
    rc = verify(args.manifests_dir)
    exit(rc)

if __name__ == "__main__":
    main()
