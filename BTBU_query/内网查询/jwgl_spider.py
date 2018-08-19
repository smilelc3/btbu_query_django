# 主要实现教务管理页面的数据查询

from bs4 import BeautifulSoup
from BTBU_query.数据库.MongoSave import MongoSaveLogin
import requests
import time, random
from BTBU_query.内网查询.verify_code_spot import verifyCode
from BTBU_query.开发装饰器.terminal import timmer
from BTBU_query.内网查询.gradeOneItem import gradeOneItem
from BTBU_query.内网查询.classTable import classTable as Table
from BTBU_query.数据库.const import *

url = 'http://jwgl.btbu.edu.cn/'


class auto_login:
    '''
    教务系统的自动登录类，不涉及查询
    '''

    def __init__(self, studentID, password, openID):
        self.studentId = studentID
        self.password = password
        self.tryTimes = 0
        self.loginCorrect = False
        self.overtime = False
        self.mongoSave = MongoSaveLogin()
        self.openID = openID

    statusMean = {
        400: "请求失败或未授权",
        403: "禁止访问",
        404: "无法找到文件",
        405: '资源禁止',
        500: '请求服务器错误',
        502: '网关错误',
    }

    @timmer
    def getCookie(self, url: str = url) -> requests.get:
        '''
        获取预先的cookies,同时做连通性测试
        :param url:
        :return: 若连接正常，返回get类，否则返回'Error'
        '''
        response = requests.get(url=url)
        if response.status_code != 200:
            print(f'无法访问：{url}\n'
                  f'状态码\t{response.status_code}')

            try:
                print(f'HTTP状态解释：{self.statusMean[requests]}')
            except KeyError as e:
                print('HTTP状态解释：未知')

            return 'Error'
        else:
            print(f'正常访问：{url}')
            response.encoding = 'urf-8'
            PreCookie = str(response.headers['Set-Cookie'])  # 提取PreCookie
            PreCookie = PreCookie.split(';')[0]
            self.cookies = {PreCookie.split('=')[0]: PreCookie.split('=')[1]}  # 字典型cookies
            return response

    @timmer
    def getVerificationCode(self) -> verifyCode:
        """
        需要借助random.random()函数和伪造url，来实现获取验证码操作
        :return:
        """

        # 伪造验证码申请
        verifyCodeFloat = random.random()
        verifCodeurl = url + '/verifycode.servlet?' + str(verifyCodeFloat)

        # 伪造headers
        headers = {
            'Host': 'jwgl.btbu.edu.cn',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        verifCodesponse = requests.get(url=verifCodeurl, headers=headers, cookies=self.cookies)

        CodeImg = verifyCode(verifCodesponse.content, size=[62, 22])

        return CodeImg  # 返回Img对象

    @timmer
    def logon(self):
        """
        该方法实现模拟登陆
        :return:
        """
        randomCodeImg = self.getVerificationCode()
        randomCode = randomCodeImg.ImageToText()

        self.logonUrl = url + '/Logon.do'
        FormData = {
            'method': 'logon',
            'USERNAME': self.studentId,
            'PASSWORD': self.password,
            'RANDOMCODE': randomCode
        }

        logonResopnse = requests.post(url=self.logonUrl,
                                      cookies=self.cookies,
                                      data=FormData)
        self.tryTimes += 1  # 登录次数纪录

        if logonResopnse.text.find("该帐号不存在或密码错误,请联系管理员!") != -1:
            print("账号不存在或密码错误")
            self.loginCorrect = False
            return

        elif logonResopnse.text.find("验证码错误!!") != -1:
            print(f"验证码错误，当前尝试次数:{self.tryTimes}次")
            if self.tryTimes >= 20:
                print("验证失败次数过多，请稍后重试")
                self.overtime = True
                return
            self.logon()


        else:
            # 保存图片和更新验证码库
            randomCodeImg.saveImg()
            VerifyCodeData = {
                'ImgPath': randomCodeImg.ImgPath,
                'ImgName': randomCodeImg.ImgName,
                'Decode': randomCode,
                'CteatedTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            self.mongoSave.updateOneVerify(VerifyCodeData, collections='Verify_code')

            # 更新person数据库
            personData = {
                "studentID": self.studentId,
                "password": self.password,
                "acceptAgreement": True,
                "openID": self.openID
            }
            self.mongoSave.updateOnePerson(personData, collection='Educational_management')

            # 进行二次确认
            self._secondLogon()
            # print("成功登陆")
            self.loginCorrect = True

    @timmer
    def _secondLogon(self):
        """
        # 二次确认登录，该为必要操作
        SSO(Single Sign On，单点登录)
        """
        params = {
            'method': 'logonBySSO',
        }
        requests.get(url=self.logonUrl, params=params, cookies=self.cookies)


# 成绩查询类
class auto_query_grade:
    """
    需要借助已登录的cookie初始化，与密码用户隔离
    """

    def __init__(self, cookies: dict):
        self.cookies = cookies
        self.time = int(time.time())
        self.DateUrl = url + '/jiaowu/cjgl/xszq/query_xscj.jsp'
        self.Datelist = []
        self.mongoSave = MongoSaveLogin()

        # 以下是一次高级获取
        self.prePage = 1  # 当前页
        self.totalPage = 1
        self.formData = dict(
            check_object_id='',
            check_object_name='',

            # 下面是筛选数据
            Field1='a.xh',  # 筛选条件一：学号
            HH1='like',  # 像
            SValue1='',  # 空为无条件
            AndOr1='and',  # 条件间关系
            Field2='a.xh',  # 条件二： 默认学号
            HH2='like',  # 像
            SValue2='',  # 空为无条件

            # 未知意义
            where1='null',
            where2='null',
            OrderBy='',

            keyCode='',
            isOutJoin='false',
            PageNum=1,  # 当前页码
            oldSelectRow='',
            printHQL='',
            sqlString='',
            sqlArgs='',
            isSql='true',
            beanName='',
            printPageSize=10,  # 显示行数 默认10
            key='',
            field='',
            totalPages=1,  # 总共页码
            ZdSzCode='',
            ZdSzCodeValue='',
            ZdSzValueTemp='',
            ZDSXkeydm='',
            PlAction='',
            tableFields='',
            otherFields='null',

        )

    # 获取时间表
    def getDateList(self) -> list:
        params = {
            'tktime': str(self.time)
        }
        response = requests.get(self.DateUrl, cookies=self.cookies, params=params)
        response.encoding = 'utf-8'

        # 获取开课时间list
        listSoup = BeautifulSoup(response.text, 'lxml').select('#kksj > option')
        self.Datelist = [Date.text for Date in listSoup][1:]  # 去除  '---请选择---' 无关项
        self.Datelist.sort(reverse=True)  # 降序排列
        return self.Datelist

    # http://jwgl.btbu.edu.cn/xszqcjglAction.do

    def getOneSemester(self, Date: str):
        """
        Date格式为:    startYear-endYear-1/2
        :param Date:
        :return:
        """
        OneSemesterUrl = url + 'xszqcjglAction.do'
        params = {
            'method': 'queryxscj',
        }
        formData = {
            'kksj': Date,  # 开课时间
            'kcxz': '',  # 课程性质
            'kcmc': '',  # 课程名称
            'xsfs': '',  # 显示方式
            'ok': '',
        }
        response = requests.post(url=OneSemesterUrl, params=params,
                                 data=formData, cookies=self.cookies)  # 必须使用post协议
        # print(Date)

        response.encoding = 'utf-8'

        OneSemesterSoup = BeautifulSoup(response.text, 'lxml')
        mainContent = OneSemesterSoup.select_one('#mxh')  # 获取主表

        # 考虑表为空的情况
        for items in mainContent.children:
            itemList = [item.text.strip() for item in items][1:]  # 切片与空转换，去序号
            if itemList.__len__() > 0 and itemList.__len__() < 13:
                print('该数据出错')
                # 错误数据deal
                continue

            # 数据无误下，保存数据库
            if itemList == []:
                print("该学年无数据")
                continue
            SpecialItem = gradeOneItem(itemList)
            self.mongoSave.updateOneItem(SpecialItem)

    @timmer
    def dellAllSemester(self, studentID: str):
        # 测试: 学号前两位为入学年份
        if studentID[0:2].isdigit():
            startYear = '20' + studentID[0:2]
            startIndex = 0
            for index, Date in enumerate(self.Datelist):
                if startYear in Date:
                    startIndex = index
                    if startYear in self.Datelist[index + 1]:
                        startIndex += 1
                    break
            effectiveList = self.Datelist[0:startIndex + 1]
            effectiveList.reverse()
            for Date in effectiveList:
                self.getOneSemester(Date)

        # 非标准学号
        else:
            for Date in self.Datelist:
                self.getOneSemester(Date)

    @timmer
    def complete_in_one_step(self):
        # 借助下一页的操作，查询所有 优点：快速 缺点： 较复杂
        self._one_step_pre_work()
        import json
        print(json.dumps(self.formData))

    def _one_step_pre_work(self):
        # 提前处理解析出 keyCode printHQL sqlString key field
        #
        preWorkUrl = url + 'xszqcjglAction.do'
        params = {
            'method': 'queryxscj',
        }
        formData = {
            'kksj': '',  # 开课时间
            'kcxz': '',  # 课程性质
            'kcmc': '',  # 课程名称
            'xsfs': '',  # 显示方式
            'ok': '',
        }
        response = requests.post(url=preWorkUrl, params=params,
                                 data=formData, cookies=self.cookies)  # 必须使用post协议
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'lxml')

        updateList = ['keyCode', 'printHQL', 'otherFields', 'isSql', 'printPageSize',
                      'key', 'field', 'totalPages', 'tableFields']

        for item in updateList:
            self.formData[item] = soup.select_one(f'#alldiv > form > input[name="{item}"]')['value']


# 课表查询类
class auto_query_classTable:
    def __init__(self, cookies: dict):
        self.cookies = cookies
        self.time = int(time.time())
        self.DateUrl = url + '/tkglAction.do'
        self.Datelist = []
        self.mongoSave = MongoSaveLogin()

    # 获取可用学期数据
    def getDateList(self) -> list:
        params = {
            'tktime': str(self.time),
            'method': 'kbxxXs',
        }
        response = requests.get(self.DateUrl, cookies=self.cookies, params=params)
        response.encoding = 'utf-8'

        # 获取课表学期list
        listSoup = BeautifulSoup(response.text, 'lxml').select('#xnxqh > option')
        self.Datelist = [Date.text for Date in listSoup][1:]  # 去除  '---请选择---' 无关项
        self.Datelist.sort(reverse=True)  # 降序排列
        return self.Datelist

    # 获取某一学期具体数据
    def getOneSemester(self, date: str, studentID: str):
        """
        Date格式为:    startYear-endYear-1/2
        :param date:
        :return:
        """
        OneSemesterUrl = url + '/tkglAction.do'
        params = {
            'method': 'goListKbByXs',
            'istsxx': 'no',
            'xnxqh': date,
            'zc': '',
            'xs0101id': studentID,
        }
        response = requests.get(url=OneSemesterUrl, params=params,
                                cookies=self.cookies)
        response.encoding = 'utf-8'

        dataList = []
        OneSemesterSoup = BeautifulSoup(response.text, 'lxml')
        mainContent = OneSemesterSoup.select_one('#kbtable')  # 获取主表
        for classNum in range(1, 6):  # 先1-5
            classList = []
            for day in range(1, 8):  # 1-7
                oneclass = mainContent.select_one(f'#{classNum}-{day}-2')
                oneclassList = oneclass.get_text(separator='%', strip=True).split('%')  # 分割、重组
                oneclassList = oneclassList if oneclassList != [""] else []
                classList.append(oneclassList)
            dataList.append(classList)

        # 晚上通选课未开始
        classNum = 6
        classList = []
        for day in range(1, 8):  # 1-7
            oneclass = mainContent.select_one(f'#{classNum}-{day}-2')
            if oneclass != None:
                oneclassList = oneclass.get_text(separator='%', strip=True).split('%')  # 分割、重组
                oneclassList = oneclassList if oneclassList != [""] else []
                classList.append(oneclassList)
        dataList.append(classList)

        # print(dataList)
        classTable = Table(dataList, semester=date, studentID=studentID)
        classTable.uploadtoMongo(MongoSaveLogin().db.get_collection(mongoCollections[3]))


if __name__ == '__main__':
    spiderTest = auto_login('1604010319', 'liuchang', '123456')
    result = spiderTest.getCookie()
    spiderTest.logon()

    # print(spiderTest.loginCorrect, spiderTest.overtime)
    queryTest = auto_query_grade(spiderTest.cookies)
    queryTest.getDateList()
    queryTest.complete_in_one_step()

    # classTableQueryTest = auto_query_classTable(spiderTest.cookies)
    # classTableQueryTest.getDateList()
    # classTableQueryTest.getOneSemester('2017-2018-2', '1604010319')
