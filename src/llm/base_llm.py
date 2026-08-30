from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    async def extract(self, text, schema):
        """
        Convert raw text into structured JSON.
        """
        pass