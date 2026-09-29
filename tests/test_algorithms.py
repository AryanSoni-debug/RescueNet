import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.algorithms.min_heap import MinHeap
from app.algorithms.graph import Graph
from app.algorithms.dijkstra import dijkstra
from app.algorithms.hospital_matcher import Requirement
from demo import build
def test_heap_order():
    h = MinHeap()
    for x in [5, 1, 4, 2, 3]: h.push(x, x)
    assert [h.pop()[0] for _ in range(5)] == [1, 2, 3, 4, 5]
def test_heap_empty():
    with pytest.raises(IndexError): MinHeap().pop()
def test_dijkstra_shortest_and_unreachable():
    g = Graph(); g.add_road("A","B",2); g.add_road("B","C",2); g.add_road("A","C",10); g.add_node("Z")
    assert dijkstra(g,"A","C").path == ["A","B","C"] and dijkstra(g,"A","C").distance_km == 4
    assert dijkstra(g,"A","Z") is None            # route unavailable
def test_demo_rejections_and_recommendation():
    e = build(); out = e.recommend("C001","LOC_A",Requirement(icu=True, departments=("Cardiology",)))
    assert [h.id for h,_,_ in out["feasible"]] == ["H003","H004"]
    assert set(out["rejected"]) == {"H001","H002","H005"}
def test_no_suitable_hospital():
    e = build(); assert not e.recommend("C9","LOC_A",Requirement(icu=True, departments=("Neurology",)))["feasible"]
def test_resource_already_allocated():
    e = build(); req = Requirement(icu=True)
    for _ in range(3): e.confirm("C1","H003",req)
    with pytest.raises(ValueError): e.confirm("C2","H003",req)   # ICU exhausted
