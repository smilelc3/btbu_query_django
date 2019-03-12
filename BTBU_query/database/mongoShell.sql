use BTBUQuery
db.createUser({
    user:"Admin_Edu",
    pwd:"92a953a04b3a2ef1eb475f26f317cf1b2b8aad0ed3e05c1284c74f2060e051d7",
    customData:{Brief:"BTBUQuery管理员"},
    roles: [ { role: "dbAdmin", db: "BTBUQuery" }],
    })
db.createCollection(name = "Educational_management")
db.createCollection(name = "Verify_code")
db.createCollection(name = "Grade_sheet")
db.createCollection(name = "Class_Table")
db.createCollection(name = "Class_Table_date")
db.createCollection(name = "Card_Consumption")
db.createCollection(name = "Card_Message")
/*
远程连接配置

1. sudo nano /etc/mongodb.conf

 bind_ip = 0.0.0.0
 port = 27017

2. service mongodb restart

*/