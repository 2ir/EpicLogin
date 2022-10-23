from threading import Thread
from time import sleep
from flask import Flask, request, render_template, redirect, send_file
from random import choices
import fortnite
from asyncio import get_event_loop
from json import dumps, loads, JSONDecodeError
from string import digits, ascii_letters
from rich import print_json

loop = get_event_loop()
run = loop.run_until_complete
app = Flask(__name__, template_folder = '.')
db = {
    'clients': {},
    'auths': {}
}


@app.route('/')
def index():
    token = request.args.get('token')
    infos: dict = db['clients'].get(token)

    if infos is None:
        return redirect('/login')

    text = open('index.html', 'r', encoding = 'utf-8').read()
    for key, value in infos.items():
        text = text.replace(r'{{ epic:%s }}' % key, value)
    return text


@app.route('/login')
def page_login():
    return render_template('login.html')


@app.route('/api/create-auth', methods = ['POST'])
def create_auth():
    user_code, device_code = run(fortnite.generate_auth())
    url = 'https://epicgames.com/id/activate?userCode=' + user_code

    auth_id = ''
    while auth_id in db['auths'].keys() or not auth_id:
        auth_id = ''.join(choices(digits, k = 10))

    db['auths'][auth_id] = device_code

    return dumps({
        'url': url,
        'auth-id': auth_id
    })


@app.route('/api/epic-authentificate', methods = ['POST'])
def epic_auth():
    try:
        data = loads(request.data)
    except JSONDecodeError:
        return '', 400

    auth_id: str = data.get('auth-id')
    device_code: str = db['auths'].get(auth_id)

    if device_code is None:
        return '', 400

    auth_data = run(fortnite.authentificate(device_code))

    token = ''
    while token in db['clients'].keys() or not token:
        token = ''.join(choices(ascii_letters, k = 15))

    infos = run(fortnite.get_account_infos(
        auth_data['access-token'],
        auth_data['account-id']
    ))

    print_json(dumps(infos, indent = 4))
    db['clients'][token] = {
        'id': auth_data['account-id'],
        'display-name': infos['displayName'],
        'email': infos['email'],
        # 'language': infos['preferredLanguage'],
        # 'tfa': infos['tfaEnabled'],
        # 'verified': infos['emailVerified'],
        'token': auth_data['access-token']
    }
    return token, 200


@app.route('/asset/<asset>')
def get_asset(asset: str):
    return send_file(asset)


def update_db() -> None:
    global db

    with open('db.json', 'r', encoding = 'utf-8') as f:
        db_init = f.read()

    db_file = open('db.json', 'a+', encoding = 'utf-8')

    try:
        db_ = loads(db_init)
    except JSONDecodeError:
        pass

    if all(key in db_ for key in ['clients', 'auths']):
        db = db_

    def update():
        db_file.truncate(0)
        db_file.write(dumps(db, indent = 4))
        db_file.flush()

    while True:
        update()
        sleep(2)


Thread(target = update_db).start()
app.run('0.0.0.0', 80)