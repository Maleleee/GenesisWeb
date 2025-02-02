import requests
from flask import Flask, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = ##

# OAuth configuration for GitHub
CLIENT_ID = ##
CLIENT_SECRET = ##
REDIRECT_URI = 'http://localhost:5000/oauth_callback'
AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
SCOPE = 'user:email'

@app.route('/login')
def login():
    auth_url = f'{AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type=code'
    return redirect(auth_url)

@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data, headers={'Accept': 'application/json'})
    access_token = response.json().get('access_token')
    # Use the access token to make requests to protected resources
    # Store the access token in the session or database for future use
    return 'OAuth successful!'

if __name__ == '__main__':
    app.run(debug=True)
