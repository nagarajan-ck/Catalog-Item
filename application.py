from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
import requests, random, string
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def appLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template("app_login.html", STATE=state)

@app.route('/')  # the route for the main page
@app.route('/catalog')
def homepage():
    if('username' not in login_session):
        login_status = False
    else:
        login_status = True
    item = session.query(Item).order_by(Item.id.desc()).limit(10).all()
    # Gets the latest added 10 items
    category = session.query(Category).all()  # gets all the Categories
    return render_template("homepage.html", item=item,
            category=category, login_status=login_status)


@app.route('/catalog/<category>/Items/')  # the route for the category page
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
    return render_template('category_page.html', category=category,
        item=item, categories=categories, count=count, login_status=login_status)


@app.route('/catalog/<category>/<item>/')  # The route for the description page
def item_page(category, item):
    if('username' not in login_session):
        login_status = False
    else:
        login_status = True
    desc = session.query(Item).filter_by(title=item).one().description
    # gets the description of the item
    return render_template('item_page.html', desc=desc,
        item=item, login_status=login_status)


@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():  # route for adding item, accepts get and post requests
    if ('username' not in login_session):
        return redirect('/login')
    if(request.method == 'GET'):
        full_categories = session.query(Category).all()
        return render_template('add_item.html', full_categories=full_categories)

    else:
        category = session.query(Category).filter_by(name=request.form['Category']).one()
        category_id = category.id
        # category is the category of the new object
        # category_id is the respective id
        item = Item(title=request.form['Title'], description=request.form['Description'],
                category_id=category_id, user_id = login_session['user_id'])
        session.add(item)
        session.commit()
        flash("Item has been added!")
        # message flashing to display item has been added
        return redirect(url_for('category_page', category=category.name))


@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def edit_item(item):  # route to edit items
    if ('username' not in login_session):
        return redirect('/login')
    item_to_edit = session.query(Item).filter_by(title=item).one()
    if (item_to_edit.user_id != login_session['user_id']):
        flash("Sorry {}, you are not the owner of the item".format(login_session['username']))
        return redirect('/')
    else:
        owner_status = False
    if (request.method == 'GET'):
        full_categories = session.query(Category).all()
        current_category = session.query(Category).filter_by(id=item_to_edit.category_id).one().name
        # category name of item
        return render_template('edit_item.html', item_to_edit=item_to_edit,
            full_categories=full_categories, current_category=current_category, owner_status=owner_status)
    else:
        item_to_edit.title = request.form['Title']
        item_to_edit.description = request.form['Description']
        item_to_edit.category_id = session.query(Category).filter_by(name=request.form['Category']).one().id
        flash("Item has been edited!")
        return redirect(url_for('category_page', category=request.form['Category']))


@app.route('/catalog/<item>/delete/', methods=['GET', 'POST'])
def delete_item(item):  # route to delete items
    if ('username' not in login_session):
        return redirect('/login')
    item_to_delete = session.query(Item).filter_by(title=item).one()
    # gets the object of the item to delete

    if (item_to_delete.user_id != login_session['user_id']):
        flash("Sorry {}, you are not the owner of the item".format(login_session['username']))
        return redirect('/')

    category = session.query(Category).filter_by(id=item_to_delete.category_id).one()
    if(request.method == 'GET'):
        return render_template('delete_item.html', item=item_to_delete, category=category)
    else:
        session.delete(item_to_delete)
        session.commit()
        flash("Item has been deleted!")
        return redirect(url_for('category_page', category=category.name))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    result = requests.get(url).json()
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if (not user_id): #user does not exist in db, user_id returns none
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    welcome_message = "Welcome to catalog item app {}".format(login_session['username'])
    flash("you are now logged in as {}".format(login_session['username']))

    return welcome_message


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print(result)
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user



def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None



@app.route('/catalog.json')  # the endpoint for JSON
def catalogJSON():
    category = session.query(Category).all()
    json_array = []  # array stores the json of individual categories
    for i in category:
        item = session.query(Item).filter_by(category_id=i.id).all()
        for j in item:
            category_json = i.serialize
            item_json = j.serialize
            consolidated_json = JSON(category_json.get('name'), category_json.get('id'), item_json)
            json_array.append(consolidated_json)
    return jsonify(Catalog=[i for i in json_array])



# called from catalogJSON,
# this function returns a dictionary of the consolidated jsons
def JSON(name, id, item):
    return
    {
        'Id': id,
        'Name': name,
        'item': [item]
    }


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
