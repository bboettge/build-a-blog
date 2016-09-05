import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", content="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, content=content, error=error,
                    blogposts = blogposts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = BlogPost(title= title, content = content)
            a.put()

            self.redirect("/blog")
        else:
            error = "Please enter both a title and content."
            self.render_front(title, content, error)

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
#    ('/newpost', NewPost)
], debug=True)
