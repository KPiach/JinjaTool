import pytest
import shutil
from JinjaTool.codegenerator import CodeGenerator
from pathlib import Path

CURRENT_DIRECTORY = Path(__file__).resolve().parent

def compare_files(file1: Path , file2: Path) -> bool:
    with file1.open() as f1, file2.open() as f2:
        assert f1.readlines() == f2.readlines()

def test_001_generate():
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
    
    dest_file = Path(CURRENT_DIRECTORY.joinpath('generated', 'qt_prop.py'))
    dest_file.unlink(True)
    pattern_dir = Path(CURRENT_DIRECTORY.joinpath('pattern'))
    
    generator = CodeGenerator(CURRENT_DIRECTORY.joinpath('templates'))
    
    generator.generate('qt_prop.py.jinja', '../generated', **ctx)
    
    # Sprawdzam zgodność wygenerowanego pliku z wzorcem
    compare_files(dest_file, pattern_dir.joinpath('qt_prop.py'))    
    

def test_002_generate_from_json():
    dest_file = Path(CURRENT_DIRECTORY.joinpath('generated', 'Person.py'))
    dest_file.unlink(True)
    pattern_dir = Path(CURRENT_DIRECTORY.joinpath('pattern'))
        
    generator = CodeGenerator(CURRENT_DIRECTORY.joinpath('templates'))
    # Generuję plik na podstawie danych zapisanych w person_prop_ctx.json
    generator.generate_from_json('person_qt_prop_ctx.json')

    # Sprawdzam zgodność wygenerowanego pliku z wzorcem
    compare_files(dest_file, pattern_dir.joinpath('Person_001.py'))
    
    # Nadpisuję wygenerowany plik, plikiem który zawiera sekcje chronione
    shutil.copyfile(pattern_dir.joinpath('Person_002.py').as_posix(), dest_file.as_posix())
    
    # Powtórnie generuję plik na podstawie person_qt_prop_ctx.json
    generator.generate_from_json('person_qt_prop_ctx.json')
    
    # Sprawdzam zgodność wygenerowanego pliku z wzorcem zawierającym
    # sekcje chronione identyczne, jak Person_002.py
    compare_files(dest_file, pattern_dir.joinpath('Person_003.py'))