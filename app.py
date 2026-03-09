from flask import Flask, request, jsonify, send_from_directory
from coin import IQSDCoin

app = Flask(__name__)
coin = IQSDCoin()
coin.init_founder("hussain")

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/stats')
def stats():
    return jsonify(coin.get_stats())

@app.route('/wallet/create', methods=['POST'])
def create_wallet():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "أرسل الاسم"})
    return jsonify(coin.create_wallet(data['name']))

@app.route('/wallet/<name>')
def get_wallet(name):
    if name not in coin.wallets:
        return jsonify({"error": "المحفظة غير موجودة"})
    return jsonify(coin.wallets[name].get_info())

@app.route('/mine', methods=['POST'])
def mine():
    data = request.json
    if not data or 'name' not in data or 'private_key' not in data:
        return jsonify({"error": "أرسل الاسم والمفتاح"})
    return jsonify(coin.mine(data['name'], data['private_key']))

@app.route('/stake', methods=['POST'])
def stake():
    data = request.json
    if not data or 'name' not in data or 'private_key' not in data or 'amount' not in data:
        return jsonify({"error": "أرسل البيانات كاملة"})
    return jsonify(coin.stake(data['name'], data['private_key'], data['amount']))

@app.route('/stake/claim', methods=['POST'])
def claim():
    data = request.json
    if not data or 'name' not in data or 'private_key' not in data:
        return jsonify({"error": "أرسل الاسم والمفتاح"})
    return jsonify(coin.claim_staking(data['name'], data['private_key']))

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    if not data:
        return jsonify({"error": "أرسل البيانات"})
    return jsonify(coin.transfer(data['from'], data['private_key'], data['to'], data['amount']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
