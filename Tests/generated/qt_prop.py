# Ten plik został wygenerowany automatycznie.
# Nie należy go edytować. Wszelkie zmiany 
# poza sekcjami zabezpieczonymi zostaną
# nadpisane w przypadku powtórnej generacji.

from PySide6.QtCore import QObject, Property, Signal

class User(QObject):
    def __init__(self):
        super().__init__()
        self.__nick_name = str()
        self.__age = 18
    
    # Właściwość nick_name    
    def getNick_name(self) -> str:
        return self.__nick_name

    def setNick_name(self, value: str):
        if self.__nick_name != value:
            self.__nick_name = value
            self.nick_name_changed.emit(value)

    nick_name_changed = Signal(str)

    nick_name = Property(str, getNick_name, setNick_name, notify=nick_name_changed)
    
    # Właściwość age    
    def getAge(self) -> int:
        return self.__age

    def setAge(self, value: int):
        if self.__age != value:
            self.__age = value
            self.age_changed.emit(value)

    age_changed = Signal(int)

    age = Property(int, getAge, setAge, notify=age_changed)

    # Metoda is_registered
    def is_registered(self):
        pass