#!/usr/bin/env python

__author__ = "Fredrique Samuels"
__copyright__ = "Copyright 2024"

import inspect
import logging
import re
from dataclasses import dataclass
from typing import Dict, Any, Callable, Tuple, List


@dataclass(frozen=True)
class InjectableItem:
    """
    Object to pair an object with a global name. Used as the parameter when
    querying injectable object form the cache.
    """
    name: str
    val: Any


class InjectableCache:
    """
    Object to manage the injectable objects
    """

    def __init__(self):
        self._items: Dict[str, Any] = {}
        # TODO Add a cache that groups the objects by lookup type

    def clear(self):
        """
        Clear the internal cache.
        """
        self._items = {}

    def lookup_instance(self, name: str):
        """
        Search the cache for an object registered with the given name.

        :param name: The name used to register object.
        :return: The object or None if no object exists.
        """
        if name not in self._items.keys():
            return None

        return self._items[name]

    def register(self, name: str, inst: Any):
        """
        Register an object into the cache.

        :param name: The name that will be used to reference the object
        :param inst: The object to tbe registered
        :raise ValueError: If the name used is already registered
        """
        if self.exists(name):
            raise ValueError(f"An object with name={name} is already exists {self._items[name]}")

        self._items[name] = inst

    def exists(self, name: str) -> bool:
        """
        Check if a name is already in use.

        :param name: The name to validate
        :return: True is the name is already registered
        """
        return name in self._items.keys()

    def print(self):
        for k, v in self._items.items():
            print(k, v)

    def query(self, predicate_func: Callable[[InjectableItem], bool]):
        """
        Run through the cache and apply the predicate to all the items.
        Note is not optimized yet so this may run slow

        :param predicate_func: Predicate function to apply to the list
        :return: A list of Tuple objects containing the name and object (<name>, <object>)
        """
        return [(k, v) for k, v in self._items.items() if predicate_func(InjectableItem(name=k, val=v))]


PRIVATE_CACHE = InjectableCache()


def injectable_get(name: str) -> Any:
    """
    Search the cache for an object registered with the given name.

    :param name: The name used to register object.
    :return: The object or None if no object exists.
    """
    return PRIVATE_CACHE.lookup_instance(name)


def print_injectables():
    PRIVATE_CACHE.print()


class Injectable(object):

    def __init__(self, class_type_, name_):
        self.class_type_ = class_type_
        self.name_ = name_

    def __call__(self, *c_args, **c_kwargs):
        if PRIVATE_CACHE.exists(self.name_):
            raise ValueError(f"Injectable with name {self.name_} is already registered")

        inst = self.class_type_(*c_args, **c_kwargs)
        PRIVATE_CACHE.register(self.name_, inst)
        logging.info(f"Injectable name={self.name_} created")
        return inst


def is_injectable(obj_) -> bool:
    return isinstance(obj_, Injectable)


def injectable(name: str):
    """
    Decorator function used to register an object into the registry. To be used on the class definition only.
    A class using this decorator should only ever have one instance in the app.
    Attempting to create a second instance will result in an exception

    @injectable(name="my_service")
    class MyService:
        pass

    :param name: The name used to register object.
    """

    def wrapper(class_type):
        return Injectable(class_type, name)

    return wrapper


def only_self_arg_allowed(func, arg_names, func_args):
    if len(func_args) == 1 and len(arg_names) > 0 and arg_names[0] == "self":
        return

    if len(func_args) > 0:
        raise ValueError(f"Callable {func} must be invoked with only kwargs")


def create_func_kwargs(arg_names, func_kwargs) -> dict:
    kwargs_ = {}
    for name in arg_names:
        if name == "self":
            continue

        if name in func_kwargs.keys():
            kwargs_[name] = func_kwargs[name]
        else:
            obj = PRIVATE_CACHE.lookup_instance(name)
            if obj is not None:
                kwargs_[name] = obj

    return kwargs_


def inject(func):
    """
    A decorator function used on function, method and constructors to auto replace
    named parameters that is defaulted to None with values from the injection cache.

    @injectable(name="my_service")
    class MyService:
        pass

    @inject
    def demo(my_service: MyService = None):
        assert my_service is not None

    MyService()
    demo()


    :param func: The function, method or constructor being decorated
    """
    arg_names = inspect.getfullargspec(func).args

    def new_init(*func_args, **func_kwargs):
        only_self_arg_allowed(func, arg_names, func_args)
        return func(*func_args, **create_func_kwargs(arg_names, func_kwargs))

    return new_init


def injectables(predicate_func: Callable[[InjectableItem], bool]) -> List[Any]:
    return list(map(lambda x: x[1], PRIVATE_CACHE.query(predicate_func)))


def injectables_keyed(predicate_func: Callable[[InjectableItem], bool]) -> List[Tuple[str, Any]]:
    return PRIVATE_CACHE.query(predicate_func)


def injectables_by_type(class_type_: Any) -> List[Any]:
    """
    Get all the registered object that are derived from the given class type.

    Note: This function has not been optimized so expect a performance hit with large
        registries

    :param class_type_: The class type used to filter the registered items
    """
    return injectables(lambda x: isinstance(x.val, class_type_))


def injectables_by_type_keyed(class_type_: Any) -> List[Any]:
    return injectables_keyed(lambda x: isinstance(x.val, class_type_))


def injectable_factory(name: str, class_type: Any, *args, **kwargs):
    @injectable(name)
    def _factory():
        return class_type(*args, **kwargs)

    return _factory


def register_injectable(name: str, factory: Any, *args, **kwargs):
    """
    Register an object lookup table to be injected using @inject.

    :param name: The name used register the object.
    :param factory: The factory to use on construction. Can be a class type or a function
    :param args: Positional arguments to be passed to the factory on construction
    :param kwargs: Named arguments to be passed to the factory
    :return: The registered instance
    """
    return injectable_factory(name, factory, *args, **kwargs)()


def register_injectable_from_type(class_type: Any, *args, **kwargs):
    """
    Register an object lookup table to be injected using @inject. The name is derived form the
    class name converted to snake case.

    :param class_type: The class type to use on construction.
    :param args: Positional arguments to be passed to the factory on construction
    :param kwargs: Named arguments to be passed to the factory
    :return: The registered instance
    """
    name = "_".join([s.lower() for s in re.sub(r"([A-Z])", r" \1", class_type.__name__).split()])
    return injectable_factory(name, class_type, *args, **kwargs)()


def injection_clear_cache():
    PRIVATE_CACHE.clear()


__all__ = ['InjectableItem',
           'injectable',
           'inject',
           'is_injectable',
           'injectable_get',
           'print_injectables',
           'injectable_factory',
           'injectables',
           'register_injectable_from_type',
           'register_injectable',
           'injection_clear_cache',
           'injectables_by_type']
