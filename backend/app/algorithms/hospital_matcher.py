from dataclasses import dataclass, field
from typing import Set


@dataclass
class Hospital:
    """
    RescueNet hospital resource model.

    Constructor order:
        id
        name
        node
        icu_capacity
        icu_available
        general_capacity
        general_available
        ventilators_available
        departments
    """

    id: str
    name: str
    node: str

    icu_capacity: int
    icu_available: int

    general_capacity: int
    general_available: int

    ventilators_available: int

    departments: Set[str] = field(default_factory=set)

    @property
    def occupancy(self) -> float:
        """
        Overall hospital occupancy ratio.
        """

        total_capacity = (
            self.icu_capacity +
            self.general_capacity
        )

        if total_capacity <= 0:
            return 1.0

        total_available = (
            self.icu_available +
            self.general_available
        )

        occupied = total_capacity - total_available

        return occupied / total_capacity


@dataclass
class Requirement:
    """
    Requirements for an emergency case.
    """

    icu: bool = False
    departments: tuple[str, ...] = ()
    ventilator: bool = False


def check_requirements(
    hospital: Hospital,
    req: Requirement
):
    """
    Return a list of reasons why the hospital
    cannot satisfy the requirement.

    Empty list = hospital is suitable.
    """

    reasons = []

    # ICU requirement
    if req.icu and hospital.icu_available <= 0:
        reasons.append("No ICU bed available")

    # General bed requirement
    if not req.icu and hospital.general_available <= 0:
        reasons.append("No general bed available")

    # Ventilator requirement
    if req.ventilator and hospital.ventilators_available <= 0:
        reasons.append("No ventilator available")

    # Department requirements
    for department in req.departments:
        if department not in hospital.departments:
            reasons.append(
                f"{department} department unavailable"
            )

    return reasons


def filter_hospitals(hospitals, req: Requirement):
    """
    Filter hospitals into:

        suitable hospitals
        rejected hospitals + reasons
    """

    suitable = []
    rejected = {}

    for hospital_id, hospital in hospitals.items():

        reasons = check_requirements(
            hospital,
            req
        )

        if reasons:
            rejected[hospital_id] = reasons
        else:
            suitable.append(hospital)

    return suitable, rejected


def find_suitable_hospitals(
    hospitals,
    req: Requirement
):
    """
    Return only hospitals that satisfy the requirement.
    """

    suitable, _ = filter_hospitals(
        hospitals,
        req
    )

    return suitable