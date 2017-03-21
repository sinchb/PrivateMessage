
from time import sleep, time
from uuid import uuid4
import logging
import threading

from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from ujson import dumps

from utils import enc, dec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PrivateMessage')

class BaseWSHandler(WebSocketHandler):

    # Class level variable
    participants = set()

    CONN_LOCK = threading.Lock()


    R_UNREAD_KEY = 'unread:v1:%s'
    
    def __init__(self, application, request, **kwargs):
        self.connid = 'NOPE'
        self.remote_ip = None

        super(BaseWSHandler, self).__init__(
            application, request, **kwargs
        )

    def emit(self, name, args):
        try:
            event_msg = enc(name, args)
            self.write_message(message=event_msg, binary=True)
        except Exception as err:
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

        # TODO: timer, ping

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

    def __init__(self, *args, **kwargs):

        self.handle_func = {
            'INIT': self.init,

            'LIST_CONTACTS_UNREAD': self.handle_list_contacts,
            'UNREAD_UPDATE': self.handle_update_unread,
            'CREATE_CONTACT': self.handle_create_contact,
            'DELETE_CONTACT': self.handle_delete_contact,
            'UPDATE_CONTACT': self.handle_update_contact,

            'CHAT_WITH': self.handle_chat_with,
            'CHAT_HISTORY': self.handle_chat_history,
            'CHAT_DELETE': self.handle_chat_delete,
            'CHAT_SEND_MSG': self.handle_chat_send_msg,
        }

    def on_event(self, name, args):
        logger.info('Received (%s) %s with %s', self.connid, name, dumps(args))

        try:
            handler = self.handle_func[name]
            handler(name, args)
        except:
            logger.exception('Error (%s) %s', self.connid, name)
            self.close()

    def handle_auth(self, args):
        """
        登录验证
        """
        email = args['email']
        passwd = args['email']

    def handle_init(self, args):
        """
        初始化工作
        """
        pass


    def handle_list_contacts(self, args):
        """
        获取用户联系人列表和未读信息数量
        """
        contacts = {}
        pip = self.redis.pipeline()

        keys = (self.UNREAD_UPDATE % email for email in
                self.current_user.contacts)

        unread_count = self.redis.mget(keys)
        for email, count in zip(keys, unread_count):
            contacts[email] = 0 if count is None else count

        self.reply_ok({'contacts': contacts})

    def handle_create_contact(self, args):
        """
        添加新的联系人
        """
        email = args['user'].strip()

        # Check if user exists
        if not User.objects(email=email).first():
            return self.reply_fail(msg='User Not Exists')

        # Atomic update. Add email to contacts only 
        # if it's not in the contacts already
        self.current_user.update(add_to_set__contacts=email)
        return self.reply_ok()

    def handle_delete_contact(self, args):
        """
        删除联系人
        """
        pass

    def handle_update_contact(self):
        """
        更新联系人信息
        """
        pass
    
    def handle_update_unread(self, args):
        """
        更新未读信息数量
        """
        pass

    def handle_chat_with(self, args):
        """
        开始聊天
        """
        pass

    def handle_chat_delete(self, args):
        """
        删除聊天记录
        """
        pass

    def handle_chat_send_msg(self, args):
        """
        发送私信
        """
        pass

    def handle_chat_history(self, args):
        """
        获取历史消息
        """
        pass

    def reply_ok(self, args):
        self.emit('OK', args)

    def reply_fail(self, args):
        self.emit('FAIL', args)

if __name__ == '__main__':
    # Just for test
    import tornado
    application = tornado.web.Application(
            [
                (r'/ws', BaseWSHandler)
            ],
    )
    port = 9999
    application.listen(9999)
    logger.info('Start websocket server in %d', port)

    tornado.ioloop.IOLoop.instance().start()

