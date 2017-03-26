#coding=utf-8
from time import sleep, time
from uuid import uuid4
import logging
import threading

from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.web import authenticated
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from ujson import dumps

from utils import enc, dec
from logger import logger
from models.user import User
from models.message import Message

class BaseWSHandler(WebSocketHandler):

    # Class level variable
    participants = set()

    CONN_LOCK = threading.Lock()


    R_UNREAD_KEY = 'unread:v1:%s:%s'

    def __init__(self, application, request, **kwargs):
        self.connid = 'NOPE'
        self.remote_ip = None
        self.user_email = None

        super(BaseWSHandler, self).__init__(
            application, request, **kwargs
        )

    def emit(self, name, args):
        try:
            event_msg = enc(name, args)
            self.write_message(message=event_msg, binary=True)
        except Exception:
            logger.exception('Unexcepted Error in emit')
            return False

    def open(self):
        self.remote_ip = self.request.remote_ip

        # generate connection uuid
        self.connid = str(uuid4())
        logger.info('Open %s @ %s' % (self.connid, self.remote_ip))

        with self.CONN_LOCK:
            self.participants.add(self.connid)

        super(BaseWSHandler, self).open()

    def get_current_user(self):
        return User.objects(email=self.user_email).first()

    @property
    def current_user(self):
        user = super(BaseWSHandler, self).current_user
        user.reload()
        return user

    def on_message(self, msg):
        """
        Received raw message.
        """
        try:
            name, args = dec(msg)
        except (ValueError, TypeError) as err:
            logger.warning('Receive invalid message %s, ' \
                           'nothing to do.' % str(err))
            self.close()
            return

        if self.ws_connection is None:
            logger.warning('Unable to dealwith %s %s: '
                           'Connection is closed' % (name, dumps(args)))

        try:
            self.on_event(name, args)
        except:
            logger.exception('Failed dealwith event: %s %s', name, args)

    def on_event(self, name, args, callback=None):
        """Process event, called by meth::on_message"""
        raise NotImplementedError()

    def on_close(self):

        logger.info('Closing %s @ %s' % (self.connid, self.remote_ip))
        super(BaseWSHandler, self).close()


class PrivateMessageHandler(BaseWSHandler):

    # email -> ws conncetions
    routes = {}
    ROUTES_LOCK = threading.Lock()

    def __init__(self, application, *args, **kwargs):

        self.handle_func = {

            'LOGON': self.handle_logon,
            'LOGIN': self.handle_login,

            'LIST_CONTACTS_UNREAD': self.handle_list_contacts,

            'CREATE_CONTACT': self.handle_create_contact,
            'DELETE_CONTACT': self.handle_delete_contact,

            'NOTIFY_UPDATE_CONTACT': self.notify_update_contact,
            'NOTIFY_UPDATE_UNREAD': self.notify_update_unread,

            'CHAT_WITH': self.handle_chat_with,
            'CHAT_HISTORY': self.handle_chat_history,
            'CHAT_DELETE': self.handle_chat_delete,
            'CHAT_SEND_MSG': self.handle_chat_send_msg,
        }
        super(PrivateMessageHandler, self).__init__(application, *args, **kwargs)

    def __unread_key(self, from_email='*', to_email='*'):
        return self.R_UNREAD_KEY % (from_email, to_email)

    @property
    def redis(self):
        return self.settings['redis']

    def on_event(self, name, args):
        logger.info('Received (%s) %s with %s', self.connid, name, dumps(args))

        try:
            handler = self.handle_func[name]
            handler(args)
        except:
            logger.exception('Error (%s) %s', self.connid, name)
            self.close()

    def handle_login(self, args):
        """
        登录验证
        """
        email = args['email']
        password = args['password']

        if not User.exists(email):
            self.reply_fail(msg='User Not Exists')
            return

        user = User.get(email, password)
        if not user:
            return self.reply_fail(msg='Wrong User or Password')

        self.user_email = user.email

        self.routes[self.user_email] = self
        return self.reply_ok()

    def get_peer_conn(self, email):
        """
        通过email获取实时的WebSocket连接
        """
        return self.routes.get(email)

    def on_close(self, *args, **kwargs):
        """
        清除路由信息
        """
        logger .warning('Connection %s is closed', self.connid)

        if not self.user_email:
            return

        with self.ROUTES_LOCK:
            self.routes.pop(self.user_email, None)

    def handle_init(self, args):
        """
        初始化工作，主要返回一个验证Token
        """
        pass

    def handle_logon(self, args):
        """
        注册一个用户
        """
        email = args['email'].lower()
        password = args['password']
        if User.exists(email):
            self.reply_fail(msg='User Exists Already')
            return
        else:
            User.create(email, password)
            self.reply_ok()
            return

    @authenticated
    def handle_list_contacts(self, args):
        """
        获取用户联系人列表和未读信息数量
        """
        contacts = {}

        keys = [
            self.__unread_key(to_email=self.user_email)
            for email in self.current_user.contacts
        ]

        unread_count = []
        if keys:
            unread_count = self.redis.mget(keys)
        for email, count in zip(self.current_user.contacts, unread_count):
            contacts[email] = 0 if count is None else count

        self.reply_ok({'contacts': contacts})

    @authenticated
    def handle_create_contact(self, args):
        """
        添加新的联系人
        """
        email = args['user'].strip()

        # Check if user exists
        if not User.exists(email):
            return self.reply_fail(msg='User Not Exists')

        # Atomic update. Add email to contacts only
        # if it's not in the contacts already
        self.current_user.update(add_to_set__contacts=email)
        return self.reply_ok()

    @authenticated
    def handle_delete_contact(self, args):
        """
        删除联系人
        """
        email = args['user'].strip()
        self.current_user.update(pull__contacts=email)
        return self.reply_ok()

    def notify_update_contact(self):
        """
        NOTIFICATION: 更新联系人信息
        """
        pass

    def notify_update_unread(self, to_email, count):
        """
        NOTIFICATION: 更新未读信息数量
        """
        peer_conn = self.get_peer_conn(email)
        if not peer_conn:
            return

        args = {self.user_email: count}
        peer_conn.emit('NOTIFY_UPDATE_UNREAD', args)

    @authenticated
    def handle_chat_with(self, args):
        """
        开始聊天
        """
        email = args['user']

        # 将未读数量清除
        self.redis.delete(self.__unread_key(self.user_email, to_email))

        self.notify_update_unread(email, 0)

    @authenticated
    def handle_chat_delete(self, args):
        """
        删除聊天记录
        """
        Message.delete(id=args['id'])
        self.reply_ok()

    @authenticated
    def handle_chat_send_msg(self, args):
        """
        发送私信
        """
        msg_id = Message.create(
            content=args['content'],
            from_email=self.current_user.email,
            to_email=args['to_email']
        )

        unread_key = self.__unread_key(self.user_email, args['to_email'])
        self.redis.inc(unread_key)

        return self.reply_ok({'id': msg_id})

    @authenticated
    def handle_chat_history(self, args):
        """
        获取历史消息
        """
        page = args['page']
        page_size = args['page_size']
        to_email = args['user']

    def reply_ok(self, args=None):
        if args is None:
            args = {}
        self.emit('OK', args)

    def reply_fail(self, msg):
        self.emit('FAIL', {'msg': msg})

if __name__ == '__main__':
    # Just for test
    import tornado
    application = tornado.web.Application(
        [(r'/ws', BaseWSHandler)],
    )
    port = 9999
    application.listen(port)
    logger.info('Start websocket server in %d', port)

    tornado.ioloop.IOLoop.instance().start()
