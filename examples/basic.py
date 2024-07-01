from rr_inject import inject, injectable


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
