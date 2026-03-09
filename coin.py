import hashlib
import random
import json
import time

class Wallet:
    def __init__(self, owner_name):
        self.owner = owner_name
        self.address = self.generate_address()
        self.private_key = self.generate_private_key()
        self.balance = 0
        self.staking = 0
        self.staking_since = None
        self.transactions = []

    def generate_address(self):
        data = str(random.randint(100000, 999999)) + self.owner
        return "IQSD" + hashlib.sha256(data.encode()).hexdigest()[:16].upper()

    def generate_private_key(self):
        return hashlib.sha256(str(random.randint(1000000, 9999999)).encode()).hexdigest()

    def verify_key(self, private_key):
        return self.private_key == private_key

    def get_info(self):
        return {
            "owner": self.owner,
            "address": self.address,
            "balance": self.balance,
            "staking": self.staking
        }

class IQSDCoin:
    def __init__(self):
        self.wallets = {}
        self.total_supply = 21000000
        self.mined_supply = 1000000
        self.founder_wallet = None
        self.block_reward = 50
        self.halving_interval = 210000
        self.staking_rate = 0.05
        self.blocks = []

    def init_founder(self, name):
        if self.founder_wallet:
            return {"error": "المؤسس موجود"}
        w = Wallet(name)
        w.balance = 1000000
        self.wallets[name] = w
        self.founder_wallet = name
        return {
            "success": True,
            "message": f"👑 محفظة المؤسس {name}",
            "address": w.address,
            "private_key": w.private_key,
            "balance": 1000000
        }

    def create_wallet(self, name):
        if name in self.wallets:
            return {"error": "المحفظة موجودة مسبقاً"}
        w = Wallet(name)
        self.wallets[name] = w
        return {
            "success": True,
            "owner": name,
            "address": w.address,
            "private_key": w.private_key,
            "message": "احتفظ بمفتاحك الخاص! لا تعطيه لأحد!"
        }

    def mine(self, name, private_key):
        if name not in self.wallets:
            return {"error": "المحفظة غير موجودة"}
        if not self.wallets[name].verify_key(private_key):
            return {"error": "🔐 مفتاح خاطئ!"}
        if self.mined_supply >= self.total_supply:
            return {"error": "تم تعدين كل العملات!"}
        halvings = int(self.mined_supply // self.halving_interval)
        reward = self.block_reward / (2 ** halvings)
        if random.randint(1, 10) > 3:
            self.wallets[name].balance += reward
            self.mined_supply += reward
            block = {
                "index": len(self.blocks),
                "miner": name,
                "reward": reward,
                "timestamp": time.time(),
                "hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
            }
            self.blocks.append(block)
            return {
                "success": True,
                "message": f"🎉 عدنت {reward} IQSD!",
                "reward": reward,
                "new_balance": self.wallets[name].balance
            }
        return {"success": False, "message": "لم تنجح، حاول مرة أخرى!"}

    def stake(self, name, private_key, amount):
        if name not in self.wallets:
            return {"error": "المحفظة غير موجودة"}
        if not self.wallets[name].verify_key(private_key):
            return {"error": "🔐 مفتاح خاطئ!"}
        w = self.wallets[name]
        if w.balance < amount:
            return {"error": "رصيد غير كافٍ"}
        w.balance -= amount
        w.staking += amount
        w.staking_since = time.time()
        daily = round(amount * self.staking_rate / 365, 4)
        return {
            "success": True,
            "message": f"تم إيداع {amount} IQSD",
            "daily_reward": f"{daily} IQSD يومياً"
        }

    def claim_staking(self, name, private_key):
        if name not in self.wallets:
            return {"error": "المحفظة غير موجودة"}
        if not self.wallets[name].verify_key(private_key):
            return {"error": "🔐 مفتاح خاطئ!"}
        w = self.wallets[name]
        if not w.staking or not w.staking_since:
            return {"error": "لا يوجد ستيكينغ"}
        days = (time.time() - w.staking_since) / 86400
        reward = round(w.staking * self.staking_rate * days / 365, 4)
        w.balance += reward
        w.staking_since = time.time()
        return {
            "success": True,
            "reward_claimed": reward,
            "new_balance": w.balance
        }

    def transfer(self, sender, private_key, receiver, amount):
        if sender not in self.wallets:
            return {"error": "محفظة المرسل غير موجودة"}
        if not self.wallets[sender].verify_key(private_key):
            return {"error": "🔐 مفتاح خاطئ!"}
        if receiver not in self.wallets:
            return {"error": "محفظة المستلم غير موجودة"}
        fee = round(amount * 0.001, 4)
        total = amount + fee
        if self.wallets[sender].balance < total:
            return {"error": "رصيد غير كافٍ"}
        self.wallets[sender].balance -= total
        self.wallets[receiver].balance += amount
        if self.founder_wallet:
            self.wallets[self.founder_wallet].balance += fee
        return {
            "success": True,
            "message": f"تم تحويل {amount} IQSD",
            "fee": fee,
            "sender_balance": self.wallets[sender].balance
        }

    def get_stats(self):
        return {
            "total_supply": self.total_supply,
            "mined_supply": self.mined_supply,
            "remaining": self.total_supply - self.mined_supply,
            "total_wallets": len(self.wallets),
            "total_blocks": len(self.blocks),
            "staking_rate": "5% سنوياً",
            "block_reward": self.block_reward
        }
