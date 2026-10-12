
import networkx as nx
from math import radians, sin, cos, asin, sqrt


def haversine_km(a, b):
    lat1, lon1 = radians(a["lat"]), radians(a["lon"])
    lat2, lon2 = radians(b["lat"]), radians(b["lon"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    value = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 6371 * 2 * asin(sqrt(value))


def build_graph(points, max_distance_km=25):
    """Connect locations that are within the selected distance threshold."""
    graph = nx.Graph()

    for point in points:
        graph.add_node(
            point["name"],
            lat=point["lat"],
            lon=point["lon"]
        )

    for i, a in enumerate(points):
        for b in points[i + 1:]:
            distance = haversine_km(a, b)

            if distance <= max_distance_km:
                graph.add_edge(
                    a["name"],
                    b["name"],
                    distance=distance
                )

    return graph


def calculate_metrics(graph):
    return {
        "degree_centrality": nx.degree_centrality(graph),
        "betweenness_centrality": nx.betweenness_centrality(
            graph,
            weight="distance",
            normalized=True
        ),
        "density": nx.density(graph),
        "components": list(nx.connected_components(graph)),
    }
