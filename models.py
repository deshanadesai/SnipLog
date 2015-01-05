import datetime
from flask import url_for
from snippetlog import db

class UserInfo(db.Document):
        email = db.EmailField(required=True)
        userID = db.StringField(unique=True,required = True, max_length=20)
        password = db.StringField(required = True)
        active = db.BooleanField(default = True)
        isAdmin = db.BooleanField(default = False)
        timestamp = db.DateTimeField(default = datetime.datetime.now())

        def is_active(self):
            return True

        def get_id(self):
            try:
                return unicode(self.userID)
            except AttributeError:
                raise NotImplementedError('No `id` attribute - override `get_id`')


        def get_by_id(self, id):
            try:
                dbUser = models.User.objects.with_id(id)
                return dbUser
            except Exception, e:
                print str(e)
    	    
        def is_authenticated(self):
            return True

        def is_anonymous(self):
            return False

class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now)
    user = db.ListField(db.ReferenceField(UserInfo), required=True)
    title = db.StringField(max_length=255, required=True)
    subtitle = db.StringField(max_length=255)
    body = db.StringField(required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    tags = db.ListField(db.StringField(max_length=255, required =False))
        
    def get_absolute_url(self):
        return url_for('post', kwargs={"title": self.title})
    def __unicode__(self):
        return self.title
    def get_bagofwords(self):
        '''
        Return a list (duplicate allowed) of all words in title and
        content combined.
        '''
        return [x.lower() for x in self.title.split()] + [x.lower() for x in self.body.split()]

	def get_user(self):
		return user

    meta = {
            'allow_inheritance': True,
            'indexes': ['-user'],
            'ordering': ['-user', '-created_at']
        }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)


        
        
