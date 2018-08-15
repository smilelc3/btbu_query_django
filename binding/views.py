from django.shortcuts import render
from BTBU_query.数据库.mongoConn import MongoConn
from django.http import HttpResponse, HttpRequest
from BTBU_query.内网查询.jwgl_spider import auto_login
from BTBU_query.数据库.const import *

import json
# Create your views here.



def index(request: HttpRequest)-> HttpResponse:


    openid = request.GET['openid']
    # print(openid)
    isBinding = MongoConn().db.get_collection(mongoCollections[0]).find_one({'openID': openid})
    if isBinding != None:
        resp = {'isBinding': True, 'status': isBinding['studentID']}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    else:
        resp = {'isBinding': False,'status':''}
        return HttpResponse(json.dumps(resp), content_type="application/json")


# 绑定账户
def doBinding(request: HttpRequest)-> HttpResponse:
    if request.method == "POST":
        # 保存请求数据
        openid = request.POST['openid']
        studentID = request.POST['studentID']
        password = request.POST['password']


        spiderTest = auto_login(studentID, password, openid)
        spiderTest.getCookie()
        spiderTest.logon()

        resp = {'isBinding': False, 'status': 'overtime'}

        if spiderTest.loginCorrect == True: # 账户正确
            resp = {'isBinding': True, 'status': studentID}

        elif spiderTest.loginCorrect == False: # 密码错误
            resp = {'isBinding': False, 'status': 'passwordError'}

        elif spiderTest.overtime == True: # 超时
            resp = {'isBinding': False, 'status': 'overtime'}

        return HttpResponse(json.dumps(resp), content_type="application/json")


# 撤销绑定
def withdrawBinding(request: HttpRequest)-> HttpResponse:
    if request.method == "POST":
        # 保存请求数据
        openid = request.POST['openid']

        if MongoConn().db.get_collection(mongoCollections[0]).delete_one({"openID":openid}).deleted_count < 1:
            resp = {'status':'notFind'}
        else:
            resp = {'status':'correct'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
