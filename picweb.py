#!/usr/bin/python

import tornado.ioloop
import tornado.web
import hashlib
import os
import shutil

port=8888
picsdir = '/home/serge/pics'
staticpath = '/static'
fullstaticpath = "%s%s" % (picsdir, staticpath)

# The test passwords are:
#passwords = { 'serge': 'x', 'serue': 'y' }
# use 'echo -n $pwd | sha256sum' to come up with the hash value below

passwords = { 'serge': '2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881',
              'serue': 'a1fce4363854ff888cff4b8e7875d600c2682390412a8cf79b37d0b11148b0fa'}


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
        self.redirect("/pics/index")

class PicHandler(BaseHandler):
    def showindex(self):
        allpath = "%s/%s" % (picsdir, "all")
        alldirs = os.listdir(allpath)
        filtered_alldirs = []
        for d in alldirs:
            p = "%s/%s" % (allpath, d)
            if os.path.isdir(p):
                filtered_alldirs.append(d)
        userpath = "%s/%s" % (picsdir, self.get_current_user())
        userdirs = os.listdir(userpath)
        filtered_userdirs = []
        for d in userdirs:
            p = "%s/%s" % (userpath, d)
            if os.path.isdir(p):
                filtered_userdirs.append(d)
        self.render("index.html", title="Hallyn Pictures", alldirs=filtered_alldirs, files = [], userdirs = filtered_userdirs, allpath=allpath, userpath=userpath, filepath=userpath)

    def show(self, path):
        if os.path.isdir(path):
            userdirs = os.listdir(path)
            dirs = []
            files = []
            for d in userdirs:
                p = "%s/%s" % (path, d)
                if os.path.isdir(p):
                    dirs.append(d)
                else:
                    files.append(d)
            self.render("index.html", title="Hallyn Pictures: %s" % (path), alldirs=[], userdirs=dirs, files=files, allpath="", userpath=path, filepath=path)
        else:
            p = str(path)
            shortpath = p[len(picsdir):]
            spath = "%s%s%s" % (picsdir, staticpath, shortpath)
            if not os.path.exists(spath):
                d=os.path.dirname(spath)
                try:
                    os.makedirs(d)
                except:
                    pass
                shutil.copyfile(p, spath)
            self.redirect("%s%s" % (staticpath, shortpath))

    def get(self, path):
        if self.get_current_user() not in passwords.keys():
            self.redirect("/invalid")
        if path == "index":
            self.showindex()
        else:
            self.show(path)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/invalid", InvalidHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler,
        dict(path=fullstaticpath)),
    (r"/pics/(.*)", PicHandler),
], cookie_secret="05af817c64914b09580fc2cc2b15eb22")

if __name__ == "__main__":
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
