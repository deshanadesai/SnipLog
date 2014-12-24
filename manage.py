# Set the path
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server
from snippetlog import app, login_manager
from flask import Flask, flash, request, render_template, url_for, redirect
from flask.views import MethodView
from wtforms import Form, StringField,TextField, PasswordField, validators
from models import Post, Comment, UserInfo
from flask.ext.login import (UserMixin, current_user, login_required, login_user, logout_user, confirm_login, fresh_login_required)
from werkzeug import generate_password_hash, check_password_hash
manager = Manager(app)


# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0')
)

class User(UserMixin):
    def __init__(self, email=None, password=None, is_active=True, userID=None):
        self.email = email
        self.password = password
        self.is_active = is_active
        self.isAdmin = False
        self.userID = None

    def create_instance(self, email, password, userID):
        UserInfo(userID=userID,email=email,password=password)
        self.email=email
        self.password=password
        self.userID=userID
        return self
            
    def save(self):
        print "in here",self.password
        User.set_password(self, self.password)
        print "reaches", self.password
        AddUser = UserInfo(email = self.email, userID=self.userID, password = self.password, is_active=True)
        print "also here"
        AddUser.save()
        print "saved"
        

    def get_by_email(self, email):
        try:
            dbUser = UserInfo.objects.get(email=email)
            
            if dbUser:
                self.email = dbUser.email
                self.is_active = dbUser.is_active
                self.password = dbUser.password
                return self
            else:
                return None
        except:
            print "there was an error"
            return None

    def get_by_userID(self, userID):
        try:
            dbUser = UserInfo.objects.get(userID=userID)
            
            if dbUser:
                self.email = dbUser.email
                self.is_active = dbUser.is_active
                self.password = dbUser.password
                return self
            else:
                return None
        except:
            print "there was an error"
            return None

    def set_password(self, password):
        print "came here"
        self.password = generate_password_hash(password)
        print "going awya"

    def check_password(self, password):
        return check_password_hash(self.password, password)

class LoginForm(Form):
        email = StringField('Email',[validators.Required()])
        password = StringField('Password',[validators.Required()])

class RegisterForm(Form):
        userID = StringField('UserID',[validators.Required()])
        email = StringField('Email',[validators.Required()])
        password = PasswordField('Password',[validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
        confirm = PasswordField('Repeat Password')
        
class AddPostForm(Form):
        title= StringField('Title',[validators.Length(min=4,max=25)])
        subtitle= StringField('Subtitle',[validators.Length(min=0,max=25)])
        body= TextField('Content',[validators.Length(min=4,max=500)])

class AddCommentForm(Form):
        comment= StringField('Comment',[validators.Length(min=1,max=100)])
        author= StringField('Author',[validators.Length(min=1,max=5)])
        
@app.route('/')
def index():
    form = LoginForm(request.form)
    return render_template("login.html", form=form)

@app.route('/reg')
def index2():
    form = RegisterForm(request.form)
    return render_template("register.html", form= form)

@app.route('/list')
def GetList():
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
        form=AddPostForm(request.form)
        title = form.title.data
        subtitle = form.subtitle.data
        body = form.body.data
        post=Post(title=title,subtitle=subtitle,body=body)
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

@app.route("/login", methods = ["GET", "POST"])
def login():
        if request.method=="POST" and "email" in request.form:
                email = request.form["email"]
                
                UserObj = User()
                user= UserObj.get_by_email(email)
                if user and user.is_active and User.check_password(user, request.form["password"]):
                        if login_user(user):
                                flash("Logged in!")
                                return redirect(url_for('GetList'))
                        else:
                                flash("unable to log you in")
                else:
                        flash("Password incorrect.")
                        print "error"
        return render_template("hello.html")
                
@app.route("/register", methods = ["GET","POST"])
def register():

        form = RegisterForm(request.form)
        if request.method == "POST" and form.validate():
                userID = request.form["userID"]
                email = request.form["email"]
                password = request.form["password"]
                
                UserObj = User()
                user= UserObj.create_instance(email, password, userID)
                print user

                try:
                        user.save()
                        dbUser=UserInfo.objects.get_or_404(userID=user.userID)
                        print dbUser.is_active,"and ",dbUser.userID
                        login_user(dbUser)
                        if 2==2:
                                print "logged in"
                                flash("Logged in!")
                                return redirect(url_for('GetList.html'))
                        else:
                                print "log no"
                                flash("Unable to log you in")

                except:
                        print "oops"
                        flash("Unable to register with that email address.")

        return render_template("hello.html") 

@login_manager.user_loader
def load_user(userID):
    if userID is None:
            redirect('/')
    user=User()
    user.get_by_userID(userID)
    if user.is_active:
            return user
    else:
            return None

@app.route("/logout")
@login_required
def logout():
        logout_user()
        flash("Logged out.")
        return redirect(url_for('Login'))


if __name__ == "__main__":
    manager.run()
