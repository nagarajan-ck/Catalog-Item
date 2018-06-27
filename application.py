'''
This file runs the server on the localhost on port 8000.
It also leverages the option of templates to display the web Page
dynamically, and uses sqlalchemy for database storage
and OAuth for authentication
'''

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
import requests
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

# Gets the client ID from the json file
CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

''' This function creates the login page and creates a state variable for
additional security
 '''


@app.route('/login')
def appLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template("app_login.html", STATE=state)


# the route for the main page which displays the Catalogs
@app.route('/')
@app.route('/catalog')
def homepage():
    if('username' not in login_session):
        login_status = False
    # If the user is logged in, the status is set True
    else:
        login_status = True
    # Gets the latest added 10 items
    item = session.query(Item).order_by(Item.id.desc()).limit(10).all()
    category = session.query(Category).all()  # gets all the Categories
    return render_template("homepage.html", item=item,
                           category=category,
                           login_status=login_status)


''' the route for the category page,
 which displays the items for a specific category'''


@app.route('/catalog/<category>/Items/')
@app.route('/catalog/<category>/')
def category_page(category):
    if('username' not in login_session):
        login_status = False
    else:
        login_status = True
    cat_id = session.query(Category).filter_by(name=category).one().id
    categories = session.query(Category).all()
    # categories has all the category
    item = session.query(Item).filter_by(category_id=cat_id).all()
    # item gets the object of the particular category
    count = len(item)  # the number of items that a category has
    return render_template('category_page.html', category=category, item=item,
                           categories=categories, count=count,
                           login_status=login_status)


'''The route for the description page
   The description page gives further info about an item'''


@app.route('/catalog/<category>/<item>/')
def item_page(category, item):
    owner_status = False
    if('username' in login_session):
        login_status = True
        item_owner_id = session.query(Item).filter_by(title=item).one().user_id
        # Checks if the current selected item is owned by the logged in user
        if(item_owner_id == login_session['user_id']):
            owner_status = True
    else:
        login_status = False
    desc = session.query(Item).filter_by(title=item).one().description
    # gets the description of the item
    return render_template('item_page.html', desc=desc, item=item,
                           owner_status=owner_status,
                           login_status=login_status)

''' route for adding item, accepts get and post requests
    User won't be able to access if not logged in '''


@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():
    if ('username' not in login_session):
        return redirect('/login')  # redirects to login page if not logged in
    if(request.method == 'GET'):
        full_categories = session.query(Category).all()
        return render_template('add_item.html',
                               full_categories=full_categories)
    else:
        category = (session.query(Category).filter_by(
                    name=request.form['Category']).one())
        category_id = category.id
        # category is the category of the new object
        # category_id is the respective id
        item = Item(title=request.form['Title'],
                    description=request.form['Description'],
                    category_id=category_id, user_id=login_session['user_id'])
        session.add(item)
        session.commit()
        flash("Item has been added!")
        # message flashing to display item has been added
        return redirect(url_for('category_page', category=category.name))


'''
If logged in, and owns the item,
a user will be able to edit an item
'''


@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def edit_item(item):
    if ('username' not in login_session):
        return redirect('/login')
    item_to_edit = session.query(Item).filter_by(title=item).one()
    if (item_to_edit.user_id != login_session['user_id']):
        flash("Sorry {}, you are not the owner of the item".format(
              login_session['username']))
        return redirect('/')  # If not owner, redirected to homepage
    if (request.method == 'GET'):
        full_categories = session.query(Category).all()
        current_category = (session.query(Category).filter_by(
                            id=item_to_edit.category_id).one().name)
        return render_template('edit_item.html', item_to_edit=item_to_edit,
                               full_categories=full_categories,
                               current_category=current_category)
    else:
        item_to_edit.title = request.form['Title']
        item_to_edit.description = request.form['Description']
        item_to_edit.category_id = (session.query(Category).filter_by(
                                    name=request.form['Category']).one().id)
        flash("Item has been edited!")
        return redirect(url_for(
                        'category_page', category=request.form['Category']))


'''
If logged in, and owns the item,
a user will be able to delete an item
'''


@app.route('/catalog/<item>/delete/', methods=['GET', 'POST'])
def delete_item(item):
    if ('username' not in login_session):
        return redirect('/login')
    item_to_delete = session.query(Item).filter_by(title=item).one()
    if (item_to_delete.user_id != login_session['user_id']):
        flash("Sorry {}, you are not the owner of the item".format(
              login_session['username']))
        return redirect('/')

    category = session.query(Category).filter_by(
                             id=item_to_delete.category_id).one()
    if(request.method == 'GET'):
        return render_template('delete_item.html',
                               item=item_to_delete,
                               category=category)
    else:
        session.delete(item_to_delete)
        session.commit()
        flash("Item has been deleted!")
        return redirect(url_for('category_page', category=category.name))


'''
This method allows users to log in to the app using google account
accepts only post request
'''


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token created during login
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # variable code contains the authorization code
    code = request.data

    try:
        # Exchange the authorization code for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Validation done to check if the access_token recieved was valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    result = requests.get(url).json()
    # In case validation failed, display
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token was generated for the correct user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Validate if access_token was generated for the correct app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
                                 "Token's client ID does not match app's."),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user trying to connect is already connected
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the login session info for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Gets user info such as name, email, picture
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if (not user_id):  # user does not exist in db, user_id returns none
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    welcome_message = ("Welcome to catalog item app {}".format
                       (login_session['username']))
    flash("You are now logged in as {}".format(login_session['username']))

    return welcome_message


# function disconnects user from the app and reditects to the homepage
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Revoke the access token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # If successful, delete the user info stored in login_session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        flash("You have successfully logged out!")
        return redirect('/')
    else:
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        return response


'''# At the first time of log in
this function is called, and the user is created'''


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# takes in user id, returns the user object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# takes in email id and returns user id if found
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Json endpoint for an arbitrary item
@app.route('/<item>/catalog.json')  # the endpoint for JSON
def catalogJSON(item):
    item_obj = session.query(Item).filter_by(title=item).one()
    return jsonify(item_obj.serialize)


# keeps the server running with facility for debug
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
