request, jsonify, send_from_directory
from coin import IQSDCoin

app = Flask(__name__)
coin = IQSDCoin()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/stats')
def stats():
    return jsonify(coin.get_stats())

@app.route('/wallet/create', methods=['POST'])
def create_wallet():
    return jsonify(coin.create_wallet())

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'private_key' not in data:
        return jsonify({"error": "أرسل المفتاح"})
    return jsonify(coin.login(data['private_key']))

@app.route('/mine', methods=['POST'])
def mine():
    data = request.json
    if not data or 'private_key' not in data:
        return jsonify({"error": "أرسل المفتاح"})
    return jsonify(coin.mine(data['private_key']))

@app.route('/stake', methods=['POST'])
def stake():
    data = request.json
    if not data or 'private_key' not in data or 'amount' not in data:
        return jsonify({"error": "أرسل البيانات"})
    return jsonify(coin.stake(data['private_key'], data['amount']))

@app.route('/stake/claim', methods=['POST'])
def claim():
    data = request.json
    if not data or 'private_key' not in data:
        return jsonify({"error": "أرسل المفتاح"})
    return jsonify(coin.claim_staking(data['private_key']))

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    if not data or 'private_key' not in data or 'to_address' not in data or 'amount' not in data:
        return jsonify({"error": "أرسل البيانات كاملة"})
    return jsonify(coin.transfer(data['private_key'], data['to_address'], data['amount']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
