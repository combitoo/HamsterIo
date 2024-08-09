import json
import random
import requests
import time
import math 


def pretty(number: int) -> str:
    return "{:,d}".format(math.floor(number)).replace(",", ".")


class HamsterIO:
    def __init__(
            self, 
            logs,
            base_url: str = "", 
            token: str = "", 
            work: bool = False,
        ):
        self.logs = logs
        self.base_url: str = base_url
        self.token: str = token
        self.balance: float = 0
        self.per_hour: float = 0
        self.work: bool = work
    
    def set_token(self, token):
        self.token = token
    
    def set_work(self, work):
        self.work = work
    
    def buy_best_upgrade(self, best_upgrades):
        if not self.work:
            return
        self.logs(message="※ Buying best upgrade...")
        for upgrade in best_upgrades:
            if upgrade["_meta"]["price"] > self.balance:
                continue
            time.sleep(random.randint(3, 5))
            request = self._make_request(
                link='/clicker/buy-upgrade',
                data={
                    "upgradeId": upgrade['id'],
                    "timestamp": int(time.time()),
                }
            )
            try:
                if 'clickerUser' in request:
                    self.balance = upgrade['_meta']['price']
                    self.logs(message=f"※※※ Bought {upgrade['id']} upgrade... \n◯ Balance: {pretty(self.balance)}")
                    break
                if 'error_code' in request:
                    self.logs(message=f"※ Oops! Something went wrong with {upgrade['id']} upgrade... \n◯ Error code: {request['error_code']} {f'\n◯ Timer: {request['cooldownSeconds']}' if 'cooldownSeconds' in request else ''}")
                    continue
            except TypeError:
                self.logs(message=f"※ Oops! Something went wrong with {upgrade['id']} upgrade...")
                continue
        
    
    def sync_profile(self):
        if not self.work:
            return
        self.logs(message="※ Syncing profile...")
        request = self._make_request(link='/clicker/sync')
        self.balance = request['clickerUser']['balanceCoins']
        self.per_hour = request['clickerUser']['earnPassivePerHour']
        lastPassiveEarn = request['clickerUser']['lastPassiveEarn']
        self.logs(message=f"※ Synced profile... \n◯ Balance: {pretty(self.balance)}\n◯ Mined coins: {pretty(int(lastPassiveEarn))}\n◯ Per hour: {pretty(int(self.per_hour))}")
        return {
            "balance": self.balance,
            "per_hour": self.per_hour,
            "lastPassiveEarn": lastPassiveEarn,
        }
    
    def get_best_upgrades(self):
        if not self.work:
            return
        self.logs(message=f"※ Getting upgrades...")
        upgrades = self._make_request(link='/clicker/upgrades-for-buy')
        self.logs(message=f"※ Got upgrades...")

        self.logs(message=f"※ Sorting upgrades...")
        best_upgrades = self._sort_upgrades(upgrades)
        self.logs(message=f"※ Sorted upgrades...")

        # self.logs(message=f"※ Printing best 5 upgrades...")
        # self.logs(message='\n'.join(['%s' % x for x in best_upgrades[:5]]))
        return best_upgrades[:10]
    
    def _sort_upgrades(self, upgrades):
        if not self.work:
            return
        best_upgrades = []

        for upgrade in upgrades['upgradesForBuy']:
            if upgrade['isAvailable'] and upgrade['price'] > 0 and not upgrade['isExpired']:
                kpd = upgrade['profitPerHour'] / upgrade['price']
                best_upgrades.append({
                    "kpd": kpd, 
                    "id": upgrade['id'], 
                    "_meta": {
                        "price": upgrade['price'],
                        "profitPerHour": upgrade['profitPerHour'],
                    }
                })
        
        sorted_upgrades = sorted(best_upgrades, key=lambda upgrade: float(upgrade['kpd']), reverse=True)
        return sorted_upgrades
    
    def _make_request(
            self, 
            method: str = 'POST', 
            link: str = '/', 
            data: dict = {},
        ):
        if not self.work:
            return
        try:
            response = requests.request(
                method=method.upper(),
                url=str(self.base_url + link), 
                data=json.dumps(data),
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Accept-Language': 'ru-RU,ru;q=0.9',
                    'Content-Type': 'application/json',
                    'Connection': 'keep-alive',
                    'Origin': 'https://hamsterkombat.io',
                    'Referer': 'https://hamsterkombat.io/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                    'Sec-Ch-Ua-mobile': '?1',
                    'Sec-Ch-Ua-platform': '"Android"',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
                }, 
            )
            return response.json()
        except:
            self.logs(message=f"※ Error making request...\nDetail: {response.text[:100]}")
            return None