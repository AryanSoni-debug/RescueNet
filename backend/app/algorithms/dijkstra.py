"""Dijkstra's shortest path using our own MinHeap. Edge weight = travel minutes.
Complexity O((V+E) log V)."""
from dataclasses import dataclass
from .min_heap import MinHeap
@dataclass
class Route:
    path: list; distance_km: float; time_min: float
def dijkstra(graph, src, dst):
    """Return Route, or None if unreachable / unknown node."""
    if not (graph.has_node(src) and graph.has_node(dst)): return None
    t = {src: 0.0}; km = {src: 0.0}; prev = {}; done = set()
    heap = MinHeap(); heap.push(0.0, src)
    while not heap.is_empty():
        d, u = heap.pop()
        if u in done: continue
        done.add(u)
        if u == dst: break
        for v, dist, spd in graph.neighbors(u):
            nd = d + dist / spd * 60
            if nd < t.get(v, float("inf")):
                t[v] = nd; km[v] = km[u] + dist; prev[v] = u; heap.push(nd, v)
    if dst not in done: return None
    path = [dst]
    while path[-1] != src: path.append(prev[path[-1]])
    return Route(path[::-1], round(km[dst], 2), round(t[dst], 1))
