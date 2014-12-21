# Set the path
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server
from snippetlog import app
from flask import Flask, request, render_template, url_for, redirect
from flask.views import MethodView
from wtforms import Form, StringField,TextField, validators
from models import Post, Comment
manager = Manager(app)


# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0')
)


class AddPostForm(Form):
        title = StringField('Title',[validators.Length(min=4,max=25)])
        subtitle = StringField('Subtitle',[validators.Length(min=0,max=25)])
        body = TextField('Content',[validators.Length(min=4,max=500)])
        tags = TextField('tags',[validators.Length(min=0,max=500)])
 
class AddCommentForm(Form):
        comment= StringField('Comment',[validators.Length(min=1,max=100)])
        author= StringField('Author',[validators.Length(min=1,max=5)])
        
@app.route('/')
def GetList():
    '''Home screen, gets all the posts, and prints the form for adding a post'''
    
    #Gets all the posts
    posts=Post.objects.all()
    form=AddPostForm(request.form)
    return render_template("list.html",posts=posts,form=form)

@app.route('/<title>')
def GetDetail(title):
        post = Post.objects.get_or_404(title=title)
        form=AddPostForm(request.form)
        form2=AddCommentForm(request.form)
        return render_template("detail.html", post=post, form=form, form2=form2)



@app.route('/addpost',  methods=['GET', 'POST'])
def addpost(): 
    ''' Gets called as post function for the addition of a snip.
    '''

    form=AddPostForm(request.form)
    title = form.title.data
    subtitle = form.subtitle.data
    body = form.body.data
    taglist = form.tags.data.split(',')
    if len(taglist) == 1 and taglist[0] == '':
        taglist = [] 
    print taglist
    post=Post(title=title,subtitle=subtitle,body=body, tags = taglist)
    print post
    post.save()
    return redirect(url_for('GetList'))

@app.route('/<title>/deletepost')
def deletepost(title):
        post=Post.objects.get(title=title)
        post.delete()
        return redirect(url_for('GetList'))

@app.route('/<title>/addcomment',methods=['GET','POST'])
def addcomment(title):
        post = Post.objects.get_or_404(title=title)
        form=AddCommentForm(request.form)
        comment= form.comment.data
        author= form.author.data
        comment= Comment(author=author, body=comment)
        post.comments.append(comment)
        post.save()
        return redirect(url_for('GetDetail', title=title))

@app.route('/tag/<tag>',methods=['GET','POST'])
def get(tag):
    posts = Post.objects(tags=tag)
    form=AddPostForm(request.form)
    return render_template("list.html",posts=posts,form=form)


if __name__ == "__main__":
    manager.run()
