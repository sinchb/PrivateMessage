#coding=utf-8
"""
User Model
"""

from datetime import datetime

from mongoengine import Document
from mongoengine.fields import \
        StringField, EmailField, ListField, DateTimeField

class User(Document):

    ctime = DateTimeField(default=datetime.now)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    # 联系人
    contacts = ListField(EmailField())

    @classmethod
    def create(cls, email, password):
        return User(email=email, password=password).save()

    @classmethod
    def exists(cls, email):
        return bool(User.objects(email=email))

    @classmethod
    def get(cls, email, password):
        return User.objects(email=email, password=password).first()
