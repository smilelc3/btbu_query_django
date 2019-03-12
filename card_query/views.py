from BTBU_query.campus_network_query.card_spider import spider as card_spider
from django.http import HttpResponse, HttpRequest

from BTBU_query.database.const import *
from BTBU_query.database.mongoConn import MongoConn

from datetime import datetime
import json
# Create your views here.

# 绑定账户
def get(request: HttpRequest)-> HttpResponse:
    if request.method == "POST":
        # 保存请求数据
        studentID = request.POST['studentID']
        password = request.POST['password']

        cardSpider = card_spider(studentID = studentID, password = password)
        resp = {
            'status': 'right',
            'data': [],
        }
        if cardSpider.isLogin == False:
            resp['status'] = 'passwordError'
        else:
            cardSpider.recentDaysMsg(days=30, limit=20)     # 默认返回近30天数据

            costList = []

            if cardSpider.data != []:
                finalRemain = cardSpider.data[0]['剩余金额(元)']     # 获取最近的余额
                cardSpider.data.reverse()  # 时间逆序
                for index, item in enumerate(cardSpider.data):

                    itemTime = datetime.strptime(item['交易时间'], "%Y-%m-%d %H:%M:%S")
                    time = {
                        'year': itemTime.year,
                        'month': itemTime.month,
                        'day': itemTime.day,
                        'hour': itemTime.hour,
                        'min': "%02d" % itemTime.minute     # 强制两位数字
                    }
                    remain =  float(item['剩余金额(元)'])
                    if index != 0:

                        # 排除简单0.0查询
                        if float(item['交易金额(元)']) == 0:
                            continue
                        location = item['交易地点']
                        gap = round(float(item['剩余金额(元)']) - float(cardSpider.data[index - 1]['剩余金额(元)']), 2)
                        cost = str(gap) if gap < 0 else '+' + str(gap)
                    else:
                        cost = ''
                        location = ''
                    costList.append(
                        {
                            'time': time,
                            'location': location,
                            'cost': cost,
                            'remain': remain
                        }
                    )

                costList.reverse()
                resp['data'] ={
                    'costList': costList,
                    'remain': finalRemain,
                }

            # update personal data
            personalMsg = cardSpider.getPersonMsg()
            personMsgCol = MongoConn().db.get_collection(mongoCollections[6])
            personMsgCol.update({"studentID":personalMsg['studentID']},{"$set": personalMsg}, upsert=True)


        return HttpResponse(json.dumps(resp), content_type="application/json")

