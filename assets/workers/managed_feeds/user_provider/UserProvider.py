from abc import ABC, abstractmethod


class UserProvider(ABC):

    @abstractmethod
    def get_username(self):
        pass


class AnonymousUserProvider(UserProvider):

    def get_username(self):
        return None
