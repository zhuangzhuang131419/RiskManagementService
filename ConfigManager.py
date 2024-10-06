import configparser

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_login_info(self):
        return {
            'BrokerID': self.config.get('Login', 'BrokerID'),
            'BrokerName': self.config.get('Login', 'BrokerName'),
            'UserID': self.config.get('Login', 'UserID'),
            'Password': self.config.get('Login', 'Password'),
            'AppID': self.config.get('Login', 'AppID'),
            'AuthCode': self.config.get('Login', 'AuthCode'),
        }

    def get_server_info(self):
        return {
            'MarketServerFront': self.config.get('Server', 'MarketServerFront'),
            'TradeServerFront': self.config.get('Server', 'TradeServerFront'),
        }
