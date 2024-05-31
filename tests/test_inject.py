import unittest

from rr.inject import injectable, inject, injectable_get, injection_clear_cache, \
    register_injectable


class TestInjection(unittest.TestCase):

    def setUp(self) -> None:
        injection_clear_cache()

    def test_injectable_registered_using_decorator(self):
        # given
        @injectable(name="x")
        class X:
            pass

        inst = X()

        assert inst == injectable_get("x")

    def test_injectable_registered_using_factory(self):
        class X:
            pass

        inst = register_injectable(name="x", factory=X)

        assert inst == injectable_get("x")

    def test_error_on_multiple_registration_attempts(self):
        # given
        @injectable(name="x")
        class X:
            pass

        X()
        try:
            X()
            assert False
        except ValueError as e:
            pass

    def test_inject_error_on_non_kwargs_used(self):
        @inject
        def test(*args):
            pass

        try:
            test(3)
            assert False
        except ValueError as e:
            pass

    def test_inject(self):

        @injectable(name="x")
        class X:

            def __init__(self):
                self.test_val = False

            def run(self):
                self.test_val = True

        inst = X()

        @inject
        def run_test(x: X = None):
            x.run()

        run_test()
        assert inst.test_val
