from functools import reduce

import polyline
import numpy as np
import scipy.spatial as spatial


class Point():
    def __init__(self, lat, lng, heat):
        self.x = lng
        self.y = lat
        self.heat = heat
        
class Line():
    def __init__(self, point_A, point_B):
        self.coordinates = [
            [point_A.y, point_A.x],
            [point_B.y, point_B.x],
        ]
        self.heat = (point_A.heat + point_B.heat) / 2 
        
    def to_dict(self):
        '''Dict passed to front-end'''
        return dict(
            coordinates=self.coordinates,
            opacity=self.heat,
        )
        
class Tree:
    def __init__(self, points, radius):
        self.points = points
        self.radius = radius
        self.tree = spatial.cKDTree(self.points)
        
    def find_neighbours(self, point):
        '''Get points in the tree that are
        within the specified radius from a particular point.
        '''
        neighbours = self.tree.data[self.tree.query_ball_point(point, self.radius)]
        return neighbours

def normalize(value, mn, mx):
    '''Rescale value to be between 0 to 1 (linear interpolation).
    
    @value : value to rescale
    @mn    : bottom value
    @max   : upper value
    
    Try also this approach to normalization (percentage of heats with lower values): https://medium.com/strava-engineering/the-global-heatmap-now-6x-hotter-23fc01d301de#--responses
    '''
    if value != 0:
        return (value - mn) / (mx - mn)
    else:
        return 0
        
def get_polylines(activities):
    '''Extract polylines from activities JSON
    and decode them into coordinates.
    '''
    decoded_polylines = [
        polyline.decode(activity['map']['summary_polyline'])
        for activity in activities
        if activity['map']['summary_polyline'] # skip activies with no polylines
    ]
    return decoded_polylines
    
def get_points(polylines):
    '''Merge points from separate polylines
    into one big list.
    '''
    all_points = np.array(
            reduce(lambda a, b: a + b, polylines)
        )
    return all_points
           
def get_lines(uploaded_gpx, activities, radius):
    '''Get lines constituting a heatmap of single activity'''
    gpx_points = uploaded_gpx.decode()
    polylines = get_polylines(activities)
    all_points = get_points(polylines)
    
    tree = Tree(all_points, radius)

    lines = []
    heats = []
    point_A = None
    for index, point in enumerate(gpx_points):
        try:
            next_point = gpx_points[index + 1]
        except IndexError:
            # if last point reached
            next_point = None 
        if next_point:
            if not point_A:
                point_A = Point(
                    point[0],
                    point[1],
                    heat=len(tree.find_neighbours(point)),
                    
                )            
            point_B = Point(
                next_point[0],
                next_point[1],
                heat=len(tree.find_neighbours(next_point)) 
            )
            line = Line(point_A, point_B)
            lines.append(line)
            heats.append(point_A.heat)
            
            # pass point_B as starting point to next iteration
            # to avoid looking for it again in the tree
            point_A = point_B
    
    # normalize line heats
    min_heat = min(heats)
    max_heat = max(heats)
    for line in lines:
        line.heat = normalize(line.heat, min_heat, max_heat)
        
    return lines
