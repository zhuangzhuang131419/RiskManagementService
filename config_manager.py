import configparser

from model.login import LoginConfig


class ConfigManager:
    def __init__(self, config_file='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.login_config = LoginConfig(
            broker_name=config.get('Login', 'BrokerName'),
            broker_id=config.get('Login', 'BrokerID'),
            user_id=config.get('Login', 'UserID'),
            investor_id=config.get('Login', 'InvestorID'),
            password=config.get('Login', 'Password'),
            app_id=config.get('Login', 'AppID'),
            auth_code=config.get('Login', 'AuthCode'),
            market_server_front = config.get('Server', 'MarketServerFront'),
            trade_server_front = config.get('Server', 'TradeServerFront')
        )

