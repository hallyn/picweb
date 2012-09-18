#!/usr/bin/python

import tornado.ioloop
import tornado.web
import hashlib

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class InvalidHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Invalid username or password")

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

# The test passwords are:
#passwords = { 'serge': 'x', 'serue': 'y' }
# use 'echo -n $pwd | sha256sum' to come up with the hash value below

passwords = { 'serge': '2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881',
              'serue': 'a1fce4363854ff888cff4b8e7875d600c2682390412a8cf79b37d0b11148b0fa'}

class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   'Password: <input type="text" name="password">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        name=self.get_argument("name")
        if name not in passwords.keys():
            self.redirect("/invalid")
        pwd = self.get_argument("password")
        if passwords[name] != hashlib.sha256(pwd).hexdigest():
            self.redirect("/invalid")
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/invalid", InvalidHandler),
], cookie_secret="05af817c64914b09580fc2cc2b15eb22")


picdirs = [ '/home/serge/pics' ]

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
