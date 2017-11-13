import fileinput
import heapq
import math
import sys

"""Problem 2: Quickly compute k closest points points to arbitrary point (No Memory constraints)
	
	Given this scenario, I would develop a batch approach that pre-calculated the solution for a 
	set of coordinates and then mapping the input to the most accurate, stored solution. Each 
	precomputed coordinate would store a sorted list of all stars. Each call to a coordinate would
	return the desired k stars.
	This would return an answer in constant time since it only require a single table look up. If we
	wanted to support absolute accuracy the solution would store a record for every valid coordinate
	(1). Whereas if we considered approximate solutions acceptable, we could save memory by storing 
	fewer coordinates and map the coordinate passed to our program to the closest stored coordinate
	in our table (2).

	(1) Absolute accuracy example
		- Say we model each coordinate of a star with 9 significant figures of the form xxx.xxxxxx
		Then we could compute the answer for all possible pairs of 3 coordinates, where the range of
		each coordinate is [-359.999999, 359.999999]. There would be about 5 * 10**26 possible
		stored entries.
	(2) Approximate answers example
		- Of the 9 significant figures with which we model a star, we only store solutions for up to
		the first 6 digits (xxx.xxx). An input coordinate would be rounded up or down to the closest
		precomputed coordinate. In this example we reduce our stored entries to 5 * 10**17 entries
	
"""

X_INDEX = 17
Y_INDEX = 18
Z_INDEX = 19
SUN_DISTANCE = 5e-06

def cartesian_distance(x,y,z):
	"""Return coordinates aproximate distance to sun"""
	return math.sqrt(x**2 + y**2 + z**2)


def manage_heap(heap, coordinates, distance):
	"""Evaluate new coordinate and add to heap if necessary
	
	Maintains a max heap of size k. Heap represents the set of smallest k distances seen so far.

	Args:
		heap: list of tuples containing coordinates of a planet and their distance to the sun
		coordinates: tuple of three floats representing x,y,z cartesian coordinates
		distance: float representing cartesian distance

	"""
	if distance > SUN_DISTANCE:
		if len(heap) < k:
			heap.append((distance, coordinates))
			if len(heap) == k:
				heapq._heapify_max(heap)
		elif distance < heap[0][0]:
			heapq._heappushpop_max(heap, (distance, coordinates))

def find_stars():
	"""Return coordinates of k nearest stars to the sun"""
	heap = []
	sys.stdin.readline()
	for star_data in sys.stdin:
		star_data = star_data.split(',')
		if len(star_data) > 18:
			coordinates = (float(star_data[X_INDEX]), float(star_data[Y_INDEX]), 
						   float(star_data[Z_INDEX]))
			distance = cartesian_distance(*coordinates)
			manage_heap(heap, coordinates, distance)
	print heap
	return [star[1] for star in heap]

if __name__ == '__main__':
	k = int(sys.argv[1])
	print find_stars()

	
