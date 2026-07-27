# LocalMind

> Ton IA locale multi-modèles avec routage intelligent et recherche web intégrée.

LocalMind est une interface unifiée qui route automatiquement tes questions vers le modèle d'IA le plus adapté (code, création, culture générale) tout en maintenant une identité cohérente. Le tout tourne en local via [Ollama](https://ollama.com).

## Fonctionnalités

- **Routage intelligent** : détecte le type de question et choisit le meilleur modèle
- **Multi-modèles** : Qwen pour le code, Mistral pour la création, Llama pour le général
- **Recherche web intégrée** : DuckDuckGo (gratuit) ou Tavily (clé API)
- **Exécution de commandes** : peut proposer et lancer des commandes système (avec confirmation)
- **Interface graphique** : GUI propre avec support Markdown
- **Mode terminal** : utilisation en CLI pour les puristes
- **100% local** : tes données ne quittent jamais ton PC

## Prérequis

- Python 3.10+
- [Ollama](https://ollama.com) installé
- Les modèles suivants dans Ollama :
  ```bash
  ollama pull llama3.2
  ollama pull llama3.2:1b
  ollama pull mistral
  ollama pull qwen2.5-coder:7b
  ```

Installation
```bash

git clone https://github.com/letitouzzz/localmind.git
cd localmind
make install
  ```
Copie le fichier d'environnement et ajoute ta clé API Tavily (optionnel) :
```bash

cp .env.example .env
nano .env
  ```
Utilisation
Interface graphique
```bash

make run-gui
```
Mode terminal
```bash

make run
```
Structure du projet
```text

localmind/
├── src/
│   ├── core.py      # Moteur de routage et appel aux modèles
│   ├── gui.py       # Interface graphique Tkinter
│   ├── web.py       # Recherche DuckDuckGo + Tavily
│   └── executor.py  # Validation et exécution de commandes
├── .env.example     # Template pour les variables d'environnement
├── .gitignore
├── requirements.txt
├── Makefile
└── README.md
```
Licence

MIT © Titouz
```text


## `LICENSE`

MIT License

Copyright (c) 2025 Titouz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
