#!/usr/bin/env python3

import sys
import math

COLORS_ORIG = {
    'r' : (74, 72, 165),  # (0, 0, 255),
    'o' : (78, 86, 213), #(0, 165, 255),
    'b' : (132, 98, 75), #(255, 0, 0),
    'g' : (105, 139, 99), #(0, 255, 0),
    'w' : (85, 84, 94), #(255, 255, 255),  (actually black)
    'y' : (118, 165, 189), #(0, 255, 255),
}

COLORS_BGR = {
    'r' : (74, 72, 165),  # (0, 0, 255),
    'o' : (78, 86, 213), #(0, 165, 255),
    'b' : (132, 98, 75), #(255, 0, 0),
    'g' : (105, 139, 99), #(0, 255, 0),
    'w' : (85, 84, 94), #(255, 255, 255),  (actually black)
    'y' : (118, 165, 189), #(0, 255, 255),
}

CLUSTERS = {
    'r' : [],
    'o' : [],
    'b' : [],
    'g' : [],
    'w' : [],
    'y' : [],
}

def name_to_bgr(name):
    """
    Converts a color name to its corresponding BGR (Blue, Green, Red) tuple.

    Args:
        name (str): The name of the color. If 'x', returns black (0, 0, 0).

    Returns:
        tuple: A tuple representing the BGR color.

    Raises:
        KeyError: If the color name is not 'x' and not found in COLORS_ORIG.
    """
    if name == 'x':
        return (0, 0, 0)
    return COLORS_ORIG[name]

def rect_average(rect):
    """
    Calculates the average BGR color of a rectangular region.
    Args:
        rect (list[list[tuple[int, int, int]]]): A 2D list representing a rectangle,
            where each element is a tuple of (R, G, B) values.
    Returns:
        tuple[int, int, int] or None: The average (R, G, B) color as a tuple of integers,
            or None if the input rectangle is empty.
    """
    r   = 0
    g   = 0
    b   = 0
    num = 0
    
    for y in range(len(rect)):
        for x in range(len(rect[y])):
            chunk = rect[y][x]
            r += int(chunk[0])   # This says r, g, b but I think it's actually BGR
            g += int(chunk[1])
            b += int(chunk[2])
            num += 1
    if not num:
        return None
    return (int(r/num), int(g/num), int(b/num))


def detect_bgr(average):
    """
    Detects the closest matching color name for a given BGR average value.
    Args:
        average (tuple or list): The average BGR color value as a tuple or list of three integers.
    Returns:
        tuple: A tuple containing the name of the closest matching color (str) and the corresponding error (float or int).
    Notes:
        - The function compares the input BGR value to predefined colors in the COLORS_BGR dictionary.
        - The distance between colors is calculated using the `distance` function.
    """
    err = 1000
    found_color = 'black'
    for name, rgb in COLORS_BGR.items():
        new_err = distance(average, rgb)
        if new_err < err:
            found_color = name
            err = new_err

    return (found_color, err)

def distance(c1, c2):
    """
    Calculates the Euclidean distance between two RGB color tuples.

    Args:
        c1 (tuple): The first color as a tuple of three integers (R, G, B).
        c2 (tuple): The second color as a tuple of three integers (R, G, B).

    Returns:
        float: The Euclidean distance between the two colors.
    """
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)

def update_centroids(state):
    for color in COLORS_BGR:
        indices = CLUSTERS[color]
        averages = list(map(lambda x: state[x]["avg"], indices))

        new_avg = rect_average([averages])
        if new_avg is not None:
            COLORS_BGR[color] = new_avg
            print(f"Updated {color} to {COLORS_BGR[color]}")
        else:
            print(f"Could not update {color}, new_avg is None")


def update_distances(square):
    distances = []
    for color in COLORS_BGR:
        dist = distance(square["avg"], COLORS_BGR[color])
        distances.append((color, dist))
    square["distances"] = sorted(distances, key=lambda x: x[1])

def print_state(state):
    t = sum(list(map(lambda x: x["distances"][0][1], state)))
    print(f"total distance = {t}")
    for color in COLORS_BGR:
        print(color, COLORS_BGR[color])
        for index in CLUSTERS[color]:
            sq = state[index]
            print(f"{sq['index']} {sq['avg']} {sq['distances']}")


def swap(state, i, j):
    sq1 = state[i]
    sq2 = state[j]
    color1 = sq1["color"]
    color2 = sq2["color"]

    CLUSTERS[color1].remove(i)
    CLUSTERS[color1].append(j)

    CLUSTERS[color2].remove(j)
    CLUSTERS[color2].append(i)

    sq1["color"] = color2
    sq2["color"] = color1

def swap_many(state):
    swapped = False

    # get all the squares thar are not entrely happy about their position yet
    print()
    candidates = list(map(lambda x: x["index"], filter(lambda x: x["color"] != x["distances"][0][0], state)))
    print(f"candidates to move {candidates}")

    swaps = []
    # very inefficient, n^2, get all pairs of swapping, sort them by
    # the potential gain, then perform swaps while cleaning the list
    # until list exchausted
    for i in candidates:
        for j in candidates:
            sq1 = state[i]
            sq2 = state[j]
            color1 = sq1["color"]
            color2 = sq2["color"]
            if color1 == color2:
                continue
            gain = distance(sq1["avg"], COLORS_BGR[color1]) - distance(sq1["avg"], COLORS_BGR[color2]) + distance(sq2["avg"], COLORS_BGR[color2]) - distance(sq2["avg"], COLORS_BGR[color1])
            if gain > 0:
                swaps.append((gain, i, j))

    sorted_swaps = list(sorted(swaps, key=lambda x: x[0]))
    while len(sorted_swaps):
        gain, i, j = sorted_swaps.pop()
        print(f"swapping {i}/{state[i]['color']} and {j}/{state[j]['color']} for {gain}")
        swap(state, i, j)
        swapped = True
        sorted_swaps = list(filter(lambda s: not (s[1] == i or s[1] == j or s[2] == i or s[2] == j), sorted_swaps))

    return swapped


def cluster(state):
    """
    Variation on similar size k-mean clustering
    https://elki-project.github.io/tutorial/same-size_k_means
    the swapping is very O(N^2) but who cares
    """
    iteration = 0
    global CLUSTERS

    CLUSTERS = {
        'r' : [],
        'o' : [],
        'b' : [],
        'g' : [],
        'w' : [],
        'y' : [],
    }

    # Initialize - calc distances, and do the initial assign
    for index, sq in enumerate(state):
        update_distances(sq)
        sq["index"] = index
    for sq in sorted(state, key=lambda x: sq["distances"][0][1] - sq["distances"][5][1]):
        for color, _ in sq["distances"]:
            if len(CLUSTERS[color]) < 9:
                # There is a place
                CLUSTERS[color].append(sq["index"])
                sq["color"] = color
                break

    print_state(state)
    
    swapped = True
    while swapped and iteration < 10000:
        swapped = False
        print(f"iteration {iteration}")
        # phase 1 - update centroids (colors)
        update_centroids(state)

        # phase 2 - reassigning
        for index, sq in enumerate(state):
            update_distances(sq)

        print("update distances")
        print_state(state)

        swapped = swap_many(state)
        iteration += 1

    return state


def get_colors(state):
   #  """
   #  Assigns a color letter to each square by finding the closest match in COLORS_BGR.
   #  Returns a string of color letters.
   #  """
   #  return "".join([detect_bgr(sq["avg"])[0] for sq in state])

    colors = cluster(state)
    return "".join(list(map(lambda x: x["color"], colors)))


if __name__ == "__main__":
    state = [{"avg": [92, 125, 67]}, {"avg": [181, 165, 163]}, {"avg": [1, 0, 77]}, {"avg": [16, 30, 154]}, {"avg": [70, 112, 48]}, {"avg": [11, 1, 73]}, {"avg": [74, 112, 61]}, {"avg": [88, 158, 162]}, {"avg": [99, 161, 163]}, {"avg": [8, 3, 85]}, {"avg": [16, 30, 153]}, {"avg": [84, 121, 59]}, {"avg": [19, 33, 155]}, {"avg": [104, 167, 165]}, {"avg": [133, 175, 169]}, {"avg": [18, 33, 154]}, {"avg": [58, 102, 50]}, {"avg": [100, 161, 163]}, {"avg": [181, 170, 170]}, {"avg": [109, 169, 166]}, {"avg": [123, 47, 2]}, {"avg": [0, 0, 82]}, {"avg": [116, 34, 0]}, {"avg": [6, 0, 76]}, {"avg": [114, 42, 8]}, {"avg": [105, 31, 0]}, {"avg": [89, 158, 163]}, {"avg": [188, 175, 171]}, {"avg": [183, 169, 167]}, {"avg": [24, 38, 157]}, {"avg": [0, 0, 81]}, {"avg": [185, 174, 175]}, {"avg": [50, 45, 157]}, {"avg": [1, 0, 87]}, {"avg": [63, 105, 54]}, {"avg": [169, 160, 165]}, {"avg": [134, 64, 18]}, {"avg": [113, 173, 171]}, {"avg": [0, 0, 87]}, {"avg": [177, 171, 174]}, {"avg": [8, 0, 84]}, {"avg": [122, 37, 0]}, {"avg": [119, 49, 13]}, {"avg": [163, 156, 167]}, {"avg": [4, 26, 155]}, {"avg": [98, 130, 79]}, {"avg": [132, 58, 13]}, {"avg": [20, 35, 158]}, {"avg": [84, 121, 67]}, {"avg": [16, 27, 158]}, {"avg": [80, 117, 59]}, {"avg": [102, 167, 173]}, {"avg": [112, 36, 1]}, {"avg": [168, 160, 168]}]    
    cluster(state)
