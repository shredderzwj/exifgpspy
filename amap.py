# coding: utf-8
# #####################
# 高德地图的一些工具api进行python封装
# 主要有高德地图地理编码和逆地理编码。
# #####################

import re
import math
from urllib import parse
import requests


class AMapGeoAndReGeoBase(object):
    def __init__(self, api_url, **parameters):
        """
        :param api_url: str 请求的api url
        :param parameters: dict 请求参数
        self.result 查询结果。返回字典
        self.status bool 查询结果状态。成功获取到结果时为 Ture， 否则为False。
        """
        self.parameters = parameters
        self.api_url = api_url
        self.__response = None
        self.result = None
        self.status = False
        data = {k: str(v).lower() for k, v in parameters.items() if v}
        params = parse.urlencode(data)
        self.url = "{}?{}".format(api_url, params)

    def __call__(self, *args, **kwargs):
        self.get_result()
        return self.result

    @property
    def response(self):
        """请求响应对象，urllib的urlopen对象"""
        if not self.__response:
            self.__response = requests.get(self.url)
        return self.__response

    def get_result(self):
        """结果"""
        if self.response.status_code == 200:
            self.result = self.response.json(strict=False)
        if hasattr(self, 'formatted_address') and self.formatted_address:
            self.status = True
        if hasattr(self, 'coordinates') and self.coordinates:
            self.status = True
        return self.result


class AMapGeo(AMapGeoAndReGeoBase):
    def __init__(self, address, key='4f53456651571c48e8b089f85a2b79ef', city=None, batch=None, sig=None,
                 callback=None, api_url="http://restapi.amap.com/v3/geocode/geo"):
        """
        将详细的结构化地址转换为高德经纬度坐标。且支持对地标性名胜景区、建筑物名称解析为高德经纬度坐标。
        结构化地址举例：北京市朝阳区阜通东大街6号转换后经纬度：116.480881,39.989410
        地标性建筑举例：天安门转换后经纬度：116.397499,39.908722
        :param address: str 结构化地址信息 必须参数
                        规则遵循：国家、省份、城市、区县、城镇、乡村、街道、门牌号码、屋邨、大厦，
                        如：北京市朝阳区阜通东大街6号。如果需要解析多个地址的话，请用"|"进行间隔，
                        并且将 batch 参数设置为 True，最多支持 10 个地址进进行"|"分割形式的请求。
        :param key: str 高德Key 必须参数，已有默认值，若不可用请更换。
                        用户在高德地图官网申请Web服务API类型Key：https://lbs.amap.com/dev/
        :param city: str 指定查询的城市 可选参数
                        可选输入内容包括：指定城市的中文（如北京）、指定城市的中文全拼（beijing）、
                        citycode（010）、adcode（110000），不支持县级市。当指定城市查询内容为空时，
                        会进行全国范围内的地址转换检索。
                        adcode信息可参考城市编码表获取：https://lbs.amap.com/api/webservice/download
        :param batch: bool 批量查询控制 可选参数 默认值为False
                        batch 参数设置为 True 时进行批量查询操作，最多支持 10 个地址进行批量查询。
                        batch 参数设置为 False 时进行单点查询，此时即使传入多个地址也只返回第一个地址的解析查询结果。
        :param sig: str 数字签名 可选参数
                        请参考数字签名获取和使用方法：https://lbs.amap.com/faq/account/key/72
        :param callback: function object 回调函数 可选参数
                        callback 值是用户定义的函数名称，此参数只在 output 参数设置为 JSON 时有效。
        """
        parameters = {
            'address': address,
            'key': key,
            'city': city,
            'batch': batch,
            'sig': sig,
            'callback': callback,
        }
        super().__init__(api_url, **parameters)

    @property
    def coordinates(self):
        """地理编码坐标列表，此方法不支持批量操作（batch=True）"""
        if not self.result:
            self.get_result()
        if self.parameters.get('batch'):
            print('此方法不支持批量操作')
            return []
        if self.result.get('status') == '1' and int(self.result.get('count')) >= 1:
            locations = [x.get('location') for x in self.result.get('geocodes')]
        else:
            locations = []
        if locations:
            coords = [tuple(map(lambda x: float(x.strip()), _.split(','))) for _ in locations]
            return coords
        return []


class AMapReGeo(AMapGeoAndReGeoBase):
    def __init__(self, location, key='4f53456651571c48e8b089f85a2b79ef', poitype=None, radius=None,
                 extensions=None, batch=None, roadlevel=None, sig=None, callback=None, homeorcorp=None,
                 api_url='http://restapi.amap.com/v3/geocode/regeo'):
        """
        逆地理编码：将经纬度转换为详细结构化的地址，且返回附近周边的POI、AOI信息。
        例如：116.480881,39.989410 转换地址描述后：北京市朝阳区阜通东大街6号
        :param location: str 经纬度坐标 必填参数
                        传入内容规则：经度在前，纬度在后，经纬度间以“,”分割，经纬度小数点后不要超过 6 位。
                        如果需要解析多个经纬度的话，请用"|"进行间隔，并且将 batch 参数设置为 true，
                        多支持传入 20 对坐标点。每对点坐标之间用"|"分割。
        :param key: str 高德Key 必须参数，已有默认值，若不可用请更换。
                        用户在高德地图官网申请Web服务API类型Key：https://lbs.amap.com/dev/
        :param poitype: str 返回附近POI类型 可选参数
                        以下内容需要 extensions 参数为 all 时才生效。
                        逆地理编码在进行坐标解析之后不仅可以返回地址描述，也可以返回经纬度附近符合限定要求的POI内容
                        （在 extensions 字段值为 all 时才会返回POI内容）。设置 POI 类型参数相当于为上述操作限定要求。
                        参数仅支持传入POI TYPECODE，可以传入多个POI TYPECODE，相互之间用“|”分隔。
                        该参数在 batch 取值为 true 时不生效。
                        获取 POI TYPECODE 可以参考POI分类码表：https://lbs.amap.com/api/webservice/download
        :param radius: float 搜索半径 可选参数 默认值为1000米
                        radius取值范围在0~3000，默认是1000。单位：米
        :param extensions: str 返回结果控制 可选参数 默认值为base
                        extensions 参数默认取值是 base，也就是返回基本地址信息；
                        extensions 参数取值为 all 时会返回基本地址信息、附近 POI 内容、道路信息以及道路交叉口信息。
        :param batch: bool 批量查询控制 可选 默认值为 False
                        batch 参数设置为 True 时进行批量查询操作，最多支持 20 个经纬度点进行批量地址查询操作。
                        batch 参数设置为 False 时进行单点查询，此时即使传入多个经纬度也只返回第一个经纬度的地址解析查询结果。
        :param roadlevel: int 道路等级 可选
                        以下内容需要 extensions 参数为 all 时才生效。
                        可选值：0，1
                        当roadlevel=0时，显示所有道路
                        当roadlevel=1时，过滤非主干道路，仅输出主干道路数据
        :param sig: str 数字签名 可选参数
                        请参考数字签名获取和使用方法：https://lbs.amap.com/faq/account/key/72
        :param callback: function object 回调函数 可选参数
                        callback 值是用户定义的函数名称，此参数只在 output 参数设置为 JSON 时有效。
        :param homeorcorp: int 是否优化POI返回顺序 可选 默认值为 0
                        以下内容需要 extensions 参数为 all 时才生效。
                        homeorcorp 参数的设置可以影响召回 POI 内容的排序策略，目前提供三个可选参数：
                        0：不对召回的排序策略进行干扰。
                        1：综合大数据分析将居家相关的 POI 内容优先返回，即优化返回结果中 pois 字段的poi顺序。
                        2：综合大数据分析将公司相关的 POI 内容优先返回，即优化返回结果中 pois 字段的poi顺序。
        """
        parameters = {
            'location': re.sub(r'\s', '', str(location)),
            'key': key,
            'poitype': poitype,
            'radius': radius,
            'extensions': extensions,
            'batch': batch,
            'roadlevel': roadlevel,
            'sig': sig,
            'callback': callback,
            'homeorcorp': homeorcorp,
        }
        super().__init__(api_url, **parameters)

    def get_cell_info_base(self, key):
        """提取常用信息的魔板"""
        if not self.result:
            self.get_result()
        if self.parameters.get('batch'):
            print('此方法不支持批量操作')
            return None
        if self.result.get('status') == '1':
            return self.result.get('regeocode').get(key)
        return None

    def get_cell_info_base1(self, key):
        info = self.get_cell_info_base('addressComponent')
        if info:
            return info.get(key)
        return None

    @property
    def formatted_address(self):
        """逆地理编码结构化地址信息，此方法不支持批量操作（batch=True）"""
        return self.get_cell_info_base('formatted_address')

    @property
    def city(self):
        return self.get_cell_info_base1('city')

    @property
    def province(self):
        return self.get_cell_info_base1('province')

    @property
    def district(self):
        return self.get_cell_info_base1('district')

    @property
    def township(self):
        return self.get_cell_info_base1('township')

    @property
    def adcode(self):
        return self.get_cell_info_base1('adcode')

    @property
    def towncode(self):
        return self.get_cell_info_base1('towncode')


class GeoDistance(object):
    @classmethod
    def single(cls, lng_0, lat_0, lng_1, lat_1, earth_radius=6378137):
        """
           计算两个地理位置(两个经纬坐标点)间的实际地面距离
           :param lng_0: float  第一个点的经度
           :param lat_0: float  第一个点的纬度
           :param lng_1: float  第二个点的经度
           :param lat_1: float  第二个点的纬度
           :param earth_radius: float 地球半径，单位m
           :return: float 距离结果，单位m
        """
        lng1, lat1, lng2, lat2 = map(math.radians, [lng_0, lat_0, lng_1, lat_1])
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        # a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        a = (1 - math.cos(dlat) + (1 - math.cos(dlng)) * math.cos(lat1) * math.cos(lat2)) / 2  # 高德地图JavaScript中的公式
        distance = 2 * earth_radius * math.asin(math.sqrt(a))  # 高德地图JavaScript中的地球平均半径，6378137m
        return distance

    @classmethod
    def multi(cls, *points, is_ring=False, earth_radius=6378137):
        """
        计算多个点所连成的折线的实际地面距离
        :param points: 二元组 点列表，格式为 (经度float, 纬度float)
        :param is_ring: bool 是否闭合
        :param earth_radius: float 地球半径，单位m
        :return: float 距离结果，单位m
        """
        if len(points) < 2:
            return 0
        distance = 0
        for i, point in enumerate(points[1:]):
            distance += cls.single(*points[i], *point, earth_radius)
        if is_ring:
            distance += cls.single(*points[0], *points[-1], earth_radius)
        return distance


if __name__ == '__main__':
    geo = AMapGeo('郑州市燕庄地铁站')
    print(geo())
    print(geo.status)
    print(geo.coordinates)

    regeo = AMapReGeo('116.407387, 39.904179')
    print(regeo())
    print(regeo.status)
    print(regeo.formatted_address)
