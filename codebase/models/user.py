"""
User Model
"""

from mogoengine import Document
from mogoengine.fields import StringField, EmailFiled, ListField

class User(Document):
    
    email = EmailFiled(required=True, unique=True)
    password = StringField(required=True)

    # 联系人
    contacts = ListField(EmailFiled())
