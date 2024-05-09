import requests
from flask import Flask, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = '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'

# OAuth configuration
CLIENT_ID = '992785662567-oeltunnotl5ft2432u206iv9c980emj2.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/oauth_callback'
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
SCOPE = 'email profile'

@app.route('/login')
def login():
    auth_url = f'{AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type=code'
    return redirect(auth_url)

@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    access_token = response.json().get('access_token')
    # Use the access token to make requests to protected resources
    # Store the access token in the session or database for future use
    return 'OAuth successful!'

if __name__ == '__main__':
    app.run(debug=True)
