#pragma once

#include <string>

#include <QtWidgets/QMainWindow>
#include "ui_devirtualizeMe.h"

struct license_info
{
    bool isRegistered = false;
    std::string licenseId;
    std::string licenseeName;
    int numberUsers = 0;

    std::string getInfo();
};

class devirtualizeMe : public QMainWindow
{
    Q_OBJECT

public:
    devirtualizeMe(QWidget *parent = Q_NULLPTR);

private slots:
    void aboutProgram();
    void registerProgram();
    void quit();

private:
    Ui::devirtualizeMeClass ui;

    QAction* actAbout;
    QAction* actExit;
    
    license_info license;

};
