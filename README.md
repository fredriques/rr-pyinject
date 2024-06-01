# rr-inject

Dependency Injection library for Python using decorators.

# Description

This library attempts to simply injection of dependencies into functions, constructors and methods
with minimal overhead during coding. This is done using the decorator @inject. When the function, 
constructor or method with this decorator is invoked the arguments are inspected to 
find any named argument that the callable allows, but is not in the argument list. The missing
values are then replaced with values registered as an injectable.

# Basic Usage

```python
from rr.inject import inject, injectable

# Mark the class type as injectable using the decorator.
@injectable(name="my_service")
class MyService:
    pass

# Register an instance of the decorated class. No need to keep a reference 
# since it will be held in the cache.
MyService()

# To receive the registered object as an argument simply use the name
# used to register the object as the parameter name and default it to `None`
@inject
def demo(my_service: MyService = None):
    print(my_service)

demo()
```
Output

```commandline
<__main__.MyService object at 0x000001780FBA0E20>
```

# Alternatives to using @injectable

Using `@injectable` requires that only one instance of the object in the application.
Attempting to create a second instance will result in an error. You may also have
types that you do not want to define and link to the decorator to not create a dependency 
on the rr-inject library in lower level packages. You can therefore use the `register_injectable`
function instead.

```python
register_injectable("my_service", MyService)
```

or 

```python
register_injectable("my_service", lambda: MyService())
```

or

```python
inst = MyService()
register_injectable("my_service", lambda: inst)
```

# Downside of using the @inject decorator

The only downside is that callables marked with `@inject` cannot be invoked
with positional arguments, if you do you will get an error. All arguments must be
named. 

```python

@inject
def add_util(a: int, b: int, calc: Calculator = None) -> int:
    return calc.add(a, b)

add_util(a=1, b=5)
```