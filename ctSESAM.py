#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hashlib import pbkdf2_hmac

import sys
from PySide.QtGui import QApplication, QWidget, QBoxLayout, QFont
from PySide.QtGui import QLabel, QTextEdit, QCheckBox, QSlider, QPushButton
from PySide.QtCore import Qt


class MainWindow(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super(MainWindow, self).__init__()
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.generator = None
        self.iterations = 4096
        # Master password
        self.master_password_label = QLabel("&Master-Passwort:")
        self.maser_password_edit = QTextEdit()
        self.maser_password_edit.textChanged.connect(self.edit_text_changed)
        self.maser_password_edit.setMaximumHeight(28)
        self.master_password_label.setBuddy(self.maser_password_edit)
        self.layout.addWidget(self.master_password_label)
        self.layout.addWidget(self.maser_password_edit)
        # Domain
        self.domain_label = QLabel("&Domain:")
        self.domain_edit = QTextEdit()
        self.domain_edit.textChanged.connect(self.edit_text_changed)
        self.domain_edit.setMaximumHeight(28)
        self.domain_label.setBuddy(self.domain_edit)
        self.layout.addWidget(self.domain_label)
        self.layout.addWidget(self.domain_edit)
        # Checkboxes
        self.special_characters_checkbox = QCheckBox("Sonderzeichen")
        self.special_characters_checkbox.setChecked(True)
        self.layout.addWidget(self.special_characters_checkbox)
        self.letters_checkbox = QCheckBox("Buchstaben")
        self.letters_checkbox.setChecked(True)
        self.layout.addWidget(self.letters_checkbox)
        self.digits_checkbox = QCheckBox("Zahlen")
        self.digits_checkbox.setChecked(True)
        self.layout.addWidget(self.digits_checkbox)
        # Length slider
        self.length_label = QLabel("&Länge:")
        self.length_display = QLabel()
        self.length_label_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.length_label_layout.addWidget(self.length_label)
        self.length_label_layout.addWidget(self.length_display)
        self.length_label_layout.addStretch()
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(20)
        self.length_slider.setPageStep(1)
        self.length_slider.setValue(10)
        self.length_display.setText(str(self.length_slider.sliderPosition()))
        self.length_slider.valueChanged.connect(self.length_slider_changed)
        self.length_label.setBuddy(self.length_slider)
        self.layout.addLayout(self.length_label_layout)
        self.layout.addWidget(self.length_slider)
        # Button
        self.generate_button = QPushButton("Erzeugen")
        self.generate_button.clicked.connect(self.generate_password)
        self.layout.addWidget(self.generate_button)
        # Password
        self.password_label = QLabel("&Passwort:")
        self.password = QLabel()
        self.password.setTextFormat(Qt.PlainText)
        self.password.setAlignment(Qt.AlignCenter)
        self.password.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.password_label.setBuddy(self.password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password)
        # Iteration display
        self.iteration_label = QLabel()
        self.iteration_label.setTextFormat(Qt.RichText)
        self.iteration_label.setVisible(False)
        self.layout.addWidget(self.iteration_label)
        # Window layout
        self.layout.addStretch()
        self.setGeometry(0, 30, 300, 400)
        self.setWindowTitle("c't SESAM")
        self.maser_password_edit.setFocus()
        self.show()

    def length_slider_changed(self):
        self.length_display.setText(str(self.length_slider.sliderPosition()))
        self.edit_text_changed()

    def edit_text_changed(self):
        self.iterations = 4096
        self.iteration_label.setVisible(False)

    def generate_password(self):
        if not self.generator:
            self.generator = PasswordGenerator()
        if len(self.domain_edit.toPlainText()) <= 0:
            self.edit_text_changed()
            return False
        self.password.setText(self.generator.generate(
            self.maser_password_edit.toPlainText(),
            self.domain_edit.toPlainText(),
            self.length_slider.sliderPosition(),
            self.iterations
        ))
        self.password.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.iteration_label.setText(
            '<span style="font-size: 10px; color: #888888;">Das Passwort wurde ' + str(self.iterations) + ' mal gehasht.</span>')
        self.iteration_label.setVisible(True)
        self.iterations += 1


class PasswordGenerator:
    small_letters = list('abcdefghijklmnopqrstuvwxyz')
    big_letters = list('ABCDEFGHJKLMNPQRTUVWXYZ')
    numbers = list('0123456789')
    special_characters = list('#!"§$%&/()[]{}=-_+*<>;:.')
    password_characters = small_letters + big_letters + numbers + special_characters
    salt = "pepper".encode('utf-8')

    def convert_bytes_to_password(self, digest, length):
        number = int.from_bytes(digest, byteorder='big')
        password = ''
        while number > 0 and len(password) < length:
            password = password + self.password_characters[number % len(self.password_characters)]
            number //= len(self.password_characters)
        return password

    def generate(self, master_password, domain, length, iterations):
        hash_string = domain + master_password
        hashed_bytes = pbkdf2_hmac('sha512', hash_string.encode('utf-8'), self.salt, iterations)
        return self.convert_bytes_to_password(hashed_bytes, length)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()