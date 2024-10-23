import configparser

from model.config.login import LoginConfig
from model.config.server import ServerConfig


class ConfigManager:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    @property
    def login_config(self):
        return LoginConfig(
            broker_name=self.config.get('Login', 'BrokerName'),
            broker_id=self.config.get('Login', 'BrokerID'),
            user_id=self.config.get('Login', 'UserID'),
            investor_id=self.config.get('Login', 'InvestorID'),
            password=self.config.get('Login', 'Password'),
            app_id=self.config.get('Login', 'AppID'),
            auth_code=self.config.get('Login', 'AuthCode'))


    @property
    def server_config(self):
        return ServerConfig(
            market_server_front=self.config.get('Server', 'MarketServerFront'),
            trade_server_front=self.config.get('Server', 'TradeServerFront')
        )

