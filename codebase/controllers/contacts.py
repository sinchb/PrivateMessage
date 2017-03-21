"""
Contacts Model
"""

from mogoengine import Document
from mogoengine.fields import StringField

class User(Document):
    
    email = StringField(required=True, unique=True)
