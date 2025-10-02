from __future__ import annotations
from typing import List, Tuple
import math

def polygon_area(points: List[Tuple[float, float]]) -> float:
    """Вычисляет площадь полигона (по модулю) методом шнурка."""
    if len(points) < 3:
        return 0.0
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0

def bbox_from_points(points: List[Tuple[float, float]]):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))
