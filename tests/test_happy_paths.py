from .context import load_context
from .data_factory import DataFactory
from .test_cases.web_happy_path import WebHappyPath
from .test_cases.api_happy_path import ApiHappyPath


def test_web_happy_path():
    ctx = load_context()
    factory = DataFactory(env=ctx.env)
    case = WebHappyPath(factory, ctx)
    assert case.run() is True


def test_api_happy_path():
    ctx = load_context()
    factory = DataFactory(env=ctx.env)
    case = ApiHappyPath(factory, ctx)
    assert case.run() is True
