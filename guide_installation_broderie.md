# Guide d'installation — Logiciels de la chaîne de broderie

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Objet : installer les logiciels nécessaires au processus décrit dans `processus_broderie.md` (dessin vectoriel → fichier DST), en mode **sans interface graphique** (serveur, script) et, en option, un **poste de revue graphique**.
> Version : **1.1** — 16 novembre 2026
> Statut : **procédure exécutée de bout en bout** sur Ubuntu 24.04.5 LTS (installation propre, vérification réussie : 1897 points, 2 changements de couleur, 80 × 60 mm, 12 s).
> Sources : `collecte_de_savoir_broderie.md` §7, §10, §16.

---

## 0. Ce qui est installé et pourquoi

| Logiciel | Version | Rôle | Licence |
|---|---|---|---|
| Ink/Stitch | **v3.3.0** (commit `b0edd963`) épinglée | Conversion SVG paramétré → DST | GPL-3.0 |
| Python | 3.12 (celui du système Ubuntu 24.04) | Exécution d'Ink/Stitch et de nos scripts | PSF |
| wxPython | 4.2.1 (paquet système) | Bibliothèque d'interface **importée obligatoirement** par Ink/Stitch, même sans écran | wxWindows |
| inkex | 1.4.1 (PyPI) | Lecture/écriture SVG pour Ink/Stitch | GPL-2.0+ |
| pystitch | 1.0.1 | Écriture/lecture des formats machine (DST, TBF…) — utilisé par Ink/Stitch | MIT |
| pyembroidery | 1.5.1 | Relecture et contrôle des DST ; écriture TBF | MIT |
| shapely, numpy, networkx… | selon Ink/Stitch | Géométrie et calcul | diverses |
| rsvg-convert | système | Aperçus PNG | LGPL |
| Inkscape | ≥ 1.2 (facultatif) | Aperçus réalistes ; poste de revue | GPL |

Principe de licence retenu : Ink/Stitch est **appelé comme programme séparé** ; nos scripts n'importent pas son code (`collecte_de_savoir_broderie.md` §15.3).

---

## 1. Prérequis

- **Système vérifié** : Ubuntu 24.04 LTS (x86_64). Autres systèmes : voir §8.
- Droits administrateur (`sudo`) pour les paquets système.
- Accès Internet à **github.com** et **pypi.org** (GitLab n'est **pas** nécessaire).
- Environ 1 Go d'espace disque.

Vérifier la version de Python du système :
```bash
python3 --version          # attendu : Python 3.12.x sur Ubuntu 24.04
```
Si la commande affiche une autre version, utiliser explicitement `python3.12` dans toute la suite (le paquet wxPython d'Ubuntu 24.04 n'existe que pour Python 3.12).

---

## 2. Paquets système

```bash
sudo apt update
sudo apt install -y git python3-venv python3-wxgtk4.0 librsvg2-bin
```
Facultatif (aperçus réalistes, poste de revue) :
```bash
sudo apt install -y inkscape
```

**Contrôle** — wxPython doit s'importer avec le Python 3.12 du système :
```bash
python3.12 -c "import wx; print(wx.version())"
# attendu : 4.2.1 gtk3 (phoenix) wxWidgets 3.2.4
```
L'import ne demande pas d'écran ; seule l'ouverture d'une fenêtre en demanderait une.

---

## 3. Dossier de travail

```bash
mkdir -p ~/broderie && cd ~/broderie
```
Toute la suite se fait dans ce dossier. Il contiendra : `inkstitch/` (code épinglé), `venv/` (environnement Python), `verifier_installation.py`.

---

## 4. Ink/Stitch, version épinglée

```bash
git clone --depth 1 --branch v3.3.0 --recurse-submodules --shallow-submodules \
    https://github.com/inkstitch/inkstitch.git inkstitch
git -C inkstitch rev-parse HEAD
```
**Contrôle** : la dernière commande doit afficher exactement
```
b0edd96311ece82ee48816dc93466274b12c2a9c
```
Toute autre valeur : **arrêter** (version non validée par nos essais).

Le message « detached HEAD » de git est normal (on est sur une étiquette, pas une branche).

---

## 5. Environnement Python

```bash
python3.12 -m venv --system-site-packages venv
```
L'option `--system-site-packages` est indispensable : elle rend visible le wxPython installé par le système.

**Contrôle** :
```bash
venv/bin/python -c "import wx; print('wx OK', wx.version())"
```

---

## 6. Dépendances Python

Ink/Stitch déclare `inkex` depuis GitLab et `wxPython` depuis les sources : on installe `inkex` depuis PyPI, on garde le wxPython du système, et on retire ces deux lignes (ainsi que les outils de développement) de la liste des dépendances :

```bash
venv/bin/pip install "inkex==1.4.1"
grep -v -e '^inkex' -e '^wxPython' -e mypy -e flake8 -e '^types-' \
    inkstitch/requirements.txt > requirements_filtrees.txt
venv/bin/pip install -r requirements_filtrees.txt pyembroidery scikit-image pytest
```
`scikit-image` (avec `scipy` et `Pillow`) sert au prototype (traçage, mesures de qualité) ; `pytest` aux tests automatiques.

**Versions de référence** : les versions des dépendances du prototype sont verrouillées dans `uv.lock` (déclarées dans `pyproject.toml`). Pour reproduire à l'identique, depuis la racine du dépôt :
```bash
uv sync --locked
```
Les dépendances propres à Ink/Stitch suivent `inkstitch/requirements.txt` (ci-dessus). Toute autre version doit être signalée et revérifiée (§7).

**Contrôle** :
```bash
venv/bin/python -c "import inkex, shapely, pystitch, pyembroidery, skimage; print('dépendances OK')"
```

**Séparation recommandée** (revue critique) : un environnement pour Ink/Stitch, un autre pour nos scripts. Les scripts du prototype acceptent la variable `INKSTITCH_PYTHON` (interpréteur de l'environnement d'Ink/Stitch). Le prototype actuel fonctionne dans un seul environnement.

---

## 7. Vérification de bout en bout

Copier `verifier_installation.py` (fourni avec ce guide) dans `~/broderie`, puis :
```bash
venv/bin/python verifier_installation.py inkstitch/inkstitch.py
```

Le script :
1. vérifie la présence et la **version épinglée** d'Ink/Stitch ;
2. vérifie l'import des bibliothèques ;
3. crée un dessin de test connu (carré en remplissage 40 × 40 mm, ligne en point droit 80 mm, colonne satin 4 × 40 mm) et l'exporte en DST **avec les règles d'exécution du processus** (cache privé, variables d'environnement, délai maximal) ;
4. relit le DST avec pyembroidery et pystitch et compare aux valeurs attendues **exactes** (l'export est déterministe : un écart signale une dérive de version) ;
5. vérifie que la sortie d'erreur d'Ink/Stitch est vide ;
6. exporte un second dessin à deux objets séparés par une coupe et vérifie la présence du **motif brut de coupe** dans le fichier ;
7. sort **en erreur** au moindre écart, en indiquant lequel.

Résultat attendu (fin de sortie) :
```
  pyembroidery : points=1897 changements de couleur=2 dimensions=80.0 x 60.0 mm
  pystitch : points=1897 changements de couleur=2 dimensions=80.0 x 60.0 mm
  OK     pyembroidery et pystitch concordent
  OK     nombre de points exact : 1897
  OK     2 changements de couleur
  OK     dimensions 80.0 x 60.0 mm
  OK     en-tête DST : étendue +X = 400 (unité 0,1 mm)

Installation vérifiée : la chaîne est opérationnelle.
```

---

## 8. Utilisation de base (rappel)

Export d'un SVG paramétré en DST, avec les règles d'exécution (`architecture_broderie.md` §5) :
```bash
cd ~/broderie
CONFIG=$(mktemp -d)        # dossier de configuration privé, propre à cet appel
XDG_CONFIG_HOME=$CONFIG INKSTITCH_OFFLINE_SCRIPT=true PYTHONUTF8=1 LANGUAGE=en_US \
    timeout 1800 venv/bin/python inkstitch/inkstitch.py --extension=output --format=dst dessin.svg > dessin.dst
rm -rf "$CONFIG"
test -s dessin.dst || echo "ERREUR : DST vide (aucun objet brodable ou erreur de lecture)"
```

Tests automatiques et validation par mutation du prototype (dossier `prototype/`) :
```bash
INKSTITCH=~/broderie/inkstitch/inkstitch.py SPIKES=<dossier spikes/results> venv/bin/python -m pytest -q prototype/tests/
venv/bin/python prototype/mutations.py <svg paramétré de référence> <largeur attendue en mm> inkstitch/inkstitch.py
```
Rappels :
- Le SVG **doit** contenir `<inkstitch:inkstitch_svg_version>4</inkstitch:inkstitch_svg_version>` dans `<metadata>` ; sans elle, Ink/Stitch plante (sans écran) ou se bloque indéfiniment.
- Le code de sortie ne prouve rien : contrôler le contenu.
- Aperçu : `--extension=stitch_plan_preview --render-mode=simple --move-to-side=false`, puis `rsvg-convert` vers PNG ; le dessin doit être placé dans un calque.

---

## 9. Poste de revue graphique (facultatif)

Pour l'étape de revue humaine (satins semi-automatiques, simulateur, carte de densité), un poste avec écran utilise **Inkscape + l'extension Ink/Stitch officielle** :
1. Installer Inkscape (≥ 1.0.2 requis par Ink/Stitch).
2. Télécharger le paquet Ink/Stitch **v3.3.0** pour Linux (`.deb`, `.rpm`, `.tar.xz`) depuis la page officielle : https://inkstitch.org/docs/install-linux/
3. Installer selon la page officielle (paquet système, ou archive décompressée dans `~/.config/inkscape/extensions`).
4. Ouvrir dans Inkscape le SVG paramétré produit par la chaîne ; menu Extensions → Ink/Stitch.

Garder **la même version** (v3.3.0) sur le poste de revue et sur la chaîne automatique, pour que les paramètres soient interprétés de façon identique.

---

## 10. Autres systèmes (non vérifiés)

| Système | Piste | Statut |
|---|---|---|
| Debian 12 | Python 3.11 (≥ 3.11 requis) ; paquet `python3-wxgtk4.0` | Non vérifié |
| Debian 13, Ubuntu plus récent | Vérifier pour quelle version de Python le paquet wxPython est construit, et créer l'environnement avec celle-ci | Non vérifié |
| Fedora | Paquet `python3-wxpython4` | Non vérifié |
| Windows | Sous-système Linux (WSL2) avec Ubuntu 24.04, puis ce guide | Non vérifié |
| Sans wxPython système | Module `wx` factice placé en tête du chemin d'import (pratique d'un projet tiers, `collecte_de_savoir_broderie.md` §16) | Non vérifié ici |

---

## 11. Dépannage

| Symptôme | Cause probable | Remède |
|---|---|---|
| `No module named 'wx'` dans l'environnement | Environnement créé sans `--system-site-packages`, ou avec une autre version de Python que celle du paquet wx | Recréer `venv` avec `python3.12 -m venv --system-site-packages venv` |
| `pip` échoue sur `gitlab.com` | Ligne `inkex` non retirée de la liste | Refaire l'étape 6 (liste filtrée) |
| `pip` tente de compiler wxPython (très long) | Ligne `wxPython` non retirée | Refaire l'étape 6 |
| « Unable to access the X Display » | Balise `inkstitch_svg_version` absente du SVG | Ajouter la balise (§8) |
| Export bloqué indéfiniment | Idem, sous écran virtuel | Ajouter la balise ; toujours utiliser `timeout` |
| DST de 0 octet, code de sortie 0 | Aucun objet brodable (texte vivant, objets ignorés, SVG illisible) | Lire la sortie d'erreur ; vérifier les attributs et la normalisation |
| Résultats incohérents d'un fichier à l'autre | Cache de plans de broderie partagé | `XDG_CONFIG_HOME` privé par appel |
| Commit différent de `b0edd963…` | Mauvaise étiquette clonée | Recloner avec `--branch v3.3.0` |

---

## 12. Mise à jour et désinstallation

- **Mise à jour d'Ink/Stitch** : ne pas modifier l'installation en place. Cloner la nouvelle version dans un autre dossier, refaire les essais du processus (`collecte_de_savoir_broderie.md` §10), mettre à jour le commit attendu dans `verifier_installation.py`, puis basculer.
- **Désinstallation** : `rm -rf ~/broderie` ; paquets système éventuels : `sudo apt remove python3-wxgtk4.0 librsvg2-bin inkscape`.

---

## Journal des versions
| Version | Date | Changements |
|---|---|---|
| 1.0 | 15/11/2026 | Première version ; procédure exécutée et vérifiée sur Ubuntu 24.04.5 LTS (installation propre) |
| 1.1 | 16/11/2026 | Après revue critique : dépendances du prototype ; versions verrouillées ; dossier de configuration privé par appel ; vérification exacte, sortie d'erreur et coupe contrôlées ; tests et mutations ; séparation des environnements recommandée |
