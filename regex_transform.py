
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QMenuBar, QMenu, QFileDialog, QMessageBox,
                              QInputDialog, QLabel, QPushButton, QDialog, QRadioButton,QDockWidget,
                              QButtonGroup, QLineEdit, QCheckBox, QFrame,QComboBox)
import re                            
                        
class RegexTransformDialog(QDialog):
    predefined_patterns = {
        "Numérique (entier ou décimal)": r"\d+(\.\d+)?",
        "Numérique dans la cellule": r"\d+",
        "Texte (lettres uniquement)": r"[a-zA-Z]+",
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Téléphone (avec indicatif)": r"\+?\d[\d\s\-]{7,}",
        "Téléphone (sans indicatif)": r"\b0\d[\d\s\-]{7,}\b"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transformation par regex")
        self.setModal(True)
        layout = QVBoxLayout()

        # Regex input
        self.regex_input = QLineEdit()
        layout.addWidget(QLabel("Expression régulière personnalisée :"))
        layout.addWidget(self.regex_input)

        # Liste des patterns prédéfinis
        self.pattern_selector = QComboBox()
        self.pattern_selector.addItem("— Sélectionner un modèle —")
        for label in self.predefined_patterns:
            self.pattern_selector.addItem(label)
        layout.addWidget(QLabel("Ou choisir un modèle courant :"))
        layout.addWidget(self.pattern_selector)

        # Bouton pour copier le modèle choisi
        self.insert_button = QPushButton("Utiliser ce modèle")
        self.insert_button.clicked.connect(self.insert_selected_pattern)
        layout.addWidget(self.insert_button)

        # Mode d'application
        self.replacement_input = QLineEdit()
        self.replacement_input.setPlaceholderText("Valeur de remplacement (laisser vide pour suppression ou extraction)")
        layout.addWidget(QLabel("Valeur de remplacement :"))
        layout.addWidget(self.replacement_input)

        self.mode_keep_match = QRadioButton("Conserver uniquement ce qui match")
        self.mode_replace_match = QRadioButton("Remplacer ce qui match")
        self.mode_keep_match.setChecked(True)
        layout.addWidget(QLabel("Mode d'application :"))
        layout.addWidget(self.mode_keep_match)
        layout.addWidget(self.mode_replace_match)

        # Fallback
        self.keep_original_if_no_match = QCheckBox("Garder la valeur originale si aucun match")
        self.keep_original_if_no_match.setChecked(True)
        layout.addWidget(self.keep_original_if_no_match)

        # Validation
        self.ok_button = QPushButton("Appliquer")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def insert_selected_pattern(self):
        label = self.pattern_selector.currentText()
        if label in self.predefined_patterns:
            self.regex_input.setText(self.predefined_patterns[label])

    def get_values(self):
        return (
            self.regex_input.text(),
            self.replacement_input.text(),
            self.mode_keep_match.isChecked(),
            self.keep_original_if_no_match.isChecked()
        )


def apply_regex_to_column(self, col_index):
    if not self._validate_column_index(col_index):
        return

    dialog = RegexTransformDialog(self)
    if dialog.exec_() == QDialog.Accepted:
        pattern_str, replacement, keep_only_match, keep_original = dialog.get_values()

        try:
            pattern = re.compile(pattern_str)
        except re.error as e:
            self._show_error_message(f"Regex invalide : {str(e)}")
            return

        changed_count = 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)
            if item:
                original_text = item.text()
                if keep_only_match:
                    matches = pattern.findall(original_text)
                    if matches:
                        new_text = "".join(matches)  # ou " ".join(matches) si tu veux les séparer
                    else:
                        new_text = original_text if keep_original else ""
                else:
                    if pattern.search(original_text):
                        new_text = pattern.sub(replacement, original_text)
                    else:
                        new_text = original_text if keep_original else ""
                if new_text != original_text:
                    self.table.setItem(row, col_index, QTableWidgetItem(new_text))
                    changed_count += 1

        self.show_message(f"{changed_count} cellules modifiées avec la regex.")
