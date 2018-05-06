from splinter import Browser
import time
import re
import pandas as pd

b = Browser()
b.visit('http://data.eastmoney.com/zjlx/list.html')

def today_up_info(b):
    today_up = b.find_by_text(u'今日涨跌')
    if today_up:
        today_up[1].click()

        table = b.find_by_xpath('//table[@id="dt_1"]/*/tr')
        head1 = table[0].text.split()
        head2 = table[1].text.split()
        head = []
        head.extend(head1[1:3])
        head.append(head2[0])
        head.extend(head2[2:4])
        head.extend(head2[5:7])
        head.extend(head2[8:9])
        head.append(head1[8])

        for i in range(len(head)):
            head[i]=re.sub(u'主力', '', head[i])
        print(head)

        today_up_stock = []
        today_up_stock.append(head)

        stat = {}
        
        for i in range(2, len(table)):
            content = []
            print(table[i].text)
            c = table[i].text.split()

            # 今日涨跌
            up_value = float(re.sub('%', '', c[9]))
            if (abs(up_value) < 9):
                break
            
            content.extend(c[1:3])
            content.append(c[7])
            content.extend(c[9:11])
            content.extend(c[12:14])
            content.extend(c[15:17])
            print(content)

            if content[-1] in stat:
                stat[content[-1]] += 1
            else:
                stat[content[-1]] = 1
            
            today_up_stock.append(content)

        st = sorted(stat.items(), key=lambda d: d[1], reverse=True)
        head_len = len(head)
        st_len = len(st)

        for i in range(0, st_len, head_len):
            content = []
            for k, v in st[i : i + head_len]:
                content.append('{}:{}'.format(k, v))
            today_up_stock.append(content)
        print(today_up_stock)
        
        h = pd.DataFrame(today_up_stock)
        h.to_csv('today_up_info.csv', index=False, header=False, encoding='gb2312')

for i in range(len(bl)):
    b.click_link_by_text(bl[i].text)
    time.sleep(1)
    b.driver.switch_to.window(b.driver.window_handles[-1])
    
    while b.is_element_not_present_by_id('htmlContent'):
        print("wait")
        time.sleep(1)
        
    t = b.find_by_tag('h1')
    c = b.find_by_xpath('//div[@id="htmlContent"]')
    f.write(t.text.encode('utf-8'))
    f.write(c.value.encode('utf-8'))
    b.windows.current.close()
