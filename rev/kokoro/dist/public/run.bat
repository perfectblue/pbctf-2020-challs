@echo off

echo Running it now :)

REM 50 on remote
set DIFFICULTY=5

REM Same image as remote
set IMAGE=facade.png

REM Java 1.8 is required!!!
java -noverify -Xint -cp ".;lib/lwjgl/*;lib/lwjgl-glfw/*;lib/lwjgl-opengl/*;lib/lwjgl-stb/*" blue.perfect.kokoro.Main %IMAGE% %DIFFICULTY%

pause
