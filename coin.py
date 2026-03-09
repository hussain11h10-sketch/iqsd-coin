import hashlib
import random
import time
import secrets
import sqlite3
import os

DB_PATH = '/app/iqsd.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        address TEXT PRIMARY KEY,
        private_key TEXT UNIQUE,
        balance REAL DEFAULT 0,
        staking REAL DEFAULT 0,
        staking_since REAL DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        miner TEXT,
        reward REAL,
        nonce TEXT,
        hash TEXT,
        timestamp REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

class IQSDCoin:
    def __init__(self):
        init_db()
        self.founder_key = "hussain_founder_key_iqsd_2024"
        self.founder_address = "IQSD" + hashlib.sha256(self.founder_key.encode()).hexdigest()[:16].upper()
        self.total_supply = 210278282828200
        self.block_reward = 500
        self.halving_interval = 21000000
        self.staking_rate = 0.05
        self._init_founder()

    def _init_founder(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT address FROM wallets WHERE address=?", (self.founder_address,))
        if not c.fetchone():
            c.execute("INSERT INTO wallets (address, private_key, balance) VALUES (?,?,?)",
                (self.founder_address, self.founder_key, 21000000))
            conn.commit()
        conn.close()

    def _get_setting(self, key, default):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row['value'] if row else default

    def _set_setting(self, key, value):
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, str(value)))
        conn.commit()
        conn.close()

    def get_difficulty(self):
        return int(self._get_setting('difficulty', 2))

    def get_last_hash(self):
        return self._get_setting('last_hash', '0000000000000000')

    def get_mined_supply(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt, SUM(reward) as total FROM blocks")
        row = c.fetchone()
        conn.close()
        return (row['total'] or 0) + 1000000

    def get_block_count(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt FROM blocks")
        row = c.fetchone()
        conn.close()
        return row['cnt']

    def create_wallet(self):
        private_key = secrets.token_hex(32)
        address = "IQSD" + hashlib.sha256(private_key.encode()).hexdigest()[:16].upper()
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO wallets (address, private_key, balance) VALUES (?,?,?)",
            (address, private_key, 0))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "address": address,
            "private_key": private_key,
            "balance": 0,
            "message": "⚠️ احتفظ بمفتاحك الخاص! لو ضيعته ضيعت عملاتك للأبد!"
        }

    def login(self, private_key):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE private_key=?", (private_key,))
        w = c.fetchone()
        conn.close()
        if not w:
            return {"error": "🔐 مفتاح خاطئ!"}
        return {
            "success": True,
            "address": w['address'],
            "balance": w['balance'],
            "staking": w['staking']
        }

    def get_mining_challenge(self):
        difficulty = self.get_difficulty()
        mined = self.get_mined_supply()
        halvings = int(mined // self.halving_interval)
        reward = self.block_reward / (2 ** halvings)
        return {
            "challenge": self.get_last_hash(),
            "difficulty": difficulty,
            "reward": reward,
            "target": "0" * difficulty
        }

    def submit_mining(self, private_key, nonce):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE private_key=?", (private_key,))
        w = c.fetchone()
        if not w:
            conn.close()
            return {"error": "🔐 مفتاح خاطئ!"}
        mined = self.get_mined_supply()
        if mined >= self.total_supply:
            conn.close()
            return {"error": "تم تعدين كل العملات!"}
        last_hash = self.get_last_hash()
        difficulty = self.get_difficulty()
        attempt = f"{last_hash}{nonce}"
        result = hashlib.sha256(attempt.encode()).hexdigest()
        if not result.startswith("0" * difficulty):
            conn.close()
            return {"error": "الحل خاطئ!"}
        halvings = int(mined // self.halving_interval)
        reward = self.block_reward / (2 ** halvings)
        new_balance = w['balance'] + reward
        c.execute("UPDATE wallets SET balance=? WHERE private_key=?", (new_balance, private_key))
        c.execute("INSERT INTO blocks (miner, reward, nonce, hash, timestamp) VALUES (?,?,?,?,?)",
            (w['address'], reward, nonce, result[:16], time.time()))
        block_count = self.get_block_count() + 1
        if block_count % 100 == 0:
            self._set_setting('difficulty', difficulty + 1)
        self._set_setting('last_hash', result[:16])
        conn.commit()
        conn.close()
        return {
            "success": True,
            "message": f"🎉 عدنت {reward} IQSD!",
            "reward": reward,
            "new_balance": new_balance
        }

    def stake(self, private_key, amount):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE private_key=?", (private_key,))
        w = c.fetchone()
        if not w:
            conn.close()
            return {"error": "🔐 مفتاح خاطئ!"}
        if w['balance'] < amount:
            conn.close()
            return {"error": "رصيد غير كافٍ"}
        c.execute("UPDATE wallets SET balance=?, staking=?, staking_since=? WHERE private_key=?",
            (w['balance']-amount, w['staking']+amount, time.time(), private_key))
        conn.commit()
        conn.close()
        daily = round(amount * self.staking_rate / 365, 4)
        return {
            "success": True,
            "message": f"تم إيداع {amount} IQSD",
            "daily_reward": f"{daily} IQSD يومياً"
        }

    def claim_staking(self, private_key):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE private_key=?", (private_key,))
        w = c.fetchone()
        if not w:
            conn.close()
            return {"error": "🔐 مفتاح خاطئ!"}
        if not w['staking'] or not w['staking_since']:
            conn.close()
            return {"error": "لا يوجد ستيكينغ"}
        days = (time.time() - w['staking_since']) / 86400
        reward = round(w['staking'] * self.staking_rate * days / 365, 4)
        c.execute("UPDATE wallets SET balance=?, staking_since=? WHERE private_key=?",
            (w['balance']+reward, time.time(), private_key))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "reward_claimed": reward,
            "new_balance": w['balance']+reward
        }

    def transfer(self, private_key, to_address, amount):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE private_key=?", (private_key,))
        sender = c.fetchone()
        if not sender:
            conn.close()
            return {"error": "🔐 مفتاح خاطئ!"}
        c.execute("SELECT * FROM wallets WHERE address=?", (to_address,))
        receiver = c.fetchone()
        if not receiver:
            conn.close()
            return {"error": "عنوان المستلم غير موجود"}
        if sender['address'] == to_address:
            conn.close()
            return {"error": "لا تقدر تحول لنفسك!"}
        fee = round(amount * 0.001, 4)
        total = amount + fee
        if sender['balance'] < total:
            conn.close()
            return {"error": "رصيد غير كافٍ"}
        c.execute("UPDATE wallets SET balance=? WHERE private_key=?",
            (sender['balance']-total, private_key))
        c.execute("UPDATE wallets SET balance=? WHERE address=?",
            (receiver['balance']+amount, to_address))
        c.execute("UPDATE wallets SET balance=balance+? WHERE address=?",
            (fee, self.founder_address))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "message": f"✅ تم تحويل {amount} IQSD",
            "to": to_address,
            "fee": fee,
            "new_balance": sender['balance']-total
        }

    def get_stats(self):
        mined = self.get_mined_supply()
        blocks = self.get_block_count()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt FROM wallets")
        wallets = c.fetchone()['cnt']
        conn.close()
        return {
            "total_supply": self.total_supply,
            "mined_supply": round(mined),
            "remaining": round(self.total_supply - mined),
            "total_wallets": wallets,
            "total_blocks": blocks,
            "difficulty": self.get_difficulty(),
            "staking_rate": "5% سنوياً",
            "block_reward": self.block_reward
    }
