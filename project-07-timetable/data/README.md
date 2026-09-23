# Data dictionary — Project 07 (Timetable Scheduler)

All names, course titles, and cohorts below are **synthetic educational data** for a campus CSP scheduling exercise. This is an educational model, not live university scheduling data.

## Campus Context: Rooms and Periods

- **Lecture Rooms**: `R01` (C201, 60 seats), `R02` (C203, 45 seats), `R03` (C301, 40 seats), `R04` (C303, 35 seats).
- **Computer Labs**: `R05` (Lab C1, 30 seats), `R06` (Lab C2, 25 seats), `R07` (Lab C3, 20 seats).
- **Class Periods**:
  - Period 1: `07:30–09:00`
  - Period 2: `09:15–10:45`
  - Period 3: `13:00–14:30`
  - Period 4: `14:45–16:15`

## Folder layout

```text
data/
├── README.md
├── instance_feasible/          # standard, easy instance — start here
├── instance_restricted_rooms/  # same courses/lecturers, only 4 rooms (tight capacity)
├── instance_extra_lecturer/    # same resources, +1 hard lecturer constraint
└── instance_unsat/             # deliberately unsatisfiable — no solution exists
```

Each instance folder has the **same five files**, the CSP for that instance:

```text
instance_<name>/
├── courses.csv
├── lecturers.csv
├── rooms.csv
├── timeslots.csv
└── constraints.json
```

There is no `sample_solution.json` or `feasible_witness.json` in this folder or anywhere under
`project-07-timetable/`. Legal-assignment witnesses are instructor-only and never shipped to
students; you must write your own solver to find one.

## `timeslots.csv`

| Field | Type | Notes |
|---|---|---|
| `slot_id` | string | Unique id, e.g. `T05`. |
| `day` | string | `Mon`, `Tue`, `Wed`, or `Thu`. |
| `period` | int | Period number within the day (`1`–`4`). |
| `start_time` / `end_time` | string | `HH:MM` class shifts (`07:30-09:00`, `09:15-10:45`, `13:00-14:30`, `14:45-16:15`). |

## `lecturers.csv`

| Field | Type | Notes |
|---|---|---|
| `lecturer_id` | string | Unique id, e.g. `L03`. |
| `name` | string | Fictional name. |
| `available_slots` | string | Either the literal `ALL` (available every timeslot) or a `;`-separated list of `slot_id`s. |

## `rooms.csv`

| Field | Type | Notes |
|---|---|---|
| `room_id` | string | Unique id, e.g. `R01` (C201), `R02` (C203), `R03` (C301), `R04` (C303), `R05` (Lab C1), `R06` (Lab C2), `R07` (Lab C3). |
| `room_type` | string | `Lecture` or `Lab`. |
| `capacity` | int | Maximum seats. |
| `available_slots` | string | `ALL` or a `;`-separated list of `slot_id`s. |

## `courses.csv`

| Field | Type | Notes |
|---|---|---|
| `course_id` | string | Unique id, e.g. `C09`. |
| `course_name` | string | Fictional course title. |
| `cohort` | string | Student cohort, e.g. `CS-2A`. Two courses in the same cohort must not share a slot (students in that cohort would clash). |
| `required_room_type` | string | `Lecture` or `Lab`; the assigned room's `room_type` must match. |
| `min_capacity` | int | The assigned room's `capacity` must be `>=` this value. |
| `eligible_lecturers` | string | `;`-separated list of `lecturer_id`s allowed to teach this course. A single entry means that lecturer is the **only** option — a specialist course. |

## `constraints.json`

```jsonc
{
  "instance_id": "feasible",
  "description": "...",
  "hard_constraints": [ /* names of the hard rules that apply, see below */ ],
  "soft_constraints": [ /* optional, scored rules you may use — see below */ ],
  "extra_constraints": [ /* instance-specific extra hard rules, only in instance_extra_lecturer */ ]
}
```

### Hard constraints (must always hold in any legal assignment)

Every instance's `constraints.json` lists the same seven hard-constraint names. A **variable** is
one course; its **domain** is every `(lecturer_id, room_id, slot_id)` triple. A legal assignment
picks exactly one domain value per course such that:

1. `lecturer_in_eligible_set` — the chosen lecturer is in that course's `eligible_lecturers`.
2. `lecturer_available_at_slot` — the chosen slot is in that lecturer's `available_slots`.
3. `room_type_and_capacity_match` — the chosen room's `room_type` matches `required_room_type` and its `capacity >= min_capacity`.
4. `room_available_at_slot` — the chosen slot is in that room's `available_slots`.
5. `no_room_double_booking` — no two courses share the same room at the same slot.
6. `no_lecturer_double_booking` — no two courses share the same lecturer at the same slot.
7. `no_cohort_double_booking` — no two courses in the same cohort share the same slot.

### `extra_constraints` (only in `instance_extra_lecturer`)

A generic, typed list so the loader/solver can interpret it without hard-coding lecturer names.
Currently one type is used:

```json
{"type": "lecturer_daily_limit", "lecturer_id": "L02", "max_per_day": 1, "reason": "..."}
```

Meaning: the named lecturer may teach at most `max_per_day` courses on the same `day`. This is the
"added lecturer constraint" hardening from the required experiment (see `README.md`).

### Soft constraints (optional, not required to satisfy)

Listed for context; your solver is not required to use them, but the spec invites you to show a
soft-constraint score if you do:

- `cohort_daily_spread` — prefer a cohort's courses spread across different days.
- `lecturer_load_balance` — prefer lecturers teaching a similar number of courses across the week.

## The four instances

| Instance | Courses | Lecturers | Rooms | Slots | Status | Demo it backs |
|---|---:|---:|---:|---:|---|---|
| `instance_feasible` | 16 | 8 | 7 | 16 | Satisfiable (easy) | Demo 1 — standard feasible schedule |
| `instance_restricted_rooms` | 16 | 8 | **4** | 16 | Satisfiable (tight) | Demo 2 — restricted room availability |
| `instance_extra_lecturer` | 16 | 8 | 7 | 16 | Satisfiable (with the extra rule) | Demo 3 — added lecturer constraint |
| `instance_unsat` | 16 | **9** | 7 | 16 | **Unsatisfiable** | Demo 4 — unsatisfiable instance |

- `instance_restricted_rooms` reuses the exact same `courses.csv`/`lecturers.csv` as
  `instance_feasible`, but `rooms.csv` only has 4 rooms (2 `Lecture`, 2 `Lab`) instead of 7. This
  is the "harden by removing rooms" version of the required experiment — already applied for you
  as a demo; your own required-experiment write-up should harden it **further** (see
  `README.md`).
- `instance_extra_lecturer` reuses the exact same courses/lecturers/rooms as `instance_feasible`,
  plus the `lecturer_daily_limit` rule on `L02` above.
- `instance_unsat` replaces two courses (`U01`, `U02`) with a deliberately impossible pair: both
  require lecturer `L09` exclusively, and `L09` has only one available slot (`T05`). See the
  instructor-only `unsat_proof.md` (not shipped to you) for the full argument — but you should be
  able to reconstruct the same argument yourself by reading `courses.csv` and `lecturers.csv` in
  that folder.

## No generator

These four instances are **committed CSV/JSON files**, not procedurally generated. There is no
`scripts/generate_*.py` for this project — the instance sizes are small enough (15–25 courses,
6–10 lecturers, 6–10 rooms, 15–25 slots) that a hand-authored, reproducible instance is simpler
than a generator, and it lets the unsatisfiable instance be constructed precisely instead of
hoped-for from randomness.

## Loading this data

Use `starter/loaders.py`:

```python
from pathlib import Path
import loaders

instance = loaders.load_instance(Path("data/instance_feasible"))
```

`load_instance` validates every hard-constraint precondition it can check statically (unknown
lecturer/room ids referenced by a course, malformed `available_slots`, negative capacities, and so
on). It does **not** search for a solution — that is your job in `starter/student_core.py::solve_csp`.
