import networkx as nx

def calculate_metrics(graph):
    return {
        "degree_centrality": nx.degree_centrality(graph),
        "betweenness_centrality": nx.betweenness_centrality(graph),
        "density": nx.density(graph),
        "components": list(nx.connected_components(graph)),
    }
