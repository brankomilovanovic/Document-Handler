from abc import ABC, abstractmethod
class Plugin(ABC):

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self): ... # skraceno za pass (ako nemamo telo)
    