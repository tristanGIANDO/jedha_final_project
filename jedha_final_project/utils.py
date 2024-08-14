<<<<<<< HEAD
def is_in_zone(coords: tuple[float, float],
               zone: list[tuple[float, float]]) -> bool:
    """Verify if a place is in a zone

    Args:
        coords (tuple[float, float]): position station meteo ou parc eolien
        zone (list[tuple[float, float]]): zone d'autorisation

    Returns:
        bool

    Example:
        coords = (43.02, 1.05)
        zone = [(50.1, -3), (48.3, 5), (32.5, -1), (25.2, 3), (40.0, 2.5)]
        result = is_in_zone(coords, zone)
        print(result)
    """
    x, y = coords
    n = len(zone)
    inside = False

    p1x, p1y = zone[0]
    for i in range(n + 1):
        p2x, p2y = zone[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


if __name__ == "__main__":
    coords = (43.02, 1.05)
    zone = [(50.1, -3), (48.3, 5), (32.5, -1), (25.2, 3), (40.0, 2.5)]
    result = is_in_zone(coords, zone)
    print(result)
=======
def is_in_zone(coords: tuple[float, float],
               zone: list[tuple[float, float]]) -> bool:
    """Verify if a place is in a zone

    Args:
        coords (tuple[float, float]): position station meteo ou parc eolien
        zone (list[tuple[float, float]]): zone d'autorisation

    Returns:
        bool

    Example:
        coords = (43.02, 1.05)
        zone = [(50.1, -3), (48.3, 5), (32.5, -1), (25.2, 3), (40.0, 2.5)]
        result = is_in_zone(coords, zone)
        print(result)
    """
    x, y = coords
    n = len(zone)
    inside = False

    p1x, p1y = zone[0]
    for i in range(n + 1):
        p2x, p2y = zone[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


if __name__ == "__main__":
    coords = (43.02, 1.05)
    zone = [(50.1, -3), (48.3, 5), (32.5, -1), (25.2, 3), (40.0, 2.5)]
    result = is_in_zone(coords, zone)
    print(result)
>>>>>>> 77dfb3648e9ec7aa468522f19e6e788adf984f01
