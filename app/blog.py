from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Post, User, Like, Comment
from app.forms import PostForm, ProfileEditForm, CommentForm
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

bp = Blueprint('blog', __name__)

# Helper function to save uploaded files
def save_file(file, folder):
    """Save an uploaded file and return the filename"""
    if not file:
        return None
    
    # Create a unique filename to avoid overwriting
    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', folder)
    
    # Ensure directory exists
    os.makedirs(upload_path, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    return filename

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('blog.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False)
    return render_template('blog/index.html', title='Home', form=form, posts=posts)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.post.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('blog.index'))
    elif request.method == 'GET':
        form.post.data = post.body
    return render_template('blog/edit.html', title='Edit Post', form=form)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('blog.index'))

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False)
    # Update last seen timestamp when viewing profile
    if user == current_user:
        user.update_last_seen()
    return render_template('blog/user.html', user=user, posts=posts)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False)
    return render_template('blog/explore.html', title='Explore', posts=posts)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm()
    
    if form.validate_on_submit():
        # Update basic information fields
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.twitter_url = form.twitter_url.data
        current_user.instagram_url = form.instagram_url.data
        current_user.github_url = form.github_url.data
        current_user.website_url = form.website_url.data
        
        # Handle avatar upload
        if form.avatar.data:
            avatar_filename = save_file(form.avatar.data, 'avatars')
            if avatar_filename:
                # Delete old avatar if it's not the default
                if current_user.avatar != 'default_avatar.png':
                    try:
                        old_avatar = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars', current_user.avatar)
                        if os.path.exists(old_avatar):
                            os.remove(old_avatar)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error removing old avatar: {e}")
                
                current_user.avatar = avatar_filename
        
        # Handle cover image upload
        if form.cover_image.data:
            cover_filename = save_file(form.cover_image.data, 'covers')
            if cover_filename:
                # Delete old cover if it's not the default
                if current_user.cover_image != 'default_cover.jpg':
                    try:
                        old_cover = os.path.join(current_app.root_path, 'static', 'uploads', 'covers', current_user.cover_image)
                        if os.path.exists(old_cover):
                            os.remove(old_cover)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error removing old cover: {e}")
                
                current_user.cover_image = cover_filename
        
        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('blog.user', username=current_user.username))
    
    elif request.method == 'GET':
        # Pre-populate form with existing data
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.twitter_url.data = current_user.twitter_url
        form.instagram_url.data = current_user.instagram_url
        form.github_url.data = current_user.github_url
        form.website_url.data = current_user.website_url
    
    return render_template('blog/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    current_user.like_post(post)
    db.session.commit()
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'likes_count': post.get_likes_count()
        })
    
    # For non-AJAX requests, redirect back to the referring page
    next_page = request.referrer or url_for('blog.index')
    return redirect(next_page)

@bp.route('/unlike/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    current_user.unlike_post(post)
    db.session.commit()
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'likes_count': post.get_likes_count()
        })
    
    # For non-AJAX requests, redirect back to the referring page
    next_page = request.referrer or url_for('blog.index')
    return redirect(next_page)

@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    """View a single post with its comments"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        current_user.add_comment(post, form.body.data)
        db.session.commit()
        flash('Your comment has been added!')
        return redirect(url_for('blog.view_post', post_id=post_id))
    
    # Get comments for this post, newest first
    comments = post.comments.order_by(Comment.timestamp.desc()).all()
    
    return render_template('blog/view_post.html', 
                          title=f"Post by {post.author.username}",
                          post=post, 
                          form=form,
                          comments=comments)

@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    
    # Check if user is the comment author or post author
    if comment.user_id != current_user.id and comment.post.author != current_user:
        abort(403)
        
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
        
    return redirect(url_for('blog.view_post', post_id=post_id))

@bp.route('/load_comments/<int:post_id>', methods=['GET'])
@login_required
def load_comments(post_id):
    """Load comments for a post via AJAX"""
    post = Post.query.get_or_404(post_id)
    comments_data = []
    
    for comment in post.comments.order_by(Comment.timestamp.desc()).all():
        comments_data.append({
            'id': comment.id,
            'body': comment.body,
            'timestamp': comment.timestamp.strftime('%b %d, %Y • %I:%M %p'),
            'username': comment.user.username,
            'user_avatar': comment.user.avatar_url(),
            'is_author': comment.user_id == current_user.id or post.author_id == current_user.id
        })
    
    return jsonify({
        'comments': comments_data,
        'count': len(comments_data)
    })
