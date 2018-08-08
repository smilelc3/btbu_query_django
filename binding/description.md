## 绑定视图数据说明

* index 查询某账户是否绑定

> url : /binding 

> method: get

```python

requestData = {
    'openid': str,
}

responseData = {
    'isBinding': bool,
}
```

* dobind 绑定视图

> url : /binding/do

> method: post


```python

requestData = {
    'openid': str,
    'studentID':str,
    'password':str,
}

responseData = {
    'isBinding': bool,
    'status':'passwordError' 'overtime' or ''
}
```

* withdrawBind 撤销绑定

> url: /binding/withdraw

> method: post

```python

requestData = {
    'openid': str,
}

responseData = {
    'status':'notFind' or 'correct'
}
```