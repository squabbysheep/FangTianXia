import scrapy
import re
from urllib.parse import urljoin
from fang.items import NewHouseItem, ESFHouseItem
from scrapy_redis.spiders import RedisSpider


class FangtianxiaSpider(RedisSpider):
    name = 'fang'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.html']
    redis_key = "fangtianxia:start_urls"

    def parse(self, response):
        trs = response.xpath('//div[@class="outCont"]//tr')
        # 首先设为None，下方判断有值在赋给province:省份
        province = None
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            # 提取省份，由于省份不是每一行都有的，所以要过滤一下
            province_td = tds[0]
            # 没有省份的那一行会有空格
            province_text = province_td.xpath('.//text()').extract_first()
            # 用sub替换一下，好判断
            province_text = re.sub(r'\s', '', province_text)
            # 如果有值，就赋给province
            if province_text:
                province = province_text
            # 不提取海外的
            if '其它' in province:
                continue
            # 接下来提取城市链接和城市名称
            city_links = tds[1].xpath('.//a')
            for city_link in city_links:
                city_url = city_link.xpath('.//@href').extract_first()  # 'http://bj.fang.com/'
                city_name = city_link.xpath('.//text()').extract_first()  # '北京'
                # 构建新房和二手房的url
                url_module = city_url.split('fang')
                prefix = url_module[0]  # 'http://bj.'
                # 北京url特殊，需特殊处理
                if 'bj' in prefix:
                    # b91代表第1页，b924代表第24页.esf同理
                    # 北京新房 按开盘时间第11页    'https://newhouse.fang.com/house/s/b1saledate-b911/'
                    newhouse_url = 'https://newhouse.fang.com/house/s/b1saledate-b91/'
                    # 北京二手房 按开盘时间第11页    'https://esf.fang.com/house/h316-i311/'
                    esf_url = 'https://esf.fang.com/house/h316-i31/'
                else:
                    # 构建新房的url
                    # 郑州新房 按开盘时间第11页      'https://zz.newhouse.fang.com/house/s/b1saledate-b911/'
                    newhouse_url = prefix + 'newhouse.fang.com/house/s/b1saledate-b91/'
                    # 构建二手房的url
                    # 郑州二手房 按开盘时间第11页    'https://zz.esf.fang.com/house/h316-i311/'
                    esf_url = prefix + 'esf.fang.com/house/h316-i31/'
                # meta里面可以携带一些参数信息放到Request里面，在callback函数里面通过response获取
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse,
                                     meta={'info': (province, city_name), 'url': newhouse_url}, errback=self.handle_err)
                # yield scrapy.Request(url=esf_url,callback=self.parse_esf,meta={'info':(province,city_name)})

    def handle_err(self, failure):
        # 1、通过meta传参获取请求失败的url
        url = failure.request.meta['url']
        # 2、将失败的url重新加入调度队列，解析方法使用parse_newhouse
        print('城市起始页 连续3次请求失败，重新放入调度队列，等待再次尝试：    ', url)
        yield scrapy.Request(url=url, callback=self.parse_newhouse)

    def parse_newhouse(self, response):
        # 解析新房具体字段
        # meta里面可以携带一些参数信息放到Request里面，在callback函数里面通过response获取
        province, city_name = response.meta.get('info')
        lis = response.xpath('//div[@class="nl_con clearfix"]/ul/li')
        for li in lis:
            # 广告和正常的房产两层class相同，唯一不同是广告有h3标签。如果是广告直接跳过
            ad = li.xpath('./div[@class="clearfix"]/h3/text()').extract_first()
            if ad:
                continue
            house_name = li.xpath(
                './/div[@class="house_value clearfix"]//div[@class="nlcd_name"]/a/text()').extract_first()
            if house_name:
                house_name = re.sub(r"\s", "", house_name)
            # 解析几居室
            rooms = '/'.join(li.xpath('.//div[@class="house_type clearfix"]/a/text()').extract())  # '3居/4居'
            # 销售电话
            phone_num = ''.join(li.xpath('.//div[@class="tel"]/p//text()').extract())
            # 解析房屋面积
            area = ''.join(li.xpath('.//div[@class="house_type clearfix"]/text()').extract())
            area = re.sub('\s|－|/', '', area)
            address = li.xpath('.//div[@class="address"]/a/@title').extract_first()
            # 是否开盘（在售、待售）
            sale = li.xpath(".//div[@class='fangyuan']/span/text()").extract_first()
            # 房屋卖点
            tags_list = li.xpath('//div[@id="sjina_C26_07"]//text()').extract()
            tags = list(filter(None, map(lambda x: x.strip(), tags_list)))[1:]
            tags = '/'.join(tags)
            # 每平米单价、少数整套价格
            price = li.xpath(".//div[@class='nhouse_price']/span/text()").extract_first()
            price_unit = li.xpath(".//div[@class='nhouse_price']/em/text()").extract_first()
            nearby = li.xpath('//div[@class="nhouse_price"]/label[2]/text()').extract_first()
            if nearby:
                price = li.xpath('//div[@class="nhouse_price"]/i/text()').extract_first()
            #
            if not price_unit:
                price = price
            else:
                price = price + price_unit  # '40500元/㎡'
            # 详情页url
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").extract_first()
            # 详情页可能会取空，加一个判断    TypeError: must be str, not NoneType
            if origin_url:
                origin_url = 'https:' + origin_url
            item = NewHouseItem()
            item['province'] = province
            item['city'] = city_name
            item['house_name'] = house_name
            item['sale'] = sale
            item['phone_num'] = phone_num if phone_num else '暂无电话'
            item['price'] = price
            item['tags'] = tags
            item['rooms'] = rooms
            item['area'] = area
            item['address'] = address
            item['origin_url'] = origin_url

            yield item

            # 提取最后一页
            last_url = response.xpath(
                '//ul[@class="clearfix"]/li[@class="fr"]/a[@class="last"]/@href').extract_first()  # '/house/s/b924/'
            # 如果某个冷门城市只有一页数据，last_url就不存在，.split('/')出异常
            if last_url:
                last_page = last_url.split('/')[-2].replace('b1saledate-b9', '')
                for i in range(1, int(last_page) + 1):
                    next_url = urljoin(response.url, '/house/s/b1saledate-b9{page}/'.format(page=str(i)))
                    if next_url:
                        yield scrapy.Request(url=next_url,
                                             callback=self.parse_newhouse,
                                             meta={'info': (province, city_name),
                                                   'url': next_url
                                                   },
                                             errback=self.handle_newhouse_err

                                             )

    def handle_newhouse_err(self, failure):
        # 1、通过meta传参获取请求失败的url
        url = failure.request.meta['url']
        # 2、将失败的url重新加入调度队列，解析方法使用parse_newhouse
        print('NewHouse 连续3次请求失败，重新放入调度队列，等待再次尝试：    ', url)
        yield scrapy.Request(url=url, callback=self.parse_newhouse)

    def parse_esf(self, response):
        # 二手房
        province, city_name = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item = ESFHouseItem()
            # 提取二手房title
            house_title = dl.xpath('//h4[@class="clearfix"]/a/@title').extract_first()

            if house_title:
                infos = dl.xpath(".//p[@class='tel_shop']/text()").extract()
                infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
                for info in infos:
                    if "厅" in info:
                        item["rooms"] = info
                    elif '层' in info:
                        item["floor"] = info
                    elif '向' in info:
                        item['toward'] = info
                    elif '㎡' in info:
                        item['area'] = info
                    elif '年建' in info:
                        item['build_year'] = re.sub("年建", "", info)

                # 省、市
                item['province'] = province
                item['city'] = city_name
                # 房子标题介绍
                item['house_title'] = house_title
                # 小区名字
                item['house_name'] = dl.xpath('.//p[@class="add_shop"]/a/@title').extract_first()
                # 联系人
                item['contacts'] = dl.xpath(
                    './/p[@class="tel_shop"]/span[@class="people_name"]/a/text()').extract_first() if dl.xpath(
                    './/p[@class="tel_shop"]/span[@class="people_name"]/a/text()') else '暂无联系人'
                # 地址
                item['address'] = dl.xpath('.//p[@class="add_shop"]/span/text()').extract_first()
                # 房屋卖点
                item['tags'] = '/'.join(dl.xpath('.//dd/p[3]/span/text()').extract()) if response.xpath(
                    './/dd/p[3]/span/text()') else '暂无卖点'
                # 总价
                price = dl.xpath('//dd[@class="price_right"]/span[1]/b/text()').extract_first()
                price_unit = dl.xpath('//dd[@class="price_right"]/span[1]/text()').extract_first()
                item['price'] = price + price_unit
                # 每平米均价
                item['unit'] = dl.xpath(".//dd[@class='price_right']/span[2]/text()").extract_first()
                # 详情页url
                detail_url = dl.xpath(".//h4[@class='clearfix']/a/@href").extract_first()
                item['origin_url'] = response.urljoin(detail_url)

                yield item

        # 下一页
        last_url = response.xpath(
            '//div[@class="page_al"]/p/a[contains(.,"末页")]/@href').extract_first()  # '/house/h316-i311/'
        # 如果某个冷门城市只有一页数据，last_url就不存在，.split('/')出异常
        if last_url:
            last_page = last_url.split('/')[-2].replace('h316-i3', '')
            for i in range(1, int(last_page) + 1):
                next_url = urljoin(response.url, '/house/h316-i3{page}/'.format(page=i))
                if next_url:
                    yield scrapy.Request(url=next_url,
                                         callback=self.parse_esf,
                                         meta={'info': (province, city_name)}
                                         )
