import random
from pathlib import Path
from typing import Tuple, Optional, List

import networkx as nx
import matplotlib.pyplot as plt
import json


class NavigationGraph:
    def __init__(self, json_path: Path = None):
        if json_path is None:
            json_path = Path("./data.json")

        self.nx_graph = nx.Graph()

        self.graph_dict = dict()
        with open(json_path) as f:
            graph_dict = json.load(f)

        for idx, waypoint in enumerate(graph_dict["waypoints"]):
            self.nx_graph.add_node(idx, x=waypoint[0], y=waypoint[1], enabled=self.is_valid_pos(waypoint))

        for x_idx, row in enumerate(graph_dict["matrix"]):
            for y_idx, connection in enumerate(row):
                if connection == 0:
                    continue
                self.nx_graph.add_edge(x_idx, y_idx, weight=connection)

    def get_pos(self, node_id):
        node = self.nx_graph.nodes[node_id]
        return node["x"], node["y"]

    def is_valid_pos(self, pos: Tuple[int, int]):
        return random.uniform(0, 1) > 0.15

    def is_valid_node(self, node_id):
        return self.is_valid_pos(self.get_pos(node_id))

    def valid_node_graph(self):
        new_graph = nx.Graph()
        new_graph.add_nodes_from({x: props for x, props in dict(self.nx_graph.nodes()).items() if props["enabled"]})
        new_graph.add_weighted_edges_from(
            filter(lambda x: x[0] in new_graph.nodes() and x[1] in new_graph.nodes(), self.nx_graph.edges(data=True))
        )
        return new_graph

    def calculate_path(self, a, b) -> Optional[List[int]]:
        search_graph = self.valid_node_graph()
        if a not in search_graph.nodes() or b not in search_graph.nodes():
            return None
        return nx.shortest_path(search_graph, a, b)

    def display(self):
        plt.figure(figsize=(12, 12))
        pos = [[n["x"], n["y"]] for n in dict(self.nx_graph.nodes()).values()]
        colors = ["blue" if v["enabled"] else "red" for k, v in dict(self.nx_graph.nodes()).items()]
        nx.draw(self.nx_graph, with_labels=True, pos=pos, node_color=colors)
        plt.show()


if __name__ == "__main__":
    n_g = NavigationGraph()
    n_g.display()
    print(n_g.calculate_path(0, 17))