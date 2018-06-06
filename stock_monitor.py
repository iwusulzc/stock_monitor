from splinter import Browser
import traceback
import time
import re
import pandas as pd

from abc import ABCMeta, abstractmethod 

import itchat

class Itchat(object):
	def __init__(self, toUserName, isChatroom):
		self.__isChatroom = isChatroom
		self.__toUserName = toUserName

	def login(self):
		itchat.auto_login()

		if (self.__isChatroom):
			self.__toUserName = itchat.search_chatrooms(userName = self.__toUserName)['UserName']
		else:
			friend = itchat.search_friends(name = self.__toUserName)
			if friend:
				self.__toUserName = friend[0]['UserName']

	def send_file(self, file):
		itchat.send_file(file, toUserName = self.__toUserName)
		
class BaseSpider(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		pass

	@abstractmethod
	def parse(self, browser):
		pass

	@abstractmethod
	def start(self):
		pass

class Spider(BaseSpider):
	start_urls = []

	def __init__(self, browser_driver_name = 'chrome'):
		self.browser = Browser(browser_driver_name)

	def start(self):
		for url in self.start_urls:
			try:
				self.browser.visit(url)
				self.parse(self.browser)
			except Exception as e:
				print(e)
				traceback.print_exc()

class EastmoneySpider(Spider):
	start_urls = ['http://data.eastmoney.com/zjlx/list.html']

	def __init__(self):
		self.__itchat = Itchat(u'九品闲人', False)
		self.__itchat.login()
		super().__init__()

	def parse(self, browser):
		filename = 'today_up_info.csv'
		for i in range(2):
			items = self.today_up_info_parse(browser)
			for data in items:
				data = [data]
				df = pd.DataFrame(data)
				df.to_csv(filename, index = False, \
					header = False, encoding = 'gbk', mode = 'a+')
		self.__itchat.send_file(filename)

	def today_up_info_parse(self, browser):
		tables = browser.find_by_xpath('//table[@id="dt_1"]')
		today_up = tables.find_by_text(u'今日涨跌').last
		if today_up:
			today_up.click()
			time.sleep(1)

			trs = browser.find_by_xpath('//table[@id="dt_1"]/*/tr')

			head1 = trs[0].text.split()
			head2 = trs[1].text.split()
			head = []
			head.extend(head1[1:3])
			head.append(head2[0])
			head.extend(head2[2:4])
			head.extend(head2[5:7])
			head.extend(head2[8:9])
			head.append(head1[8])

			for i in range(len(head)):
				head[i] = re.sub(u'主力', '', head[i])
			yield head

			today_up_stock = []
			today_up_stock.append(head)

			stat = {}

			for i in range(2, len(trs)):
				content = []
				c = trs[i].text.split()

				# 今日涨跌值
				up_value = float(re.sub('%', '', c[9]))
				if (abs(up_value) < 5):
					break

				content.extend(c[1:3])
				content.append(c[7])
				content.extend(c[9:11])
				content.extend(c[12:14])
				content.extend(c[15:17])

				# 统计行业占比
				if content[-1] in stat:
					stat[content[-1]] += 1
				else:
					stat[content[-1]] = 1

				yield content

			st = sorted(stat.items(), key = lambda d: d[1], reverse = True)
			head_len = len(head)
			st_len = len(st)

			for i in range(0, st_len, head_len):
				content = []
				for k, v in st[i : i + head_len]:
					content.append('{}:{}'.format(k, v))
				yield content

s = EastmoneySpider()
s.start()