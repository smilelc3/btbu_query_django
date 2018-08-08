# 课程表查询视图数据说明


## 查询可用数据

> method: get

> url: /curriculum/available_data
```python
requestData = {
    "openId" :str,
}

# 每个学期对应可用数据
responseData = {
    list,    
    # ……
}
```

## 查询具体周次数据

> method: get

> url: /curriculum/get
```python
requestData = {
    'openId' :str,
    'semester': str,
    'week':int,
}

# 每个学期对应可用数据
responseData = {
    
}
```
