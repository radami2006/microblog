from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ProfileEditForm(FlaskForm):
    bio = TextAreaField('About me', validators=[Length(min=0, max=200)])
    location = StringField('Location', validators=[Length(min=0, max=64)])
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    cover_image = FileField('Cover Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    
    # Fix URL validation to properly handle empty URLs
    twitter_url = URLField('Twitter URL', validators=[Optional()])
    instagram_url = URLField('Instagram URL', validators=[Optional()])
    github_url = URLField('GitHub URL', validators=[Optional()])
    website_url = URLField('Website URL', validators=[Optional()])
    
    submit = SubmitField('Save Changes')
    
    # Add custom validators for URLs
    def validate_twitter_url(self, field):
        if field.data and not self._is_valid_url(field.data):
            raise ValidationError('Invalid URL format.')
            
    def validate_instagram_url(self, field):
        if field.data and not self._is_valid_url(field.data):
            raise ValidationError('Invalid URL format.')
            
    def validate_github_url(self, field):
        if field.data and not self._is_valid_url(field.data):
            raise ValidationError('Invalid URL format.')
            
    def validate_website_url(self, field):
        if field.data and not self._is_valid_url(field.data):
            raise ValidationError('Invalid URL format.')
            
    def _is_valid_url(self, url):
        from wtforms.validators import url as url_validator
        return url_validator(url)

class CommentForm(FlaskForm):
    """Form for submitting comments on posts"""
    body = TextAreaField('Write a comment...', validators=[
        DataRequired(), Length(min=1, max=500)
    ])
    submit = SubmitField('Post Comment')
