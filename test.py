# coding: utf-8

from exifGPS import GPSInfo


def test():
    info = GPSInfo('test.jpg')
    print(info)

    import coordinate_transform
    amap_coord = coordinate_transform.wgs84_to_gcj02(*info.coordinate)
    bmap_coord = coordinate_transform.wgs84_to_bd09(*info.coordinate)
    print('WGS84坐标：', info.coordinate)
    print('高德地图坐标：', amap_coord)
    print('百度地图坐标：', bmap_coord)
    
    from amap import AMapReGeo
    AMAP_KEY = '4f53456651571c48e8b089f85a2b79ef'  # 我的高德key

    regeo = AMapReGeo("{},{}".format(*amap_coord), AMAP_KEY)
    print("拍摄地址：", regeo.formatted_address)


if __name__ == '__main__':
    test()