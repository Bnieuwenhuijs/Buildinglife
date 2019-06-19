from Building_information_api import get_building_properties
import pandas as pd 
import csv

building = []

n = 21
while n < 56:
    building_properties = get_building_properties('8603EW', str(n), False)
    building_properties['windows'] = 5
    building.append(building_properties)
    n = n + 1



n = 42
while n < 49:
    building_properties = get_building_properties('7813AA', str(n), False)
    building_properties['windows'] = 5
    building.append(building_properties)
    n = n + 1


n = 2
while n < 11:
    building_properties = get_building_properties('6051MW', str(n), False)
    building_properties['windows'] = 5
    building.append(building_properties)
    n = n + 2

n = 19
while n < 25:
    building_properties = get_building_properties('6051HN', str(n), False)
    building_properties['windows'] = 5
    building.append(building_properties)
    n = n + 2

df = pd.DataFrame(building) 
export_csv = df.to_csv (r'C:\Users\Bart Nieuwenhuijs\Documents\export_dataframe.csv', index = None, header=True)