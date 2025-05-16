from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QMenuBar, QMenu, QFileDialog, QMessageBox,
                              QInputDialog, QLabel, QPushButton, QDialog, QRadioButton,QDockWidget,
                              QButtonGroup, QLineEdit, QCheckBox, QFrame)
import utils
# Generique actions 
def sort_table(self, logical_index, order):
        """Tri personnalisé qui gère les types de données"""
        self.table.blockSignals(True)  # Bloquer les signaux pendant le tri

        # Déterminer si la colonne contient des nombres
        is_numeric = all(utils.is_number(self.table.item(row, logical_index).text())
                         for row in range(self.table.rowCount()) if self.table.item(row, logical_index))

        # Trier les éléments
        items = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, logical_index)
            key = float(item.text()) if is_numeric and item.text() else item.text()
            items.append((key, row))

        # Trier selon l'ordre demandé
        items.sort(reverse=(order == Qt.DescendingOrder), key=lambda x: x[0])

        # Réorganiser les lignes
        for new_row, (_, old_row) in enumerate(items):
            self.table.insertRow(new_row)
            for col in range(self.table.columnCount()):
                self.table.setItem(new_row, col, self.table.takeItem(old_row, col))
            self.table.removeRow(old_row)

        self.table.blockSignals(False)  # Débloquer les signaux

def sort_numeric_column(self, col, order):
        """Tri personnalisé pour les colonnes numériques"""
        items = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col)
            value = float(item.text()) if item and item.text() else 0.0
            items.append((value, row))

        # Trier selon l'ordre demandé
        items.sort(reverse=(order == Qt.DescendingOrder), key=lambda x: x[0])

        # Réorganiser les lignes
        self.table.blockSignals(True)
        for new_row, (_, old_row) in enumerate(items):
            self.table.insertRow(self.table.rowCount())
            for column in range(self.table.columnCount()):
                self.table.setItem(new_row, column, self.table.takeItem(old_row, column))
            self.table.removeRow(old_row)
        self.table.blockSignals(False)

def add_column_right(self, col_index):
        """Ajoute une nouvelle colonne à droite de la colonne spécifiée"""

        try:
            current_cols = self.table.columnCount()

            # Cas où le tableau est vide
            if current_cols == 0:
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderItem(0, QTableWidgetItem("Nouvelle colonne"))
                return True

            # Cas normal
            insert_pos = col_index + 1 if col_index >= 0 else current_cols


            self.table.insertColumn(insert_pos)
            # Initialiser toutes les cellules avec une chaîne vide
            for row in range(self.table.rowCount()):
                self.table.setItem(row, insert_pos, QTableWidgetItem(""))
            self.table.setHorizontalHeaderItem(insert_pos, QTableWidgetItem(f"Colonne {insert_pos + 1}"))

            # Mettre à jour les rôles si nécessaire
            if hasattr(self, 'col_roles'):
                # Décaller les rôles des colonnes suivantes
                new_roles = {}
                for col, role in self.col_roles.items():
                    if col >= insert_pos:
                        new_roles[col + 1] = role
                    else:
                        new_roles[col] = role
                self.col_roles = new_roles

            # Mettre à jour les headers si existants
            if hasattr(self, 'headers') and self.headers:
                self.headers.insert(insert_pos, f"Colonne {insert_pos + 1}")
            self.show_message(f"Colonne ajoutée à la position {insert_pos + 1}")

            new_name, ok = QInputDialog.getText(
                self,
                "Nom de la colonne",
                "Entrez le nom de la nouvelle colonne :",
                text=f"Colonne {insert_pos + 1}"
            )

            if ok:
                self.table.setHorizontalHeaderItem(insert_pos, QTableWidgetItem(new_name))
                if hasattr(self, 'headers') and self.headers:
                    self.headers[insert_pos] = new_name
                    self.show_message(f"Colonne nommée : {new_name}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la colonne : {str(e)}")
            return False


def delete_column(self, col_index):
        """Supprime une colonne du tableau avec gestion des erreurs"""
        print("deleted_column", col_index)
        if not self._validate_column_index(col_index):
            return False

        try:
            self.table.removeColumn(col_index)
            _update_after_column_deletion(self, col_index)
            _show_success_message(self, col_index)
            return True
        except Exception as e:
            self._show_error_message(e)
            return False
        
def _update_after_column_deletion(self, deleted_index):
        """Met à jour les métadonnées après suppression"""
        # Mettre à jour les rôles de colonne
        self.col_roles.pop(deleted_index, None)

        # Décaller les index des colonnes suivantes
        new_roles = {}
        for col, role in self.col_roles.items():
            if col > deleted_index:
                new_roles[col - 1] = role
            elif col < deleted_index:
                new_roles[col] = role
        self.col_roles = new_roles

        # Mettre à jour les en-têtes si nécessaire
        if hasattr(self, 'headers'):
            self.headers.pop(deleted_index)
        
def _show_success_message(self, col_index):
        """Affiche un message de confirmation"""
        self.show_message(f"Colonne {col_index + 1} supprimée avec succès")

        self.statusBar().showMessage(f"Colonne {col_index + 1} supprimée avec succès", 3000)

