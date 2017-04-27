import base64
import logging
import pymysql
from core.config import *
from gevent.wsgi import WSGIServer
from flask import Flask
from logging.handlers import RotatingFileHandler


class WebServer(object):

    def __init__(self, args):
        # we will reference these variables throughout the class
        self.protocol = args.protocol
        self.external_address = args.external_address
        self.port = args.port
        self.profile = args.profile

        # tries to open the database connection
        try:
            self.connection = pymysql.connect(host="localhost",
                                              port=3306,
                                              user=username,
                                              passwd=password,
                                              db=database,
                                              autocommit=True)

        # exception raised during database connection
        except Exception:
            raise

    def is_base64(self, string):
        """
        DESCRIPTION:
            This function checks if the specified string is Base64 encoded or not

        RETURNS:
            Bool
        """
        try:
            base64.b64decode(string).decode()
            return True

        except Exception:
            return False

    def start_web_server(self, port):
        """
        DESCRIPTION:
            This function creates and starts the Flask web server

        RETURNS:
            None
        """
        # tries to create and start the Flask web server
        try:
            # creates Flask app
            app = Flask(__name__)
            app.debug = True

            # configures Flask logging with 100 meg max file size
            # all requests are logged to "listener/logs/access.log"
            log_handler = RotatingFileHandler("logs/access.log", maxBytes=100000000, backupCount=3)
            app.logger.addHandler(log_handler)
            app.logger.setLevel(logging.INFO)

            # TO DO: add in "INSERT INTO listeners" statement here

            # starts Flask web server
            server = WSGIServer(("0.0.0.0", port), app, log=app.logger)
            server.serve_forever()

        # ignores KeyboardInterrupt exception
        except KeyboardInterrupt:
            pass

        # exception raised creating and starting the Flask web server
        except Exception:
            raise

        # deletes all entries from "listeners" table
        # also closes the database connection
        finally:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM listeners")

            if self.connection.open:
                self.connection.close()
