from torando.web import RequestHandler

class UserHandler(RequestHandler):
    def get(self):
        """
        用户登录
        """
        self.write("Hello, world")

    def post(self):
        """
        用户注册
        """
        pass
