:: -------------------------------------------------------------------
:: Copyright (c) 2010-2018 Denis Machard
:: This file is part of the extensive automation project
::
:: This library is free software; you can redistribute it and/or
:: modify it under the terms of the GNU Lesser General Public
:: License as published by the Free Software Foundation; either
:: version 2.1 of the License, or (at your option) any later version.
::
:: This library is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
:: Lesser General Public License for more details.
::
:: You should have received a copy of the GNU Lesser General Public
:: License along with this library; if not, write to the Free Software
:: Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
:: MA 02110-1301 USA
:: -------------------------------------------------------------------

@echo off

set Project=%~dp0..\

set PythonVersion=34
set Python=C:\Python%PythonVersion%\python.exe
set PythonPath=C:\Python%PythonVersion%\
set PyQtPath=Lib\site-packages\PyQt4\

:: build resources
echo Building resources...
%PythonPath%\%PyQtPath%\pyrcc4.exe -py3 -o "%Project%\Resources\Resources.py" "%Project%\Resources\__resources.qrc"

:: build executable
cd "%Project%"
%Python% "%Project%\BuildExe.py" py2exe

:: build with cx_Freeze
:: %Python% "%Project%\BuildExe.py" build

pause