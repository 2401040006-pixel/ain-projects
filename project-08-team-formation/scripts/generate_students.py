"""Generate synthetic student records for Project 08 (Smart Team Formation Optimizer).

This script only *samples data*. It does not form teams, compute an objective,
run Hill Climbing, or run Simulated Annealing -- those are the graded student
core in `starter/student_core.py` (`objective`, `hill_climbing`,
`simulated_annealing`). Do not import this script's output as a shortcut for
that core.

All rows produced by this script are synthetic educational data. They do not
describe any real student.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

ROLES: Sequence[str] = ("Leader", "Coder", "Researcher", "Presenter")
AVAILABILITY_SLOTS: Sequence[str] = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
SKILL_MIN, SKILL_MAX = 1, 10

FIELDNAMES = [
    "student_id",
    "programming",
    "mathematics",
    "presentation",
    "preferred_role",
    "availability_vector",
]


def _sample_availability(rng: random.Random) -> str:
    """Sample a 6-bit availability string, one bit per weekday slot in
    AVAILABILITY_SLOTS order. Resamples on the all-zero case (a student must
    be available at least one slot) using the same rng stream so the process
    stays deterministic for a fixed seed.
    """
    while True:
        bits = "".join(str(rng.randint(0, 1)) for _ in AVAILABILITY_SLOTS)
        if "1" in bits:
            return bits


def generate_students(n: int, seed: int) -> List[Dict[str, object]]:
    """Sample `n` synthetic student rows.

    Sampling is deterministic for a fixed (n, seed) pair: exactly one
    `random.Random(seed)` stream is drawn from, in a fixed per-student field
    order (programming, mathematics, presentation, preferred_role,
    availability_vector), so regenerating with the same arguments reproduces
    the committed file byte-for-byte.
    """
    if n < 1:
        raise ValueError("n must be a positive integer")

    rng = random.Random(seed)
    rows: List[Dict[str, object]] = []
    for i in range(1, n + 1):
        student_id = f"S{i:03d}"
        programming = rng.randint(SKILL_MIN, SKILL_MAX)
        mathematics = rng.randint(SKILL_MIN, SKILL_MAX)
        presentation = rng.randint(SKILL_MIN, SKILL_MAX)
        preferred_role = rng.choice(ROLES)
        availability_vector = _sample_availability(rng)
        rows.append(
            {
                "student_id": student_id,
                "programming": programming,
                "mathematics": mathematics,
                "presentation": presentation,
                "preferred_role": preferred_role,
                "availability_vector": availability_vector,
            }
        )
    return rows


def write_csv(rows: List[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _default_output(n: int, seed: int) -> Path:
    if n == 60 and seed == 42:
        # Matches the committed sample so `--seed 42` (the default) is
        # reproducible byte-for-byte against data/students_seed42.csv, as
        # checked by data/SHA256SUMS.
        return DATA_DIR / f"students_seed{seed}.csv"
    return DATA_DIR / f"students_n{n}_seed{seed}.csv"


def write_sha256sums(paths: Sequence[Path], sums_path: Path) -> None:
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Sample synthetic student records for team formation. All output "
            "is synthetic educational data, not real student records."
        )
    )
    parser.add_argument("--n", type=int, default=60, help="Number of students to sample (default: 60).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path. Defaults to data/students_seed<seed>.csv for n=60, seed=42.",
    )
    parser.add_argument(
        "--write-sha256sums",
        action="store_true",
        help="Also (re)write data/SHA256SUMS covering the config/scenarios/student files.",
    )
    args = parser.parse_args(argv)

    rows = generate_students(args.n, args.seed)
    output_path = args.output or _default_output(args.n, args.seed)
    write_csv(rows, output_path)
    print(f"Wrote {len(rows)} synthetic rows (seed={args.seed}) to {output_path}")

    if args.write_sha256sums:
        covered = [
            DATA_DIR / "config.json",
            DATA_DIR / "scenarios.json",
            DATA_DIR / "students_seed42.csv",
        ]
        write_sha256sums(covered, DATA_DIR / "SHA256SUMS")
        print(f"Wrote checksums to {DATA_DIR / 'SHA256SUMS'}")


if __name__ == "__main__":
    main()
