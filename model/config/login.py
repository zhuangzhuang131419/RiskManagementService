from dataclasses import dataclass

@dataclass
class LoginConfig:
    broker_name: str
    broker_id: str
    user_id: str
    investor_id: str
    password: str
    app_id: str
    auth_code: str