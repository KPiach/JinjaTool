import os
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Union, Sequence
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

####################################################
# Funkcje filtrów wykorzystywane w szablonach jinja.

def quotation(input):
    return '"' + input + '"'

def exttrim(input):
    return input.strip()

def getsect(sect_dict, name, comment_tag):
    ''' 
    Zwraca sformatowaną zawartość sekcji zabezpieczonej, jeżeli
    istnieje sekcja o wskazanej nazwie. W przeciwnym razie
    zwraca domyślną postać pustej sekcji zabezpieczonej o wskazanej
    nazwie.
    Funkcja używana przez szablony jinja, jako filtr. Przeznaczona
    do wywołania, analogicznego do:
    {{__protSect|getsect('Sekcja I', '#')}}
    __proSect jest nazwą pod jaką metody klasy CodeGenerator przekazują
    w kontekście szablonu słownik z odnalezionymi sekcjami zabezpieczonymi.
            
    Argumenty:
    ----------
    * sect_dict - słownik wiążący nazwy sekcji z wystąpieniami klas ProtSect
    * name - nazwa sekcji
    * comment_tag - znak wiodący komentarza; używany w przypadku generowania
                    domyślnej pustej sekcji.
    '''
    if name in sect_dict:
        return sect_dict[name].formattedSect()
    return f'''{comment_tag} {CodeGenerator.prot_sec_open_tag} {name} {CodeGenerator.prot_sec_close_tag}
{comment_tag} {CodeGenerator.prot_sec_open_tag} {CodeGenerator.prot_sec_close_tag}'''

def check(input):
    '''
    W celach debugingu.
    '''
    return input

####################################################

@dataclass
class ProtSect:
    '''
    Klasa przechowująca imformacje o sekcji zabezpieczonej.
    '''
    first_line: int     # Pierwsza linia sekcji
    last_line: int      # Ostatnia linia sekcji
    sect_name: str      # Nazwa sekcji
    lines: list[str]    # Tablica z liniami sekcji
    
    
    def isNotDef(self) -> bool:
        return not self.sect_name
    
    
    def numberOfLines(self) -> int:
        if self.first_line == -1 or self.last_line == -1:
            return 0
        return self.last_line - self.first_line + 1


    def formattedSect(self) -> str:
        return '\n'.join([s.strip() for s in self.lines])


class CodeGenerator(object):
    '''
    Klasa umożliwiające generowanie plików z użyciem
    szablonów jinja.
    '''
    def_comment_tags = [
        ('.js', '//'),
        ('.py', '#'),
        ('.rb', '#'),
        ('.java', '//'),
        ('.swift', '//'),
        ('.cpp', '//'),
        ('.php', '//'),
        ('.pl', '#'),
        ('.r', '#'),
        ('.scala', '//'),
        ('.sh', '#'),
        ('.ps1', '#'),
        ('.bat', 'REM'),
        ('.groovy', '//'),
        ('.kt', '//'),
        ('.m', '//'),
        ('.ts', '//'),
        ('.sql', '--'),
        ('.css', '/*'),
        ('.html', '<!--'),
        ('.xml', '<!--'),
        ('.md', '[//]:# ('),
        ('.md', '[//]: # ('),
        ('.ini', ';'),  
        ('.cfg', '//'),
        ('.jinja', '{#'),
        ('.ui', '<!--'),
    ]
    
    def_prot_sec_open_tag = '>>>'
    def_prot_sec_close_tag = '<<<'
    prot_sec_open_tag = '>>>'
    prot_sec_close_tag = '<<<'

    
    def __init__(self, templatepaths: str | os.PathLike | Sequence[str | os.PathLike]):
        '''
        Konstruktor.
    
        Argumenty:
        ----------
        * templatepaths - ścieżki dostępu, w których będą poszukiwane
                            pliki szablonów oraz definicji.
        '''
        super().__init__()
        
        self.__comment_tags = self.def_comment_tags
        self.set_default_prot_sec_tags()
                
        self.__env = Environment(
            loader=FileSystemLoader(templatepaths),
            autoescape=select_autoescape(),
            trim_blocks=False,
            extensions=["jinja2.ext.debug", "jinja2.ext.do"])
        
        self.__env.filters['quotation'] = quotation
        self.__env.filters['exttrim'] = exttrim
        self.__env.filters['check'] = check
        self.__env.filters['getsect'] = getsect
        
        self.__env.tests['isinstance'] = isinstance

        
    def __parse_protected_sections(self, filepath: Path) -> ProtSect:
        if not filepath.exists():
            return None
        
        ext = filepath.suffix
        tags = [t for t in self.__comment_tags if t[0] == ext]
                
        if not tags:
            return
            
        with filepath.open('rt') as f:
            lines = f.readlines()
        
        pattern = r'\s*{0}' + rf"\s*{self.prot_sec_open_tag}\s*(?P<name>.*?)\s*{self.prot_sec_close_tag}.*"
                    
        res: dict[str, ProtSect] = dict()
                    
        for t in tags:
            pattern = pattern.format(t[1])
            ct = re.compile(pattern)
            
            section_opened = False
            opened_section_name = ''
            section_nline_start = -1
            for i, l in enumerate(lines):
                m = ct.match(l)
                if not m:
                    continue
                section_name = m.group('name')
                if not section_name:
                # Zamykanie sekcji.
                    if not section_opened:
                        # Próba zamknięcia nieotwartej sekcji. Ostrzeżenie.
                        pass
                    else:
                        # Zamykanie sekcji.
                        res[opened_section_name] = ProtSect(opened_section_name, 
                                                            section_nline_start,
                                                            i,
                                                            lines[section_nline_start : i + 1])
                        section_opened = False
                        opened_section_name = ''
                        section_nline_start = -1
                else:
                    # Otwieranie sekcji.
                    if section_opened:
                        # Zagnieżdżona sekcja - nieobsługiwany przypadek. Błąd.
                        raise Exception(f'W pliku {filepath} wykryto zagnieżdżoną sekcję chronioną: '
                                        f'{section_name} w {opened_section_name}.')
                    # Otwieranie sekcji
                    if section_name in res:
                        # Powtórzona nazwa sekcji. Błąd.
                        raise Exception(f'W pliku {filepath} wykryto wielokrotną nazwę sekcji: {section_name}.')
                                        
                    section_opened = True
                    opened_section_name = section_name
                    section_nline_start = i
                        
        return res        


    @classmethod
    def __resolve_dest_path(cls, template: Template, destpath: Path, filename: str) -> Path:
        '''
        Ustala ścieżkę docelową.
        Jeżeli nie została wskazana ścieżka docelowa to jako 
        ścieżka docelowa zostanie użyty katalog szablonu.
        Jeżeli została wskazana ścieżka docelowa względna, to
        ostateczna ścieżka docelowa zostanie określona względem ścieżki
        katalogu szablonu.
        Jeżeli nie została wskazana nazwa pliku, to w katalogu docelowym 
        zostanie zapisany plik o nazwie identycznej, jak nazwa szablonu
        z odrzuconym ostatnim członem. Dla przykładowej nazwy szablonu:
        requirements.md.jinja
        zostanie wygenerowany plik: requirements.md.
        
        Argumenty:
        ----------
        * template - nazwa szablonu; plik szablonu będzie poszukiwany
                        w ścieżkach przekazanych do konstruktora
        * destpath - (opcjonalne) ścieżka docelowa dla generowanego pliku;
                        może być względna lub bezwzględna; powinna wskazywać
                        istniejący katalog;
        * filename - (opcjonalne) nazwa generowanego pliku 
        '''
        if destpath is None:
            destpath = Path(template.filename).parent 
        else:
            if isinstance(destpath, str):
                destpath = Path(destpath)

            if not destpath.is_absolute():
                destpath = Path(template.filename).parent.joinpath(destpath)

            destpath = Path(destpath).resolve()

        if filename is None:
            destpath = destpath.joinpath(Path(template.filename).stem)
        else:
            destpath = destpath.joinpath(filename)
            
        return destpath


    @classmethod    
    def set_prot_sec_tags(cls, open: str, close: str):
        '''
        Umożliwia zmianę domyślnych znaczników używanych do zdefiniwania
        sekcji.
        Uwaga: znaczniki są zdefiniowane statycznie. Powinny być zmieniane
        przed utworzeniem instancji klasy CodeGenerator.
        '''
        if open:
            cls.prot_sec_open_tag = open
            
        if close:
            cls.prot_sec_open_tag = close


    @classmethod            
    def set_default_prot_sec_tags(cls):
        cls.prot_sec_open_tag = cls.def_prot_sec_open_tag
        cls.prot_sec_close_tag = cls.def_prot_sec_close_tag

        
    def add_comment_tags(self, tags: list[tuple[str, str]]):
        
        def checkExt(tag: tuple[str, str]):
            if not tag[0].startswith('.'):
                tag[0] = '.' + tag[0]
            return tag
            
        [checkExt(t) for t in tags]
        
        self.__comment_tags += tags

        
    def add_comment_tag(self, ext: str, tag: str):
        self.add_comment_tags([(ext, tag)])    
        
    
    def generate(self, 
                 template: str, 
                 destpath: Union[str, Path] = None, 
                 filename: str = None, 
                 **arg):
        '''
        Generuje plik wyjściowy na podstawie wskazanego szablonu.
        
        Argumenty:
        ----------
        * template - nazwa szablonu; plik szablonu będzie poszukiwany
                        w ścieżkach przekazanych do konstruktora
        * destpath - (opcjonalne) ścieżka docelowa dla generowanego pliku;
                        może być względna lub bezwzględna; powinna wskazywać
                        istniejący katalog;
        * filename - (opcjonalne) nazwa generowanego pliku 
        arg - zestaw zmiennych stanowiących kontekst generacji
        '''
        template = self.__env.get_template(template)
        destpath = self.__resolve_dest_path(template, destpath, filename)
        template.stream(arg).dump(str(destpath))
        
    
    def generate_with_prot_sect(self,
                             template: str,
                             destpath: Union[str, Path] = None, 
                             filename: str = None,
                             **arg):
        '''
        Generacja pliku docelowego z użyciem sekcji zabezpieczonych.
        Przed generacją sprawdza, czy istnieje plik docelowy. Jeżeli
        tak, to plik jest analizowany pod kątem obecności sekcji
        oznaczonych:
        ?? >>> Unikalna nazwa sekcji <<<
        <Dowolna zawartość>
        ?? >>> <<<
        Gdzie ?? symbolizują znaki wiodące dla linii komentarza 
        charakterystycznej dla danego typu pliku. Klasa przechowuje
        tablicę z wartościami domyślnymi wiążącymi rozszerzenia plików
        ze znakami wiodącymi komentarzy. Tablicę można modyfikować poprzez
        wywołania: setProtSecTags oraz setDefaultProtSecTags.
        Ciągi '>>>' oraz '<<<' są zdefiniowane w def_prot_sec_open_tag
        oraz def_prot_sec_close_tag.
        Tablica zawierająca zawartość odnalezionych sekcji przekazywana jest
        do szablonu jako zmienna __protSect.
        '''
        template = self.__env.get_template(template)
        destpath = self.__resolve_dest_path(template, destpath, filename)
        prot_sect = self.__parse_protected_sections(destpath)
        
        arg['__protSect'] = prot_sect
        template.stream(arg).dump(str(destpath))
        
        
    def generate_from_json(self, file):
        '''
        Generuje plik wynikowy na podstawie danych zawartych w pliku definicji
        json. Plik poszukiwany jest w katalogach wskazanych w konstruktorze
        identycznie jak pliki szablonów.
        Plik json powinien zawierać dwie grupy ustawień:
        - generate:
            - template - nazwa pliku szablonu
            - destpath - (opcjonalne) ścieżka dostępu do pliku docelowego
                            zgodnie z regułami __resolveDestPath
            - filename - (opcjonalne) nazwa pliku docelowego
                            zgodnie z regułami __resolveDestPath
            - protsect - (opcjonalne) jeżeli zdefiniowane, to użyte
                            będą sekcje zabezpieczone
        - context - dane kontekstowe, które zostaną przekazane do szablonu.
        '''
        json_src, filepath, _ = self.__env.loader.get_source(self.__env, file)
        
        json_data = json.loads(json_src)
        
        if not json_data['generate'] or not json_data['generate']['template']:
            raise Exception(f'Nieprawidłowy format pliku {filepath}, nie może być użyty do generowania pliku.')
        
        template = json_data['generate']['template']
        destpath = None
        if json_data['generate']['destpath']:
            destpath = json_data['generate']['destpath']
        filename = None
        if json_data['generate']['filename']:
            filename = json_data['generate']['filename']
        ctx = None
        if json_data['context']:
            ctx = json_data['context']    
            
        if json_data['generate']['protsect']:
            self.generate_with_prot_sect(template, destpath, filename, **ctx)
        else:
            self.generate(template, destpath, filename, **ctx)