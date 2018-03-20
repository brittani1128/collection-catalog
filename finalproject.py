from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Collection, CollectionItem, User

# Imports for login step
from flask import session as login_session
import random
import string

# Imports for GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///collectioncatalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Render the login template
    return render_template('login.html', STATE=state)


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
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
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
        print "Token's client ID does not match app's."
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
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'\
              ' height: 300px;' \
              'border-radius: 150px;'\
              '-webkit-border-radius: 150px;'\
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


 # DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Collection Information
@app.route('/collection/JSON')
def collectionsJSON():
    collections = session.query(Collection).all()
    return jsonify(collections=[c.serialize for c in collections])


@app.route('/collection/<int:collection_id>/items/JSON')
def collectionItemsJSON(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    items = session.query(CollectionItem).filter_by(
        collection_id=collection_id).all()
    return jsonify(CollectionItems=[i.serialize for i in items])


@app.route('/collection/<int:collection_id>/items/<int:item_id>/JSON')
def collectionItemJSON(collection_id, item_id):
    Collection_Item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Collection_Item=Collection_Item.serialize)


# Show all collections
@app.route('/')
@app.route('/collection/')
def showCollections():
    collections = session.query(Collection).all()
    #return "This page will show all my collections"
    return render_template('collections.html', collections=collections)


# Create a new collection
@app.route('/collection/new/', methods=['GET', 'POST'])
def newCollection():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCollection = Collection(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCollection)
        flash('New Collection %s Successfully Created' % newCollection.name)
        session.commit()
        return redirect(url_for('showCollections'))
    else:
        return render_template('newCollection.html')
        #return "This page will be for making a new collection"


# Edit a collection
@app.route('/collection/<int:collection_id>/edit/', methods=['GET', 'POST'])
def editCollection(collection_id):
    editedCollection = session.query(
        Collection).filter_by(id=collection_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCollection.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this collection. Please create your own collection in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCollection.name = request.form['name']
            flash('Collection Successfully Edited %s' % editedCollection.name)
            return redirect(url_for('showCollections'))
    else:
        return render_template('editCollection.html',
                                collection=editedCollection)
        #return 'This page will be for editing collection %s' % collection_id


# Delete a collection
@app.route('/collection/<int:collection_id>/delete/', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    if 'username' not in login_session:
        return redirect('/login')
    collectionToDelete = session.query(
        Collection).filter_by(id=collection_id).one()
    if request.method == 'POST':
        session.delete(collectionToDelete)
        session.commit()
        return redirect(
            url_for('showCollections', collection_id=collection_id))
    else:
        return render_template('deleteCollection.html',
                                collection=collectionToDelete)
        #return 'This page will be for deleting collection %s' % collection_id


# Show collection items
@app.route('/collection/<int:collection_id>/')
@app.route('/collection/<int:collection_id>/items/')
def showItems(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id)
    creator = getUserInfo(collection.user_id)
    items = session.query(CollectionItem).filter_by(
        collection_id=collection_id).all()
    return render_template('collectionItems.html',
                            items=items, collection=collection)
    #return 'This page is the list of items for collection %s' % collection_id


# Create a new collection item
@app.route(
    '/collection/<int:collection_id>/items/new/', methods=['GET', 'POST'])
def newCollectionItem(collection_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    if login_session['user_id'] != collection.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this collection. Please create your own collection in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = CollectionItem(name=request.form['name'],
                                description=request.form['description'],
                                price=request.form['price'],
                                category=request.form['category'],
                                collection_id=collection_id,
                                user_id=collection.user_id)
        session.add(newItem)
        session.commit()

        return redirect(url_for('showItems', collection_id=collection_id))
    else:
        return render_template('newCollectionItem.html', collection=collection)
        #return 'This page is for making a new menu item for collection %s' % collection_id


# Edit a collection item
@app.route('/collection/<int:collection_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCollectionItem(collection_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCollectionItem = session.query(CollectionItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCollectionItem.name = request.form['name']
        if request.form['description']:
            editedCollectionItem.description = request.form['name']
        if request.form['price']:
            editedCollectionItem.price = request.form['price']
        if request.form['category']:
            editedCollectionItem.category = request.form['category']
        session.add(editedCollectionItem)
        session.commit()
        return redirect(url_for('showItems', collection_id=collection_id))
    else:
        return render_template('editCollectionItem.html',
                                collection_id=collection_id,
                                item_id=item_id,
                                item=editedCollectionItem)
        #return 'This page is for editing collection item %s' % item_id


# Delete a collection item
@app.route('/collection/<int:collection_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCollectionItem(collection_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    itemToDelete = session.query(CollectionItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Collection Item Successfully Deleted')
        return redirect(url_for('showItems', collection_id=collection_id))
    else:
        return render_template('deleteCollectionItem.html', item=itemToDelete)
        #return "This page is for deleting collefction item %s" % collection_id


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
