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

Podana, jako parametr ścieżka dostępu jest ustawiana jako ścieżka wyszukiwania w <em>jinja2.FileSystemLoader</em>. Ta sama ścieżka jest używana przez JinjaTool do odnajdowania plików definicji.

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

Pierwszy parametr *template* jest obowiązkowy i wskazuje na wzorzec jinja. Drugi parametr *destpath* jest opcjonalny i wskazuje na ścieżkę docelową dla wygenerowanego pliku, która może być względna lub bezwzględna. Jeżeli nie jest podana, to plik wynikoway zostanie zapisany w katalogu wzorca. Możliwe jest również użycie opcjonalnego parametru <em>filename</em>, aby jawnie określić nazwę pliku wynikowego. W powyższym przykładzie zostanie ona określona na podstawie nazwy wzorca, poprzez odrzucenie rozszerzenia .jinja: <em>qt\_prop.py</em>.

Efekt użycia powyższego kodu można sprawdzić w [qt_prop.py](Tests/generated/qt_prop.py).

Istnieje również rozszerzona wersja metody <em>generate</em>:

```python
generator.generate_with_prot_sect('qt_prop_protsect.py.jinja', '../generated', **ctx) 
```

Posiada ona identyczne parametry wywołania, ale obsługuje [sekcje zabezpieczone](#sekcje-zabezpieczone).

Kolejną metodą jest metoda wykorzystująca plik json:

```json
{
    "generate": {
        "template": "qt_prop_protsect.py.jinja",
        "destpath": "../generated",
        "filename": "Person.py",
        "protsect": true
    },
    "context": {
        "class_name": "Person",
        "props": [
            {"name": "name", "type": "str"},
            {"name": "surname", "type": "str"},
            {"name": "age", "type": "int"}
        ],
        "methods": [
            {"name": "dumps", "args": ["one", "two"]},
            {"name": "isAdult", "args": []},
            {"name": "isCorrect", "args": []}
        ]
    }
}
```

```python
 generator.generate_from_json('person_qt_prop_ctx.json')
```

Sekcja *generate* pliku zawiera parametry odpowiadające parametrom metody *generate.* Jeżeli właściwość *protsect* jest ustawiona na <em>true</em>, to jest wykorzystywana metoda *generate\_with\_prot\_sect.*

Sekcja *context* zawiera kontekst, który jest przekazywany do szablonu jinja.

## Sekcje zabezpieczone

Sekcje zabezpieczone umożliwiają użytkownikowi modyfikowanie wygenerowanych plików i zachowanie tych modyfikacji podczas regeneracji pliku.
Format sekcji zabezpieczonej wygląda następująco:

```
{comment_open_tag} {prot_sec_open_tag} prot_sec_name {prot_sec_close_tag} [{comment_close_tag}]
prot_sect_context
{comment_open_tag} {prot_sec_open_tag} {prot_sec_close_tag} [{comment_close_tag}]
```

Sekcja zabezpieczona jest wyodrębniona specjalnie sformatowanym komentarzem i zawsze posiada unikalną nazwę:

```python
# >>> Implementacja isAdult <<<
return self.age > 18
# >>> <<<
```

* <em>comment\_open\_tag</em>: łańcuch wiodący komentarza zgodny z formatem generowanego pliku (patrz: [Konfiguracja](#konfiguracja)); w przykładzie <em>#</em>
* <em>prot\_sec\_open\_tag</em>: łańcuch wiodący dekcji zabezpieczonej (patrz: [Konfiguracja](#konfiguracja)); domyślnie <em>\>\>\></em>
* <em>prot\_sec\_name</em>: dowolna, unikalna nazwa sekcji zabezpieczonej; w przykładzie: <em>Implementacja isAdult</em>
* <em>comment\_close\_tag</em>: opcjonalny łańcuch zamykający komentarz zgodny z formatem generowanego pliku (patrz: [Konfiguracja](#konfiguracja)); w przykładzie nie występuje; ma znaczenie w przypadku formatów, takich jak XML, gdzie comment\_open\_tag to <em><!--</em> a comment\_close\_tag <em>--></em>
* <em>prot\_sect\_context</em>: kontekst chroniony; w przykładzie <em>return self.age > 18</em>

Jeżeli do generowania pliku wynikowego używana jest metoda obsługująca sekcje zabezpieczone, jej praca zaczyna się od sprawdzenia, czy istnieje już plik wynikowy. Jeżeli tak, to jest on analizowany pod kątem obecności sekcji zabezpieczonych. Odnalezione sekcje są zapisywane w słowniku, w którym kluczami są nazwy sekcji. Słownik jest dodawany do kontekstu wzorca jinja pod nazwą <em>\_\_protSect,</em> dzięki czemu w szablonie możliwa jest następujące użycie:

```jinja
{%- for method in methods %}
    # Metoda {{ method.name }}
    def {{ method.name }}({{ (['self'] + method.args[:])|join(', ') }}):
        {{ __protSect|getsect('Implementacja ' + method.name)|indent(8) }}
{%- endfor -%}
```

*getsect* jest [dodatkowym testem](#dodatkowe-testy-jinja) Jinja zdefiniowanym w JinjaTool. W przypadku gdy została odnaleziona sekcja o wskazanej nazwie zostanie ona w całości umieszczona w pliku wynikowym. Jeżeli nie została odnaleziona to zostanie umieszczona sekcja o wskazanej nazwie, ale bez kontekstu. Dzięki temu w pliku wynikowym zostanie utworzony obszar, który można bezpiecznie modyfikować.

Plik [Person_001.py](Tests/pattern/Person_001.py) pokazuje efekt pierwszej generacji pliku z wykorzystaniem [person_qt_prop_ctx.json](Tests/templates/person_qt_prop_ctx.json). W pliku wynikowym znajdują się puste sekcje zabezpieczone. Plik [Person_003.py](Tests/pattern/Person_003.py) pokazuje efekt generacji pliku wynikowego po uzupełnieniu kontekstu sekcji zabezpieczonych. 

## Konfiguracja

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