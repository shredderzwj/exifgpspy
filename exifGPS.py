# coding: utf-8


from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import sys
import os


class GPSInfo(object):
    def __init__(self, img_file):
        """
        :param img_file: str 图像文件的路径
        """
        self.file = img_file
        self.is_image = True
        try:
            self.image = Image.open(img_file)
            if not hasattr(self.image, '_getexif'):
                print('This image does not have EXIF -> {}'.format(self.file))
        except Exception as e:
            self.is_image = False
            print('Input file is not a image file -> {}'.format(self.file))
            #raise Image.UnidentifiedImageError

    def __repr__(self):
        if self.coordinate:
            return 'coordinate:({}, {})'.format(*self.coordinate)
        return 'This image does not have GPSInfo -> {}'.format(self.file)

    @property
    def exif_raw(self):
        """原始的exif"""
        if hasattr(self.image, '_getexif'):
            return self.image._getexif()
        return {}

    @property
    def exif(self):
        """exif"""
        if self.exif_raw:
            return {TAGS.get(k, k): v for k, v in self.exif_raw.items()}
        return {}

    @property
    def gps_info_raw(self):
        """exif中原始的GPSInfo"""
        if self.exif_raw:
            if self.exif_raw.get(34853):
                return self.exif_raw.get(34853)
        return {}

    @property
    def gps_info(self):
        """GPSInfo"""
        if self.gps_info_raw:
            return {GPSTAGS.get(k, k): v for k, v in self.gps_info_raw.items()}
        return {}

    def __get_lng_lat(self, ref_code):
        """
        获取exif中的GPS信息的经纬度方法。
        :param ref_code: 是经度还是纬度的代码
        :return: tuple 返回 度分秒格式的坐标值，为三元组，三个值分别为度分秒
        """
        try:
            d, m, s = self.gps_info_raw.get(ref_code + 1)
            d = float(d)
            m = float(m)
            s = float(s)
            if self.gps_info_raw.get(ref_code) == 'W' or self.gps_info_raw.get(ref_code) == 'S':
                return -d, -m, -s
            return d, m, s
        except:
            return None

    @staticmethod
    def convert_to_ddd(degree, minute, second):
        """
        将度分秒格式转换为 度
        :param degree: float 度
        :param minute: float 分
        :param second: float 秒
        :return: float 转换后的度
        """
        return degree + minute / 60 + second / 3600

    @property
    def latitude_dms(self):
        """度分秒格式的纬度，返回值为三元组，分别为度分秒"""
        return self.__get_lng_lat(1)

    @property
    def latitude(self):
        """纬度"""
        if self.latitude_dms:
            return self.convert_to_ddd(*self.latitude_dms)
        return None

    @property
    def longitude_dms(self):
        """度分秒格式的经度，返回值为三元组，分别为度分秒"""
        return self.__get_lng_lat(3)

    @property
    def longitude(self):
        """经度"""
        if self.longitude_dms:
            return self.convert_to_ddd(*self.longitude_dms)
        return None

    @property
    def coordinate(self):
        """经纬坐标，返回值为二元组，分别为经度和纬度"""
        if self.latitude and self.longitude:
            return self.longitude, self.latitude
        return ()


if __name__ == '__main__':
    help_str = """
    获取图像文件EXIF中的GPS经纬坐标点(WGS84坐标系)

    使用方法如下：python exifGPS.py imageFile
    """
    if len(sys.argv) < 2:
        print(help_str)
    else:
        file = sys.argv[1]
        if os.path.exists(file):
            info = GPSInfo(file)
            if info.coordinate:
                print(info.coordinate)
            else:
                if info.is_image:
                    print('This image does not have GPSInfo -> {}'.format(file))
        else:
            print('输入的文件不存在！！')
