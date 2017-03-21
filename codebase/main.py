import tornado.ioloop
import tornado.web

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

routes = [

]

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
