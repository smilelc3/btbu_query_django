
class oneItem:
    def __init__(self, courceDate:list):

        self.studentID = 0          # 学号
        self.name = ''              # 姓名
        self.courseCode = ''        # 课程编码
        self.semester = ''          # 开学时间
        self.courseName = ''        # 课程名称
        self.overall = 0            # 总成绩
        self.gradeSign = ''         # 成绩标示
        self.courseNature = ''      # 课程性质
        self.courseCategory = ''    # 课程类别
        self.classHour = 0          # 学时
        self.academicCredit = 0.0   # 学分
        self.examNature = ''        # 考试性质
        self.makeupRetakeSem = ''   # 补重学期

        self.studentID, self.name, \
        self.courseCode, self.semester, self.courseName, \
        self.overall, self.gradeSign, self.courseNature, \
        self.courseCategory, self.classHour, \
        self.academicCredit, self.examNature, self.makeupRetakeSem =  courceDate

        self.DateDict = {"学号":self.studentID, "姓名": self.name,
                         "课程编号": self.courseCode, "开学时间": self.semester, "课程名称": self.courseName,
                         "总成绩":self.overall, "成绩标示": self.gradeSign, "课程性质": self.courseNature,
                         "课程类别": self.courseCategory, "学时": self.classHour, "学分": self.academicCredit,
                         "考试性质": self.examNature, "补重学期": self.makeupRetakeSem,}