import pandas as pd
import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely import geometry
import matplotlib.pyplot as plt

def parseData(path):
    tree = ET.parse(path)
    root = tree.getroot()
    coordinates = [data.text for data in root.findall('.//{http://www.opengis.net/gml/3.2}posList')]
    df = pd.DataFrame.from_dict({'geometry': coordinates})
    df['geometry'] = df['geometry'].apply(create_polygon)
    print(df)
    crs = {'init': 'epsg:4326'}
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=df['geometry'])
    print(type(gdf))
    return gdf

def create_polygon(x):
    #print(x.split('\n'))
    lat_list = []
    long_list = []
    for i in x.split('\n'):
        if i is not '':
            lat_list.append(float(i.split(' ')[0]))
            long_list.append(float(i.split(' ')[1]))

    return geometry.Polygon([long, lat] for long, lat in zip(long_list, lat_list))




if __name__ == '__main__':
    path = 'FG-GML-493004-ALL-20190101\FG-GML-493004-BldA-20190101-0001.xml'
    path2 = 'FG-GML-493005-ALL-20190101\FG-GML-493005-BldA-20190101-0001.xml'
    gdf = parseData(path)
    figure = gdf.plot()

    plt.savefig('kumamoto.png', dpi=1800)
    plt.show()
    #df2 = parseData(path2)