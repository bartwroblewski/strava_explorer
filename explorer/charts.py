import pandas as pd
import numpy as np
import polyline

from .tree import normalize
from .helpers import month_name

def add_polyline_heat(df, inputs):    
    '''Add column containing polyline heat value 
    for a given heat name.
    
    @df      : dataframe to add column to
    
    '''
    # name of the column to calculate heat of 
    # (picked on front-end)
    map_layer = inputs['map_layer'][0]
    if map_layer == 'off':
        df['polyline_heat'] = 0.5
    else:
        # setting default minimum to be above 0
        # to avoid displaying edge case polylines
        # in the table, but not on map.
        # Otherwise "mn = df[map_layer].min()" can be used.
        mn = 0.01
        
        mx = df[map_layer].max()
        df['polyline_heat'] = df[map_layer].fillna(0).map(lambda x: normalize(x, mn, mx)) 
    return df

def replace_nan(list_of_dicts):
    for dictionary in list_of_dicts:
        for k, v in dictionary.items():
            try:
                if np.isnan(v):
                    dictionary[k] = None  
            except:
                pass
    return list_of_dicts
  
def decode_polyline(poly_line):
    return polyline.decode(poly_line)
       
def get_polyline_minmax(polyline):
    '''
    
    @polyline: list of tuples of lat and lng coordinates
    
    '''
    z = zip(*polyline) 
    lats, lngs = tuple(z)
    min_max = {
        'min_lat': min(lats),
        'max_lat': max(lats),
        'min_lng': min(lngs),
        'max_lng': max(lngs),
    }
    return min_max 
    
def get_pan_bounds(data):
    '''Calculate how to pan the map
    to display all selected activities.
    
    @data : dataframe containing 'polyline_minmax' column
    
    '''
    min_lat = data['polyline_minmax'].map(lambda x: x['min_lat']).min()
    max_lat = data['polyline_minmax'].map(lambda x: x['max_lat']).max()
    min_lng = data['polyline_minmax'].map(lambda x: x['min_lng']).min()
    max_lng = data['polyline_minmax'].map(lambda x: x['max_lng']).max()
    pan_bounds = [
       [min_lat, min_lng], # map corner 1
       [max_lat, max_lng], # map corner 2
    ]
    return pan_bounds 
    
def get_data(data):
    '''Create a dataframe from list of dicts and
    add some columns to it.
    
    @data : list of dictionaries
    
    '''
    df                  = pd.DataFrame(data)
    df['start_date']    = pd.to_datetime(df['start_date'])
    df['year']          = df['start_date'].dt.year
    df['month']         = df['start_date'].dt.month
    df['month_name']    = df['month'].map(lambda month_number: month_name(month_number))
    df['week']          = df['start_date'].dt.week
    df['day']           = df['start_date'].dt.dayofweek
    df['moving_time']   = df['moving_time'].apply(lambda seconds : round(seconds / 3600, 1)) # seconds to hours
    df['elapsed_time']  = df['elapsed_time'].apply(lambda seconds : round(seconds / 3600, 1)) # seconds to hours
    df['distance']      = df['distance'].apply(lambda meters : round(meters / 1000, 1)) # m to km
    df['average_speed'] = df['average_speed'].apply(lambda meters : round(meters * 3.6, 1)) # m/s to km/h
    
    df['achievement_count'] = df['achievement_count'].astype(float)
    df['kudos_count']       = df['kudos_count'].astype(float)
    df['comment_count']     = df['comment_count'].astype(float)
    df['total_photo_count'] = df['total_photo_count'].astype(float)
    return df

def get_map_data(df):
    '''Add some columns to the df required for plotting the map.'''     
    # drop activities with no polylines (cannot be displayed on map anyway)
    has_polyline = df['map'].map(lambda x: True if x.get('summary_polyline') else False)
    #~ df = df.set_index(has_polyline) 
    #~ df = df.loc[True]
    df = df[has_polyline]

    df['polyline_decoded'] = df['map'].map(lambda x: decode_polyline(x['summary_polyline']))
    df['polyline_minmax']  = df['polyline_decoded'].map(get_polyline_minmax)
    df['strava_link']      = df['id'].map(lambda ID: 'https://www.strava.com/activities/{}'.format(ID))
    df['start_date']       = df['start_date'].dt.strftime('%d %B %Y') # overwrite
    return df
    
def fltr(df, inputs):
    '''Filter a dataframe by the provided
    inputs dict.
    '''
    user_cols = list(df)
    for k, v in inputs.items():
        if k in user_cols:
            # don't filter if no filter value provided (initial load)
            if v[0] != '': 
                mask = (df[k].astype(str).isin(v))
                df = df[mask]
        #~ else:
            #~ print('Skipping {}'.format(k))
    return df
    
class Chart:
    def __init__(self, data_df):
        self.data = data_df
        
class Heatmap(Chart):
    def __init__(self, data_df, inputs):
        super().__init__(data_df)
        self.inputs = inputs
        self.x_name = self.axis_name('x')
        self.y_name = self.axis_name('y')
        self.z_name = self.axis_name('z')
        
        self.xy_axis_map = {
            'year': sorted(self.data['year'].unique().tolist()),
            'month': [i for i in range(1, 13)],
            'week': [i for i in range(1, 53)],
            'day': [i for i in range(7)],
        }
        
    def axis_name(self, xyz):
        key = 'heatmap_{}_name'.format(xyz)
        return self.inputs[key][0]
    
    def xy_axis(self, axis_name):
        return self.xy_axis_map[axis_name]
    
    #~ def z_axis_OLD(self):
        #~ # are those fillnas required?
        #~ z_axis = [
            #~ [
                #~ self.data[(self.data[self.y_name] == y_value) & (self.data[self.x_name] == x_value)][self.z_name].sum()
                #~ for x_value in sorted(self.data[self.x_name].fillna(0).unique().tolist())
            #~ ]
            #~ for y_value in sorted(self.data[self.y_name].fillna(0).unique().tolist())
        #~ ]
        #~ return z_axis
        
    def z_axis(self):
        df = self.data
        x = df[self.x_name]
        y = df[self.y_name]
        
        bottom = min(self.xy_axis_map[self.x_name])
        top = max(self.xy_axis_map[self.x_name]) + 1
        
        mux = pd.MultiIndex.from_product([y.unique(), np.arange(bottom, top)])
        z = (df[self.z_name].groupby([y, x])
              .sum()
              .reindex(mux, fill_value=0)
              .groupby(level=0)
              .apply(list)
              .tolist()
            )
        return z
        
    def to_dict(self):
        d = {
            'x_axis': self.xy_axis(self.x_name),
            'y_axis': self.xy_axis(self.y_name),
            'z_axis': self.z_axis(),
        }
        return d

class Map(Chart):
    def __init__(self, data_df):
        super().__init__(data_df)
       
    def to_list(self):
        '''Return a list of dicts,
        each dict representing an activity.
        '''
        # limiting the json output to only those columns that are required by the map - for better perfomance!
        select_cols = [
            'id',
            'name',
            'start_date',
            'polyline_decoded',
            'polyline_heat',
            'strava_link',
        ]
        lst = self.data[select_cols].to_dict(orient='records') 
        return lst
        
class Table:
    def __init__(self, data_df):
        self.data = data_df

    def to_list(self):
        lst = self.data.to_dict(orient='records')
        lst = replace_nan(lst)
        return lst        
