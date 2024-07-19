from flask import Flask, redirect, request, render_template_string
import requests
import base64
import urllib.parse

app = Flask(__name__)

# Spotify API credentials
spotify_client_id = 'SPOTIFY_CLIENT_ID'          # Api key taken from spotify dashboard
spotify_client_secret = 'SPOTIFY_CLIENT_SECRET'  # Client secret taken from spotify dashboard
callback_uri = 'http://localhost:5000/callback'  # Redirect URI for the Flask app

# HTML templates with Bootstrap and custom CSS
index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Follow Checker</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .container {
            max-width: 600px;
        }
        .form-control, .btn-primary {
            border-radius: 0.25rem;
        }
        .spotify-green {
            color: #1DB954; /* Spotify Green */
        }
        .btn-spotify {
            background-color: #1DB954;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h2 class="text-center spotify-green">Spotify Follow Checker</h2>
        <form action="/check_follow" method="post" class="mt-4">
            <input type="hidden" name="access_token" value="{{ access_token }}">
            <div class="form-group">
                <label for="user_id" class="spotify-green">Your Spotify User ID:</label>
                <input type="text" id="user_id" name="user_id" class="form-control" placeholder="Enter your Spotify User ID" required>
            </div>
            <div class="form-group">
                <label for="target_user_id" class="spotify-green">Target Spotify User ID:</label>
                <input type="text" id="target_user_id" name="target_user_id" class="form-control" placeholder="Enter target Spotify User ID" required>
            </div>
            <button type="submit" class="btn btn-spotify btn-block">Check Follow Status</button>
        </form>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''

result_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Follow Status</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .container {
            max-width: 600px;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
        }
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
        .spotify-green {
            color: #1DB954; /* Spotify Green */
        }
        .btn-check {
            background-color: #1DB954;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h2 class="text-center spotify-green">Follow Status</h2>
        <div class="alert alert-{{ 'success' if is_following else 'danger' }} mt-4">
            <h4 class="alert-heading spotify-green">Result:</h4>
            <p class="spotify-green">{{ 'True' if is_following else 'False' }}</p>
        </div>
        <a href="/" class="btn btn-check btn-block">Check Another</a>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''

# Redirect to Spotify authorization URL
@app.route('/')
def home():
    scope = 'user-follow-read'
    authorization_url = (
        'https://accounts.spotify.com/authorize'
        f'?response_type=code&client_id={spotify_client_id}'
        f'&redirect_uri={urllib.parse.quote(callback_uri)}'
        f'&scope={scope}'
    )
    return redirect(authorization_url)

# Get the authorization code and exchange it for an access token
@app.route('/callback')
def handle_callback():
    auth_code = request.args.get('code')
    token = exchange_code_for_token(auth_code)
    return render_template_string(index_html, access_token=token)

# Check follow status and display the result
@app.route('/check_follow', methods=['POST'])
def verify_follow_status():
    access_token = request.form['access_token']
    target_user_id = request.form['target_user_id']
    following_status = is_user_following(access_token, target_user_id)
    return render_template_string(result_html, is_following=following_status)

def exchange_code_for_token(auth_code):
    token_endpoint = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': callback_uri
    }
    response = requests.post(token_endpoint, headers=headers, data=payload)
    return response.json().get('access_token')

def is_user_following(access_token, target_user_id):
    api_endpoint = 'https://api.spotify.com/v1/me/following/contains'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'type': 'user',
        'ids': target_user_id
    }
    response = requests.get(api_endpoint, headers=headers, params=params)
    return response.json()[0]

if __name__ == '__main__':
    app.run(debug=True)
