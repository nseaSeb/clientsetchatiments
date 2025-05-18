from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QMenuBar, QMenu, QFileDialog, QMessageBox,
                              QInputDialog, QLabel, QPushButton, QDialog, QRadioButton,QDockWidget,
                              QButtonGroup, QLineEdit, QCheckBox, QFrame)
import re
from pays import iso
import utils
# Tranformations cellules de selected_column
def show_transformations_dialog(self, col_index):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choisir une transformation")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel(f"Colonne {col_index + 1} - Choisir une transformation :")
        layout.addWidget(label)

        transformations = [
            "Numérique",
            "Limiter à N caractères",
            "Remplacer pays par code ISO",
            "Adresse principale"
        ]

        self.transform_group = QButtonGroup()

        for transform in transformations:
            radio = QRadioButton(transform)
            self.transform_group.addButton(radio)
            layout.addWidget(radio)

        # Bouton Valider
        validate_btn = QPushButton("Valider")
        validate_btn.clicked.connect(lambda: apply_transformation(self,col_index, dialog))
        layout.addWidget(validate_btn)

        dialog.exec_()

   
def apply_transformation(self, col_index, dialog):
        selected_transform = self.transform_group.checkedButton()
        if not selected_transform:
            QMessageBox.critical(self, "Erreur", "Veuillez choisir une transformation.")
            return

        transform = selected_transform.text()

        if transform == "Numérique":
            transform_numeric(self, col_index)
        elif transform == "Limiter à N caractères":
            limit_column_length(self, col_index)
        elif transform == "Remplacer pays par code ISO":
            transform_iso_code(self,col_index)
        elif transform == "Adresse principale":
            transform_address_primary(self,col_index)

        dialog.close()

def limit_column_length(self, col_index):
        dialog = QDialog(self)
        dialog.setWindowTitle("Limiter à N caractères")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel("Choisir une limite :")
        layout.addWidget(label)

        # Boutons pour les valeurs prédéfinies
        btn_frame = QFrame()
        btn_layout = QtWidgets.QHBoxLayout(btn_frame)

        for val in [100, 128, 255, 510]:
            btn = QPushButton(str(val))
            btn.clicked.connect(lambda _, v=val: apply_limit(self,col_index, v, dialog))
            btn_layout.addWidget(btn)

        layout.addWidget(btn_frame)

        # Champ de saisie personnalisé
        custom_label = QLabel("Ou saisir une valeur :")
        layout.addWidget(custom_label)

        self.limit_input = QLineEdit()
        layout.addWidget(self.limit_input)

        # Bouton Valider
        validate_btn = QPushButton("Valider")
        validate_btn.clicked.connect(lambda: validate_custom_limit(self, col_index, dialog))
        layout.addWidget(validate_btn)

        dialog.exec_()

def apply_search_replace(self, col_index, dialog):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        case_sensitive = self.case_check.isChecked()
        increment = self.increment_check.isChecked()
        contains = self.contains_check.isChecked()

        counter = 1
        changes = 0

        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)
            if not item:
                continue

            cell_text = item.text()
            match = False

            if not search_text:
                # Recherche des cellules vides
                match = not cell_text.strip()
            else:
                if contains:
                    # Mode "contient"
                    if case_sensitive:
                        match = search_text in cell_text
                    else:
                        match = search_text.lower() in cell_text.lower()
                else:
                    # Mode "correspondance exacte"
                    if case_sensitive:
                        match = (cell_text == search_text)
                    else:
                        match = (cell_text.lower() == search_text.lower())

            if match:
                if contains and search_text:
                    # Remplacer uniquement la partie trouvée
                    if case_sensitive:
                        new_text = cell_text.replace(
                            search_text,
                            replace_text if not increment else f"{replace_text} {counter}"
                        )
                    else:
                        # Pour ne pas respecter la casse tout en préservant le format d'origine
                        pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                        repl = replace_text if not increment else f"{replace_text} {counter}"
                        new_text = pattern.sub(repl, cell_text)

                    item.setText(new_text)
                    if increment:
                        counter += 1
                else:
                    # Remplacement complet de la cellule
                    if increment:
                        item.setText(f"{replace_text} {counter}")
                        counter += 1
                    else:
                        item.setText(replace_text)
                changes += 1

        dialog.close()
        self.show_message(f"{changes} remplacement(s) effectué(s).")

def transform_numeric(self, col_index):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)
            if item:
                numeric_value = utils.get_string_as_number(item.text().replace(" ", ""))
                item.setText(str(numeric_value))

        self.show_message(f"Transformation numérique appliquée à la colonne {col_index + 1}")

def transform_iso_code(self, col_index):
        mapping = {entry["pays"].lower(): entry["iso"] for entry in iso}
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Traitement ISO")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel("Que faire si un pays n'est pas reconnu ?")
        layout.addWidget(label)

        self.iso_group = QButtonGroup()

        # Options
        empty_option = QRadioButton("Laisser vide")
        self.iso_group.addButton(empty_option)
        layout.addWidget(empty_option)

        custom_option = QRadioButton("Remplacer par un code personnalisé :")
        self.iso_group.addButton(custom_option)
        layout.addWidget(custom_option)

        self.custom_iso_input = QLineEdit("FR")
        layout.addWidget(self.custom_iso_input)

        empty_option.setChecked(True)

        # Bouton Valider
        validate_btn = QPushButton("Valider")
        validate_btn.clicked.connect(lambda: apply_iso_transform(self,col_index, mapping, dialog))
        layout.addWidget(validate_btn)

        dialog.exec_()

def apply_iso_transform(self, col_index, mapping, dialog):
        selected_option = self.iso_group.checkedButton()
        custom_value = ""

        if selected_option.text().startswith("Remplacer"):
            custom_value = self.custom_iso_input.text().strip().upper()
            if not custom_value:
                QMessageBox.critical(self, "Erreur", "Veuillez entrer un code personnalisé.")
                return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)
            if item:
                country = item.text().strip().lower()
                iso_code = mapping.get(country, custom_value if selected_option.text().startswith("Remplacer") else "")
                item.setText(iso_code)

        dialog.close()
        self.show_message(f"Transformation ISO appliquée à la colonne {col_index + 1}")

def search_replace_column(self, col_index):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Rechercher / Remplacer - Colonne {col_index + 1}")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Champ de recherche
        search_label = QLabel("Texte à rechercher (laisser vide pour cellules vides) :")
        layout.addWidget(search_label)

        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        # Champ de remplacement
        replace_label = QLabel("Remplacer par :")
        layout.addWidget(replace_label)

        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_input)

        # Options
        self.contains_check = QCheckBox("Rechercher si contenu dans la cellule")
        self.contains_check.setChecked(True)
        layout.addWidget(self.contains_check)

        self.case_check = QCheckBox("Respecter la casse")
        layout.addWidget(self.case_check)

        self.increment_check = QCheckBox("Incrémenter (ex: Nom 1, Nom 2, ...)")
        layout.addWidget(self.increment_check)

        # Bouton Appliquer
        apply_btn = QPushButton("Remplacer")
        apply_btn.clicked.connect(lambda: apply_search_replace(self,col_index, dialog))
        layout.addWidget(apply_btn)

        dialog.exec_()

def apply_limit(self, col_index, limit, dialog=None):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)
            if item and item.text():
                text = item.text()
                if len(text) > limit:
                    item.setText(text[:limit])

        if dialog:
            dialog.close()

        self.show_message(f"Limite de {limit} caractères appliquée à la colonne {col_index + 1}")
def validate_custom_limit(self, col_index, dialog):
        try:
            limit = int(self.limit_input.text())
            if limit > 0:
                self.apply_limit(col_index, limit, dialog)
            else:
                QMessageBox.critical(self, "Erreur", "Veuillez entrer une valeur positive.")
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Valeur invalide.")

def transform_address_primary(self, col_index):
        # Trouver la colonne de référence (code postal, ville, rue ou pays)
        reference_col = None
        for idx, role in self.col_roles.items():
            if role in ["Code postal", "Ville", "Rue", "Pays"]:
                reference_col = idx
                break

        if reference_col is None:
            QMessageBox.critical(self, "Erreur",
                                 "Aucune colonne avec le rôle 'Code postal / Ville / Rue / Pays' n'a été définie.")
            return

        for row in range(self.table.rowCount()):
            ref_item = self.table.item(row, reference_col)
            if ref_item and ref_item.text().strip():
                item = self.table.item(row, col_index)
                if not item or not item.text().strip():
                    self.table.setItem(row, col_index, QTableWidgetItem("Adresse principale"))

        self.show_message(f"Transformation 'Adresse principale' appliquée à la colonne {col_index + 1}")
