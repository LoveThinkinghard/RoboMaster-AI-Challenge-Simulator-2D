from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
import json

class NavigationGraph:
    def __init__(self, json_path: Path=None):
        if json_path is None:
            json_path = Path("./data.json")

        self.nx_graph = nx.Graph()

        self.graph_dict = dict()
        with open(json_path) as f:
            graph_dict = json.load(f)

        for idx, waypoint in enumerate(graph_dict["waypoints"]):
            self.nx_graph.add_node(idx, x=waypoint[0], y=waypoint[1])

        for x_idx, row in enumerate(graph_dict["matrix"]):
            for y_idx, connection in enumerate(row):
                if connection == 0:
                    continue
                self.nx_graph.add_edge(x_idx, y_idx, weight=connection)

    def get_pos(self, node_id):
        pass

    def is_node_valid(self, node_id):
        pass

    def calculate_path(self):
        pass

    def display(self):
        plt.figure(figsize=(12, 12))
        pos = [[n["x"], n["y"]] for n in dict(self.nx_graph.nodes()).values()]
        nx.draw(self.nx_graph, with_labels=True, pos=pos)
        plt.show()


if __name__ == "__main__":
    n_g = NavigationGraph()
    n_g.display()

