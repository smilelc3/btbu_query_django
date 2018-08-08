from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from BTBU_query.数据库.const import *
from binding.models import MongoConn
from BTBU_query.内网查询.bs_spider import auto_login, auto_query_grade
import json

mongoFilter = {
    '_id':        False,
    #'课程编号':     False,
    # '姓名':        False,
    '学分':        True,
    #'学号':        False,
    #'学时':        False,
    '开学时间':     True,
    '总成绩':       True,
    #'成绩标示':     False,
    #'考试性质':     False,
    #'补重学期':     False,
    #'课程名称':     False,
    #'课程性质':     False,
    #'课程类别':     False,
    }

# Create your views here.
def gpa(request: HttpRequest)-> HttpResponse:
    openid = request.GET['openID']
    queryStudentID = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openid},
                                                                                 {'_id': False, 'studentID': True})
    if queryStudentID != None:
        studentID = queryStudentID['studentID']
        data = list(
            MongoConn().db.get_collection(mongoCollections[2]).find({'学号': studentID},
                                                                mongoFilter).sort("开学时间", 1)  # --升序
            )

        # 考虑还未开始抓取
        if data == []:
            password = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openid},
                                                                                 {'_id': False, 'password': True})['password']
            spiderTest = auto_login(studentID, password, openid)
            spiderTest.connTest()
            spiderTest.logon()
            queryTest = auto_query_grade(spiderTest.cookies)
            queryTest.getDateList()
            queryTest.dellAllSemester(studentID)



            data = list(
                MongoConn().db.get_collection(mongoCollections[2]).find({'学号': studentID},
                                                                        mongoFilter).sort("开学时间", 1)  # --升序
            )

        # 对数据进行处理(绩点计算)
        currentSemester = data[0]['开学时间']

        resp = {'gpa': {}, 'credit':{}, 'GPA':0}
        creditList = []  # 记录一学期学分
        gradeList = []  # 记录一学期成绩
        for index,item in enumerate(data):
            if item['开学时间'] != currentSemester or index == len(data) - 1:
                if index == len(data) -1:
                    creditList.append(float(item['学分']))
                    gradeList.append(float(item['总成绩']))

                resp['credit'][currentSemester] = sum(creditList)
                resp['gpa'][currentSemester] = sum([creditList[index] * gradeList[index] for index in range(len(creditList))]) / resp['credit'][currentSemester]
                currentSemester =item['开学时间']
                creditList = []
                gradeList = []

            creditList.append(float(item['学分']))
            gradeList.append(float(item['总成绩']))

        resp['GPA'] = sum([resp['gpa'][key] * resp['credit'][key] for key in [key for key,value in resp['credit'].items()]]) / \
            sum(resp['credit'].values())

        # 四舍五入
        resp['GPA'] = round((resp['GPA'] -50) / 10, 2)
        for key,value in resp['gpa'].items():
            resp['gpa'][key] = round((value -50) / 10, 2)
        return HttpResponse(json.dumps(resp), content_type="application/json;charset=utf-8")