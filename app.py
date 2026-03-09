from flask import Flask, request, jsonify
from coin import IQSDCoin

app = Flask(__name__)
coin = IQSDCoin()

# تهيئة محفظة المؤسس
coin.init_founder("hussain")

@app.route('/')
def home():
    return jsonify({
        "name": "IQSD Coin",
        "message": "عملة IQSD العربية تعمل!",
        "version": "1.0",
        "stats": coin.get_stats()
    })

@app.route('/founder')
def founder():
    if coin.founder_wallet:
        return jsonify(coin.wallets[coin.founder_wallet].get_info())
    return jsonify({"error": "لا يوجد مؤسس"})

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
    if not data or 'name' not in data:
        return jsonify({"error": "أرسل الاسم"})
    return jsonify(coin.mine(data['name']))

@app.route('/stake', methods=['POST'])
def stake():
    data = request.json
    if not data or 'name' not in data or 'amount' not in data:
        return jsonify({"error": "أرسل الاسم والمبلغ"})
    return jsonify(coin.stake(data['name'], data['amount']))

@app.route('/stake/claim', methods=['POST'])
def claim():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "أرسل الاسم"})
    return jsonify(coin.claim_staking(data['name']))

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    if not data:
        return jsonify({"error": "أرسل البيانات"})
    return jsonify(coin.transfer(data['from'], data['to'], data['amount']))

@app.route('/stats')
def stats():
    return jsonify(coin.get_stats())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
