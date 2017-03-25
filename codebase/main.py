
import tornado.ioloop
import tornado.web
from controllers.handler import PrivateMessageHandler

from redis import StrictRedis
from mongoengine import connect

from logger import logger

connect('localhost')

redis = StrictRedis(host='localhost', port=6379, db=0)

def make_app():
    return tornado.web.Application(
        [(r"/chat", PrivateMessageHandler)],
        settings={'redis': redis}
    )

if __name__ == "__main__":
    port = 8888
    app = make_app()
    app.listen(port)
    logger.info('Start websocket server in %d', port)
    tornado.ioloop.IOLoop.current().start()
