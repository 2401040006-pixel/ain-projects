#!/usr/bin/env python3
"""Generate Hanoi University (HANU) Campus Route Planner data (Project 01).

Based on the official HANU Campus Wayfinding Map and 3D schematic diagram:
- Covers key HANU landmarks: Main Gate (Nguyễn Trãi), Buildings A, A1, B, C,
  D1, D2, D3, D4, D5, D6, D7, Library, Green Square, Stadium, Canteen,
  Souvenir Shop, and Parking zones.
- Complies strictly with Project 01 scale:
  - 30-60 nodes (committed: 54 nodes)
  - 50-120 edges (committed: 74 edges)
- Generates 5 realistic scenarios: S1 (normal route), S2 (blocked main road),
  S3 (accessibility route via elevator), S4 (Euclidean vs Manhattan comparison),
  and S5 (isolated attic lab with only stairs -> clean failure in accessibility mode).
- Produces `campus_map.png` (detailed schematic wayfinding map).
- Produces `SHA256SUMS` matching committed CSV/JSON files.
"""
from __future__ import annotations

import argparse
import binascii
import csv
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT_DIR = PROJECT_DIR / "data"

NODE_FIELDS = ["node_id", "name", "x", "y", "floor", "building", "node_type"]
EDGE_FIELDS = [
    "source",
    "target",
    "distance",
    "travel_time",
    "crowd_level",
    "stairs",
    "indoor",
    "accessible",
]

# ---------------------------------------------------------------------------
# HANU Campus Master Nodes Definition
# ---------------------------------------------------------------------------

HANU_NODES_SPEC = [
    # Cổng & Khu Phía Đông (Gate & East)
    ("N_GATE", "Cổng Chính HANU (Nguyễn Trãi)", 575.0, 196.0, 0, "Campus Grounds", "plaza"),
    ("N_SOUVENIR", "Cửa Hàng HANU Souvenir", 550.0, 125.0, 1, "HANU Souvenir", "room"),
    ("N_B_ENTRANCE", "Sảnh Nhà B", 530.0, 250.0, 1, "Nhà B", "entrance"),
    ("N_B_101", "Phòng Học B.101", 545.0, 290.0, 1, "Nhà B", "room"),
    ("N_A1_GARDEN", "Sân Vườn A1", 480.0, 265.0, 0, "Campus Grounds", "plaza"),
    ("N_A1_ENTRANCE", "Sảnh Nhà A1", 480.0, 340.0, 1, "Nhà A1", "entrance"),
    ("N_A1_HALL", "Hội Trường A1", 450.0, 365.0, 1, "Nhà A1", "room"),
    ("N_A1_201", "Phòng Học A1.201", 515.0, 365.0, 2, "Nhà A1", "room"),
    ("N_A1_PARKING", "Bãi Đỗ Xe A1", 500.0, 440.0, 0, "Campus Grounds", "plaza"),
    ("N_A_ENTRANCE", "Sảnh Nhà A", 412.0, 230.0, 1, "Nhà A", "entrance"),
    ("N_A_101", "Phòng Học A.101", 412.0, 305.0, 1, "Nhà A", "room"),

    # Khu D1, D2, D3 & Tòa Nhà C (Khoa CNTT)
    ("N_D1_ENTRANCE", "Sảnh Nhà D1", 515.0, 175.0, 1, "Nhà D1", "entrance"),
    ("N_D1_101", "Phòng D1.101", 515.0, 105.0, 1, "Nhà D1", "room"),
    ("N_D2_ENTRANCE", "Sảnh Nhà D2", 475.0, 175.0, 1, "Nhà D2", "entrance"),
    ("N_D2_101", "Phòng D2.101", 475.0, 105.0, 1, "Nhà D2", "room"),
    ("N_D3_ENTRANCE", "Sảnh Nhà D3", 435.0, 175.0, 1, "Nhà D3", "entrance"),
    ("N_D3_101", "Phòng D3.101", 435.0, 105.0, 1, "Nhà D3", "room"),
    ("N_C_ENTRANCE", "Sảnh Chính Nhà C", 482.0, 68.0, 1, "Nhà C", "entrance"),
    ("N_C_101", "Phòng Lab C.101", 445.0, 38.0, 1, "Nhà C", "room"),
    ("N_C_201", "Phòng Lab & Server C.201", 520.0, 38.0, 2, "Nhà C", "room"),
    ("N_C_ATTIC", "Phòng Gác Mái Kỹ Thuật Nhà C", 482.0, 24.0, 3, "Nhà C", "room"),

    # Sân Vận Động & Trung Tâm
    ("N_STADIUM_EAST", "Khán Đài Đông Sân Vận Động", 360.0, 282.0, 0, "HANU Stadium", "plaza"),
    ("N_STADIUM_WEST", "Khán Đài Tây Sân Vận Động", 190.0, 282.0, 0, "HANU Stadium", "plaza"),
    ("N_STADIUM_PITCH", "Sân Cỏ & Đường Chạy", 275.0, 282.0, 0, "HANU Stadium", "plaza"),
    ("N_GREEN_SQUARE", "Quảng Trường Xanh", 355.0, 155.0, 0, "Campus Grounds", "plaza"),
    ("N_LIB_ENTRANCE", "Sảnh Thư Viện HANU", 355.0, 125.0, 1, "Thư Viện", "entrance"),
    ("N_LIB_101", "Phòng Đọc Thư Viện", 335.0, 100.0, 1, "Thư Viện", "room"),
    ("N_LIB_201", "Phòng Đa Phương Tiện Thư Viện", 375.0, 100.0, 2, "Thư Viện", "room"),
    ("N_E_ENTRANCE", "Sảnh Nhà E", 355.0, 68.0, 1, "Nhà E", "entrance"),
    ("N_E_101", "Giảng Đường E.101", 355.0, 42.0, 1, "Nhà E", "room"),

    # Cụm D4, D5, D6 & Bãi Đỗ Xe D4
    ("N_D4_ENTRANCE", "Sảnh Nhà D4", 255.0, 175.0, 1, "Nhà D4", "entrance"),
    ("N_D4_101", "Phòng D4.101", 255.0, 115.0, 1, "Nhà D4", "room"),
    ("N_D4_PARKING", "Bãi Đỗ Xe D4", 205.0, 140.0, 0, "Campus Grounds", "plaza"),
    ("N_D5_ENTRANCE", "Sảnh Nhà D5", 155.0, 175.0, 1, "Nhà D5", "entrance"),
    ("N_D5_101", "Phòng D5.101", 155.0, 115.0, 1, "Nhà D5", "room"),
    ("N_D6_ENTRANCE", "Sảnh Nhà D6", 205.0, 75.0, 1, "Nhà D6", "entrance"),
    ("N_D6_101", "Phòng D6.101", 175.0, 45.0, 1, "Nhà D6", "room"),

    # Căn Tin & Khu Phía Tây (D7)
    ("N_CANTEEN_ENTRANCE", "Sảnh Căn Tin", 140.0, 280.0, 1, "Căn Tin", "entrance"),
    ("N_CANTEEN_HALL", "Khu Ẩm Thực Căn Tin", 115.0, 255.0, 1, "Căn Tin", "room"),
    ("N_D7_ENTRANCE", "Sảnh Ký Túc Xá D7", 65.0, 215.0, 1, "Ký Túc Xá D7", "entrance"),
    ("N_D7_101", "Phòng D7.101", 35.0, 215.0, 1, "Ký Túc Xá D7", "room"),
    ("N_D7_GROCERY", "Cửa Hàng Tạp Hóa D7", 40.0, 325.0, 1, "Dịch Vụ D7", "room"),
    ("N_D7_PARKING", "Bãi Đỗ Xe D7", 60.0, 60.0, 0, "Campus Grounds", "plaza"),

    # Trục Đường & Điểm Giao Cắt (Walkway & Road Waypoints)
    ("W_A_B", "Trục Đường Trước Nhà B & Sân Vườn A1", 480.0, 196.0, 0, "Campus Grounds", "hallway"),
    ("W_CROSS_EAST", "Ngã Tư Trung Tâm Phía Đông", 375.0, 196.0, 0, "Campus Grounds", "hallway"),
    ("W_SOUTH_STADIUM", "Trục Đường Nam Sân Vận Động", 275.0, 196.0, 0, "Campus Grounds", "hallway"),
    ("W_CROSS_WEST", "Ngã Tư Căn Tin - Sân Vận Động", 155.0, 196.0, 0, "Campus Grounds", "hallway"),
    ("W_WEST_ALLEY", "Lối Rẽ KTX D7", 75.0, 196.0, 0, "Campus Grounds", "hallway"),
    ("W_NE_CORNER", "Lối Rẽ Đông Bắc Sân Vận Động", 375.0, 370.0, 0, "Campus Grounds", "hallway"),
    ("W_A1_ROAD", "Đường Lên Bãi Xe A1", 500.0, 395.0, 0, "Campus Grounds", "hallway"),
    ("W_NORTH_STADIUM", "Đường Vành Đai Bắc Sân Vận Động", 275.0, 370.0, 0, "Campus Grounds", "hallway"),
    ("W_NW_CORNER", "Lối Rẽ Tây Bắc Sân Vận Động", 155.0, 370.0, 0, "Campus Grounds", "hallway"),
    ("W_SOUTH_EAST", "Lối Đi D3 - Nhà C", 405.0, 100.0, 0, "Campus Grounds", "hallway"),
    ("W_SOUTH_CENTRAL", "Lối Đi Thư Viện - Giảng Đường D", 295.0, 100.0, 0, "Campus Grounds", "hallway"),
]

# ---------------------------------------------------------------------------
# HANU Campus Master Edges Definition
# ---------------------------------------------------------------------------

HANU_EDGES_SPEC = [
    # 1. Trục Đường Chính Đông - Tây (Main East-West Spine)
    ("N_GATE", "W_A_B", "high", False, False, True),
    ("W_A_B", "W_CROSS_EAST", "medium", False, False, True),
    ("W_CROSS_EAST", "W_SOUTH_STADIUM", "medium", False, False, True),
    ("W_SOUTH_STADIUM", "W_CROSS_WEST", "medium", False, False, True),
    ("W_CROSS_WEST", "W_WEST_ALLEY", "medium", False, False, True),

    # 2. Vành Đai Bắc Sân Vận Động (North Stadium Loop)
    ("W_CROSS_EAST", "W_NE_CORNER", "low", False, False, True),
    ("W_NE_CORNER", "W_NORTH_STADIUM", "low", False, False, True),
    ("W_NORTH_STADIUM", "W_NW_CORNER", "low", False, False, True),
    ("W_NW_CORNER", "N_CANTEEN_ENTRANCE", "medium", False, False, True),
    ("N_CANTEEN_ENTRANCE", "W_CROSS_WEST", "high", False, False, True),

    # 3. Khu Đông Bắc (A1, A1 Garden, Bãi Xe A1, Nhà B, Nhà A)
    ("W_A_B", "N_A1_GARDEN", "low", False, False, True),
    ("N_A1_GARDEN", "N_A1_ENTRANCE", "low", False, False, True),
    ("W_NE_CORNER", "W_A1_ROAD", "low", False, False, True),
    ("W_A1_ROAD", "N_A1_ENTRANCE", "low", False, False, True),
    ("W_A1_ROAD", "N_A1_PARKING", "low", False, False, True),
    ("W_A_B", "N_B_ENTRANCE", "medium", False, False, True),
    ("N_A1_GARDEN", "N_B_ENTRANCE", "low", False, False, True),
    ("W_CROSS_EAST", "N_A_ENTRANCE", "medium", False, False, True),
    ("N_A1_GARDEN", "N_A_ENTRANCE", "low", False, False, True),

    # 4. Khu Cổng, Souvenir & D1-D3
    ("N_GATE", "N_SOUVENIR", "low", False, False, True),
    ("W_A_B", "N_D1_ENTRANCE", "low", False, False, True),
    ("W_A_B", "N_D2_ENTRANCE", "low", False, False, True),
    ("W_A_B", "N_D3_ENTRANCE", "low", False, False, True),
    ("W_CROSS_EAST", "N_D3_ENTRANCE", "low", False, False, True),

    # 5. Cụm D1-D3 & Tòa Nhà C
    ("W_CROSS_EAST", "W_SOUTH_EAST", "low", False, False, True),
    ("N_D3_ENTRANCE", "W_SOUTH_EAST", "low", False, False, True),
    ("N_D1_ENTRANCE", "N_D1_101", "low", False, True, True),
    ("N_D2_ENTRANCE", "N_D2_101", "low", False, True, True),
    ("N_D3_ENTRANCE", "N_D3_101", "low", False, True, True),
    ("W_SOUTH_EAST", "N_C_ENTRANCE", "low", False, False, True),
    ("N_D1_101", "N_C_ENTRANCE", "low", False, False, True),

    # 6. Bên Trong Nhà C (CNTT)
    ("N_C_ENTRANCE", "N_C_101", "low", False, True, True),
    # Cầu thang bộ tầng 1 -> 2
    ("N_C_ENTRANCE", "N_C_201", "low", True, True, False),
    # Thang máy tầng 1 -> 2 (accessible)
    ("N_C_ENTRANCE", "N_C_201", "low", False, True, True),
    # Cầu thang gác mái kỹ thuật (stairs-only, isolated -> S5 failure target)
    ("N_C_201", "N_C_ATTIC", "low", True, True, False),

    # 7. Khu Trung Tâm (Quảng Trường Xanh, Thư Viện, Nhà E)
    ("W_CROSS_EAST", "N_GREEN_SQUARE", "low", False, False, True),
    ("W_SOUTH_STADIUM", "N_GREEN_SQUARE", "low", False, False, True),
    ("W_SOUTH_EAST", "N_GREEN_SQUARE", "low", False, False, True),
    ("N_GREEN_SQUARE", "N_LIB_ENTRANCE", "low", False, False, True),
    ("N_LIB_ENTRANCE", "N_LIB_101", "low", False, True, True),
    ("N_LIB_ENTRANCE", "N_LIB_201", "low", True, True, False),
    ("N_LIB_ENTRANCE", "N_LIB_201", "low", False, True, True),
    ("N_LIB_ENTRANCE", "N_E_ENTRANCE", "low", False, False, True),
    ("N_E_ENTRANCE", "N_E_101", "low", False, True, True),

    # 8. Sân Vận Động HANU
    ("W_CROSS_EAST", "N_STADIUM_EAST", "medium", False, False, True),
    ("W_SOUTH_STADIUM", "N_STADIUM_PITCH", "low", False, False, True),
    ("W_NORTH_STADIUM", "N_STADIUM_PITCH", "low", False, False, True),
    ("N_STADIUM_EAST", "N_STADIUM_PITCH", "low", False, False, True),
    ("N_STADIUM_WEST", "N_STADIUM_PITCH", "low", False, False, True),
    ("N_STADIUM_WEST", "W_CROSS_WEST", "medium", False, False, True),

    # 9. Cụm D4, D5, D6 & Bãi Đỗ Xe D4
    ("W_SOUTH_STADIUM", "N_D4_ENTRANCE", "low", False, False, True),
    ("N_D4_ENTRANCE", "N_D4_101", "low", False, True, True),
    ("N_D4_ENTRANCE", "N_D4_PARKING", "low", False, False, True),
    ("N_D4_PARKING", "N_D5_ENTRANCE", "low", False, False, True),
    ("N_D5_ENTRANCE", "W_CROSS_WEST", "low", False, False, True),
    ("N_D5_ENTRANCE", "N_D5_101", "low", False, True, True),
    ("W_SOUTH_STADIUM", "W_SOUTH_CENTRAL", "low", False, False, True),
    ("W_SOUTH_CENTRAL", "N_LIB_ENTRANCE", "low", False, False, True),
    ("W_SOUTH_CENTRAL", "N_D4_101", "low", False, False, True),
    ("W_SOUTH_CENTRAL", "N_D6_ENTRANCE", "low", False, False, True),
    ("W_SOUTH_CENTRAL", "N_E_ENTRANCE", "low", False, False, True),
    ("N_D6_ENTRANCE", "N_D6_101", "low", False, True, True),
    ("N_D5_101", "N_D6_ENTRANCE", "low", False, False, True),

    # 10. Căn Tin & Khu Phía Tây (D7)
    ("N_CANTEEN_ENTRANCE", "N_CANTEEN_HALL", "high", False, True, True),
    ("W_WEST_ALLEY", "N_D7_ENTRANCE", "low", False, False, True),
    ("N_D7_ENTRANCE", "N_D7_101", "low", False, True, True),
    ("W_WEST_ALLEY", "N_D7_GROCERY", "low", False, False, True),
    ("N_D7_GROCERY", "W_NW_CORNER", "low", False, False, True),
    ("W_WEST_ALLEY", "N_D7_PARKING", "low", False, False, True),
    ("N_D7_PARKING", "N_D5_101", "low", False, False, True),

    # 11. Bên Trong Nhà A, A1, B
    ("N_B_ENTRANCE", "N_B_101", "low", False, True, True),
    ("N_A_ENTRANCE", "N_A_101", "low", False, True, True),
    ("N_A1_ENTRANCE", "N_A1_HALL", "medium", False, True, True),
    ("N_A1_ENTRANCE", "N_A1_201", "low", True, True, False),
    ("N_A1_ENTRANCE", "N_A1_201", "low", False, True, True),
]


def build_campus(seed: int = 42) -> Tuple[List[dict], List[dict], dict]:
    """Build the deterministic HANU campus graph."""
    nodes: List[dict] = [
        {
            "node_id": n[0],
            "name": n[1],
            "x": float(n[2]),
            "y": float(n[3]),
            "floor": int(n[4]),
            "building": n[5],
            "node_type": n[6],
        }
        for n in HANU_NODES_SPEC
    ]

    node_dict = {n["node_id"]: n for n in nodes}

    def euclid(u: str, v: str) -> float:
        nu, nv = node_dict[u], node_dict[v]
        return round(math.hypot(nu["x"] - nv["x"], nu["y"] - nv["y"]), 1)

    def calc_travel_time(dist: float, stairs: bool, crowd: str) -> float:
        speed = 1.4
        if stairs:
            speed *= 0.6
        if crowd == "medium":
            speed *= 0.85
        elif crowd == "high":
            speed *= 0.6
        return round(dist / speed, 2)

    edges: List[dict] = []
    for src, tgt, crowd, stairs, indoor, accessible in HANU_EDGES_SPEC:
        d = euclid(src, tgt)
        if d == 0:
            d = 10.0
        tt = calc_travel_time(d, stairs, crowd)
        edges.append(
            {
                "source": src,
                "target": tgt,
                "distance": d,
                "travel_time": tt,
                "crowd_level": crowd,
                "stairs": stairs,
                "indoor": indoor,
                "accessible": accessible,
            }
        )

    meta = {
        "seed": seed,
        "campus": "Hanoi University (HANU)",
        "num_nodes": len(nodes),
        "num_edges": len(edges),
    }

    return nodes, edges, meta


def build_scenarios(nodes: List[dict], edges: List[dict], meta: dict) -> dict:
    """Build the 5 realistic route planner scenarios for HANU campus."""
    scenarios = [
        {
            "id": "S1_normal_route",
            "class": "normal",
            "start": "N_GATE",
            "end": "N_D7_101",
            "constraints": {},
            "description": (
                "Lộ trình cơ bản không có ràng buộc: Đi từ Cổng Chính HANU "
                "(đường Nguyễn Trãi) đến Phòng D7.101 (Ký túc xá D7). "
                "Thuật toán tìm đường trực tiếp dọc theo trục chính của trường."
            ),
        },
        {
            "id": "S2_blocked_edge",
            "class": "difficult",
            "start": "N_GATE",
            "end": "N_D7_101",
            "constraints": {
                "blocked_edges": [["W_CROSS_EAST", "W_SOUTH_STADIUM"]]
            },
            "description": (
                "Cùng điểm đi/đến như S1, nhưng đoạn trục đường chính Nam Sân Vận Động "
                "(W_CROSS_EAST - W_SOUTH_STADIUM) đang sửa chữa/bị chặn. "
                "Thuật toán phải tìm được lộ trình vòng hợp lệ (qua Quảng Trường Xanh "
                "hoặc Vành Đai Bắc Sân Vận Động) thay vì báo thất bại."
            ),
        },
        {
            "id": "S3_accessibility_mode",
            "class": "difficult",
            "start": "N_GATE",
            "end": "N_C_201",
            "constraints": {"accessible_only": True},
            "description": (
                "Đi từ Cổng Chính lên Phòng Lab & Server Tầng 2 Nhà C "
                "với chế độ hỗ trợ tiếp cận (accessible_only=True). "
                "Lộ trình bắt buộc phải tránh cầu thang bộ và sử dụng thang máy / lối đi bằng phẳng."
            ),
        },
        {
            "id": "S4_heuristic_comparison",
            "class": "extra",
            "start": "N_A1_PARKING",
            "end": "N_D6_101",
            "constraints": {},
            "heuristics": ["euclidean", "manhattan"],
            "description": (
                "Thí nghiệm so sánh hàm heuristic: Chạy A* từ Bãi Đỗ Xe A1 (góc Đông Bắc) "
                "đến Phòng D6.101 (góc Tây Nam) lần lượt với Heuristic Euclidean và Heuristic Manhattan. "
                "So sánh chi phí đường đi, số node đã mở rộng (expanded nodes) và thời gian thực thi."
            ),
        },
        {
            "id": "S5_accessibility_no_path",
            "class": "failure",
            "start": "N_GATE",
            "end": "N_C_ATTIC",
            "constraints": {"accessible_only": True},
            "description": (
                "Phòng Gác Mái Kỹ Thuật Nhà C (N_C_ATTIC) chỉ có thể tiếp cận qua "
                "cầu thang xoắn ốc hẹp (stairs=True, accessible=False) mà không có thang máy. "
                "Khi bật accessible_only=True, thuật toán phải báo 'no path found' một cách an toàn "
                "chứ không bị crash hoặc trả về đường đi vi phạm."
            ),
        },
    ]

    return {
        "seed": meta["seed"],
        "generated_by": "scripts/generate_campus.py",
        "scenarios": scenarios,
    }


def write_nodes_csv(path: Path, nodes: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=NODE_FIELDS)
        writer.writeheader()
        for n in nodes:
            writer.writerow({k: n[k] for k in NODE_FIELDS})


def write_edges_csv(path: Path, edges: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=EDGE_FIELDS)
        writer.writeheader()
        for e in edges:
            row = dict(e)
            row["stairs"] = str(row["stairs"])
            row["indoor"] = str(row["indoor"])
            row["accessible"] = str(row["accessible"])
            writer.writerow({k: row[k] for k in EDGE_FIELDS})


def write_scenarios_json(path: Path, scenarios: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(scenarios, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(out_dir: Path, filenames: List[str]) -> None:
    lines = []
    for name in filenames:
        digest = sha256_of(out_dir / name)
        lines.append(f"{digest}  {name}")
    with open(out_dir / "SHA256SUMS", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Map Rendering (PIL with pure stdlib fallback)
# ---------------------------------------------------------------------------

def _render_with_pil(nodes: List[dict], edges: List[dict], out_path: Path, width: int = 1200, height: int = 900) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False

    min_x, max_x = 0.0, 620.0
    min_y, max_y = 0.0, 470.0

    margin_x = 90
    margin_y = 80
    map_w = width - 2 * margin_x
    map_h = height - 2 * margin_y

    scale = min(map_w / (max_x - min_x), map_h / (max_y - min_y))

    def to_px(x: float, y: float) -> Tuple[int, int]:
        px = margin_x + (x - min_x) * scale
        py = height - margin_y - (y - min_y) * scale
        return int(round(px)), int(round(py))

    def to_rect(x1: float, y1: float, x2: float, y2: float) -> Tuple[int, int, int, int]:
        p1 = to_px(x1, y1)
        p2 = to_px(x2, y2)
        return min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])

    img = Image.new("RGB", (width, height), (245, 248, 246))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
    except Exception:
        font_title = font_sub = font_large = font_med = font_small = font_label = ImageFont.load_default()

    # Title & Subtitle
    draw.text((margin_x, 24), "HANU CAMPUS — WAYFINDING & ROUTE MAP", fill=(20, 50, 30), font=font_title)
    draw.text((margin_x, 56), "HANOI UNIVERSITY · TRƯỜNG ĐẠI HỌC HÀ NỘI", fill=(80, 105, 95), font=font_sub)

    # Compass
    cx, cy = width - margin_x - 30, 42
    draw.text((cx - 6, cy - 24), "N", fill=(30, 30, 30), font=font_large)
    draw.line([(cx, cy + 18), (cx, cy - 6)], fill=(40, 40, 40), width=3)
    draw.polygon([(cx, cy - 14), (cx - 5, cy - 4), (cx + 5, cy - 4)], fill=(210, 40, 40))

    # Buildings & Landmarks
    # 1. A1 Parking
    draw.rounded_rectangle(to_rect(440, 410, 560, 465), radius=8, fill=(0, 190, 230), outline=(0, 150, 190), width=2)
    draw.text((to_px(500, 437)[0]-42, to_px(500, 437)[1]-7), "A1 PARKING", fill=(255, 255, 255), font=font_med)

    # 2. A1
    draw.rounded_rectangle(to_rect(420, 335, 545, 385), radius=8, fill=(255, 255, 255), outline=(195, 205, 200), width=2)
    draw.text((to_px(482, 360)[0]-10, to_px(482, 360)[1]-7), "A1", fill=(40, 50, 45), font=font_large)

    # 3. A1 Garden
    draw.rounded_rectangle(to_rect(440, 220, 520, 315), radius=8, fill=(215, 238, 210), outline=(175, 215, 165), width=2)
    draw.text((to_px(480, 267)[0]-35, to_px(480, 267)[1]-7), "A1 Garden", fill=(35, 90, 45), font=font_large)

    # 4. Building A
    draw.rounded_rectangle(to_rect(395, 215, 430, 330), radius=8, fill=(255, 255, 255), outline=(195, 205, 200), width=2)
    draw.text((to_px(412, 272)[0]-6, to_px(412, 272)[1]-9), "A", fill=(40, 50, 45), font=font_large)

    # 5. Building B
    draw.rounded_rectangle(to_rect(530, 220, 560, 320), radius=8, fill=(255, 255, 255), outline=(195, 205, 200), width=2)
    draw.text((to_px(545, 270)[0]-6, to_px(545, 270)[1]-9), "B", fill=(40, 50, 45), font=font_large)

    # 6. HANU Gate Box & Souvenir
    draw.rectangle(to_rect(540, 180, 595, 212), fill=(255, 255, 255), outline=(30, 30, 30), width=3)
    draw.text((to_px(567, 196)[0]-22, to_px(567, 196)[1]-8), "HANU", fill=(20, 20, 20), font=font_large)

    draw.rounded_rectangle(to_rect(535, 80, 565, 170), radius=6, fill=(252, 190, 130), outline=(225, 155, 85), width=2)
    draw.text((to_px(550, 125)[0]-25, to_px(550, 125)[1]-10), "HANU\nSOUVENIR", fill=(110, 55, 15), font=font_small)

    # 7. D1, D2, D3
    draw.rounded_rectangle(to_rect(500, 80, 530, 170), radius=6, fill=(195, 175, 220), outline=(160, 140, 190), width=2)
    draw.text((to_px(515, 125)[0]-8, to_px(515, 125)[1]-7), "D1", fill=(60, 40, 90), font=font_large)

    draw.rounded_rectangle(to_rect(460, 80, 490, 170), radius=6, fill=(248, 218, 110), outline=(218, 188, 80), width=2)
    draw.text((to_px(475, 125)[0]-8, to_px(475, 125)[1]-7), "D2", fill=(95, 75, 15), font=font_large)

    draw.rounded_rectangle(to_rect(420, 80, 450, 170), radius=6, fill=(245, 150, 188), outline=(215, 120, 158), width=2)
    draw.text((to_px(435, 125)[0]-8, to_px(435, 125)[1]-7), "D3", fill=(95, 25, 65), font=font_large)

    # 8. Building C (CNTT)
    draw.rounded_rectangle(to_rect(420, 15, 545, 68), radius=8, fill=(0, 215, 215), outline=(0, 175, 175), width=2)
    draw.text((to_px(482, 42)[0]-7, to_px(482, 42)[1]-9), "C", fill=(10, 65, 65), font=font_large)

    # 9. HANU Stadium
    stadium_rect = to_rect(175, 220, 375, 345)
    draw.rounded_rectangle(stadium_rect, radius=22, fill=(195, 235, 180), outline=(135, 195, 120), width=3)
    track_rect = to_rect(190, 232, 360, 332)
    draw.rounded_rectangle(track_rect, radius=18, fill=(238, 247, 232), outline=(255, 255, 255), width=3)
    field_rect = to_rect(210, 245, 340, 318)
    draw.rectangle(field_rect, fill=(75, 185, 95), outline=(255, 255, 255), width=2)
    draw.text((to_px(275, 282)[0]-55, to_px(275, 282)[1]-8), "HANU STADIUM", fill=(255, 255, 255), font=font_large)

    # 10. Green Square, Library, E
    draw.rounded_rectangle(to_rect(320, 135, 390, 180), radius=6, fill=(65, 175, 95), outline=(45, 145, 75), width=2)
    draw.text((to_px(355, 157)[0]-27, to_px(355, 157)[1]-11), "GREEN\nSQUARE", fill=(255, 255, 255), font=font_small)

    draw.rounded_rectangle(to_rect(320, 85, 390, 125), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(355, 105)[0]-30, to_px(355, 105)[1]-7), "LIBRARY", fill=(95, 75, 15), font=font_large)

    draw.rounded_rectangle(to_rect(320, 25, 390, 68), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(355, 46)[0]-6, to_px(355, 46)[1]-9), "E", fill=(95, 75, 15), font=font_large)

    # 11. D4, D4 Parking, D5, D6
    draw.rounded_rectangle(to_rect(235, 95, 275, 180), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(255, 137)[0]-8, to_px(255, 137)[1]-7), "D4", fill=(95, 75, 15), font=font_large)

    draw.rounded_rectangle(to_rect(185, 95, 225, 180), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(205, 137)[0]-25, to_px(205, 137)[1]-11), "D4\nPARKING", fill=(95, 75, 15), font=font_small)

    draw.rounded_rectangle(to_rect(135, 95, 175, 180), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(155, 137)[0]-8, to_px(155, 137)[1]-7), "D5", fill=(95, 75, 15), font=font_large)

    draw.rounded_rectangle(to_rect(135, 25, 275, 75), radius=6, fill=(248, 212, 80), outline=(218, 182, 50), width=2)
    draw.text((to_px(205, 50)[0]-8, to_px(205, 50)[1]-7), "D6", fill=(95, 75, 15), font=font_large)

    # 12. Canteen
    draw.rounded_rectangle(to_rect(90, 220, 140, 335), radius=8, fill=(255, 255, 255), outline=(195, 205, 200), width=2)
    draw.text((to_px(115, 277)[0]-17, to_px(115, 277)[1]-11), "CAN\nTEEN", fill=(40, 50, 45), font=font_large)

    # 13. D7, Grocery, Parking
    draw.rounded_rectangle(to_rect(15, 305, 65, 345), radius=6, fill=(75, 180, 95), outline=(45, 140, 65), width=2)
    draw.text((to_px(40, 325)[0]-25, to_px(40, 325)[1]-11), "D7\nGROCERY", fill=(255, 255, 255), font=font_small)

    draw.rounded_rectangle(to_rect(10, 160, 65, 265), radius=8, fill=(0, 195, 235), outline=(0, 155, 195), width=2)
    draw.text((to_px(37, 212)[0]-9, to_px(37, 212)[1]-7), "D7", fill=(255, 255, 255), font=font_large)

    draw.rounded_rectangle(to_rect(25, 25, 95, 95), radius=8, fill=(0, 195, 235), outline=(0, 155, 195), width=2)
    draw.text((to_px(60, 60)[0]-25, to_px(60, 60)[1]-11), "D7\nPARKING", fill=(255, 255, 255), font=font_small)

    # Edges
    node_coords = {n["node_id"]: to_px(n["x"], n["y"]) for n in nodes}
    for e in edges:
        p1 = node_coords[e["source"]]
        p2 = node_coords[e["target"]]
        if e["stairs"]:
            draw.line([p1, p2], fill=(225, 105, 30), width=3)
        elif not e["accessible"]:
            draw.line([p1, p2], fill=(185, 45, 45), width=2)
        else:
            draw.line([p1, p2], fill=(50, 60, 70), width=4)

    # Nodes with clean badges
    type_colors = {
        "plaza": (225, 55, 40),
        "entrance": (35, 155, 60),
        "hallway": (35, 100, 215),
        "room": (245, 155, 15),
    }

    for n in nodes:
        px, py = node_coords[n["node_id"]]
        r = 6 if n["node_type"] in ("plaza", "entrance") else 4
        color = type_colors.get(n["node_type"], (50, 50, 50))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color, outline=(255, 255, 255), width=2)

        nid = n["node_id"]
        dx, dy = 8, -6
        if nid == "N_GATE":
            dx, dy = -22, 18
        elif nid == "W_NORTH_STADIUM":
            dx, dy = -50, -18
        elif nid == "W_NW_CORNER":
            dx, dy = -85, -16
        elif nid == "W_NE_CORNER":
            dx, dy = 10, -16
        elif nid == "W_SOUTH_STADIUM":
            dx, dy = -52, -18
        elif nid == "W_CROSS_WEST":
            dx, dy = -85, 12
        elif nid == "W_CROSS_EAST":
            dx, dy = 10, -16
        elif nid == "N_STADIUM_WEST":
            dx, dy = 6, -18
        elif nid == "N_STADIUM_PITCH":
            dx, dy = -45, -18
        elif nid == "N_STADIUM_EAST":
            dx, dy = 8, -16
        elif nid == "N_D3_ENTRANCE":
            dx, dy = -36, -18
        elif nid == "N_D2_ENTRANCE":
            dx, dy = -36, 12
        elif nid == "N_D1_ENTRANCE":
            dx, dy = -36, -18
        elif nid == "N_D4_ENTRANCE":
            dx, dy = -36, -18
        elif nid == "N_D5_ENTRANCE":
            dx, dy = -36, 12
        elif nid == "N_D4_PARKING":
            dx, dy = -36, 12
        elif nid == "N_D7_101":
            dx, dy = -55, 6
        elif nid == "N_CANTEEN_HALL":
            dx, dy = -75, 6
        elif nid == "N_CANTEEN_ENTRANCE":
            dx, dy = -95, -6
        elif nid == "N_A1_PARKING":
            dx, dy = -60, -18
        elif nid == "N_GREEN_SQUARE":
            dx, dy = 8, -6
        elif nid == "N_LIB_101":
            dx, dy = -30, 10
        elif nid == "N_LIB_201":
            dx, dy = 6, 10
        elif nid in ("N_C_101", "N_C_201", "N_C_ATTIC"):
            dx, dy = 8, 4

        tx, ty = px + dx, py + dy
        bbox = draw.textbbox((tx, ty), nid, font=font_label)
        bg_rect = [bbox[0] - 2, bbox[1] - 1, bbox[2] + 2, bbox[3] + 1]
        draw.rounded_rectangle(bg_rect, radius=2, fill=(255, 255, 255, 225), outline=(210, 215, 210), width=1)
        draw.text((tx, ty), nid, fill=(30, 35, 40), font=font_label)

    # Legend
    lx, ly = margin_x, height - 38
    draw.text((lx, ly), "LEGEND:", fill=(30, 30, 30), font=font_large)
    lx += 85
    for n_type, color in type_colors.items():
        draw.ellipse([lx, ly + 3, lx + 13, ly + 15], fill=color, outline=(255, 255, 255), width=1)
        draw.text((lx + 18, ly + 1), n_type.capitalize(), fill=(50, 50, 50), font=font_med)
        lx += 95
    draw.line([(lx, ly + 10), (lx + 22, ly + 10)], fill=(225, 105, 30), width=3)
    draw.text((lx + 28, ly + 1), "Stairs", fill=(50, 50, 50), font=font_med)
    lx += 85
    draw.line([(lx, ly + 10), (lx + 22, ly + 10)], fill=(50, 60, 70), width=4)
    draw.text((lx + 28, ly + 1), "Walkway / Road", fill=(50, 50, 50), font=font_med)

    img.save(out_path, "PNG")
    return True


def _render_fallback_png(nodes: List[dict], edges: List[dict], path: Path, width: int = 900, height: int = 700) -> None:
    """Pure stdlib PNG fallback writer."""
    import zlib
    margin = 40
    xs = [n["x"] for n in nodes]
    ys = [n["y"] for n in nodes]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    scale = min((width - 2 * margin) / span_x, (height - 2 * margin) / span_y)

    def to_px(x: float, y: float) -> Tuple[int, int]:
        px = margin + (x - min_x) * scale
        py = height - margin - (y - min_y) * scale
        return int(round(px)), int(round(py))

    rows = [bytearray([255] * (width * 3)) for _ in range(height)]

    def set_pixel(x: int, y: int, color: Tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            i = x * 3
            rows[y][i] = color[0]
            rows[y][i + 1] = color[1]
            rows[y][i + 2] = color[2]

    def draw_line(x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            set_pixel(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def draw_disc(cx: int, cy: int, r: int, color: Tuple[int, int, int]) -> None:
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    set_pixel(cx + dx, cy + dy, color)

    node_px = {n["node_id"]: to_px(n["x"], n["y"]) for n in nodes}
    for e in edges:
        color = (200, 100, 30) if e["stairs"] else (70, 80, 90)
        x0, y0 = node_px[e["source"]]
        x1, y1 = node_px[e["target"]]
        draw_line(x0, y0, x1, y1, color)

    type_colors = {
        "plaza": (220, 50, 40),
        "entrance": (40, 150, 60),
        "hallway": (40, 90, 200),
        "room": (230, 150, 20),
    }
    for n in nodes:
        color = type_colors.get(n["node_type"], (0, 0, 0))
        r = 5 if n["node_type"] in ("plaza", "entrance") else 3
        x, y = node_px[n["node_id"]]
        draw_disc(x, y, r, color)

    def png_chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    compressed = zlib.compress(raw, level=9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(png_chunk(b"IHDR", ihdr))
        fh.write(png_chunk(b"IDAT", compressed))
        fh.write(png_chunk(b"IEND", b""))


def render_campus_map(nodes: List[dict], edges: List[dict], path: Path) -> None:
    """Render schematic map of HANU campus."""
    if not _render_with_pil(nodes, edges, path):
        _render_fallback_png(nodes, edges, path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Project 01 HANU campus route data.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <project>/data next to this script).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir if args.out_dir is not None else DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes, edges, meta = build_campus(args.seed)
    scenarios = build_scenarios(nodes, edges, meta)

    write_nodes_csv(out_dir / "nodes.csv", nodes)
    write_edges_csv(out_dir / "edges.csv", edges)
    write_scenarios_json(out_dir / "scenarios.json", scenarios)
    render_campus_map(nodes, edges, out_dir / "campus_map.png")
    write_sha256sums(out_dir, ["nodes.csv", "edges.csv", "scenarios.json"])

    print(f"seed={args.seed} campus={meta['campus']} nodes={len(nodes)} edges={len(edges)} out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
