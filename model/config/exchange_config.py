from dataclasses import dataclass
from typing import Dict


@dataclass
class ExchangeConfig:
    broker_name: str
    broker_id: str
    user_id: str
    investor_id: str
    password: str
    app_id: str
    auth_code: str
    market_server_front: str
    trade_server_front: str

    def __init__(self, exchange_config: Dict):
        self.broker_name = exchange_config.get('BrokerName', '')
        self.broker_id = exchange_config.get('BrokerID', '')
        self.user_id = exchange_config.get('UserID', '')
        self.investor_id = exchange_config.get('InvestorID', '')
        self.password = exchange_config.get('Password', '')
        self.app_id = exchange_config.get('AppID', '')
        self.auth_code = exchange_config.get('AuthCode', '')
        self.market_server_front = exchange_config.get('MarketServerFront', '')
        self.trade_server_front = exchange_config.get('TradeServerFront', '')
