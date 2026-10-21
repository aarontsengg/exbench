"""Strict serial ExUnit adapter retaining doctests as distinct identities."""
import importlib.util
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('qualified_adapter',ROOT/'findings/cachex-cluster/audit_identities.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)

def parse(text):
    text='\n'.join(text.splitlines())
    text=re.sub(r'^(\s*\* )doctest ',r'\1test [doctest] ',text,flags=re.MULTILINE)
    text=re.sub(r'^(\s*\d+\) )doctest ',r'\1test [doctest] ',text,flags=re.MULTILINE)
    text=re.sub(r'^(\d+) doctests?, (\d+) tests?, (\d+) failures?$',lambda m:f'{int(m[1])+int(m[2])} tests, {m[3]} failures',text,flags=re.MULTILINE)
    return adapter.parse(text)
