# RescueNet Professional Demo

This version uses the existing DSA backend and presents a Durg–Bhilai emergency operations scenario.

## Run

From the RescueNet root containing `backend/`, `demo.py`, and this `web_server.py`:

```powershell
$env:PYTHONPATH="$PWD;$PWD\backend"
python -m uvicorn web_server:app --reload
```

Open http://127.0.0.1:8000

Demo login: admin@rescuenet.demo / RescueNet123

## Data note

Hospital identities, locations and selected published capacity facts are based on public sources. Current availability numbers and the five incidents are demonstration/simulation values, not live hospital feeds. The map uses OpenStreetMap tiles; route-network allocation continues to use the project's Dijkstra implementation.
