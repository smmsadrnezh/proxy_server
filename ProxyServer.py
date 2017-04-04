from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
import httplib

from datetime import datetime


class ProxyHandler(BaseHTTPRequestHandler):
    cache = {}

    def print_response(self, response, body):
        self.send_response(code=response.status,
                           message=response.reason + '\n' + str(response.getheaders()) + '\n' + body)

    def do_GET(self):

        http = self.path[(self.path.find("://") + 3):]

        if http in self.cache:

            if (self.cache[http].keys()[0] - datetime.now()).total_seconds() < -120:

                # find the response from cache storage
                response = self.cache[http].values()[0].keys()[0]
                body = self.cache[http].values()[0].values()[0]
                self.print_response(response, body)

            else:

                # update the expired cached item
                self.cache.pop(http)
                response, body = self.update_cache(http)
                self.print_response(response, body)

        else:
            response, body = self.update_cache(http)
            self.print_response(response, body)

    def update_cache(self, http):

        # find host and path
        if http.find("/") is not -1:
            host = http[:(http.find("/"))]
            path = http[(http.find("/")):]
        else:
            host = http
            path = "/"

        # send request and get the response header and body
        conn = httplib.HTTPConnection(host)
        conn.request("GET", path)
        response = conn.getresponse()
        body = response.read()

        # save response in cache storage
        self.cache[http] = {datetime.now(): {response: body}}

        return response, body


HOST, PORT = "localhost", 8004
SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.ThreadingTCPServer((HOST, PORT), ProxyHandler)

try:
    httpd.serve_forever()
except:
    httpd.server_close()
    raise
