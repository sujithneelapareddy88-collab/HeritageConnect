
import networkx as nx

def build_graph(points):
    graph = nx.Graph()

    for point in points:
        graph.add_node(point["name"])

    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        graph.add_edge(
            a["name"],
            b["name"],
            distance=nx.utils.misc.distance(
                (a["lat"], a["lon"]),
                (b["lat"], b["lon"])
            )
        )

    return graph


def calculate_metrics(graph):
    return {
        "degree_centrality": nx.degree_centrality(graph),
        "betweenness_centrality": nx.betweenness_centrality(
            graph, weight="distance", normalized=True
        ),
        "density": nx.density(graph),
        "components": list(nx.connected_components(graph)),
    }
