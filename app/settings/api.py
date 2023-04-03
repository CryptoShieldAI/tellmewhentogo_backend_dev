from flask import jsonify, request
from app import marketManager
import json
from . import settings

@settings.route('/')
def getSettings():
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

@settings.route('/cycle-duration', methods=['POST'])
def setCycleDuration():
    data = json.loads(request.data)
    marketManager.setCycleDuration(data.get('duration'))
    return jsonify({'result': 'success'}), 200

@settings.route('/repeat-count', methods=['POST'])
def setRepeatingCount():
    data = json.loads(request.data)
    marketManager.setRepeatingCount(data['count'])
    return jsonify({'result': 'success'})

@settings.route('/repeat-break', methods=['POST'])
def setRepeatingBreak():
    data = json.loads(request.data)
    marketManager.setRepeatingBreak(data['breakCount'])
    return jsonify({'result': 'success'})

@settings.route('/level', methods=['POST'])
def setRankLevel():
    data = json.loads(request.data)
    marketManager.setRankLevel(data['levelCount'])
    return jsonify({'result': 'success'})

@settings.route('/level/percent', methods=['POST'])
def setLevelPercent():
    data = json.loads(request.data)
    marketManager.setLevelPercent(data['level'], data['percent'])
    return jsonify({'result': 'success'})

@settings.route('/cryptos', methods=['POST'])
def setCryptoList():
    data = json.loads(request.data)
    marketManager.setSymbolList(data['cryptoList'])
    return jsonify({'result': 'success'})