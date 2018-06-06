from abc import ABCMeta, abstractmethod


class IStorageProviderDelegate(metaclass=ABCMeta):
    """
    Interface that every concrete implementation of the the DB (or its analog) should conform to. It contains methods
    that StorageProvider instance would call to get desired data
    """

    @abstractmethod
    def open(self) -> None:
        """
        This method is called to let DB know that StorageProvider expects that everything needed is loaded and DB is
        ready for operations.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        StorageProvider calls this method when DB is no longer needed and DB should perform any additional saving operations
        and unloading of DB file.
        """
        pass

    @abstractmethod
    def get_card(self, card: Card):
        pass
