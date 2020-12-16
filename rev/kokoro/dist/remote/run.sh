#!/bin/bash
echo 'Running it now. You have 120 seconds :)'
LIBGL_ALWAYS_SOFTWARE=1 timeout 120 java -noverify -Xint -cp ".:lib/lwjgl/*:lib/lwjgl-glfw/*:lib/lwjgl-opengl/*:lib/lwjgl-stb/*" blue.perfect.kokoro.Main facade.png 50
