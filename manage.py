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
from forms import LoginForm, RegisterForm, AddPostForm, AddCommentForm

manager = Manager(app)

from lib import search
# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0')
)

@app.route('/')
def index():
    '''Welcome to SnipLog Page. Login to Continue.'''

    form = LoginForm(request.form)
    return render_template("login.html", form=form)

@app.route('/reg')
def register_page():
    '''Go to URL to access Register form and register the new user.
       Redundant method. Needs to be integrated in the index page
    '''

    form = RegisterForm(request.form)
    return render_template("register.html", form= form)

@app.route('/list')
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

@app.route("/login", methods = ["GET", "POST"])
def login():
	
	''' Logs in by asking the user for userID and password. Performs checks and shows error messages.'''
	#Bug: Should be (userID or EmailID) optional.
	
        if request.method=="POST" and "userID" in request.form:
                userID = request.form["userID"]
                
		try:
                	user = UserInfo.objects.get(userID=userID)
                
		   	if user.active and check_password_hash(user.password, request.form["password"]):
                     	   if login_user(user):
                                return redirect(url_for('GetList'))
                 	else:
                           error="Password Incorrect. Please try again."
                except:
			error="UserID Incorrect. Please try again."
                        
        form = LoginForm(request.form)
    	return render_template("login.html", form=form, error=error)
                
@app.route("/register", methods = ["GET","POST"])
def register():
	
	''' Registers the user. Performs Validation Checks. 
	    Encrypts the password by Hashing AND Salting. Very secure.
	    Error messages need to be more specific.
	    Need to pinpoint the error instead of the list of possible errors.
	'''
	#Bug: Verify Email functionality.

        form = RegisterForm(request.form)
        if request.method == "POST" and form.validate():
                userID = request.form["userID"]
                email = request.form["email"]
                password = request.form["password"]
                
                hashedPassword = generate_password_hash(password)
                user = UserInfo(userID= userID,email= email,password= hashedPassword)
            
                try:
                        user.save()                       
                        if login_user(user):
                                return redirect(url_for('GetList'))
                        else:
                                error="Unable to Log you in due to inactive account."

                except Exception,e:
                        print str(e)
			error="Unable to Register your account due to system error."
	error="The form did not pass the validations. Please check \n\t1. If your passwords match.\n\t2. UserID, password length [5-15] characters.\n\t3. Your EmailID is previously registered."
        form = RegisterForm(request.form)
    	return render_template("register.html", form= form, error=error)

@login_manager.user_loader
def load_user(userID):

    '''Loads user from session or remember_me cookie as applicable
       If a remember cookie is set, and the session is not, moves the
       cookie user ID to the session.
        
       However, the session may have been set if the user has been
       logged out on this request, 'remember' would be set to clear,
       It checks for that and does not restore the session.
    '''
    #Bug: Yet to ask for 'remember' to user.

    if userID is None:
            redirect('/')
    
    user = UserInfo.objects.get(userID= userID)
    if user.active:
            return user
    else:
            return None

@app.route("/logout")
@login_required
def logout():
	'''
    	Logs a user out. (No need to pass the actual user, pops current_user out of session). 
	This will also clean up the remember me cookie if it exists.
    	'''
        logout_user()
        flash("Logged out.")
        return redirect(url_for('index'))

@app.route('/tag/<tag>',methods=['GET','POST'])
def atleast_these_tags(tag):
    '''Method to search all the posts with atleast all the tags
    <tag> = tag1,tag2,tag3
    No ranking mechanism. But output contains all the posts which atleast
    contain all the tags provided.
    '''
    taglist = tag.split(',')
    print taglist
    #If atleast one of the tags is present
    # posts = Post.objects(tags__in=taglist)

    #If all the tags are exactly present
    # posts = Post.objects(tags=taglist)
    
    #If atleast all the tags specified are present. 
    posts = Post.objects(tags__all=taglist)

    print posts
    form=AddPostForm(request.form)
    return render_template("list.html",posts=posts,form=form)
    
@app.route('/search/<query>',methods=['GET','POST'])
def Search(query):
    ''' 
    Input query : +tag1 +tag2 keywords
    Currently employed version of search : v1
    '''
    #need to take out the tag terms out of the query if they exist.
    #Starting with just content based topics
    content = query
    form=AddPostForm(request.form)

    # posts = Post.objects(body__icontains=content)
    posts = search.search_v1(query)
    return render_template("list.html",posts=posts,form=form)


if __name__ == "__main__":
    manager.run()
