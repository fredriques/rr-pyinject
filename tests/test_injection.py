import unittest

from rr.inject import injectable, inject, print_injectables, is_injectable


@injectable("i_my_service")
class MyService(object):

    def __init__(self, x: int):
        self.x = x


@injectable("i_person")
class Person:

    @inject
    def __init__(self, name: str, age: int, i_my_service: MyService):
        print(self, "On Init")
        self.service = i_my_service
        self.age = age
        self.name = name


@inject
def a_func(i_my_service: MyService):
    return i_my_service.x


@injectable("from_factory_method")
def injectable_factory_method():
    return 99


def hidden_injectable_factory_method(name: str, value: int) -> int:
    @injectable(name)
    def _create():
        return value

    return _create()


class TestInjection(unittest.TestCase):

    def test_distance_to_node(self):
        my_service = MyService(x=3)
        self.assertEqual(3, my_service.x)

        p = Person(name="Derp", age=13)
        self.assertEqual("Derp", p.name)
        self.assertEqual(13, p.age)
        self.assertIsNotNone(p.service)
        self.assertEqual(3, p.service.x)

    def test_inject_function(self):
        MyService(x=3)
        self.assertEqual(3, a_func())

    def test_injectable_factor_method(self):
        inst = hidden_injectable_factory_method("test_val", 6)
        self.assertEqual(6, inst)

        print_injectables()

        @inject
        def inject_test(test_val: int):
            return test_val

        self.assertEqual(6, inject_test())

        inst = hidden_injectable_factory_method("test_val_2", 10)
        self.assertEqual(10, inst)

        print_injectables()

        @inject
        def inject_test(test_val_2: int):
            return test_val_2

        self.assertEqual(10, inject_test())

    def test_is_injectable(self):
        self.assertTrue(is_injectable(Person))
        self.assertFalse(is_injectable(hidden_injectable_factory_method))
        self.assertTrue(is_injectable(injectable_factory_method))
