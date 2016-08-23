from distutils.core import setup
import py2exe
from glob import glob

data_files = [("Microsoft.VC140.CRT",
               glob(r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\redist\x86\Microsoft.VC140.CRT\*.*'))]

setup(console=['main.py'],
      data_files=data_files)
