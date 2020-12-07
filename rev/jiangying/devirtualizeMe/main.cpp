#include <QtWidgets/QApplication>
#include <Windows.h>
//#include <stdio.h>

#include "devirtualizeMe.h"

int main(int argc, char *argv[])
{
    //AllocConsole();
    //AttachConsole(0);
    //freopen("CONOUT$", "w", stdout);
    //freopen("CONIN$", "r", stdin);

    //getchar();

    //return 0;

    QApplication a(argc, argv);
    devirtualizeMe w;
    w.show();
    return a.exec();
}
