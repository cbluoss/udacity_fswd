import sys
from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
import flask_restless

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.secret_key = "notverysecretatall"
blueprint = make_github_blueprint(
    client_id="3883f6b5210b9657c37f",
    client_secret="017bcd844374b17205d5abfaeb072fe55c61d95f",
)
app.register_blueprint(blueprint, url_prefix="/login")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username


class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    info = db.Column(db.String(255))

    def __init__(self, name, info):
        self.name = name
        self.info = info

    def __repr__(self):
        return '<Category %r>' % self.name


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    desc = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('items', lazy='dynamic'))

    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship(User,
                            backref=db.backref('items', lazy='dynamic'))

    def __init__(self, name, desc, category, owner, pub_date=None):
        self.name = name
        self.desc = desc
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category
        self.owner = owner

    def __repr__(self):
        return '<Post %r>' % self.title

# begin user login/auth etc.

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'github.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# setup SQLAlchemy backend
blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

# create/login local user on successful OAuth login


@oauth_authorized.connect_via(blueprint)
def github_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with {name}".format(name=blueprint.name))
        return
    # figure out who the user is
    resp = blueprint.session.get("/user")
    if resp.ok:
        username = resp.json()["login"]
        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create a user
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with GitHub")
    else:
        msg = "Failed to fetch user info from {name}".format(
            name=blueprint.name)
        flash(msg, category="error")

# notify on OAuth provider error


@oauth_error.connect_via(blueprint)
def github_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))
# end user foo

# VIEWS
@app.route("/")
def index():
    cats = Category.query.all()
    items = Item.query.order_by(Item.pub_date.desc()).limit(10)
    return render_template("home.html", cats=cats, items=items)

# Category VIEWS
@app.route("/category/add", methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'GET':
        return render_template("category_add.html")
    else:
        db.session.add(Category(request.form['name'], request.form['info']))
        db.session.commit()
        return redirect(url_for("index"))


@app.route("/category/delete/<name>")
@login_required
def del_category(name=None):
    db.session.delete(Category.query.filter_by(name=name).first_or_404())
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/category/edit/<name>", methods=['GET', 'POST'])
@login_required
def edit_category(name=None):
    if request.method == 'GET':
        return render_template("category_edit.html",
                               cat=Category.query.filter_by(name=name).\
                               first_or_404())
    else:
        cat = Category.query.filter_by(name=name).first_or_404()
        cat.name = request.form['name']
        cat.info = request.form['info']
        db.session.commit()
    return redirect(url_for("show_category", name=cat.name))


@app.route("/categories/<name>")
def show_category(name=None):
    cat = Category.query.filter_by(name=name).first_or_404()
    items = Item.query.filter_by(category=cat)
    return render_template("category.html", cat=cat, items=items)


#Item VIEWS
@app.route("/item/add/for/<name>", methods=['GET', 'POST'])
@login_required
def add_item(name=None):
    if request.method == 'GET':
        return render_template("item_add.html", 
            cat=Category.query.filter_by(name=name).first_or_404())
    else:
        db.session.add(Item(request.form['name'], request.form['info'],
                            Category.query.filter_by(name=name).\
                            first_or_404(), current_user))
        db.session.commit()
        return redirect(url_for("show_category", name=name))


@app.route("/items/<name>")
def show_item(name=None):
    return render_template("item.html", item=Item.query.\
        filter_by(name=name).first_or_404())


@app.route("/item/delete/<name>")
@login_required
def del_item(name=None):
    item = Item.query.filter_by(name=name).first_or_404()
    if item.owner == current_user:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/item/edit/<name>", methods=['GET', 'POST'])
@login_required
def edit_item(name=None):
    if request.method == 'GET':
        return render_template("item_edit.html",
                               cats=Category.query.all(),
                               item=Item.query.filter_by(name=name).first_or_404())
    else:
        item = Item.query.filter_by(name=name).first_or_404()
        if item.owner == current_user:
            item.name = request.form['name']
            item.desc = request.form['desc']
            item.category = Category.query.\
                filter_by(name=request.form['cat']).first_or_404()
            db.session.commit()
    return redirect(url_for("show_item", name=item.name))

# API Endpoints
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Item, methods=['GET'])
manager.create_api(Category, methods=['GET'])

# hook up extensions to app
db.init_app(app)
login_manager.init_app(app)

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(host="0.0.0.0", port=8000, debug=True,
                ssl_context=('ssl.crt',
                             'ssl.key'))
