from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import current_app

# Define the likes association table
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Define a unique constraint to ensure a user can only like a post once
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

# Define the comments model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    
    # Define relationship with user (commenter)
    user = db.relationship('User', backref='comments')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # New profile fields
    bio = db.Column(db.String(200))
    avatar = db.Column(db.String(120), default='default_avatar.png')
    cover_image = db.Column(db.String(120), default='default-cover.jpg')
    location = db.Column(db.String(64))
    twitter_url = db.Column(db.String(120))
    instagram_url = db.Column(db.String(120))
    github_url = db.Column(db.String(120))
    website_url = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    # Add relationship for likes given by this user
    likes = db.relationship('Like', 
                           foreign_keys='Like.user_id',
                           backref=db.backref('user', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar_url(self):
        """Get the URL for the user's avatar"""
        return f'/static/uploads/avatars/{self.avatar}'
        
    def cover_url(self):
        """Get the URL for the user's cover image"""
        if self.cover_image:
            return f'/static/uploads/covers/{self.cover_image}'
        else:
            # Fallback to default cover if none set
            return '/static/uploads/covers/default-cover.jpg'
        
    def update_last_seen(self):
        """Update the last seen timestamp for the user"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
        
    def get_total_character_count(self):
        """Calculate the total number of characters in all user's posts"""
        return sum(len(post.body) for post in self.posts)
        
    def like_post(self, post):
        """Like a post if not already liked"""
        if not self.has_liked_post(post):
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)
            
    def unlike_post(self, post):
        """Unlike a post"""
        if self.has_liked_post(post):
            Like.query.filter_by(user_id=self.id, post_id=post.id).delete()
            
    def has_liked_post(self, post):
        """Check if user has liked a post"""
        return Like.query.filter(
            Like.user_id == self.id,
            Like.post_id == post.id
        ).count() > 0
        
    def add_comment(self, post, body):
        """Add a comment to a post"""
        comment = Comment(body=body, user_id=self.id, post_id=post.id)
        db.session.add(comment)
        return comment

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Add relationship for likes received by this post
    likes = db.relationship('Like', 
                           foreign_keys='Like.post_id',
                           backref=db.backref('post', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')
                           
    # Add relationship for comments on this post
    comments = db.relationship('Comment', 
                              backref='post', 
                              lazy='dynamic',
                              cascade='all, delete-orphan',
                              order_by='Comment.timestamp')
                           
    def get_likes_count(self):
        """Get the number of likes for this post"""
        return self.likes.count()
        
    def get_comments_count(self):
        """Get the number of comments for this post"""
        return self.comments.count()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
