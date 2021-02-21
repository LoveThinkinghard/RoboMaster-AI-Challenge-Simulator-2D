import numpy as np
import cv2
import json
from typing import Tuple

FIELD_DIMS = (808 - 1, 448 - 1)
WAYPOINT_WIDTH = 6
SELECTOR_WIDTH = 2
CONNECTION_THICKNESS = 2
DIST_HOVER_THRESHOLD = 28
WAYPOINT_LABEL_OFFSET = (8, 4)
LABEL_FONT_SIZE = 0.32

WAYPOINT_COLOR = (0, 255, 0)
HOVER_SELECTOR_COLOR = (88, 88, 88)
CLICK_SELECTOR_COLOR = (30, 30, 30)
DELETE_SELECTOR_COLOR = (0, 0, 220)
CONNECTION_COLOR = (30, 30, 30)
LABEL_COLOR = (0, 0, 0)


class NavGraphBuilder:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.count_waypoints = 0
        self.centers = []
        self.corners = []
        self.connections = set()

    def add_waypoint(self, center: Tuple[int, int]):
        mirrored_center = mirror(center)
        swap = np.sum(mirrored_center) < np.sum(center)
        center1, center2 = (mirrored_center, center) if swap else (center, mirrored_center)
        self.centers.append(center1)
        self.centers.append(center2)
        self.corners.append(square_corners(center1, WAYPOINT_WIDTH))
        self.corners.append(square_corners(center2, WAYPOINT_WIDTH))
        self.count_waypoints += 2
        if self.verbose:
            print(f'Added waypoints {self.count_waypoints - 2}, {self.count_waypoints - 1} at {center1} and {center2}.')

    def remove_waypoint(self, index: int):
        index = min(index, mirror_index(index))
        del self.centers[index: index + 2]
        del self.corners[index: index + 2]

        connections = set()
        for connection in self.connections:
            if index not in connection and (index + 1) not in connection:
                index1, index2 = connection
                if index1 >= index + 2:
                    index1 -= 2
                if index2 >= index + 2:
                    index2 -= 2
                connections.add((index1, index2))
        self.connections = connections
        self.count_waypoints -= 2
        if self.verbose:
            print(f'Removed waypoints {index} and {index + 1}.')

    def draw_waypoints(self, image):
        for index in range(self.count_waypoints):
            text_position = (self.centers[index][0] + WAYPOINT_LABEL_OFFSET[0], self.centers[index][1] + WAYPOINT_LABEL_OFFSET[1])
            cv2.fillPoly(image, np.array([self.corners[index]]), WAYPOINT_COLOR)
            cv2.putText(image, str(index), text_position, cv2.FONT_HERSHEY_SIMPLEX, LABEL_FONT_SIZE, LABEL_COLOR)

    def add_connection(self, index1: int, index2: int):
        if (index1, index2) in self.connections or (index2, index1) in self.connections:
            return
        self.connections.add((index1, index2))
        self.connections.add((mirror_index(index1), mirror_index(index2)))
        if self.verbose:
            print(f'Added connections {index1}-{index2} and {mirror_index(index1)}-{mirror_index(index2)}.')

    def remove_connection(self, index1, index2):
        if (index2, index1) in self.connections:
            index1, index2 = index2, index1
        elif (index1, index2) not in self.connections:
            return
        self.connections.remove((index1, index2))
        self.connections.remove((mirror_index(index1), mirror_index(index2)))
        if self.verbose:
            print(f'Removed connections {index1}-{index2} and {mirror_index(index1)}-{mirror_index(index2)}.')

    def draw_connections(self, image):
        for index1, index2 in self.connections:
            cv2.line(image, self.centers[index1], self.centers[index2], CONNECTION_COLOR, CONNECTION_THICKNESS)

    def draw_selector(self, image, index: int, mode=0):  # mode = 0/1/2 for hover/click/delete
        color = [HOVER_SELECTOR_COLOR, CLICK_SELECTOR_COLOR, DELETE_SELECTOR_COLOR][mode]
        for index in (index, mirror_index(index)):
            cv2.circle(image, self.centers[index], WAYPOINT_WIDTH - SELECTOR_WIDTH + 1, color, SELECTOR_WIDTH)

    def index_closest(self, point: Tuple[int, int]) -> int:
        min_distance = DIST_HOVER_THRESHOLD + 1
        min_index = None
        for index, center in enumerate(self.centers):
            distance = find_distance(point, center)
            if distance < min_distance:
                min_distance = distance
                min_index = index
        return min_index

    def distance_matrix(self):
        matrix = np.zeros((self.count_waypoints, self.count_waypoints), dtype=np.int)
        for index1, index2 in self.connections:
            matrix[index1, index2] = matrix[index2, index1] = find_distance(self.centers[index1], self.centers[index2])
        return matrix.tolist()

    def save(self, file_name: str):
        data = {'waypoints': self.centers, 'connections': list(self.connections), 'matrix': self.distance_matrix()}
        with open(file_name, 'w+') as file:
            json.dump(data, file, indent=2)
        if self.verbose:
            print(f'Saved {self.count_waypoints} waypoints and {len(self.connections)} connections to "{file_name}".')


def mirror(point):
    return FIELD_DIMS[0] - point[0], FIELD_DIMS[1] - point[1]


def mirror_index(index):
    return index - 2 * (index % 2) + 1


def find_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def square_corners(center, width):
    left, right = center[0] - width // 2, center[0] + width // 2
    top, bottom = center[1] - width // 2, center[1] + width // 2
    return [(left, top), (left, bottom), (right, bottom), (right, top)]
