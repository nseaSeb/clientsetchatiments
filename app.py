import sys
import os
import csv
import re
import openpyxl
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QMenuBar, QMenu, QFileDialog, QMessageBox,
                              QInputDialog, QLabel, QPushButton, QDialog, QRadioButton,QDockWidget,
                              QButtonGroup, QLineEdit, QCheckBox, QFrame)
from PySide6.QtGui import QAction, QKeySequence
import version
import utils
from pays import iso
from console import PythonConsole
import menu_actions
import menu_transform
import io_file

class MainWindow(QMainWindow):
    print("test on the mount")
    def __init__(self):
        super().__init__()
        self.setWindowTitle(version.APP_NAME)
        self.resize(800, 600)
        self.leftClicked = Signal(int)
        self.rightClicked = Signal(int)
        self.doubleClicked = Signal(int)
        # Variables d'état
        self.col_roles = {}  # col_index : rôle attribué
        self.headers = None

        # Création de l'interface
        self.create_menu()
        self.create_main_widget()
        self.create_status_bar()
        # Configurer le menu contextuel pour les en-têtes de colonnes
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)

        # Permettre la sélection des en-têtes
        self.table.horizontalHeader().setSectionsClickable(True)
        # Configurer le tri initial
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        # Configurer les raccourcis clavier
        self.setup_shortcuts()
        self.setup_console()
   

    def handle_console_command(self, command):
        """Gère les commandes exécutées depuis la console Python"""
        try:
            # Vous pouvez personnaliser le traitement des commandes ici
            # Par exemple, ajouter des commandes spéciales pour manipuler l'application

            if command.startswith("show_stats"):
                # Exemple de commande spéciale
                rows = self.table.rowCount()
                cols = self.table.columnCount()
                self.status_label.setText(f"Statistiques: {rows} lignes, {cols} colonnes")
                return f"Statistiques: {rows} lignes, {cols} colonnes"

            elif command.startswith("help_app"):
                # Exemple d'aide spécifique à l'application
                return """Commandes spéciales:
    - show_stats : affiche des statistiques sur le tableau
    - help_app : affiche cette aide
    """

            # Commandes standard
            self.status_label.setText(f"Commande exécutée : {command}")
            return None  # Pas de retour spécial pour les commandes standard

        except Exception as e:
            self.status_label.setText(f"Erreur : {str(e)}")
            return f"Erreur : {str(e)}"

    def setup_console(self):
        """Ajoute la console à l'interface"""
        self.console = PythonConsole(self)
        self.console.set_table_reference(self.table)
        self.console.set_data_reference(self.get_table_data())

        # Ajoute la console dans un dock
        self.dock = QDockWidget("Console Python", self)
        self.dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

        # Connecte le signal execute
        self.console.execute.connect(self.handle_console_command)
    def show_header_context_menu(self, pos):
        menu = QMenu(self)
        col = self.table.horizontalHeader().logicalIndexAt(pos)

        if col >= 0:
            # Ajouter les actions de tri
            sort_asc = QAction("Trier A→Z", self)
            sort_asc.triggered.connect(lambda: self.table.sortByColumn(col, Qt.AscendingOrder))
            menu.addAction(sort_asc)

            sort_desc = QAction("Trier Z→A", self)
            sort_desc.triggered.connect(lambda: self.table.sortByColumn(col, Qt.DescendingOrder))
            menu.addAction(sort_desc)

            menu.addSeparator()


        # Obtenir la colonne cliquée
        col = self.table.horizontalHeader().logicalIndexAt(pos)
        if col < 0:
            return
        # Action pour ajouter une colonne (disponible même sans colonne sélectionnée)
        add_col_action = QAction("Ajouter une colonne à droite", self)
        add_col_action.triggered.connect(lambda: menu_actions.add_column_right(self, col if col >= 0 else self.table.columnCount() - 1))
        menu.addAction(add_col_action)
        delete_action = QAction("Supprimer la colonne", self)
        delete_action.triggered.connect(lambda: menu_actions.delete_column(self, col))
        menu.addAction(delete_action)
        # Ajouter les actions au menu
        limit_action = QAction("Limiter à N caractères...", self)
        limit_action.triggered.connect(lambda: menu_transform.limit_column_length(self, col))
        menu.addAction(limit_action)

        role_action = QAction("Définir un rôle...", self)
        role_action.triggered.connect(lambda: self.set_column_role(col))
        menu.addAction(role_action)

        transform_action = QAction("Transformations", self)
        transform_action.triggered.connect(lambda: self.show_transformations_dialog(col))
        menu.addAction(transform_action)

        search_replace_action = QAction("Rechercher / Remplacer...", self)
        search_replace_action.triggered.connect(lambda: self.search_replace_column(col))
        menu.addAction(search_replace_action)

        # Afficher le menu à la position du clic
        header = self.table.horizontalHeader()
        menu.exec(header.mapToGlobal(pos))

    def create_menu(self):
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        open_action = QAction("Ouvrir un fichier...", self)
        open_action.triggered.connect(lambda: io_file.open_file(self))
        file_menu.addAction(open_action)

        save_action = QAction("Enregistrer sous...", self)
        save_action.triggered.connect(lambda: io_file.save_file(self))
        file_menu.addAction(save_action)

        save_segment_action = QAction("Enregistrer par segments...", self)
        save_segment_action.triggered.connect(lambda: io_file.save_segments(self))
        file_menu.addAction(save_segment_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        # Menu affichage
        view_menu = menubar.addMenu("Affichage")
        console_show_action = QAction("Afficher la console", self)
        console_show_action.triggered.connect(self.show_console)
        view_menu.addAction(console_show_action)
        # Menu Aide
        help_menu = menubar.addMenu("Aide")

        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    def show_console(self):
        self.dock.show()

    def create_main_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Création du tableau avec tri activé
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)  # Activation du tri
        self.table.setRowCount(40)
        self.table.setColumnCount(20)
        self.table.setAlternatingRowColors(True)

        # Configurer le header pour gérer le tri
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)  # Permettre le clic sur les en-têtes
        header.sectionClicked.connect(self.on_header_clicked)  # Connexion du signal

        # Activer le menu contextuel
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)


    def preserve_column_roles(self):
        """Réapplique les rôles des colonnes après le tri"""
        # Crée une copie des rôles avant le tri
        old_roles = self.col_roles.copy()
        self.col_roles.clear()

        # Réassigne les rôles selon les nouvelles positions
        for old_col, role in old_roles.items():
            new_col = self.table.horizontalHeader().visualIndex(old_col)
            if new_col != -1:  # Si la colonne existe toujours
                self.col_roles[new_col] = role


    def on_header_clicked(self, logical_index):
        """Gère le tri intelligent (nombre vs texte)"""
 

        header = self.table.horizontalHeader()

        # Déterminer si c'est une colonne numérique
        is_numeric = True
        for row in range(self.table.rowCount()):
            item = self.table.item(row, logical_index)
            if item and not utils.is_number(item.text()):
                is_numeric = False
                break

        # Trier en fonction du type de données
        if is_numeric:
            self.sort_numeric_column(logical_index, header.sortIndicatorOrder())
        else:
            # Laisser QTableWidget gérer le tri alphabétique
            self.table.sortByColumn(logical_index, header.sortIndicatorOrder())

        self.preserve_column_roles()

    def create_status_bar(self):
        self.status_label = QLabel()
        self.statusBar().addWidget(self.status_label, 1)

    def setup_shortcuts(self):
        # Raccourcis clavier
        open_shortcut = QAction(self)
        open_shortcut.setShortcut(QKeySequence("Ctrl+O"))
        open_shortcut.triggered.connect(lambda: io_file.open_file(self))

        self.addAction(open_shortcut)

        save_shortcut = QAction(self)
        save_shortcut.setShortcut(QKeySequence("Ctrl+S"))
        save_shortcut.triggered.connect(lambda: io_file.save_file(self))
        self.addAction(save_shortcut)

        quit_shortcut = QAction(self)
        quit_shortcut.setShortcut(QKeySequence("Ctrl+Q"))
        quit_shortcut.triggered.connect(self.close)
        self.addAction(quit_shortcut)

        about_shortcut = QAction(self)
        about_shortcut.setShortcut(QKeySequence("F1"))
        about_shortcut.triggered.connect(self.show_about)
        self.addAction(about_shortcut)

        search_replace_shortcut = QAction(self)
        search_replace_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        search_replace_shortcut.triggered.connect(self.shortcut_search_replace)
        self.addAction(search_replace_shortcut)

        role_shortcut = QAction(self)
        role_shortcut.setShortcut(QKeySequence("Ctrl+R"))
        role_shortcut.triggered.connect(self.shortcut_set_role)
        self.addAction(role_shortcut)

        truncate_shortcut = QAction(self)
        truncate_shortcut.setShortcut(QKeySequence("Ctrl+K"))
        truncate_shortcut.triggered.connect(self.shortcut_truncate)
        self.addAction(truncate_shortcut)

        transform_shortcut = QAction(self)
        transform_shortcut.setShortcut(QKeySequence("Ctrl+T"))
        transform_shortcut.triggered.connect(self.shortcut_transform)
        self.addAction(transform_shortcut)

    def show_context_menu(self, pos):
        menu = QMenu(self)

        selected_col = self.table.currentColumn()
        if selected_col >= 0:
            # Action pour ajouter une colonne
            add_col_action = QAction("Ajouter une colonne à droite", self)
            add_col_action.triggered.connect(lambda: self.add_column_right(selected_col if selected_col >= 0 else self.table.columnCount() - 1))
            menu.addAction(add_col_action)

            delete_action = QAction("Supprimer la colonne", self)
            delete_action.triggered.connect(lambda: self.delete_column(selected_col))
            menu.addAction(delete_action)

            limit_action = QAction("Limiter à N caractères...", self)
            limit_action.triggered.connect(lambda: menu_transform.limit_column_length(self,selected_col))
            menu.addAction(limit_action)

            role_action = QAction("Définir un rôle...", self)
            role_action.triggered.connect(lambda: self.set_column_role(selected_col))
            menu.addAction(role_action)

            transform_action = QAction("Transformations", self)
            transform_action.triggered.connect(lambda: self.show_transformations_dialog(selected_col))
            menu.addAction(transform_action)

            search_replace_action = QAction("Rechercher / Remplacer...", self)
            search_replace_action.triggered.connect(lambda: self.search_replace_column(selected_col))
            menu.addAction(search_replace_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))
    






    def set_column_role(self, col_index):
        dialog = QDialog(self)
        dialog.setWindowTitle("Définir le rôle de la colonne")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel(f"Colonne {col_index + 1} - Choisir un rôle :")
        layout.addWidget(label)

        # Liste des rôles disponibles
        roles = [
            "Code postal", "Ville", "Pays", "Rue",
            "Nom de l'adresse", "Téléphone",
            "Numérique", "Texte", "Code ISO"
        ]

        self.role_group = QButtonGroup()

        current_role = self.col_roles.get(col_index, "")

        for role in roles:
            radio = QRadioButton(role)
            if role == current_role:
                radio.setChecked(True)
            self.role_group.addButton(radio)
            layout.addWidget(radio)

        # Bouton Valider
        validate_btn = QPushButton("Valider")
        validate_btn.clicked.connect(lambda: self.validate_role(col_index, dialog))
        layout.addWidget(validate_btn)

        dialog.exec_()

    def validate_role(self, col_index, dialog):
        selected_role = self.role_group.checkedButton()
        if not selected_role:
            QMessageBox.critical(self, "Erreur", "Veuillez choisir un rôle.")
            return

        role = selected_role.text()
        self.col_roles[col_index] = role

        # Appliquer la transformation si nécessaire
        if role == "Nom de l'adresse":
            self.transform_address_primary(col_index)
        elif role == "Numérique":
            self.transform_numeric(col_index)
        elif role == "Code ISO":
            self.transform_iso_code(col_index)

        dialog.close()
        self.show_message(f"Rôle '{role}' attribué à la colonne {col_index + 1}")



    def _validate_column_index(self, col_index):
        """Valide que l'index de colonne existe"""
        if col_index < 0 or col_index >= self.table.columnCount():
            QMessageBox.warning(self, "Erreur", "Index de colonne invalide")
            return False
        return True



    def _show_error_message(self, error):
        """Affiche les erreurs"""
        QMessageBox.critical(self, "Erreur", f"Échec de la suppression : {str(error)}")




    # ===== Fonctions utilitaires =====

    def show_message(self, message, duration=7000):
        self.status_label.setText(message)
        
        # Afficher aussi dans la console Python (si présente)
        if hasattr(self, "console") and self.console:
            self.console._print(f'<span style="color:#66d9ef;">[INFO]</span> {message}')


        if duration > 0:
            QTimer.singleShot(duration, lambda: self.status_label.setText(""))

    def show_about(self):
        about_text = (
            f"{version.APP_NAME}\n"
            f"Version : {version.VERSION}\n"
            f"Auteur : {version.AUTHOR}\n\n"
            f"{version.DESCRIPTION}"
        )
        QMessageBox.about(self, f"À propos de {version.APP_NAME}", about_text)

    def has_data(self):
        return self.table.rowCount() > 0 and self.table.columnCount() > 0

    def get_table_data(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    # ===== Raccourcis clavier =====

    def shortcut_search_replace(self):
        col = self.table.currentColumn()
        if col >= 0:
            self.search_replace_column(col)
        else:
            self.show_message("Aucune colonne sélectionnée !")

    def shortcut_set_role(self):
        col = self.table.currentColumn()
        if col >= 0:
            self.set_column_role(col)
        else:
            self.show_message("Aucune colonne sélectionnée !")

    def shortcut_truncate(self):
        col = self.table.currentColumn()
        if col >= 0:
            menu_transform.limit_column_length(self, col)
        else:
            self.show_message("Aucune colonne sélectionnée !")

    def shortcut_transform(self):
        col = self.table.currentColumn()
        if col >= 0:
            self.show_transformations_dialog(col)
        else:
            self.show_message("Aucune colonne sélectionnée !")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Clients & Châtiments")
    app.setOrganizationName("A Paul")
    app.setApplicationDisplayName("Clients & Châtiments")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())