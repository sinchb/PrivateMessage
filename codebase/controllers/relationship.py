from torando.web import RequestHandler

class RelationShipHandler(RequestHandler):

    def get(self):
        """
        获取联系人
        """
        self.write("Hello, world")

    def post(self):
        """
        添加联系人
        """
        pass

    def delete(self):
        """
        删除联系人
        """
