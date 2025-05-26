from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QTableWidgetItem, QPlainTextEdit
from PySide6.QtCore import Qt, Signal,QEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QTableWidgetItem, QPlainTextEdit, QPushButton,QSplitter
)

import sys
from io import StringIO
import re
import numpy as np

class PythonConsole(QWidget):
    execute = Signal(str)  # Signal émis quand du code est exécuté

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_python_env()
        self.show_welcome_message()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Vertical)

        # Console de sortie
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #001400;
                color: #00ff00;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 11pt;
                border: none;
            }
        """)
        splitter.addWidget(self.output)

        # Bloc contenant l'entrée et le bouton Exécuter
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("Tapez du code Python ici... shift + enter pour exécuter")
        self.input.setMinimumHeight(40)
        self.input.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00ff00;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 11pt;
                padding: 4px;
                border: 1px solid #00bb00;
            }
        """)
        self.input.installEventFilter(self)
        input_layout.addWidget(self.input)
        # Conteneur vertical pour aligner le bouton en bas
        button_container = QVBoxLayout()
        button_container.addStretch()  # pousse le bouton en bas

        execute_button = QPushButton("▶")
        #execute_button.setFixedWidth(100)
        execute_button.clicked.connect(self.execute_code)
        execute_button.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                color: #00ff00;
                font-weight: bold;
                font-family: Consolas, Monaco, monospace;
                padding: 4px 8px;
                border: 1px solid #00aa00;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005500;
            }
            QPushButton:pressed {
                background-color: #007700;
            }
        """)
        button_container.addWidget(execute_button)

        input_layout.addLayout(button_container)
    

        splitter.addWidget(input_container)

        # Taille par défaut des zones (facultatif)
        splitter.setSizes([300, 100])

        layout.addWidget(splitter)
        #self.setStyleSheet("background-color: #000000;")  # Fond général

    def eventFilter(self, source, event):
        if source == self.input and event.type() == QEvent.KeyPress:
            if (event.key() in (Qt.Key_Return, Qt.Key_Enter)) and (
                event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.ShiftModifier
            ):
                self.execute_code()
                return True  # événement traité

        return super().eventFilter(source, event)


    def setup_python_env(self):
        import builtins

        # Attache les fonctions utiles au scope global
        builtins.get_col = self._safe_get_col
        builtins.set_col = self.set_column_values
        builtins.get_cell = self._safe_get_cell_text
        builtins.set_cell = self._safe_set_cell
        builtins.rowcount = lambda: self.locals['table'].rowCount()
        builtins.colcount = lambda: self.locals['table'].columnCount()

        """Configure l'environnement Python"""
        self.locals = {
            'app': self.parent(),
            're': re,
            'math': __import__('math'),  # optionnel
            'len': len,
            'str': str,
            'import numpy as np': __import__('numpy'),
            'get_cell': self._safe_get_cell_text,
            'set_cell': self._safe_set_cell,
            'get_col': self._safe_get_col,
            'get_row': self._safe_get_row,
            'table': None,  # Sera remplacé par la référence au tableau
            'print': self._print,
            'help': self.show_help,
            'QTableWidgetItem': QTableWidgetItem,
            'show_headers': self.show_headers,
            'sum_col': self.sum_column,
            'set_col': self.set_column_values,
            'rowcount': lambda: self.locals['table'].rowCount(),
            'colcount': lambda: self.locals['table'].columnCount(),
            'clear_col': lambda col: [self.locals['table'].setItem(r, col, QTableWidgetItem(""))
                                      for r in range(self.locals['table'].rowCount())],
            'h': self.show_help,
            'show_doc': self.show_doc
        }
        self.locals['regex_col'] = self.regex_col
        self._redirect_stdout()
    def show_doc(self, obj):
        """
        Affiche dynamiquement la docstring d'une fonction ou d'un objet.
        Exemple : show_doc(table.setItem)
        """
        import inspect

        try:
            doc = inspect.getdoc(obj)
            if not doc:
                self._print("Aucune documentation disponible.")
            else:
                self._print(f"Documentation de {obj} :\n" + "-"*50 + f"\n{doc}")
            return "Documentation affichée"
        except Exception as e:
            self._print(f"Erreur lors de l'inspection : {str(e)}")
            return f"Erreur : {str(e)}"

    def show_welcome_message(self):
        """Affiche un message de bienvenue avec des retours ligne HTML"""
        welcome_msg = """
        <span style="color:#a6e22e;font-weight:bold;">
        ╔════════════════════════╗<br>
        ║ Clients Et Châtiments. ║<br>
        ╚════════════════════════╝
        </span><br><br>

        <span style="color:#66d9ef;">Bienvenue dans la console Python interactive!</span><br><br>

        Vous pouvez accéder aux objets suivants :<br>
        - <span style="color:#f92672;">table</span> : référence au tableau principal<br>
        - <span style="color:#f92672;">app</span> : référence à l'application<br><br>

        <span style="color:#e6db74;">Exemples de commandes :</span><br>
        ➤ print(table.rowCount())<br>
        ➤ print(table.item(0, 0).text())<br>
        ➤ help()<br><br>

        Tapez <span style="color:#a6e22e;">help()</span> pour plus d'informations.
        """
  

        self.output.append(welcome_msg)

    def show_help(self):
        """Affiche l'aide enrichie de la console"""
        help_text = """
        <span style="color:#a6e22e;font-weight:bold;">
        ╔══════╗<br>
        ║ AIDE ║<br>
        ╚══════╝<br>
        </span>
        <br>
        <span style="color:#66d9ef;">shift + enter pour exécuter</span>
        <br>
        <span style="color:#66d9ef;">Objets disponibles :</span>
        <br>
        ➤ <span style="color:#f92672;">table</span> : tableau principal (QTableWidget)
        <br>
        ➤ <span style="color:#f92672;">app</span> : fenêtre principale
        <br>
        ➤ <span style="color:#f92672;">QTableWidgetItem</span> : classe pour créer de nouvelles cellules
        <br>

        <span style="color:#66d9ef;">Fonctions pratiques :</span>
        <br>
        ➤ print(...)                   - Affiche dans la console
        <br>
        ➤ rowcount()                  - Nombre de lignes du tableau <br>
        ➤ colcount()                  - Nombre de colonnes du tableau <br>
        ➤ get_col(col)                - Liste des valeurs d'une colonne (ex: get_col(0)) <br>
        ➤ set_col(col, func)          - Affecte les valeurs via une fonction (voir exemples) <br>
        ➤ clear_col(col)              - Vide toutes les cellules d'une colonne <br>
        ➤ get_cell()                  - Renvoit la valeur d'une cellule <br>
        ➤ show_headers()              - Renvoit l'index et le nom des colonnes <br>
        ➤ sum_col(col_index)                   - Renvoit la sommation de la colonne <br>
       
        <span style="color:#66d9ef;">Exemples d'analyse :</span><br>
        ➤ print(table.item(0, 0).text())               - Affiche la cellule [0, 0]<br>
        ➤ [table.item(r, 1).text() for r in range(rowcount())]      - Liste des valeurs de la colonne 2<br>
        ➤ sum(float(table.item(r, 2).text()) for r in range(rowcount()))  - Somme des valeurs en col. 3<br>
        <br>
        <span style="color:#66d9ef;">Exemples d'édition avec set_col :</span><br>
        ➤ set_col(0, lambda r: f"Client {r}")          - Colonne 1 = "Client 0", "Client 1", ...<br>
        ➤ set_col(1, lambda r: "FIXED")                - Colonne 2 = "FIXED" partout<br>
        ➤ set_col(2, lambda r: get_col(2)[r].upper())  - Met en majuscules<br>
        ➤ set_col(3, lambda r: "")                     - Vide toute la colonne 4<br>
        ➤ set_col(4, lambda r: ">> " + table.item(r, 4).text() if table.item(r, 4) else "")  - Ajoute un préfixe<br>
        <br>
        <span style="color:#66d9ef;">Aide au développement :</span><br>
        ➤ dir(table)               - Liste les méthodes de QTableWidget<br>
        ➤ help(table.setItem)      - Aide Python sur une méthode<br>
        ➤ regex_col(col, pattern, mode='extract'|'replace', replacement='', fallback='')<br>
        - Applique une transformation regex<br>
        - Exemple : regex_col(1, r'\\d+')<br>

        <span style="color:#e6db74;">Exemple de code :</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;def clean_phone(val):<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;val = val.strip()<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if val.startswith("+"):<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return "+" + re.sub(r"[^\d]", "", val[1:])<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;digits = re.sub(r"[^\d]", "", val)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return "+" + digits<br><br>

        &nbsp;&nbsp;&nbsp;&nbsp;for r in range(rowcount()):<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;original = get_col(6)[r]<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cleaned = clean_phone(original)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;set_cell(r, 6, cleaned)<br>


        """
   

        self._print(help_text)
        return "Aide affichée"

    def _redirect_stdout(self):
        """Redirige stdout vers la console"""
        self._stdout = sys.stdout
        self._stringio = StringIO()
        sys.stdout = self._stringio

    def _print(self, *args, **kwargs):
        """Implémentation personnalisée de print()"""
        text = ' '.join(str(arg) for arg in args)
        self.output.append(text)

    def _check_table_ready(self):
        """Vérifie si le tableau est disponible et valide"""
        if 'table' not in self.locals or not self.locals['table']:
            self._print("⚠️ Erreur : Référence au tableau non définie. Utilisez set_table_reference()")
            return False
        return True
    def show_headers(self):
        """Affiche les entêtes de colonnes et leur index"""
        if not self._check_table_ready():
            return

        table = self.locals['table']
        headers = []
        for col in range(table.columnCount()):
            item = table.horizontalHeaderItem(col)
            header = item.text() if item else "(sans nom)"
            headers.append(f"{col}: {header}")

        result = "\n".join(headers)
        self._print(result)
    def sum_column(self, col_index):
        """Fait la somme des valeurs numériques d'une colonne donnée."""
        if not self._check_table_ready():
            return 0

        total = 0.0
        errors = 0
        for r in range(self.locals['table'].rowCount()):
            text = self._safe_get_cell_text(r, col_index)
            try:
                total += float(text)
            except ValueError:
                errors += 1  # on ignore les erreurs de conversion

        if errors:
            self._print(f"⚠️ {errors} valeur(s) ignorée(s) (non numériques).")

        self._print(f"Somme de la colonne {col_index} : {total}")
        return total

    def _safe_get_cell(self, row, col):
        """Récupère une cellule de manière sécurisée"""
        if not self._check_table_ready():
            return None

        try:
            return self.locals['table'].item(row, col)
        except Exception as e:
            self._print(f"⛔ Erreur d'accès à la cellule [{row},{col}] : {str(e)}")
            return None

    def _safe_get_cell_text(self, row, col, default=""):
        """Récupère le texte d'une cellule avec valeur par défaut"""
        cell = self._safe_get_cell(row, col)
        return cell.text() if cell else default

    def _safe_get_row(self, row_index):
        """Récupère une ligne entière sous forme de liste avec gestion sécurisée"""
        if not self._check_table_ready():
            return []

        try:
            row_data = []
            table = self.locals['table']
            col_count = table.columnCount()

            for col in range(col_count):
                item = table.item(row_index, col)
                row_data.append(item.text() if item else "")

            return row_data

        except Exception as e:
            self._print(f"⛔ Erreur lecture ligne {row_index} : {str(e)}")
            return []

    def _safe_get_col(self, col_index):
        """Récupère une colonne entière avec gestion d'erreur"""
        if not self._check_table_ready():
            return []

        try:
            return [
                self._safe_get_cell_text(r, col_index)
                for r in range(self.locals['table'].rowCount())
            ]
        except Exception as e:
            self._print(f"⛔ Erreur lecture colonne {col_index} : {str(e)}")
            return []

    def _safe_set_cell(self, row, col, value):
        """Modifie une cellule de manière sécurisée"""
        if not self._check_table_ready():
            return False

        try:
            item = self.locals['table'].item(row, col) or QTableWidgetItem()
            item.setText(str(value))
            self.locals['table'].setItem(row, col, item)
            return True
        except Exception as e:
            self._print(f"⛔ Erreur écriture cellule [{row},{col}] : {str(e)}")
            return False

    def set_column_values(self, col_index, generator_func):
        """
        Remplit une colonne entière avec les valeurs retournées par generator_func(row).
        Exemple :
            set_col(2, lambda row: f"Ligne {row}")
        """
        from PySide6.QtWidgets import QTableWidgetItem

        if not self.locals.get("table"):
            self._print("Erreur : table non définie.")
            return

        table = self.locals["table"]
        for row in range(table.rowCount()):
            value = generator_func(row)
            item = table.item(row, col_index)
            if item:
                item.setText(str(value))
            else:
                table.setItem(row, col_index, QTableWidgetItem(str(value)))
    def regex_col(self, col_index, pattern, mode='extract', replacement='', fallback=''):
        """
        Applique une transformation par regex à une colonne entière.
        """
        if not self._check_table_ready():
            return

        try:
            compiled = re.compile(pattern)
        except re.error as e:
            self._print(f"Regex invalide : {str(e)}")
            return

        table = self.locals['table']
        for r in range(table.rowCount()):
            item = table.item(r, col_index)
            text = item.text() if item else ""
            if mode == 'extract':
                matches = compiled.findall(text)
                new_val = "".join(matches) if matches else fallback
            elif mode == 'replace':
                new_val = compiled.sub(replacement, text) if compiled.search(text) else fallback
            else:
                new_val = text

            if not item:
                item = QTableWidgetItem()
                table.setItem(r, col_index, item)
            item.setText(new_val)

        self._print(f"regex_col() appliqué à la colonne {col_index}")




    def execute_code(self):
        """Exécute le code saisi"""
        #code = self.input.text()
        code = self.input.toPlainText()

        if not code.strip():
            return

        # Afficher la commande dans la console
        self.output.append(f'<span style="color:#e6db74;">>>> {code}</span>')
        self.input.clear()

        try:
            # Exécuter le code et capturer le résultat
            result = eval(code, globals(), self.locals)

            # Si le résultat n'est pas None, l'afficher
            if result is not None:
                self.output.append(f'<span style="color:#a6e22e;">{result}</span>')

            # Émettre le signal avec la commande exécutée
            self.execute.emit(code)

        except SyntaxError:
            # Si eval échoue, essayer exec
            try:
                exec(code, globals(), self.locals)

                # Capturer la sortie stdout
                output = self._stringio.getvalue()
                if output:
                    self.output.append(output)
                    self._stringio.truncate(0)
                    self._stringio.seek(0)

                # Émettre le signal avec la commande exécutée
                self.execute.emit(code)

            except Exception as e:
                self.output.append(f'<span style="color:#f92672;">Erreur: {str(e)}</span>')

        except Exception as e:
            self.output.append(f'<span style="color:#f92672;">Erreur: {str(e)}</span>')

        # Auto-scroll vers le bas
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def set_table_reference(self, table_widget):
        """Injecte la référence au tableau"""
        self.locals['table'] = table_widget
    def set_data_reference(self, data):
        """Injecte la référence au tableau"""
        self.locals['data'] = data
