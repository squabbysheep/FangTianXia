import scrapy
from scrapy import Field


class NewHouseItem(scrapy.Item):
    collection = 'newhouseitem'
    # 省份
    province = Field()
    # 城市
    city = Field()
    # 小区名字
    house_name = Field()
    # 是否开盘
    sale = Field()
    # 销售电话
    phone_num = Field()
    # 每平米价格
    price = Field()
    # 房屋卖点
    tags = Field()
    # 几居室
    rooms = Field()
    # 面积
    area = Field()
    # 地址
    address = Field()
    # 房天下详情url
    origin_url = Field()


class ESFHouseItem(scrapy.Item):
    collection = 'esfhouseitem'
    # 省份
    province = Field()
    # 城市
    city = Field()
    # 房子描述
    house_title = Field()
    # 小区名字
    house_name = Field()
    # 几室几厅
    rooms = Field()
    # 建筑面积
    area = Field()
    # 层
    floor = Field()
    # 朝向
    toward = Field()
    # 年代
    build_year = Field()
    # 联系人
    contacts = Field()
    # 地址
    address = Field()
    # 房屋卖点
    tags = Field()
    # 总价
    price = Field()
    # 单价
    unit = Field()
    # 详情页url
    origin_url = Field()
