#coding=utf-8
"""
Private Message Model
"""

from mongoengine import Document
from mongoengine.fields import EmailField, IntField, DateTimeField

class Message(Document):
    
    from_email = EmailFiled(required=True)
    to_email = EmailFiled(required=True)
    content = StringField(required=True, default=u'')
    ctime = DateTimeFiled(default=datetime.now)

    # 消息未读
    M_UNREAD = 0
    # 消息已读
    M_READ = 1
    # 消息删除
    M_DELETE = 2
    status = IntField(
        required=True, default=M_UNREAD,
        choices=(M_UNREAD, M_READ, M_DELETE)
    )

    @classmethod
    def create(cls, content, from_email, to_email):
        """
        Create message
        """
        msg = cls(from_email=from_email, to_email=to_email, content=content)
        msg.save()
        return str(msg.id)

    @classmethod
    def delete(cls, id):
        """
        Delete message
        """
        cls.ojbects(id=id).update(set__status=self.M_DELETE)

    @classmethod
    def fetch_history(cls, from_email, to_email, page=1, page_size=20):
        page -= 1
        emails = (from_email, to_email)
        records = Message.objects(
            to_email__in=emails,
            from_email__in=emails,
        ).order_by('-ctime').skip(page*pagesize).limit(pagesize)

        result = []
        for record in records:
            result.append({
                'content': record.content,
                'ctime': record.ctime.isoformat()
                'from_email': from_email,
                'to_email': to_email
            })

        return result
