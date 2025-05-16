import csv
import os
import re
import openpyxl
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QMenuBar, QMenu, QFileDialog, QMessageBox,
                              QInputDialog, QLabel, QPushButton, QDialog, QRadioButton,QDockWidget,
                              QButtonGroup, QLineEdit, QCheckBox, QFrame)

def open_file(self):
        def guess_separator(line):
            """Devine le séparateur le plus probable dans une ligne CSV"""
            if not line:
                return ';' 
            candidates = [',', ';', '\t', '|']
            counts = {sep: line.count(sep) for sep in candidates}
            best_sep = max(counts, key=counts.get)

            # Si tous les counts sont à 0 (aucun séparateur trouvé)
            if counts[best_sep] == 0:
                return ';'  # valeur par défaut

            return best_sep
        self.table.setSortingEnabled(False)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier Excel ou CSV",
            "",
            "Fichiers Excel ou CSV (*.xlsx *.csv);;Tous les fichiers (*.*)"
        )

        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            data = []

            if ext == ".xlsx":
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                for row in ws.iter_rows(values_only=True):
                    data.append(list(row))
            elif ext == ".csv":
                with open(file_path, newline='', encoding='utf-8') as f:
                    first_line = f.readline()
                    sep = guess_separator(first_line)
                    self.show_message(f"Fichier CSV chargé avec séparateur détecté : '{sep}'")
                    f.seek(0)  # Revenir au début
                    reader = csv.reader(f, delimiter=sep)
                    data = [row for row in reader]
            else:
                QMessageBox.critical(self, "Erreur", "Format de fichier non pris en charge.")
                return

            self.setWindowTitle(f"{file_path} - {len(data)} lignes")
            self.headers = data[0]

            self.table.setRowCount(len(data) - 1)
            self.table.setColumnCount(len(self.headers))

            for col_idx, header in enumerate(self.headers):
                self.table.setHorizontalHeaderItem(col_idx, QTableWidgetItem(str(header)))

            for row_idx, row in enumerate(data[1:]):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
            # Réactiver le tri une fois les données chargées
            self.table.setSortingEnabled(True)

            # Configurer le header pour permettre le tri
            header = self.table.horizontalHeader()
            header.setSortIndicatorShown(True)
            header.setSectionsClickable(True)
            self.show_message(f"Fichier chargé : {file_path}")
            self.show_message(f"Nombre de lignes : {len(data) - 1}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier :\n{str(e)}")

def save_file(self):
        if not self.has_data():
            QMessageBox.critical(self, "Erreur", "Aucune donnée à sauvegarder.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            "",
            "Fichier CSV (*.csv);;Fichier Excel (*.xlsx)"
        )

        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        data = self.get_table_data()

        try:
            if ext == ".xlsx":
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(self.headers)
                for row in data:
                    ws.append(row)
                wb.save(file_path)
            elif ext == ".csv":
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(self.headers)
                    writer.writerows(data)
            else:
                QMessageBox.critical(self, "Erreur", "Extension non prise en charge.")
                return

            self.show_message(f"Fichier sauvegardé avec succès : {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

def save_segments(self):
        if not self.has_data():
            QMessageBox.critical(self, "Erreur", "Aucune donnée à sauvegarder.")
            return

        data = self.get_table_data()

        segment_size, ok = QInputDialog.getInt(
            self,
            "Taille segment",
            "Nombre de lignes par segment (hors en-tête) :",
            min=1
        )

        if not ok:
            return

        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sauvegarde")
        if not folder:
            return

        base_name, ok = QInputDialog.getText(
            self,
            "Nom de base",
            "Nom de base du fichier ? (ex: segment => segment_0-99.csv)"
        )

        if not ok or not base_name:
            return

        try:
            for i in range(0, len(data), segment_size):
                start = i
                end = min(i + segment_size, len(data))
                segment = data[start:end]

                file_name = f"{base_name}_{start}-{end - 1}.csv"
                file_path = os.path.join(folder, file_name)

                with open(file_path, mode="w", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(self.headers)
                    writer.writerows(segment)

            self.show_message(f"Segments sauvegardés dans {folder}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
