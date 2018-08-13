from django.db import models
import datetime
# Create your models here.
class Date:
    '''
    自动判断应显示学期的类
    '''
    thisYear = datetime.datetime.now().year
    springStartDate = datetime.date(thisYear, 3, 1)       # 3月1日春季开学
    springEndDate = datetime.date(thisYear, 7, 16)  # 7月16日春季结束

    autumnStartDate = datetime.date(thisYear, 9, 1)  # 9月1日秋季开学
    autumnEndDate = datetime.date(thisYear, 1, 21)  # 上个学期在今年的1月21日秋季结束

    today = datetime.date.today()

    semesterList = [str(thisYear - 1), str(thisYear), '1']
    week = 1

    def getSemester(self):
        if self.today <= self.autumnEndDate:
            self.semesterList = [str(self.thisYear - 1), str(self.thisYear), '1']

        elif self.today > self.autumnEndDate and self.today < self.springStartDate:
            self.semesterList = [str(self.thisYear - 1), str(self.thisYear), '2']

        if self.today >= self.springStartDate and self.today <= self.springEndDate:
            self.semesterList = [str(self.thisYear - 1), str(self.thisYear), '2']

        if self.today > self.springEndDate and self.today < self.autumnStartDate:
            self.semesterList = [str(self.thisYear), str(self.thisYear + 1), '1']

        if self.today >= self.autumnStartDate:
            self.semesterList = [str(self.thisYear), str(self.thisYear + 1), '1']
        return self._convertSemester()

    def _convertSemester(self):
        return "-".join(self.semesterList)


    def getWeek(self):
        if self.today <= self.autumnEndDate:
            self.week = (self.today - datetime.date(self.thisYear - 1, 9, 1)).days //7 + 1

        elif self.today > self.autumnEndDate and self.today < self.springStartDate:
            self.week = 1

        if self.today >= self.springStartDate and self.today <= self.springEndDate:
            self.week = (self.today - self.springStartDate).days // 7 + 1

        if self.today > self.springEndDate and self.today < self.autumnStartDate:
            self.week = 1

        if self.today >= self.autumnStartDate:
            self.week = (self.today - self.autumnStartDate).days // 7 + 1

        return self.week