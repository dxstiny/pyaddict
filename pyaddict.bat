@echo off

set command=%1
set arg=%2

echo %arg%

if /i "%command%" == "build" goto build
if /i "%command%" == "push" goto push
if /i "%command%" == "lint" goto lint
if /i "%command%" == "" goto build

:lint
python3 -m pylint src/pyaddict
python3 -m mypy src/pyaddict
exit

:build
py -m build
exit

:push
py -m twine upload dist/*
exit
