from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.options
import tornado.log
import logging

from app import create_app
from app.settings import AppConfig

app = create_app()


class LogFormatter(tornado.log.LogFormatter):

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


if __name__ == '__main__':
    tornado.options.define("port", default=AppConfig.SERVER_PORT, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    tornado.options.log_file_prefix = AppConfig.LOG_PATH + 'tornado_main.log'
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(AppConfig.SERVER_PORT)
    IOLoop.instance().start()
