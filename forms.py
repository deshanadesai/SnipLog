from wtforms import Form, StringField,TextField, PasswordField, validators
from models import Post, Comment, UserInfo

class LoginForm(Form):
        email = StringField('Email',[validators.Required()])
        password = StringField('Password',[validators.Required()])

class RegisterForm(Form):
        userID = StringField('UserID',[validators.Required()])
        email = StringField('Email',[validators.Required()])
        password = PasswordField('Password',[validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
        confirm = PasswordField('Repeat Password')
        
class AddPostForm(Form):
        title = StringField('Title',[validators.Length(min=4,max=25)])
        subtitle = StringField('Subtitle',[validators.Length(min=0,max=25)])
        body = TextField('Content',[validators.Length(min=4,max=500)])
        tags = TextField('tags',[validators.Length(min=0,max=500)])
 
class AddCommentForm(Form):
        comment= StringField('Comment',[validators.Length(min=1,max=100)])
        author= StringField('Author',[validators.Length(min=1,max=5)])
        
