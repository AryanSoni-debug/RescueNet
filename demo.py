"""Scenario C001: needs ICU + Cardiology + bed. Run: python demo.py"""
from app.algorithms.graph import Graph
from app.algorithms.hospital_matcher import Hospital, Requirement
from app.algorithms.allocation_optimizer import AllocationEngine
def build():
    g = Graph()
    for a, b, km in [("LOC_A","J1",2),("J1","H001",3),("J1","J2",2),("J2","H002",2.5),("J2","H003",2),
                     ("LOC_A","J3",4),("J3","H004",6),("J3","H005",3),("J2","J3",3)]: g.add_road(a, b, km)
    D = {"Cardiology","Emergency","ICU"}
    hs = {h.id: h for h in [
      Hospital("H001","CityCare Hospital (demo)","H001",6,0,40,10,2,D),                # A: no ICU bed
      Hospital("H002","LifeSpring Medical Center (demo)","H002",6,2,40,10,2,{"Emergency"}), # B: no cardiology
      Hospital("H003","Metro General Hospital (demo)","H003",8,3,50,12,3,D),           # C: suitable
      Hospital("H004","Sunrise Multi-Speciality (demo)","H004",8,3,50,12,3,D),         # D: suitable, farther
      Hospital("H005","Central Medical Institute (demo)","H005",4,0,30,0,1,D)]}        # E: no bed
    return AllocationEngine(g, hs)
if __name__ == "__main__":
    e, req = build(), Requirement(icu=True, departments=("Cardiology",))
    out = e.recommend("C001", "LOC_A", req)
    for h, r, c in out["feasible"]:
        print(f"OK  {h.id} {h.name}: {r.distance_km} km, {r.time_min} min, cost {c}, path {' > '.join(r.path)}")
    for hid, why in out["rejected"].items(): print(f"NOT SUITABLE {hid}: {'; '.join(why)}")
    print("\n" + out["reason"])
    best = out["feasible"][0][0]; a = e.confirm("C001", best.id, req)
    print("CONFIRMED:", a, "| ICU left at", best.id, "=", best.icu_available); print("AUDIT:", e.audit)
