from ws4py.client.threadedclient import WebSocketClient
from utils import dec, enc

class DummyClient(WebSocketClient):
    def opened(self):
        import pdb;pdb.set_trace()
        msg = enc('OK', {'event': 'FUCK'})
        self.send(msg)

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print m
        if len(m) == 175:
            self.close(reason='Bye bye')

if __name__ == '__main__':
    try:
        ws = DummyClient('ws://localhost:8888/chat', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
