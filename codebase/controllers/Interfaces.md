# API 接口定义

选用WebSocket作为实时通信的接口, 使用event + json作为API协议
规定
* \>>> 为client向服务发送事件
* \<<< 为server向client发送事件


## 注册
### >>> Request
event ``LOGON``
```python
{
    'user': 'sinchb128@gmail.com',
    'password': '123456'
}
```

## 登录
```python
{
    'user': 'sinchb128@gmail.com':
    'password': '123456'
}
```

### 
event ``LOGIN``
```python
{
}

```

## 获取所有联系人以及未读消息数量
### >>> Request
event: ``LIST_CONTACTS_UNREAD``
```python
{}
```
### <<< Response
```python
{
  'contacts': {
    'sinchb128@gmail.com': 0,
    'Cherish.Chen@gmail.com': 2
  }
}
```

## 未读消息数更新
### <<< Request
event: ``NOTIFY_UPDATE_UNREAD``
```python
{
  'unread_msg_count': {
    'sinchb128@gmail.com': 9,
    'eva@gmail.com': 8
  }
}
```

## 添加联系人
### >>> Request
event: ``CREATE_CONTACT``
```python
{
  'user': 'Eva@gmail.com'
}
```
### <<< Response
event: ``OK``
```python
{}
```
event: <<< ``FAIL``
```python
{
  'msg': 'Already exists'
}
```

## 删除联系人
### >>> Request
event: DELETE_CONTACT
```python
{
  'user': 'Eva@gmail.com'
}
```
### <<< Response
event: ``OK``

## 联系人列表更新
### <<< Request
event: NOTIFY_UPDATE_CONTACT
```python
{
  'contacts': {
    'sinchb128@gmail.com': 9,
    'eva@gmail.com': 8
  }
}
```

## 进入聊天
### >>> Request
event: CHAT_WITH
```python
{
  'user': 'Eva@gmail.com'
}
```
## <<< Response
event: ``OK``

## 查看聊天记录
### >>> Request
event: CHAT_HISTORY
```python
{
   'user': 'Eva@gmail.com'
   'page': 1
   'pagesize': 20
}
```
### <<< Response
event: ``OK``
```python
{
  'chat_history': [
    {
      'content': 'Hello, Baby!',
      'time': '2017-03-22T16:32:26.272345'
      'user': 'Eva@gmail.com'
      'id': '58d2383aeba27c5fb1e7600d'
    },
    {
      'content': u'明天去看电影么',
      'time': '2017-03-22T16:33:48.272345'
      'user': 'sinchb128@gmail.com'
      'id': '68d2383aeba27c5fb1e7600d'
    },
    {
      'content': u'好啊，看什么呢？',
      'time': '2017-03-22T16:34:26.272345'
      'user': 'Eva@gmail.com'
      'id': '58d2384deba27c5fb1e7600e'
    },
  ]
  'current_page': 3
}
```

## 发送私信
### >>> Request
event: ``CHAT_SEND_MSG``
```python
{
  'content': '《金刚狼吧》'
  'time': '2017-03-22T16:36:45.272345'
  'user': 'sinchb@gmail.com'
}
```
### <<< Response
event: ``OK``
```python
{
  'id': '58d2384deba27c5fb1e7600e'
}
```

## 接收私信
### <<< Request
event: ``NOTIFY_NEW_MSG``
```python
{
    'msg': {
        'content': 'How are you?',
        'time': '2017-03-22T16:34:26.272345',
        'from_email': 'sinchb128@gmail.com',
    }
}
```

## 收到私信
### >>> Request
event: ``CHAT_RECEIVE_MSG``
```python
{
    'content':
}
```

## 删除记录
### >>> Request
event: ``CHAT_DELETE``
```python
{
  'id': '58d2384deba27c5fb1e7600e'
}
```
### <<< Response
event: ``OK``
