from torando.web import RequestHandler

class PrivateMessageHandler(RequestHandler):

    def get(self):
        """
        获取消息
        """
        self.write("Hello, world")

    def post(self):
        """
        发送消息
        """
        pass
