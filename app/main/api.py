from flask import jsonify, request
from app.models import Signal
from app.models import Market
import time
from app import db, marketManager
from . import main

@main.route('/')
def index():
    responseObject = {
            'message': 'running...'
        }
    return jsonify(responseObject), 200 

@main.route('/pump/<period>')
def getPump(period):
    currentTime = time.time()
    startTime = currentTime - (24 * 3600 if period == 'day' else 24 * 3600 * 7)
    # startTime = int(startTime * 1000)

    subq = db.select(Signal.symbol, db.func.count(Signal.symbol).label("count")).filter_by(
            type = 'pump', 
            ).filter(Signal.start_time >= startTime).group_by(Signal.symbol).subquery()
    
    # stmt = db.select(Market, subq.c.count).join(subq, Market.symbol == subq.c.symbol)
    stmt = db.select(Market.symbol, subq.c.count).join(subq, Market.symbol==subq.c.symbol, isouter=True).order_by(
        subq.c.count.desc()
    ).limit(10)
    
    pumpList = db.session.execute(
        stmt
    ).all()
    

    pumpList = list(map(lambda market: {
        'symbol': market.symbol, 
        'spot': marketManager.getSpot(market.symbol),
        'count': 0 if market.count is None else market.count
    }, pumpList))

    return jsonify(pumpList), 200

@main.route('/dump/<period>')
def getDump(period):
    currentTime = time.time()
    startTime = currentTime - (24 * 3600 if period == 'day' else 24 * 3600 * 7)
    # startTime = int(startTime * 1000)

    subq = db.select(Signal.symbol, db.func.count(Signal.symbol).label("count")).filter_by(
            type = 'dump', 
            ).filter(Signal.start_time >= startTime).group_by(Signal.symbol).subquery()
    
    # stmt = db.select(Market, subq.c.count).join(subq, Market.symbol == subq.c.symbol)
    stmt = db.select(Market.symbol, subq.c.count).join(subq, Market.symbol==subq.c.symbol, isouter=True).order_by(
        subq.c.count.desc()
    ).limit(10)
    
    dumpList = db.session.execute(
        stmt
    ).all()
    

    dumpList = list(map(lambda market: {
        'symbol': market.symbol, 
        'spot': marketManager.getSpot(market.symbol),
        'count': 0 if market.count is None else market.count
    }, dumpList))

    return jsonify(dumpList), 200
    
@main.route('/current/signals')
def getCurrentSignals():
    currentSignals = marketManager.getCurrentSignals()
    return jsonify(currentSignals), 200

@main.route('/market/<symbol>')
def getMarketHistory(symbol):
    resolution = request.args.get('resolution')
    _from = request.args.get('from')
    to = request.args.get('to')
    limit = request.args.get('limit')
    data = marketManager.getMarketHistory(symbol, resolution, _from, to)
    return jsonify(data)