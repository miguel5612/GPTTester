from dataclasses import dataclass

@dataclass
class UserData:
    username: str
    password: str


@dataclass
class BaseTestData:
    timestamp: str


@dataclass
class WebTestData(BaseTestData):
    browser: str


@dataclass
class APITestData(BaseTestData):
    token: str


@dataclass
class MobileTestData(BaseTestData):
    device: str
