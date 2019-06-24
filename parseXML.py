import pandas as pd
import xml.etree.ElementTree as EleT
import geopandas as gpd
from shapely import geometry
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import numpy as np


def parse_data(path):
    tree = EleT.parse(path)
    root = tree.getroot()
    coordinates = [data.text for data in root.findall('.//{http://www.opengis.net/gml/3.2}posList')]
    df = pd.DataFrame.from_dict({'polygons': coordinates})
    df['polygons'] = df['polygons'].apply(create_polygon)
    df['centroid'] = df['polygons'].apply(create_centriod)
    return df


def create_centriod(x):
    if x:
        return x.centroid
    else:
        return None

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
    try:
        assert len(x.split('\n')) > 4, 'LinearRing must have at least 3 coordinates'
    except (AssertionError, ValueError):
        print("There are points less than 3 coordinates")
        points = []
        for i in x.split('\n'):
            if i is not '':
                points.append(tuple(reversed([float(yx) for yx in i.split(' ')])))
        print(points)
        assert len(points) == 2, 'Not two points!'
        return geometry.LineString(points)
    for i in x.split('\n'):
        if i is not '':
            lat_list.append(float(i.split(' ')[0]))
            long_list.append(float(i.split(' ')[1]))
    return geometry.Polygon([long, lat] for long, lat in zip(long_list, lat_list))


def ams_kumamoto():
    ams_kumamoto_df = pd.read_csv('kumamoto_data.csv', encoding='cp932')
    ams_kumamoto_df = ams_kumamoto_df[(ams_kumamoto_df['取込緯度'] < 32.92) & (ams_kumamoto_df['取込緯度'] > 32.67) & \
                (ams_kumamoto_df['取込経度'] < 130.9) & (ams_kumamoto_df['取込経度'] > 130.5)].reset_index(drop=True)
    # There are outlayers from the AMS data in terms of latitude and longitude
    ams_kumamoto_df.rename(columns={'取込緯度': 'lat', '取込経度': 'long'}, inplace=True)
    points = [geometry.Point(xy) for xy in zip(ams_kumamoto_df.long, ams_kumamoto_df.lat)]
    ams_kumamoto_df = ams_kumamoto_df.drop(['long', 'lat'], axis=1)
    crs = {'init': 'epsg:4326'}
    ams_kumamoto_gdf = gpd.GeoDataFrame(ams_kumamoto_df, crs=crs, geometry=points)
    return ams_kumamoto_gdf


def ckdnearest(gdfa, gdfb, gbf):
    print(gdfa)
    print(gdfb)
    print(gbf)
    nA = np.array(list(zip(gdfa.geometry.x, gdfa.geometry.y)))
    nB = np.array(list(zip(gdfb.geometry.x, gdfb.geometry.y)))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    return gbf.loc[idx].reset_index(drop=True)


def data_all():
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
    return df_all


def plot_basic(df_all):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    gdf = convert_to_polygon(df_all)
    gdf.plot(ax=ax, color='white', edgecolor='black')
    plt.show()


def plot_basic_ams(df_all):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    gdf = convert_to_polygon(df_all)
    gdf = gdf.copy()
    gdf.plot(ax=ax, color='white', edgecolor='black')
    ams_gdf = ams_kumamoto()
    ams_gdf.plot(ax=ax, marker='o', color='red', markersize=1)
    plt.show()


def plot_matched_ams(df_all):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    kumamoto_df = ams_kumamoto()
    cent_df = convert_to_centroid(df_all)
    cent_df = cent_df.copy()
    gbf = convert_to_polygon(df_all)
    matched_df = ckdnearest(kumamoto_df, cent_df, gbf)
    isin(kumamoto_df, matched_df)
    """
    print(kumamoto_df)
    matched_df.plot(ax=ax, color='white', edgecolor='black')
    kumamoto_df.plot(ax=ax, marker='o', color='red', markersize=0.5)
    plt.show()
    """


def isin(kumamoto_df, matched_df):
    kumamoto_df.rename(columns={'geometry': 'geometry_kumamoto'}, inplace=True)
    matched_df.rename(columns={'geometry': 'geometry_matched'}, inplace=True)
    kumamoto_df['geometry_matched'] = matched_df['geometry_matched']

    kumamoto_df['isin'] = kumamoto_df[['geometry_kumamoto', 'geometry_matched']].apply(lambda x: x[1].contains(x[0]), raw=True, axis=1)
    print(kumamoto_df['isin'].value_counts())
    return kumamoto_df


if __name__ == '__main__':
    path = 'FG-GML-493004-ALL-20190101\FG-GML-493004-BldL-20190101-0001.xml'
    path1 = 'FG-GML-493004-ALL-20190101\FG-GML-493004-BldA-20190101-0001.xml'
    df = parse_data(path)
    df1 = parse_data(path1)
    gdf = convert_to_polygon(df)
    gdf1 = convert_to_polygon(df1)
    base = gdf.plot(color='white', edgecolor='black', linewidth=2)
    gdf1.plot(ax=base)
    plt.show()
    # print(ams_kumamoto())
    #df_all = data_all()
    #plot_matched_ams(df_all)
    #plot_basic(df_all)
    # plot_matched_ams(df_all)
    # df2 = parseData(path2)
