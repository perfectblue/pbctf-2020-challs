#include <QtWidgets/QDialog>
#include <QtWidgets/QLabel>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QFrame>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QDialogButtonBox>
#include <QtWidgets/QMessageBox>
#include <QtGui/QPixmap>

#include <stdio.h>
#include <stdint.h>
#include <sstream>

#include "devirtualizeMe.h"

#include "licenseCheck.h"

devirtualizeMe::devirtualizeMe(QWidget *parent)
    : QMainWindow(parent)
{
    ui.setupUi(this);

    actAbout = new QAction(tr("&About program..."), this);
    connect(actAbout, &QAction::triggered, this, &devirtualizeMe::aboutProgram);

    actExit = new QAction(tr("&Exit"), this);
    connect(actExit, &QAction::triggered, this, &devirtualizeMe::quit);

    QMenu* fileMenu = menuBar()->addMenu(tr("&File"));
    fileMenu->addAction(actExit);
    menuBar()->addMenu(tr("&Edit"));
    menuBar()->addMenu(tr("&Jump"));
    menuBar()->addMenu(tr("&Search"));
    menuBar()->addMenu(tr("&View"));
    menuBar()->addMenu(tr("&Debugger"));
    menuBar()->addMenu(tr("&Options"));
    menuBar()->addMenu(tr("&Windows"));
    QMenu* helpMenu = menuBar()->addMenu(tr("&Help"));
    helpMenu->addAction(actAbout);
}

std::string license_info::getInfo()
{
    if (!this->isRegistered)
    {
        return "Unregistered";
    }
    else
    {
        std::stringstream ss;
        ss << "Registered\n";
        ss << "License ID: " << this->licenseId << "\n";
        ss << "Registered to: " << this->licenseeName << "\n";
        if (this->numberUsers)
            ss << this->numberUsers << " users license\n";
        else
            ss << "Unlimited user license\n";
        return ss.str();
    }
}

void devirtualizeMe::aboutProgram()
{
    QDialog* about = new QDialog(0, 0);
    about->setWindowTitle("About");
    QVBoxLayout* layout = new QVBoxLayout();
    about->setLayout(layout);

    QFrame* frame = new QFrame(about);
    frame->setStyleSheet(".QFrame{border: 1px solid black; border-radius: 2px;}");
    layout->addWidget(frame);

    QHBoxLayout* buttonsHbox = new QHBoxLayout();
    layout->addLayout(buttonsHbox);

    QDialogButtonBox* buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok);
    connect(buttonBox, &QDialogButtonBox::accepted, about, &QDialog::accept);
    buttonsHbox->addWidget(buttonBox, 0, Qt::AlignCenter);

    if (!license.isRegistered)
    {
        QPushButton* registerButton = new QPushButton(about);
        registerButton->setText("Register");
        registerButton->setMaximumWidth(64);
        buttonsHbox->addWidget(registerButton, 0, Qt::AlignCenter);
        connect(registerButton, SIGNAL(released()), this, SLOT(registerProgram()));
    }

    QVBoxLayout* frameLayout = new QVBoxLayout();
    frame->setLayout(frameLayout);
    
    QHBoxLayout* hbox = new QHBoxLayout();
    frameLayout->addLayout(hbox);

    QPixmap pic(":/devirtualizeMe/lillullmoa.png");
    QLabel* picLabel = new QLabel(about);
    picLabel->setPixmap(pic);
    hbox->addWidget(picLabel);

    QVBoxLayout* vbox = new QVBoxLayout();
    hbox->addLayout(vbox);

    QLabel* titleLabel = new QLabel(about);
    titleLabel->setText("JDA - The Jiang Ying Disassembler");
    titleLabel->setStyleSheet("font-weight: bold");
    titleLabel->setAlignment(Qt::AlignCenter);
    vbox->addWidget(titleLabel);

    QLabel* versionLabel = new QLabel(about);
    versionLabel->setText("Version 69.0 Windows x64 (64-bit address size)");
    versionLabel->setAlignment(Qt::AlignCenter);
    vbox->addWidget(versionLabel);

    QLabel* copyrightLabel = new QLabel(about);
    copyrightLabel->setText("(c) 2020 Jiang Ying");
    copyrightLabel->setAlignment(Qt::AlignCenter);
    vbox->addWidget(copyrightLabel);

    QLabel* licenseLabel = new QLabel(about);
    licenseLabel->setText(QString::fromStdString(license.getInfo()));
    licenseLabel->setAlignment(Qt::AlignCenter);
    frameLayout->addWidget(licenseLabel);

    QLabel* licenseeLabel = new QLabel(about);
    licenseeLabel->setText(QString::fromStdString(license.licenseeName));
    licenseeLabel->setStyleSheet("font-weight: bold");
    licenseeLabel->setAlignment(Qt::AlignCenter);
    frameLayout->addWidget(licenseeLabel);

    QLabel* urlLabel = new QLabel(about);
    urlLabel->setText("<a href=\"http://twitter.com/gf_256\">ctf.perfect.blue</a>");
    urlLabel->setStyleSheet("font-weight: bold");
    urlLabel->setAlignment(Qt::AlignCenter);
    urlLabel->setTextInteractionFlags(Qt::TextBrowserInteraction);
    urlLabel->setOpenExternalLinks(true);
    frameLayout->addWidget(urlLabel);


    about->show();
}

void devirtualizeMe::registerProgram()
{
    FILE* fd = fopen("jda.key", "rb");
    if (!fd)
    {
        QMessageBox::warning(this, "Registration Error", "Missing jda.key");
        return;
    }
    fseek(fd, 0, SEEK_END);
    long filelen = ftell(fd);
    fseek(fd, 0, SEEK_SET);
    if (filelen < 84 || filelen > 1024)
    {
        goto invalidKey;
    }
    uint8_t* buf = (uint8_t*) malloc(filelen);
    if (fread(buf, 1, filelen, fd) != filelen)
    {
        goto invalidKey;
    }

    if (!CheckLicenseSignature(buf, filelen))
    {
        goto invalidKey;
    }

    this->license.isRegistered = true;
    this->license.licenseId = (char*)(buf + 16);
    this->license.licenseeName = (char*)(buf + 48);
    this->license.numberUsers = *(int*)(buf + 80);

    free(buf);

    if (true)
    {
        QMessageBox::information(this, "OK", "Thank you for registering this software!");
    }
    else
    {
invalidKey:
        QMessageBox::warning(this, "Registration Error", "Invalid jda.key");
        return;
    }

    fclose(fd);
}

void devirtualizeMe::quit()
{
    exit(0);
}

