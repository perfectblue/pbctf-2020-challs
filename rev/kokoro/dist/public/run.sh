#!/bin/bash
echo 'Running it now :)'

# 50 on remote
DIFFICULTY=5

# Same image as remote
IMAGE=facade.png

# Java 1.8 is required!!!
java -noverify -Xint -cp ".:lib/lwjgl/*:lib/lwjgl-glfw/*:lib/lwjgl-opengl/*:lib/lwjgl-stb/*" blue.perfect.kokoro.Main $IMAGE $DIFFICULTY

# Have fun :-)
