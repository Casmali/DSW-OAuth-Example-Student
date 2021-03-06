from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask import render_template
from flask import flash

import pprint
import os

# This code originally from https://github.com/lepture/flask-oauthlib/blob/master/example/github.py
# Edited by P. Conrad for SPIS 2016 to add getting Client Id and Secret from
# environment variables, so that this will work on Heroku.
# Edited by S. Adams for Designing Software for the Web to add comments and remove flash messaging

app = Flask(__name__)

app.debug = True #Change this to False for production
#use secret key to sign the session
app.secret_key = os.environ['SECRET_KEY'] 

oauth = OAuth(app)

#set github as oath provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github Oath
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'], #your web app's "password" for githuboath
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)


@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')
#redirect to githubs oath page and confirm the callback URL
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='https'))

@app.route('/logout')
def logout():
    session.clear()
    flash("you were logged outa")
    return render_template('home.html')

@app.route('/login/authorized')#the route should match the callback URL registered with the OAuth provider
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token']=(resp['access_token'],'')
            session['user_data']=github.get('user').data
            message="you done did it" + session['user_data']['login']
            flash(message)
            #save user data and set log in message
        except:
            session.clear()
            message='what do ya think you are doin punk'
            
            #clear the session and give error message
    return render_template('home.html')


@app.route('/page1')
def renderPage1():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
    else:
        user_data_pprint = '';
    return render_template('page1.html',dump_user_data=user_data_pprint)

@app.route('/page2')
def renderPage2():
    return render_template('page2.html')

#never have to call this it just automatically is calle dto check how is logged in
@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    app.run()
