import pandas as pd
import xml.etree.ElementTree as ET

def parseData(path):
    tree = ET.parse(path)
    root = tree.getroot()
    coordinates = [data.text for data in root.findall('.//{http://www.opengis.net/gml/3.2}posList')]
    df = pd.DataFrame.from_dict({'geometry': coordinates})
    print(df)
    return df 


if __name__ == '__main__':
    path = r'C:\kawaguchi_research\FG-GML-493004-ALL-20190101\FG-GML-493004-BldA-20190101-0001.xml'
    path2 = r'C:\kawaguchi_research\FG-GML-493005-ALL-20190101\FG-GML-493005-BldA-20190101-0001.xml'
    df = parseData(path)
    df2 = parseData(path2)