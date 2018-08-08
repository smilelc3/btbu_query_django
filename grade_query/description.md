# 成绩查询视图数据说明

> method: get

> url: /grade

```python
requestData = {
    "openId" :str,
}


responseData = {
    "data": list,
    "status": "notBinding" or "correct"
}
```