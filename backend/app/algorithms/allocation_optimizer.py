"""AllocationEngine: find -> check -> filter -> route -> cost -> rank -> recommend -> confirm.
Ranks hospital options only. No patient priority scoring."""
import threading, itertools
from .dijkstra import dijkstra
from .priority_queue import PriorityQueue
from .hospital_matcher import filter_hospitals, check_requirements
CAPACITY_WEIGHT = 10.0   # cost = travel_minutes + 10 * occupancy_ratio (transparent, tunable)
class AllocationEngine:
    def __init__(self, graph, hospitals):
        self.graph, self.hospitals = graph, hospitals      # hospitals: HashMap id -> Hospital
        self.allocations, self.audit = [], []
        self._lock = threading.Lock(); self._ids = itertools.count(1)
    def recommend(self, case_id, source_node, req):
        candidates, rejected = filter_hospitals(self.hospitals, req)
        pq, feasible = PriorityQueue(), []
        for h in candidates:
            r = dijkstra(self.graph, source_node, h.node)
            if r is None: rejected[h.id] = ["Route unavailable"]; continue
            pq.enqueue(r.time_min + CAPACITY_WEIGHT * h.occupancy, (h, r))
        while len(pq):
            cost, (h, r) = pq.dequeue(); feasible.append((h, r, round(cost, 2)))
        rec = None
        if feasible:
            h, r, c = feasible[0]
            rec = (f"Recommended because {h.name} satisfies all required facilities, has available "
                   f"capacity, and has the lowest calculated route cost ({c}) among "
                   f"{len(feasible)} feasible hospital(s).")
        self.audit.append(("ALLOCATION_RECOMMENDED", case_id))
        return {"feasible": feasible, "rejected": rejected, "reason": rec}
    def confirm(self, case_id, hospital_id, req):
        with self._lock:

            if hospital_id not in self.hospitals:
                raise ValueError(
                    f"Hospital {hospital_id} does not exist"
                )

            h = self.hospitals[hospital_id]

            # Re-check resources atomically before allocation
            reasons = check_requirements(h, req)

            if reasons:
                raise ValueError(
                    "Allocation failed: " + "; ".join(reasons)
                )

            # ICU allocation
            if req.icu:
                h.icu_available -= 1
                bed = "ICU"

            # General bed allocation
            else:
                h.general_available -= 1
                bed = "GENERAL"

            # Ventilator allocation
            if req.ventilator:
                h.ventilators_available -= 1

            allocation = {
                "id": f"A{next(self._ids):03d}",
                "case": case_id,
                "hospital": hospital_id,
                "bed": bed
            }

            self.allocations.append(allocation)

            self.audit.extend([
                ("ALLOCATION_CONFIRMED", case_id),
                ("BED_ASSIGNED", hospital_id)
            ])

            return allocation