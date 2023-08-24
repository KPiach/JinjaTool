# Ten plik został wygenerowany automatycznie.
# Nie należy go edytować. Wszelkie zmiany 
# poza sekcjami zabezpieczonymi zostaną
# nadpisane w przypadku powtórnej generacji.

from PySide6.QtCore import QObject, Property, Signal

class Person(QObject):
    def __init__(self):
        super().__init__()
        self.__name = str()
        self.__surname = str()
        self.__age = int()
    
    # Właściwość name    
    def getName(self) -> str:
        return self.__name

    def setName(self, value: str):
        if self.__name != value:
            self.__name = value
            self.name_changed.emit(value)

    name_changed = Signal(str)

    name = Property(str, getName, setName, notify=name_changed)
    
    # Właściwość surname    
    def getSurname(self) -> str:
        return self.__surname

    def setSurname(self, value: str):
        if self.__surname != value:
            self.__surname = value
            self.surname_changed.emit(value)

    surname_changed = Signal(str)

    surname = Property(str, getSurname, setSurname, notify=surname_changed)
    
    # Właściwość age    
    def getAge(self) -> int:
        return self.__age

    def setAge(self, value: int):
        if self.__age != value:
            self.__age = value
            self.age_changed.emit(value)

    age_changed = Signal(int)

    age = Property(int, getAge, setAge, notify=age_changed)

    # Metoda dumps
    def dumps(self, one, two):
        # >>> Implementacja dumps <<<
        # >>> <<<

    # Metoda isAdult
    def isAdult(self):
        # >>> Implementacja isAdult <<<
        # >>> <<<

    # Metoda isCorrect
    def isCorrect(self):
        # >>> Implementacja isCorrect <<<
        # >>> <<<