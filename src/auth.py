from flask import Flask, redirect, request, session, url_for
from linked_roles import LinkedRolesOAuth2, RoleConnection
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY')

client = LinkedRolesOAuth2(
    client_id = os.environ.get('DISCORD_CLIENT_ID'),
    client_secret = os.environ.get('DISCORD_CLIENT_SECRET'),
    redirect_uri = os.environ.get('DISCORD_REDIRECT_URI'),
    scopes=('role_connections.write', 'identify'),
)

oauth = OAuth(app)
oauth.register(
    'keycloak',
    client_id=os.environ.get('KEYCLOAK_CLIENT_ID'),
    client_secret=os.environ.get('KEYCLOAK_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=os.environ.get('KEYCLOAK_OPENID_CONFIG_URL')
)

@app.route('/linked-role')
async def linked_role():
    url = client.get_oauth_url()
    return redirect(location=url)

@app.route('/discord-oauth-callback')
async def discord_oauth_callback():
    code = request.args.get('code')
    print(code)
    await client.start()
    token = await client.get_access_token(code)
    user = await client.fetch_user(token)
    if user is None:
        raise ValueError

    role = await user.fetch_role_connection()
    if role is None:
        # set role connection
        role = RoleConnection(platform_name='BostonDSA', platform_username=str(user))

        # set role metadata
        await user.edit_role_connection(role)

    return 'Role metadata set successfully. Please check your Discord profile.'

@app.route('/test')
async def test():
    print('Redirecting')
    return oauth.keycloak.authorize_redirect(
        redirect_uri=os.environ.get('KEYCLOAK_REDIRECT_URI'), _external=True)

@app.route('/keycloak-callback')
def keycloak_callback():
    token = oauth.keycloak.authorize_access_token()
    print('Token: ')
    print(token)

    return 'Keycloaked'
