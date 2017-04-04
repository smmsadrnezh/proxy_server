from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
import httplib

from datetime import datetime


class ProxyHandler(BaseHTTPRequestHandler):
    cache = {}

    def do_GET(self):

        print datetime.now().time()

        http = self.path[(self.path.find("://") + 3):]

        if http in self.cache:

            # print the response from cache storage
            response = self.cache[http]
            print response.status, response.reason
            print response.getheaders()
            print response.read()

        else:

            # send request and get the response
            host = http[:(http.find("/"))]
            path = http[(http.find("/")):]
            conn = httplib.HTTPConnection(host)
            conn.request("GET", path)
            response = conn.getresponse()

            # save response in cache storage
            self.cache[http] = response

            # print the response
            print response.status, response.reason
            print response.getheaders()
            print response.read()


HOST, PORT = "localhost", 8004
SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.ThreadingTCPServer((HOST, PORT), ProxyHandler)

try:
    httpd.serve_forever()
except:
    httpd.server_close()
    raise
