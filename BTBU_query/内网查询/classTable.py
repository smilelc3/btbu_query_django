
'''
classTable类，实现对课程表申明和接口返回
'''
import re
import json
import pymongo
from BTBU_query.开发装饰器.terminal import timmer

# 以一学期为单位更新
class classTable:
    def __init__(self,dataList:list, semester:str, studentID:str):
        '''
        dataList 是一个length = 7 的list，代表七天的数据,是三重list嵌套，课表中 每一行 为末级数据
        weekList 是指可用周数，元素格式为："第*周"
        semester 学期
        '''
        self.rawData = dataList
        #self.weekList = [re.findall(r'\d+', weekStr)[0] for weekStr in weekList]
        self.semester = semester
        self.datalist = []
        self.studentID = studentID
        self._dellAll()


    def _dellSpecificTime(self, day:int, classNum:int, rawMessage:list):
        # 考虑无课 和 网络课
        if rawMessage == [] or '视频课' in rawMessage[0]:
            return

        # 有课情况
        className = rawMessage[0]
        if className in rawMessage[1:]: #存在单双周情况
            classOne = _oneClass(rawMessage[0: rawMessage.index(className, 1)], day)
            classTwo = _oneClass(rawMessage[rawMessage.index(className, 1):], day)
            self.datalist.append(classOne)
            self.datalist.append(classTwo)
        else:
            classOne = _oneClass(rawMessage, day)
            self.datalist.append(classOne)

    @timmer
    def _dellAll(self):
        for classIndex, classAllTwo in enumerate(self.rawData):
            for dayIndex, item in enumerate(classAllTwo):
                self._dellSpecificTime(day=dayIndex + 1, classNum= classIndex*2 + 1, rawMessage=item)
                self._dellSpecificTime(day=dayIndex + 1, classNum= classIndex*2 + 2, rawMessage=item)


    # 上传数据
    def uploadtoMongo(self, mongoCollection:pymongo.mongo_client.database.Collection):
        for classItem in self.datalist:
            data = {
                "studentID": self.studentID,
                "semester": self.semester,  # 记录学期
                "name": classItem.name,
                "sameClass": classItem.sameClass,
                "teacher": classItem.teacher,
                "day": classItem.day,
                "startNum": classItem.startNum,
                "endNum": classItem.endNum,
                "startWeek": classItem.startWeek,
                "endWeek": classItem.endWeek,
                "isOdd": classItem.isOdd,
                "isEven": classItem.isEven,
                "location": classItem.location,
                "extraMessage": classItem.extraMessage
            }
            #print(data)
            #print(classItem.startNum, classItem.endNum)
            subkey = ['studentID', 'day', 'name', 'teacher', 'isOdd', 'isEven','startNum']
            mongoCollection.update_one({key:data[key] for key in subkey}, {'$set':data}, upsert=True)


# ——oneClass做单次课堂的类
class _oneClass:
    def __init__(self, dataList:list, day):
        self.rawData = dataList
        self.name = self.rawData[0]           # 课程名
        self.sameClass = self.rawData[1].split(',')  # 同课班级
        self.teacher = self.rawData[2]

        self.day = day            # 星期

        self.startNum = 0        # 开始节数
        self.endNum = 0          # 结束节数

        self.startWeek = 0       # 开始周次
        self.endWeek = 0         #结束周次

        try:
        # 标准格式
            self.startWeek, self.endWeek, self.startNum, self.endNum = \
                [int(item) for item in re.search("([0-9]+)-([0-9]+)[\u4e00-\u9fa5]{1,2}?\[([0-9]+)-([0-9]+)", self.rawData[3]).groups()]

        except AttributeError:
            try:
                self.startWeek, self.endWeek, self.startNum, self.endNum = \
                    [int(item) for item in
                     re.search("([0-9]+)-([0-9]+)[\u4e00-\u9fa5]{1,2}?\[([0-9]{2})[0-9]{2}([0-9]{2})", self.rawData[3]).groups()]
            except Exception as e:
                print(e)

        self.isOdd = True        # 单周判定
        self.isEven = True       # 双周判定

        if '单' in self.rawData[3]:
            self.isEven = False
        if '双' in self.rawData[3]:
            self.isOdd = False
        # isOdd 和 isEven同是为False，表示不分单双周周

        self.location = self.rawData[4]

        self.extraMessage = ''  # 记录额外信息
        if self.rawData.__len__() > 4:
            self.extraMessage = self.rawData[5:]

