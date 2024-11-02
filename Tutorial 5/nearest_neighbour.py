import functools
import itertools
import pathlib
import random
import time
import math
import re
import matplotlib.pyplot as plt
from collections import Counter, defaultdict, namedtuple
from statistics import mean, median, stdev
from typing import Set, List, Tuple, Iterable, Dict
import sqlite3
import folium

City = complex  # e.g. City(300, 100)
Cities = frozenset  # A set of cities
Tour = list  # A list of cities visited, in order
TSP = callable  # A TSP algorithm is a callable function
Link = Tuple[City, City]  # A city-city link


def distance(A: City, B: City) -> float:
    "Distance between two cities"
    return abs(A - B)


def shortest(tours: Iterable[Tour]) -> Tour:
    "The tour with the smallest tour length."
    return min(tours, key=tour_length)


def tour_length(tour: Tour) -> float:
    "The total distances of each link in the tour, including the link from last back to first."
    return sum(distance(tour[i], tour[i - 1]) for i in range(len(tour)))


def valid_tour(tour: Tour, cities: Cities) -> bool:
    "Does `tour` visit every city in `cities` exactly once?"
    return Counter(tour) == Counter(cities)


def nearest_tsp(cities, start=None) -> Tour:
    """Create a partial tour that initially is just the start city. 
    At each step extend the partial tour to the nearest unvisited neighbor 
    of the last city in the partial tour, while there are unvisited cities remaining."""
    start = start or first(cities)
    tour = [start]
    unvisited = set(cities) - {start}
    def extend_to(C): tour.append(C); unvisited.remove(C)
    while unvisited:
        extend_to(nearest_neighbor(tour[-1], unvisited))
    return tour


def first(collection):
    """The first element of a collection."""
    return next(iter(collection))


def nearest_neighbor(A: City, cities) -> City:
    """Find the city C in cities that is nearest to city A."""
    return min(cities, key=lambda C: distance(C, A))


conn = sqlite3.connect('bridgesII.sql')
cursor = conn.cursor()

cursor.execute('SELECT latitude, longitude FROM node')
points = cursor.fetchall()

conn.close()

cities = (City(p[0], p[1]) for p in points)

tour = nearest_tsp(cities)

tour_points = [(p.real, p.imag) for p in tour]

lat = (min([loc[0] for loc in points]) + max([loc[0] for loc in points])) / 2
lon = (min([loc[1] for loc in points]) + max([loc[1] for loc in points])) / 2
m = folium.Map(location=(lat, lon), zoom_start=13)

for lat, lon in points:
    folium.CircleMarker(
        location=(lat, lon),
        radius=5,
        fill=True,
        fill_opacity=0.5,
    ).add_to(m)

folium.PolyLine(tour_points, color='red').add_to(m)

m.save('bridges_groningen_tourI.html')


def opt2(tour) -> Tour:
    "Perform 2-opt segment reversals to optimize tour."
    changed = False
    # old_tour = list(tour) # make a copy
    for (i, j) in subsegments(len(tour)):
        if reversal_is_improvement(tour, i, j):
            tour[i:j] = reversed(tour[i:j])
            changed = True
    return (tour if not changed else opt2(tour))


def reversal_is_improvement(tour, i, j) -> bool:
    "Would reversing the segment `tour[i:j]` make the tour shorter?" 
    # Given tour [...A,B--C,D...], would reversing B--C make the tour shorter?
    A, B, C, D = tour[i-1], tour[i], tour[j-1], tour[j % len(tour)]
    return distance(A, B) + distance(C, D) > distance(A, C) + distance(B, D)


cache = functools.lru_cache(None)


# All tours of length N have the same subsegments, so cache them.
@cache
def subsegments(N) -> Tuple[Tuple[int, int]]:
    "Return (i, j) index pairs denoting tour[i:j] subsegments of a tour of length N."
    return tuple((i, i + length)
                 for length in reversed(range(2, N - 1))
                 for i in range(N - length))


opt2tour = opt2(tour)

tour_points = [(p.real, p.imag) for p in opt2tour]

lat = (min([loc[0] for loc in points]) + max([loc[0] for loc in points])) / 2
lon = (min([loc[1] for loc in points]) + max([loc[1] for loc in points])) / 2
m = folium.Map(location=(lat, lon), zoom_start=13)

for lat, lon in points:
    folium.CircleMarker(
        location=(lat, lon),
        radius=4,
        fill=True,
        fill_opacity=0.5,
    ).add_to(m)

folium.PolyLine(tour_points, color='red').add_to(m)

m.save('bridges_groningen_tourII.html')
