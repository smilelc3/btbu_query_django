from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from BTBU_query.数据库.const import *
from BTBU_query.数据库.mongoConn import MongoConn
from BTBU_query.内网查询.jwgl_spider import auto_login, auto_query_classTable
from classTable_query.models import Date
import json

# Create your views here.

def available_data(request: HttpRequest)-> HttpResponse:
    openID = request.GET['openid']
    queryStudent = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openID},)

    resp = []
    if queryStudent == None:
        resp = []
    else:

        studentID = queryStudent['studentID']
        password = queryStudent['password']
        queryDate = MongoConn().db.get_collection(mongoCollections[4]).find_one({'studentID': studentID}, {'_id':False})

        if queryDate != None:

            for key in queryDate:
                if key  != 'studentID':
                    resp.append(key)
            resp.sort(reverse = True) # 降序排列

        # 第一次访问
        else:
            spiderTest = auto_login(studentID, password, openID)
            spiderTest.getCookie()
            spiderTest.logon()
            classTableQueryTest = auto_query_classTable(spiderTest.cookies)
            DateList = classTableQueryTest.getDateList()

            if studentID[0:2].isdigit():
                startYear = '20' + studentID[0:2]
                startIndex = 0
                for index, Date in enumerate(DateList):
                    if startYear in Date:
                        startIndex = index
                        if startYear in DateList[index + 1]:
                            startIndex += 1
                        break
                resp = DateList[0:startIndex + 1]
            else:
                resp = DateList

            mongodata = {"studentID": studentID}

            # 设置原始dateList
            for Date in resp:
                mongodata[Date] = False

            MongoConn().db.get_collection(mongoCollections[4]).update_one({"studentID":studentID}, {"$set":mongodata}, upsert=True)
    return HttpResponse(json.dumps(resp), content_type="application/json;charset=utf-8")

def get(request: HttpRequest)-> HttpResponse:

    openID = request.GET['openid']
    semester = request.GET['semester']
    week = int(request.GET['week'])
    queryStudent = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openID},)
    resp = []
    if queryStudent == None:
        resp = []
    else:

        studentID = queryStudent['studentID']
        quertDate = MongoConn().db.get_collection(mongoCollections[4]).find_one({'studentID': studentID})
        password = queryStudent['password']
        # 第一次访问该学期
        if quertDate[semester] == False:
            spiderTest = auto_login(studentID, password, openID)
            spiderTest.getCookie()
            spiderTest.logon()
            classTableQueryTest = auto_query_classTable(spiderTest.cookies)
            classTableQueryTest.getDateList()
            classTableQueryTest.getOneSemester(semester, studentID)
            #更新学期
            MongoConn().db.get_collection(mongoCollections[4]).update_one({"studentID": studentID}, {"$set": {semester: True}},
                                                                          upsert=True)

        collection = MongoConn().db.get_collection(mongoCollections[3])
        filter = {
            'semester': semester,
            'studentID': studentID,
            'startWeek':{'$lte':week},
            'endWeek':{"$gte":week},
        }
        if week % 2 == 1:
            filter['isOdd'] = True
        else:
            filter['isEven'] = True
        classTable = list(collection.find(filter, {'_id': False}))
        for classItem in classTable:
            respItem = {}
            respItem['day'] = classItem['day']
            respItem['startNum'] = classItem['startNum']
            respItem['continued'] = classItem['endNum'] - classItem['startNum'] + 1
            respItem['extraMessage'] = {
                'sameClass': classItem['sameClass'],
                'extra': ' '.join(classItem['extraMessage']),
            }
            message = {
                'name': classItem['name'],
                'location': classItem['location'],
                'teacher': classItem['teacher'],
            }
            respItem['message'] = message
            resp.append(respItem)



    return HttpResponse(json.dumps(resp), content_type="application/json;charset=utf-8")


def current(request: HttpRequest)-> HttpResponse:
    date = Date()
    resp = {
        'week': date.getWeek(),
        'semester': date.getSemester(),
    }
    return HttpResponse(json.dumps(resp), content_type="application/json;charset=utf-8")