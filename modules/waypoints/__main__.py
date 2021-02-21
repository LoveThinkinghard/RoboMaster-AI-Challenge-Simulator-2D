import copy
import cv2
from modules.waypoints.navigation_graph import NavigationGraph

DATA_FILE_NAME = 'data.json'
WINDOW_NAME = 'Navigation Graph Generator'
DELAY = 20


def equal(index1, index2):
    return index1 // 2 == index2 // 2


def mouse_event(event, x, y, *args):
    global mouse_position, hover_index, left_click_index, right_click_index

    if event == cv2.EVENT_MOUSEMOVE:
        mouse_position = (x, y)
        hover_index = graph.index_closest(mouse_position)
    elif event == cv2.EVENT_LBUTTONDOWN:
        left_click_index = hover_index
    elif event == cv2.EVENT_LBUTTONUP:
        if left_click_index is None and hover_index is None:
            graph.add_waypoint(mouse_position)
        elif left_click_index is not None and hover_index is not None and not equal(hover_index, left_click_index):
            graph.add_connection(left_click_index, hover_index)
            left_click_index = None
    elif event == cv2.EVENT_RBUTTONDOWN:
        right_click_index = hover_index
    elif event == cv2.EVENT_RBUTTONUP:
        if hover_index is not None and right_click_index is not None and hover_index == right_click_index:
            graph.remove_waypoint(right_click_index)
            hover_index, left_click_index, right_click_index = None, None, None
        elif hover_index is not None and right_click_index is not None:
            graph.remove_connection(right_click_index, hover_index)
            left_click_index, right_click_index = None, None


if __name__ == '__main__':
    graph = NavigationGraph()
    mouse_position = (0, 0)
    hover_index, left_click_index, right_click_index = None, None, None

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, mouse_event)
    image_original = cv2.imread('field.png')

    while cv2.waitKey(DELAY) != ord('s'):
        image = copy.deepcopy(image_original)
        graph.draw_connections(image)
        graph.draw_waypoints(image)

        if hover_index is not None:
            graph.draw_selector(image, hover_index, mode=0)
        if left_click_index is not None:
            graph.draw_selector(image, left_click_index, mode=1)
        elif right_click_index is not None:
            graph.draw_selector(image, right_click_index, mode=2)

        cv2.imshow(WINDOW_NAME, image)
    cv2.destroyWindow(WINDOW_NAME)
    graph.save(DATA_FILE_NAME)
