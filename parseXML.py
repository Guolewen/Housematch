import pandas as pd
import xml.etree.ElementTree as EleT
import geopandas as gpd
from shapely import geometry
import matplotlib.pyplot as plt


def parse_data(path):
    tree = EleT.parse(path)
    root = tree.getroot()
    coordinates = [data.text for data in root.findall('.//{http://www.opengis.net/gml/3.2}posList')]
    df = pd.DataFrame.from_dict({'polygons': coordinates})
    df['polygons'] = df['polygons'].apply(create_polygon)
    df['centroid'] = df['polygons'].apply(create_centriod)
    return df


def create_centriod(x):
    return x.centroid


def convert_to_polygon(df):
    crs = {'init': 'epsg:4326'}
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=df['polygons'])
    return gdf


def convert_to_centroid(df):
    crs = {'init': 'epsg:4326'}
    cent_df = gpd.GeoDataFrame(df, crs=crs, geometry=df['centroid'])
    return cent_df


def create_polygon(x):
    lat_list = []
    long_list = []
    for i in x.split('\n'):
        if i is not '':
            lat_list.append(float(i.split(' ')[0]))
            long_list.append(float(i.split(' ')[1]))

    return geometry.Polygon([long, lat] for long, lat in zip(long_list, lat_list))


def ams_kumamoto():
    ams_kumamoto_df = pd.read_csv('kumamoto_data.csv', encoding='cp932')
    # There are outlayers from the AMS data in terms of latitude and longitude
    ams_kumamoto_df.rename(columns={'取込緯度': 'lat', '取込経度': 'long'}, inplace=True)
    points = [geometry.Point(xy) for xy in zip(ams_kumamoto_df.long, ams_kumamoto_df.lat)]
    ams_kumamoto_df = ams_kumamoto_df.drop(['long', 'lat'], axis=1)
    crs = {'init': 'epsg:4326'}
    ams_kumamoto_gdf = gpd.GeoDataFrame(ams_kumamoto_df, crs=crs, geometry=points)
    return ams_kumamoto_gdf


def main():
    path1 = 'FG-GML-493004-ALL-20190101\FG-GML-493004-BldA-20190101-0001.xml'
    path2 = 'FG-GML-493005-ALL-20190101\FG-GML-493005-BldA-20190101-0001.xml'
    path3 = 'FG-GML-493006-ALL-20190401\FG-GML-493006-BldA-20190401-0001.xml'
    path4 = 'FG-GML-493014-ALL-20181001\FG-GML-493014-BldA-20181001-0001.xml'
    path5 = 'FG-GML-493015-ALL-20190401\FG-GML-493015-BldA-20190401-0001.xml'
    path6 = 'FG-GML-493016-ALL-20190401\FG-GML-493016-BldA-20190401-0001.xml'
    path7 = 'FG-GML-493024-ALL-20190401\FG-GML-493024-BldA-20190401-0001.xml'
    path8 = 'FG-GML-493025-ALL-20190401\FG-GML-493025-BldA-20190401-0001.xml'
    path9 = 'FG-GML-493026-ALL-20190401\FG-GML-493026-BldA-20190401-0001.xml'
    path_list = [path1, path2, path3, path4, path5, path6, path7, path8, path9]
    df_list = []
    for path in path_list:
        df = parse_data(path)
        df_list.append(df)
    df_all = pd.concat(df_list, ignore_index=True)
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    gdf = convert_to_polygon(df_all)
    gdf = gdf.copy()
    ams_gdf = ams_kumamoto()
    #cent_df = convert_to_centroid(df_all)
    gdf.plot(ax=ax, color='white', edgecolor='black')
    ams_gdf.plot(ax=ax, marker='o', color='red', markersize=0.8)
    #cent_df = cent_df.to_crs(gdf.crs)
    #cent_df.plot(ax=ax, marker='o', color='red', markersize=0.5)

    # plt.savefig('kumamoto_all.png', dpi=1000)
    plt.show()


if __name__ == '__main__':
    # print(ams_kumamoto())
    main()
    # df2 = parseData(path2)
