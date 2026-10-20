from __future__ import annotations
from abc import ABC, abstractmethod

"""
abstractions for observer pattern inform software component about 
an event occuring
"""
class Observer(ABC):

    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass


class Subject(ABC):

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass
    

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    
    @abstractmethod
    def notify(self) -> None:
        pass


class SubjectKey(ABC):

    @abstractmethod
    def attach(self, key: str,observer: Observer) -> None:
        pass
    

    @abstractmethod
    def detach(self, key: str) -> None:
        pass

    
    @abstractmethod
    def notify(self, key: str) -> None:
        pass


