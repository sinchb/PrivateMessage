#coding=utf-8
from time import sleep
from ws4py.client.threadedclient import WebSocketClient
from utils import dec, enc

class DummyClient(WebSocketClient):

    def logon(self, email, password):
        print 'Logon', email, password
        msg = enc(
            'LOGON',
            {'email': email, 'password': password}
        )
        self.send(msg)

    def login(self, email, password):
        print 'Login', email, password
        msg = enc(
            'LOGIN',
            {'email': email, 'password': password}
        )
        self.send(msg)

    def create_contact(self, user):
        print 'Create contacts', user
        msg = enc(
            'CREATE_CONTACT',
            {'user': user}
        )
        self.send(msg)

    def delete_contact(self, user):
        print 'Delete contacts', user
        msg = enc(
            'DELETE_CONTACT',
            {'user': user}
        )
        self.send(msg)

    def list_contacts_unread(self):
        print 'List contacts unread'
        msg = enc(
            'LIST_CONTACTS_UNREAD',
            {}
        )
        self.send(msg)

    def chat_with(self, email):
        print 'chat with'
        msg = enc(
            'CHAT_WITH',
            {'user': email}
        )
        self.send(msg)

    def send_msg(self, content, email):
        print 'send_msg'
        msg = enc(
            'CHAT_SEND_MSG',
            {
                'to_email': email,
                'content': content
            }
        )

        self.send(msg)

    def send(self, *args, **kwargs):
        super(DummyClient, self).send(*args, **kwargs)
        sleep(0.2)

    def opened(self):
        self.logon('eva@gmail.com', '123456')
        self.login('eva@gmail.com', '123456')
        self.create_contact('sinchb128@gmail.com')
        self.list_contacts_unread()

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print m

if __name__ == '__main__':
    try:
        ws = DummyClient('ws://localhost:8888/chat', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
