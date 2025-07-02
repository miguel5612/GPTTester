import os
from ..context import load_context
from ..data_factory import DataFactory


def test_dynamic_placeholders():
    os.environ["TEST_ENV"] = "qa"
    ctx = load_context()
    factory = DataFactory(env=ctx.env)
    user = factory.get_user()
    assert user.username.startswith("qa_")
    assert user.password == "qa_pass"
