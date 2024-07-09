from enum import Enum
from .aspect import Limit, Loss 

# def Scale(enum):
#     @classmethod
#     def class_name(cls) -> str:
#         """Returns class name 
#         """
#         return cls.__name__
    
#     @classmethod
#     def all(cls) -> List[str]:
#         return [i for i in cls]

#     @classmethod
#     def resource(cls) -> List[str]:
#         return [i for i in cls if i.name in [j.name for j in Loss.resource() + Limit.resource()]]
    
#     @classmethod
#     def process(cls) -> List[str]:
#         return [i for i in cls if i.name in [j.name for j in Limit.process()]]
    
#     @classmethod
#     def transport(cls) -> List[str]:
#         return [i for i in cls if i.name in [j.name for j in Loss.transport() + Limit.transport()]]

# for i in Limit.all():
#     setattr(Scale, i.name, i.name)



