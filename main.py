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
    def render_front(self):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
#        post_id = blogposts.key().id()
        self.render("front.html", blogposts = blogposts)

    def get(self):
        self.render_front()


class NewPost(Handler):
    def render_form(self, title="", content="", error=""):
        self.render("form.html", title=title, content=content, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = BlogPost(title= title, content = content)
            a.put()
            new_id = str(a.key().id())
            self.redirect("/blog/" + new_id)
        else:
            error = "Please enter both a title and content."
            self.render_form(title, content, error)

class ViewPostHandler(Handler):
    def render_post(self, title="", content="", url="", error=""):
        self.render("posts.html", title=title, content=content, url=url, error=error)

    def get(self, id):
#        post_id = self.request.get("id")
        new_id = id
        new_post = BlogPost.get_by_id(int(new_id))
        if new_post:
            title = new_post.title
            content = new_post.content
            url = "http://localhost:11080/blog/" + str(new_post.key().id())
#            response = title + content
            self.render_post(title, content, url)
        else:
            error = "Sorry, there is no post with that id."
            self.render_post("", "", "", error)




app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
