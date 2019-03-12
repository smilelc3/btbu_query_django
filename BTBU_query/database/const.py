
MONGODB_CONFIG = {
    'host': '127.0.0.1',    #阿里云 120.25.192.203
    'port': 27017,
    'username': 'Admin_Edu',
    'password': '92a953a04b3a2ef1eb475f26f317cf1b2b8aad0ed3e05c1284c74f2060e051d7',
    'db_name': 'BTBUQuery',
}

mongoCollections =[
    "Educational_management",           # 主表，存储教务管理查询的个人信息
    "Verify_code",                      # 验证码表，存储图片数据
    "Grade_sheet",                      # 成绩表
    "Class_Table",                      # 课程表
    "Class_Table_date",                 # 记录个人课程学期
    'Card_Consumption',                 # 记录一卡通消费数据
    'Card_Message',                     # 记录一卡通个人数据
]

mongoUrl = f'mongodb://{MONGODB_CONFIG["username"]}:{MONGODB_CONFIG["password"]}@{MONGODB_CONFIG["host"]}:{MONGODB_CONFIG["port"]}/{MONGODB_CONFIG["db_name"]}'
