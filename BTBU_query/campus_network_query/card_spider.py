
# 用 card.btbu.edu.cn接口实现 一卡通查询功能
import requests
import datetime
import bs4

class spider:

    def __init__(self, studentID, password):
        self.studentID = studentID
        self.password = password
        self.url = 'http://card.btbu.edu.cn/'
        self.data = []
        self.totalPage = 1
        self.personMsg = {'studentID': self.studentID, 'password': self.password}
        self.personMsgItems = ['姓名', '性别', '部门', '职务', '身份', '证件号码', '一卡通号', '卡状态']
        self.isLogin = False

        # 第一步 获取cookies
        self.cookies = self.getCookie().get_dict()
        # 第二步 自动登录
        self.autoLogin()


    def getCookie(self):
        url = self.url + 'CardWeb/query.asp'
        response = requests.get(url = url)
        cookies = response.cookies
        return cookies

    def autoLogin(self):
        url = self.url + 'CardWeb/queryresult.asp'
        params ={
            'cardno': self.studentID,
            'password': self.password,
            'Submit': '查询',     #
        }
        response = requests.get(url = url, params=params, cookies = self.cookies)
        response.encoding = 'gbk'
        if response.text.find('退出登陆') != -1:
            self.isLogin = True


    def recentDaysMsg(self, days:int = 90, limit:int = 20, _offset:int = 1):     # 查询最近90天情况，最多20条有效数据，offset代表第几页
        if self.isLogin is False:
            # print('卡号密码不对!')
            return
        url = self.url + 'CardWeb/finance.asp'

        dateEnd = datetime.datetime.now()
        dateStart = dateEnd + datetime.timedelta(days= - days)

        params = {
            'offset': _offset,
            'start': dateStart.strftime('%Y-%m-%d'),
            'endto': dateEnd.strftime('%Y-%m-%d'),
        }

        response = requests.get(url = url, params = params, cookies = self.cookies)
        #print(response.text.encode('latin1').decode('gbk'))
        soup = bs4.BeautifulSoup(response.text.encode('latin1').decode('gbk'), 'lxml')

        # 抓取网页总数
        self.totalPage = int(soup.select('.main')[1].select('font')[0].text)
        currentPage =  int(soup.select('.main')[1].select('font')[1].text)

        # 依照标签进行查找表数据
        tableSoup = soup.find_all('tr', attrs={'bgcolor': '#e6e6e6'})
        item: bs4.element.Tag
        for item in tableSoup:
            itemList = [temp.text for temp in item.find_all('td')]
            itemData = {
                'studentID': self.studentID,
                '交易时间': itemList[0],
                '交易内容': itemList[1],
                '交易金额(元)': itemList[2],
                '剩余金额(元)': itemList[3],
                '交易地点': itemList[4],
            }
            self.data.append(itemData)
            limit -= 1

        if tableSoup != [] and limit > 0 and currentPage < self.totalPage:
            self.recentDaysMsg(days = days, limit = limit, _offset = int(currentPage) + 1)

    def getPersonMsg(self, personMsgItems = []):
        '''
        获取个人信息,以便存入数据库
        :param personMsgItems: 个人信息的名目的list
        :return: dict
        '''
        if personMsgItems != []:
            self.personMsgItems = personMsgItems
        if self.isLogin is False:
            # print('卡号密码不对!')
            return
        url = self.url + 'CardWeb/ShowPersonnel.asp'
        response = requests.get(url = url, cookies = self.cookies)
        soup = bs4.BeautifulSoup(response.text.encode('latin1').decode('gbk'), 'lxml')
        tableSoup = soup.find('table', attrs={'cellspacing': "1"})

        for item in tableSoup:
            if item.__class__.__name__ is 'Tag':
                key, value = [temp.text for temp in item.find_all('td')]
                if key in self.personMsgItems:
                    self.personMsg[key] = value

        return self.personMsg

if __name__ == '__main__':
    cardSpider = spider('1604010319', '085952')
    cardSpider.recentDaysMsg(days=30, limit = 20)
    print(cardSpider.data, '\n')
    print(cardSpider.getPersonMsg())

