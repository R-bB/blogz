from flask import Flask, request, redirect, render_template, flash, session
from datetime import datetime
from app import app, db
from models import User, Post
from hashutils import make_pw_hash, check_pw_hash

app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route("/blog")
def display_blog_posts():
    username = request.args.get('username')
    owner = User.query.filter_by(username=username).first() 
    if request.args.get('id'):        
        title_id = request.args.get('id')
        blogs = Post.query.get(title_id)
        blog_title = blogs.title
        blog_body = blogs.body 
        return render_template('single_post.html', posts=blogs, blog_title=blog_title, blog_body=blog_body, userId=owner)
    elif request.args.get('user'):
        userId = request.args.get('user')
        posts = Post.query.filter_by(owner_id=userId).all()          
        return render_template('singleUser.html', posts=posts)
    if not request.args.get('id'):        
        posts = Post.query.all()
        return render_template('all_posts.html', page_title='Blogz', posts=posts)
    sort = request.args.get('sort')
    if (sort=="newest"):
        all_posts = Post.query.order_by(Post.created.desc()).all()
    else:
        all_posts = Post.query.all()   
    return render_template('all_posts.html', title="All Posts", all_posts=all_posts)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    
    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Post(new_post_title, new_post_body, owner)

        if new_post.is_valid():
            db.session.add(new_post)
            db.session.commit() 

            url = "/blog?id=" + str(new_post.id)
            return redirect(url)
        else:
            flash("Please check your post for errors. Both a title and a body are required.")
            return render_template('new_post_form.html',
                title="Create new blog post",
                new_post_title=new_post_title,
                new_post_body=new_post_body)

    else: 
        return render_template('new_post_form.html', title="Create new blog post")

@app.before_request        
def require_login():
    allowed_routes = ['login', 'signup', 'main_blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            flash('Invalid username', 'error')
            return redirect('/login')
        user = User.query.filter_by(username=username).first()
        if user and not check_pw_hash(password, user.pw_hash):
            flash('Password is incorrect', 'error')
            return redirect('/login')
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in", 'information')
            flash('Welcome back ' + username.capitalize() + '!', 'information')
            print(session)
            return redirect('/new_post')
        elif not user:
            flash('Username does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == '' or password == '' or verify == '':
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')
        if len(username) < 3:
            flash('Invalid username', 'error')
            return redirect('/signup')
        if len(password) < 3 or len(verify) < 3:
            flash('Invalid password', 'error')
            return redirect('/signup')
        else:
            if password != verify:
                flash("Password don't match", 'error')
                return redirect('/signup')
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:#new user
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Welcome to your blog, ' + username.capitalize() + '!', 'information')
            return redirect('/new_post')
        else:
            flash('Username already exists', 'error')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/blog')

def logged_in_user():
    owner = User.query.filter_by(email=session['username']).first()
    return owner

if __name__ == '__main__':
    app.run()