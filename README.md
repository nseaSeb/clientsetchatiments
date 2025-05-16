# clientsetchatiments

Manipulations de CSV / XLS en python (tableur avec console Python)

## Pour installer et executer le code

Dans un terminal copier le projet github

```
git clone https://github.com/nseaSeb/clientsetchatiments.git

```

Une fois fait nous nous rendons dans le dossier du projet et nous installons l'environement virtuel

```
cd clientsetchatiments

py -m venv .venv

source .venv/bin/activate
```

Installation des dépendances

```
pip install openpyxl
pip install PySide6

```

Pour executer l'application

```
python app.py
```

(si vous avez en console "command not found:" adapter à votre installation de python par exemple pip3 et python3, sinon assurez-vous d'avoir
bien installé python dans votre environnement)

Pour compiler l'application D'abord rendre le script executable et installer la dépendance pyintaller

```
chmod +x build.sh
pip install pyinstaller
```

Pour exécuter le script

```
./build.sh
```

Une fois fait vous devriez avoir dans le dossier ./dist une application exécutable

## A propos

![alt text](./resources/cc_image01.png 'Logo Title Text 1')
