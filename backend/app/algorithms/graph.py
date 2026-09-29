class Graph:
    """
    Weighted graph for the RescueNet hospital network.

    Each road stores:
        destination
        distance in kilometers
        average speed in km/h
    """

    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_road(self, a, b, distance_km, speed_kmh=40.0):
        """
        Add a two-way road.

        speed_kmh is optional so the existing demo.py
        does not need to be changed.
        """

        self.add_node(a)
        self.add_node(b)

        self.adj[a].append(
            (b, float(distance_km), float(speed_kmh))
        )

        self.adj[b].append(
            (a, float(distance_km), float(speed_kmh))
        )

    def has_node(self, node):
        return node in self.adj

    def neighbors(self, node):
        return self.adj.get(node, [])

    def nodes(self):
        return self.adj.keys()