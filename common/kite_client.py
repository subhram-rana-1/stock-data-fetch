from kiteconnect import KiteConnect, KiteTicker

from common import configs


def new_kite_connect_instance() -> KiteConnect:
    kc: KiteConnect = KiteConnect(
        api_key=configs.API_KEY,
    )

    print("Please login with here and fetch the 'request_token' from redirected "
          "url after successful login : ", kc.login_url())

    request_token: str = input("enter 'request_token': ")

    session_data: dict = kc.generate_session(
        request_token=request_token,
        api_secret=configs.API_SECRETE,
    )

    configs.ACCESS_TOKEN = session_data['access_token']
    kc.set_access_token(configs.ACCESS_TOKEN)

    print('\nkite connect client creation successful !!! ')

    return kc


# call KiteConnectClient() to get the singleton instance
class KiteConnectClient:
    _instance: KiteConnect = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = new_kite_connect_instance()

        return cls._instance


def new_kite_websocket_client(market: str) -> KiteTicker:
    if configs.ACCESS_TOKEN is None:
        err_msg = ('access_token is not initialised. Please connect to kite connect first with'
                   ' "get_kite_connect_client()" function, and then try to create websocket client')

        raise Exception(err_msg)

    kws: KiteTicker = KiteTicker(
        api_key=configs.API_KEY,
        access_token=configs.ACCESS_TOKEN,
    )

    print(f'\n [{market}]: kite websocket client creation successful !!!')

    return kws

