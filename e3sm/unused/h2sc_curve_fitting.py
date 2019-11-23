import shapely
from shapely.geometry import LineString, Point

#find the intersection of two lines using the 
def h2sc_find_water_table_intersection(A, B, C, D):
    line1 = LineString([A, B])
    line2 = LineString([C, D])

    int_pt = line1.intersection(line2)
    point_of_intersection = int_pt.x, int_pt.y
    
    print(point_of_intersection)
    return point_of_intersection 