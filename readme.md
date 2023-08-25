# JinjaTool

## Wstęp

Pakiet **JinjaTool** zawiera narzędzia wspomagające generowanie kodu źródłowego w oparciu o szablony Jinja. Pakiet implementuje mechanizm obszarów chronionych umożliwiający wprowadzanie zmian w plikach wynikowych bez ryzyka utraty tychże zmian podczas regeneracji. Umożliwia to na przykład wygenerowanie z modelu UML deklaracji klas i dopisanie implementacji w wygenerowanym pliku bez obawy o utratę zmian w przypadku powtórnej generacji.

Pakiet był tworzony i testowany z użyciem:

* Python 3.11.0
* jinja2 3.1.2

## Funkcjonalność

**JinjaTool** umożliwia prostą generację plików na podstawie wskazanego szablonu i kontekstu, generację z wykorzystaniem obszarów chronionych oraz oba powyższe przypadki, ale w oparciu o dane przechowywane w pliku .json (pliki definicji).

**JinjaTool** tworzy i konfiguruje obiekt klasy jinja2.Environment z następującymi ustawieniami:

* autoescape: select\_autoescape
* trim\_blocks: false
* extensions:
    * jinja2.ext.debug
    * jinja2.ext.do
* filtry: [Dodatkowe filtry jinja](#dodatkowe-filtry-jinja)
* testy: [Dodatkowe testy jinja](#dodatkowe-testy-jinja)

## Sposób użycia

Pierwszym krokiem jest utworzenie obiektu klasy CodeGenerator:

```python
from JinjaTool.codegenerator import CodeGenerator
from pathlib import Path

CURRENT_DIRECTORY = Path(__file__).resolve().parent

generator = CodeGenerator(CURRENT_DIRECTORY.joinpath('templates'))
```

Podana, jako parametr ścieżka dostępu jest ustawiana jako ścieżka wyszukiwania w \*jinja2.FileSystemLoader\*. Ta sama ścieżka jest używana przez JinjaTool do odnajdowania plików definicji.

Teraz możliwe jest wygenerowanie pliku na podstawie wskazanego szablonu oraz kontekstu:

```python
ctx = \
{        
    "class_name": "User",        
    "props": [
        {"name": "nick_name", "type": "str"},
        {"name": "age", "type": "int", "default": "18"}
    ],
    "methods": [            
        {"name": "is_registered", "args": []}           
    ]
}

generator.generate('qt_prop.py.jinja', '../generated', **ctx)
```

Pierwszy parametr \*template\* jest obowiązkowy i wskazuje na wzorzec jinjla. Drugi parametr \*destpath\* jest opcjonalny i wskazuje na ścieżkę docelową dla wygenerowanego pliku, która może być względna lub bezwzględna. Jeżeli nie jest podana, to plik wynikoway zostanie zapisany w katalogu wzorca. Możliwe jest również użycie opcjonalnego parametru \*filename\*, aby jawnie określić nazwę pliku wynikowego. W powyższym przykładzie zostanie ona określona na podstawie nazwy wzorca, poprzez odrzucenie rozszerzenia \*.jinja\*: \*qt\_prop.py\*.

Efekt użycia powyższego kodu można sprawdzić w [qt_prop.py](Tests/generated/qt_prop.py)

## Sekcje zabezpieczone

## Dodatkowe filtry Jinja

### quotation(input)

Zwraca tekst przekazany w *input* obłożony znakami cydzysłowów.

### exttrim(input)

Zwraca tekst przekazany w *input* z usuniętymi białymi znakami z początku oraz końca.

### check(input)

Zwraca input. Zaimplementowany jako metoda wspomagajaca debugowanie.

### getsect(sect\_info, name)

Zwraca sformatowaną zawartość [sekcji zabezpieczonej](#sekcje-zabezpieczone), jeżeli istnieje sekcja o wskazanej nazwie. W przeciwnym razie zwraca domyślną postać pustej sekcji zabezpieczonej o wskazanej nazwie.

* sect\_info: krotka zawierająca informacje o łańcuchach wiodących komentarzy oraz słownik z informacjami o odnalezionych sekcjach; podczas generowania pliku z wykorzystaniem zabezpieczonych sekcji do kontekstu dodawana jest zmienna \_\_protSect przechowująca te dane
* name: nazwa sekcji

## Dodatkowe testy Jinja

### isinstance(\_\_obj, \_\_class\_or\_tuple)

Metoda *isinstance* wbudowana w Python.