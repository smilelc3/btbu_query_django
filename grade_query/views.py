from django.shortcuts import render

from django.http import HttpRequest, HttpResponse
from BTBU_query.database.const import *
from BTBU_query.database.mongoConn import MongoConn
from BTBU_query.campus_network_query.jwgl_spider import auto_login, auto_query_grade
import json
# Create your views here.

# Projection cannot have a mix of inclusion and exclusion.
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
    '课程名称':     True,
    #'课程性质':     False,
    #'课程类别':     False,
    }

def grade(request: HttpRequest)-> HttpResponse:
    openid = request.GET['openid']
    queryStudentID = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openid},
                                                                                 {'_id': False, 'studentID': True})
    if queryStudentID != None:
        studentID = queryStudentID['studentID']
        data = list(
            MongoConn().db.get_collection(mongoCollections[2]).find({'学号': studentID},
                                                                mongoFilter).sort("开学时间", -1)  # --降序
            )


        if data != []:
            resp = {"status": "correct", "data": data}
        # 考虑还未开始抓取
        else:
            password = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openid},
                                                                                 {'_id': False, 'password': True})['password']
            spiderTest = auto_login(studentID, password, openid)

            spiderTest.getCookie()
            spiderTest.logon()
            queryTest = auto_query_grade(spiderTest.cookies)
            queryTest.getDateList()
            queryTest.dellAllSemester(studentID)



            data = list(
                MongoConn().db.get_collection(mongoCollections[2]).find({'学号': studentID},
                                                                        mongoFilter).sort("开学时间", -1)  # --降序
            )


            resp = {"status": "correct", "data": data}

    # 考虑未绑定或绑定错误
    else:
        resp = {"status": "notBinding", "data": []}

    return HttpResponse(json.dumps(resp), content_type="application/json;charset=utf-8")