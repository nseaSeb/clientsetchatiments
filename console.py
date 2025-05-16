from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
import sys
from io import StringIO


class PythonConsole(QWidget):
    execute = Signal(str)  # Signal émis quand du code est exécuté

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_python_env()
        self.show_welcome_message()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Zone de sortie
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #001400;
                color: #f8f8f2;
                font-family: Consolas, Monaco, "Courier New", monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.output)
        # Ligne de commande
        self.input = QLineEdit()
        self.input.setPlaceholderText("Tapez du code Python ici et appuyez sur Entrée...")
        self.input.returnPressed.connect(self.execute_code)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #001400;
                color: #00bb00;
                font-family: Consolas, Monaco, "Courier New", monospace;
                font-size: 10pt;
                padding: 5px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.input)

        # Donner le focus à la ligne de commande
        self.input.setFocus()

    def setup_python_env(self):
        """Configure l'environnement Python"""
        self.locals = {
            'app': self.parent(),
            'get_cell': self._safe_get_cell_text,
            'set_cell': self._safe_set_cell,
            'get_col': self._safe_get_col,
            'get_row': self._safe_get_row,
            'table': None,  # Sera remplacé par la référence au tableau
            'print': self._print,
            'help': self.show_help,
            'QTableWidgetItem': QTableWidgetItem,
            'set_col': self.set_column_values,
            'rowcount': lambda: self.locals['table'].rowCount(),
            'colcount': lambda: self.locals['table'].columnCount(),
            'clear_col': lambda col: [self.locals['table'].setItem(r, col, QTableWidgetItem(""))
                                      for r in range(self.locals['table'].rowCount())],
            'h': self.show_help,
            'show_doc': self.show_doc
        }
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

    def execute_code(self):
        """Exécute le code saisi"""
        code = self.input.text()
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
