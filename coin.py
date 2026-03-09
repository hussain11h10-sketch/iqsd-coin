import hashlib
import random
import time
import secrets

class Wallet:
    def __init__(self):
        self.private_key = self.generate_private_key()
        self.address = self.generate_address()
        self.balance = 0
        self.staking = 0
        self.staking_since = None

    def generate_private_key(self):
        return secrets.token_hex(32)

    def generate_address(self):
        return "IQSD" + hashlib.sha256(self.private_key.encode()).hexdigest()[:16].upper()

    def verify_key(self, private_key):
        return self.private_key == private_key

    def get_info(self):
        return {
            "address": self.address,
            "balance": self.balance,
            "staking": self.staking
        }

class IQSDCoin:
    def __init__(self):
        self.wallets = {}
        self.total_supply = 21000000
        self.mined_supply = 1000000
        self.block_reward = 50
        self.halving_interval = 210000
        self.staking_rate = 0.05
        self.blocks = []
        self.difficulty = 4
        self.last_block_hash = "0000000000000000"
        self.founder_address = None
        self._init_founder()

    def _init_founder(self):
        w = Wallet()
        w.private_key = "hussain_founder_key_iqsd_2024"
        w.address = "IQSD" + hashlib.sha256(w.private_key.encode()).hexdigest()[:16].upper()
        w.balance = 1000000
        self.wallets[w.address] = w
        self.founder_address = w.address

    def create_wallet(self):
        w = Wallet()
        self.wallets[w.address] = w
        return {
            "success": True,
            "address": w.address,
            "private_key": w.private_key,
            "balance": 0,
            "message": "⚠️ احتفظ بمفتاحك الخاص! لو ضيعته ضيعت عملاتك للأبد!"
        }

    def login(self, private_key):
        for w in self.wallets.values():
            if w.verify_key(private_key):
                return {
                    "success": True,
                    "address": w.address,
                    "balance": w.balance,
                    "staking": w.staking
                }
        return {"error": "🔐 مفتاح خاطئ!"}

    def get_wallet_by_key(self, private_key):
        for w in self.wallets.values():
            if w.verify_key(private_key):
                return w
        return None

    def get_wallet_by_address(self, address):
        return self.wallets.get(address, None)

    def get_mining_challenge(self):
        halvings = int(self.mined_supply // self.halving_interval)
        reward = self.block_reward / (2 ** halvings)
        return {
            "challenge": self.last_block_hash,
            "difficulty": self.difficulty,
            "reward": reward,
            "target": "0" * self.difficulty
        }

    def submit_mining(self, private_key, nonce):
        w = self.get_wallet_by_key(private_key)
        if not w:
            return {"error": "🔐 مفتاح خاطئ!"}
        if self.mined_supply >= self.total_supply:
            return {"error": "تم تعدين كل العملات!"}
        attempt = f"{self.last_block_hash}{nonce}"
        result = hashlib.sha256(attempt.encode()).hexdigest()
        target = "0" * self.difficulty
        if not result.startswith(target):
            return {"error": "الحل خاطئ! حاول مرة أخرى"}
        halvings = int(self.mined_supply // self.halving_interval)
        reward = self.block_reward / (2 ** halvings)
        w.balance += reward
        self.mined_supply += reward
        self.last_block_hash = result[:16]
        block = {
            "index": len(self.blocks),
            "miner": w.address,
            "nonce": nonce,
            "hash": result[:16],
            "reward": reward,
            "timestamp": time.time()
        }
        self.blocks.append(block)
        if len(self.blocks) % 10 == 0:
            self.difficulty += 1
        return {
            "success": True,
            "message": f"🎉 عدنت {reward} IQSD!",
            "reward": reward,
            "new_balance": w.balance,
            "block": len(self.blocks)
        }

    def stake(self, private_key, amount):
        w = self.get_wallet_by_key(private_key)
        if not w:
            return {"error": "🔐 مفتاح خاطئ!"}
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

    def claim_staking(self, private_key):
        w = self.get_wallet_by_key(private_key)
        if not w:
            return {"error": "🔐 مفتاح خاطئ!"}
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

    def transfer(self, private_key, to_address, amount):
        sender = self.get_wallet_by_key(private_key)
        if not sender:
            return {"error": "🔐 مفتاح خاطئ!"}
        receiver = self.get_wallet_by_address(to_address)
        if not receiver:
            return {"error": "عنوان المستلم غير موجود"}
        if sender.address == to_address:
            return {"error": "لا تقدر تحول لنفسك!"}
        fee = round(amount * 0.001, 4)
        total = amount + fee
        if sender.balance < total:
            return {"error": "رصيد غير كافٍ"}
        sender.balance -= total
        receiver.balance += amount
        if self.founder_address:
            self.wallets[self.founder_address].balance += fee
        return {
            "success": True,
            "message": f"✅ تم تحويل {amount} IQSD",
            "to": to_address,
            "fee": fee,
            "new_balance": sender.balance
        }

    def get_stats(self):
        return {
            "total_supply": self.total_supply,
            "mined_supply": self.mined_supply,
            "remaining": self.total_supply - self.mined_supply,
            "total_wallets": len(self.wallets),
            "total_blocks": len(self.blocks),
            "difficulty": self.difficulty,
            "staking_rate": "5% سنوياً",
            "block_reward": self.block_reward
        }
