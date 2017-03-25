#coding=utf-8
"""
User Model
"""

from datetime import datetime

from mongoengine import Document
from mongoengine.fields import \
        StringField, EmailField, ListField, DateTimeFiled

class User(Document):
    
    ctime = DateTimeField(default=datetime.now)
    email = EmailFiled(required=True, unique=True)
    password = StringField(required=True)

    # 联系人
    contacts = ListField(EmailFiled())
