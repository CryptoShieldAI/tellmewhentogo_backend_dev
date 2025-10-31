from threading import Thread\nimport os
import json
import time
import hmac
import hashlib
import websocket
import requests


class BybitApi:
    ws_url_main = "wss://stream.bybit.com/v5/public/spot"
    ws_url_test = "wss://stream-testnet.bybit.com/v5/public/spot"
    url_main = "https://api.bybit.com"
    url_test = "https://api-testnet.bybit.com"
    recv_window = str(5000)

    def __init__(
        self,
        market="USD",
        api_key=os.environ.get("BYBIT_API_KEY"),
        secret=os.environ.get("BYBIT_SECRET"),
        test=False,
    ):
        self.api_key = api_key
        self.secret = secret
        self.url = self.url_main if not test else self.url_test
        self.ws_url = self.ws_url_main if not test else self.ws_url_test
        self.market = market
        self.socket_status = False
        self._connect_socket()

    def __del__(self):
        print("destory bybit api")

    def _connect_socket(self):
        self.socket_status = True
        self.ws = websocket.WebSocketApp(
            url=self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )

        self.socket_thread = Thread(target=self.ws.run_forever, daemon=True)
        self.socket_thread.start()

    def close_socket(self):
        self.socket_status = False
        self.ws.close()
        self.ws.on_close = None
        self.ws.on_open = None
        self.ws.on_error = None
        self.ws.on_message = None

    def _on_open(self, open_object):
        expires = int((time.time() + 10) * 1000)
        # Generate signature.
        signature = str(
            hmac.new(
                bytes(self.secret, "utf-8"),
                bytes(f"GET/realtime{expires}", "utf-8"),
                digestmod="sha256",
            ).hexdigest()
        )
        # Authenticate with API.
        self.ws.send(
            json.dumps({"op": "auth", "args": [self.api_key, expires, signature]})
        )

        self.ws.send(
            json.dumps(
                {"op": "subscribe", "args": ["tickers." + str(self.market.symbol)]}
            )
        )

    def _on_close(self, close_status_code, close_msg):
        # print("### about to close please don't close ###")
        if self.socket_status:
            self._connect_socket()
        else:
            pass

    def _on_error(self, error_object, exception_object):
        try:
            time.sleep(5)
            self.ws.close()
        except Exception as e:
            print(e)

    def _on_message(self, message, utf8_received_data):
        message = json.loads(message)
        if "topic" in message:
            # print(message)
            ts = message["ts"]
            lastPrice = message["data"]["lastPrice"]
            self.market.on_ticker(ts, lastPrice)

    def genSignature(self, time_stamp, payload):
        param_str = str(time_stamp) + self.api_key + self.recv_window + payload
        hash = hmac.new(
            bytes(self.secret, "utf-8"), param_str.encode("utf-8"), hashlib.sha256
        )
        signature = hash.hexdigest()
        return signature

    def getKline(self, resolution, _from, to):
        req_params = f"symbol={self.market.symbol}&interval={resolution}"

        if _from != None:
            req_params += f"&from={_from}"

        if to != None:
            req_params += f"&to={to}"

        try:
            time_stamp = str(int(time.time() * 10**3))
            signature = self.genSignature(time_stamp, req_params)
            res = json.loads(
                requests.get(f"{self.url}/v5/market/kline?{req_params}").text
            )
            # res = requests.get(f"{self.url}/v5/market/kline?{req_params}")
            return res
        except Exception as e:
            print(e)
            return []
