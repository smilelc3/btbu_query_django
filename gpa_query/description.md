# 绩点查询视图说明

## 绩点数据查询
> method: get

> url: /gpa/
```python
requestData = {
    "openID" :str,
}


responseData = {
    'gpa': dict,       # 每一学期对应当学期的绩点
    'credit':dict,     # 每一学期对应当学期的学分
    'GPA':float        # 总绩点，保留两位小数
}
```