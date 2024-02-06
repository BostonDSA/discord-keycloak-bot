import asyncio
from flask import Flask, redirect, request
from linked_roles import LinkedRolesOAuth2, RoleConnection
import os

app = Flask(__name__)

client = LinkedRolesOAuth2(
    client_id = os.environ.get('DISCORD_CLIENT_ID'),
    client_secret = os.environ.get('DISCORD_CLIENT_ID'),
    redirect_uri = os.environ.get('REDIRECT_URI'),
    scopes=('role_connections.write', 'identify'),
)

asyncio.run(client.start())

@app.route("/linked-role")
async def linked_role():
    url = client.get_oauth_url()
    return redirect(location=url)

@app.route("/discord-oauth-callback")
async def discord_oauth_callback():
    code = request.args.get('code')
    print(code)
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

