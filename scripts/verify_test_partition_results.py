"""Verify complete non-overlapping test distribution before combining coverage."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def verify(root, count):
    selections = sorted(Path(root).rglob("probe-selection-result.json"))
    if len(selections) != count: raise ValueError("Missing coverage partition metadata")
    seen = set(); indices = set(); eligible = None
    for file in selections:
        data = json.loads(file.read_text(encoding="utf-8"))
        if data["count"] != count or data["index"] in indices: raise ValueError("Invalid or repeated partition")
        indices.add(data["index"])
        population = set(data["eligible"])
        if eligible is None: eligible = population
        if population != eligible: raise ValueError("Different test populations")
        selected = set(data["selected"])
        if len(selected) != len(data["selected"]) or seen & selected: raise ValueError("Repeated test cases")
        seen.update(selected)
        execution = json.loads(file.with_name("probe-execution-result.json").read_text(encoding="utf-8"))
        if execution["exit"] != 0: raise ValueError("Incomplete or failed test partition")
        completed = {row["id"] for row in execution["reports"] if row["phase"] == "call" or (row["phase"] == "setup" and row["outcome"] == "skipped")}
        if completed != selected: raise ValueError("Selected test cases were not fully executed")
    if indices != set(range(count)) or seen != eligible: raise ValueError("Missing test cases")
    return len(seen)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("root"); parser.add_argument("--partitions",type=int,required=True)
    args = parser.parse_args(); print("Complete coverage test population:",verify(args.root,args.partitions))

if __name__ == "__main__": main()
