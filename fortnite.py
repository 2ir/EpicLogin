from base64 import b64encode
from aiohttp import ClientSession

switch_client = b64encode(('98f7e42c2e3a4f86a74eb43fbb41ed39' + ':' + '0a2449a2-001a-451e-afec-3e812901c4d7').encode()).decode()


async def generate_auth() -> tuple[str, str]:
    http = ClientSession()
    http.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    payload = {
        'grant_type': 'client_credentials',
    }

    basic_access = await http.post(
        'https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token',
        headers = {
            'Authorization': f'Basic {switch_client}'
        },
        data = payload
    )

    access_token = (await basic_access.json())['access_token']
    device_auth = await http.post(
        'https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization',
        headers = {
            'Authorization': f'Bearer {access_token}'
        },
        data = payload
    )

    resp = await device_auth.json()
    print(resp)
    user_code, device_code = resp['user_code'], resp['device_code']

    await http.close()
    return user_code, device_code


async def get_account_infos(token: str, id: str) -> dict:
    http = ClientSession()

    resp = await http.get(
        f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{id}',
        headers = {
            'Authorization': f'Bearer {token}'
        }
    )
    infos = await resp.json()

    await http.close()
    return infos


async def authentificate(device_code: str) -> dict:
    http = ClientSession()

    resp = await http.post(
        'https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token',
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {switch_client}'
        },
        data = {
            'grant_type': 'device_code',
            'device_code': device_code
        }
    )

    data = await resp.json()
    token = data['access_token']
    id = data['account_id']

    infos = await http.post(
        f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{id}/deviceAuth',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )

    infos = await infos.json()
    await http.close()

    return {
        'device-id': infos['deviceId'],
        'account-id': id,
        'secret': infos['secret'],
        'access-token': data['access_token'],
        'refresh-token': data['refresh_token'],
    }