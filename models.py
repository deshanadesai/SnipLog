import datetime
from flask import url_for
from snippetlog import db

class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    subtitle = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    tags = db.ListField(db.StringField(max_length=255, required =False))
        
    def get_absolute_url(self):
        return url_for('post', kwargs={"title": self.title})
    def __unicode__(self):
        return self.title

    meta = {
            'allow_inheritance': True,
            'indexes': ['-created_at', 'title'],
            'ordering': ['-created_at']
        }

class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)
