from dataclasses import dataclass

@dataclass
class ServerConfig:
    market_server_front: str
    trade_server_front: str