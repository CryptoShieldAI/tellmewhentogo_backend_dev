from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import threading
import time
from MarketManager import MarketManager
from Database import Database
from datetime import timedelta, datetime, timezone
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
                        unset_jwt_cookies, jwt_required, JWTManager
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = "WhenToGo"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

db = Database()
# symbolList = 'BTC, ETH, GMT, OP, LUNA2, WAVES, GAL, APE, RUNE, AVAX, ETC, ZIL, SAND, JASMY, OGN, ADA, SHIB1000, XRP, MANA, LINK, BIT, DOT, DOGE, BNB, SFP, UNI, CRO, ATOM, NEAR, FIL, LTC, MATIC, ALGO, BCH, ICP, XLM, VET, AXS, TRX, XTZ, THETA, HBAR, EGLD, EOS, ZEN, AAVE, FLOW, FTM, GALA, REQ, KSM, IMX, OMG, SC, IOTX, BAT, DASH, COMP, ONE, CHZ, LRC, STX, ZEC, ENJ, XEM, SUSHI, ANKR, GRT, REN, DYDX, RSR, CRV, IOST,CELR, 1INCH, STORJ, AUDIO, COTI, CHR, CVC, WOO, ALICE, ENS, C98, YGG, ILV, RNDR, MASK, TLM, SLP, GTC, LIT, CTK, BICO, YFI, STMX, SXP, BSV, KLAY, QTUM, SNX, LPT, SPELL, ANT, DUSK, AR, PEOPLE, IOTA, CELO, TVN, KNC, KAVA, DENT, XMR, ROSE, CREAM, LOOKS, HNT, 10000NFT, NEO, CKB, MKR, REEF, BAND, RSS3, DGB, OCEAN, 10000BTT, SUN, JST, API3, KDA, PAXG, SKL, BSW, CTSI, HOT, ZRX, ALPHA, GLMR, SCRT, BAKE, ASTR, FXS, MINA, BNX, BOBA, ACH, BAL, 1000XEC, ICX, MTL, LINA, ARPA, CVX, DODO, AGLD, TOMO, XCN, DAR, FLM, FITFI, CTC,AKRO, UNFI, BLZ, ONT, USDC, TRB, BEL, CEEK, LDO, INJ, STG, XNO, 1000LUNC, ETHW, GMX, APT, SWEAT, SOL, TWT, MAGIC, 1000BONK, FET, CORE, AGIX, GFT'
# symbols = symbolList.split(",")


marketManager = MarketManager(db)
# for symbol in symbols:
    # marketManager.addMarket(symbol.strip() + 'USDT')


@app.route('/')
def hello():
    return jsonify(
        message='success'
    )

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/login', methods=["POST"])
def create_token():
    data = json.loads(request.data)
    email = data.get("email", None)
    password = data.get("password", None)
    if email != 'test@gmail.com' or password !='test':
        return {'msg', "Wrong email or password"}, 401
    
    access_token = create_access_token(identity=email)
    response = {"access_token": access_token}
    return jsonify(response)

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg":"logout successful"})
    unset_jwt_cookies(response)
    return response
    

@app.route('/pump/<period>')
def getPump(period):
    pumpList = db.getPumpList(period)
    pumpList = list(map(lambda market: {
        'symbol': market[0],
        'spot': marketManager.getSpot(market[0]),
        'count': 0 if market[1] is None else market[1]
    }, pumpList))
    return jsonify(pumpList)

@app.route('/dump/<period>')
def getDump(period):
    dumpList = db.getDumpList(period)
    dumpList = list(map(lambda market: {
        'symbol': market[0],
        'spot': marketManager.getSpot(market[0]),
        'count': 0 if market[1] is None else market[1]
    }, dumpList))
    return jsonify(dumpList)

@app.route('/current/signals')
def getCurrentSingals():
    currentSignals = marketManager.getCurrentSignals()
    return jsonify(currentSignals)

@app.route('/setting')
def getSetting():
    return jsonify(
        {
            'cycleDuration': marketManager.cycle_duration, 
            'repeatingCount': marketManager.repeating_count,
            'repeatingBreak': marketManager.repeating_break,
            'rankLevel': marketManager.rank_level,
            'levelPercents': marketManager.level_percents,
            'symbolList': marketManager.getSymbolList()
        }
    )

@app.route('/setting/cycle-duration', methods=['POST'])
def setCycleDuration():
    data = json.loads(request.data)
    marketManager.setCycleDuration(data['duration'])
    return jsonify({'result': 'success'})

@app.route('/setting/repeat-count', methods=['POST'])
def setRepeatingCount():
    data = json.loads(request.data)
    marketManager.setRepeatingCount(data['count'])
    return jsonify({'result': 'success'})

@app.route('/setting/repeat-break', methods=['POST'])
def setRepeatingBreak():
    data = json.loads(request.data)
    marketManager.setRepeatingBreak(data['breakCount'])
    return jsonify({'result': 'success'})

@app.route('/setting/level', methods=['POST'])
def setRankLevel():
    data = json.loads(request.data)
    marketManager.setRankLevel(data['levelCount'])
    return jsonify({'result': 'success'})

@app.route('/setting/level/percent', methods=['POST'])
def setLevelPercent():
    data = json.loads(request.data)
    marketManager.setLevelPercent(data['level'], data['percent'])
    return jsonify({'result': 'success'})

@app.route('/setting/cryptos', methods=['POST'])
def setCryptoList():
    data = json.loads(request.data)
    marketManager.setSymbolList(data['cryptoList'])
    return jsonify({'result': 'success'})

@app.route('/market/<symbol>')
def getMarketHistory(symbol):
    resolution = request.args.get('resolution')
    _from = request.args.get('from')
    to = request.args.get('to')
    limit = request.args.get('limit')
    data = marketManager.getMarketHistory(symbol, resolution, _from, to)
    return jsonify(data)


def startApi():
    app.run()


if __name__ == "__main__":    
    threading.Thread(target=startApi, daemon=True).start()
    
    while True:
        time.sleep(1)
