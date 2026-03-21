# 🧠 Bot Psychologue Telegram

Un bot Telegram qui joue le rôle du **Dr. Émile**, psychologue clinicien virtuel. Il aide les utilisateurs à comprendre et gérer leurs émotions grâce à l'IA.

---

## Fonctionnalités

- Conversation continue avec mémoire de l'historique par utilisateur
- Personnalité fixe : Dr. Émile, psychologue avec 20 ans d'expérience
- Bouton inline pour effacer l'historique de conversation
- Commande `/start` pour démarrer une session
- Logs automatiques dans `bot.log`

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Framework bot | [aiogram 3](https://docs.aiogram.dev/) |
| IA | [OpenAI GPT-4o-mini](https://platform.openai.com/) |
| Containerisation | Docker / Docker Compose |
| Langage | Python 3.12 |

---

## Installation

### Prérequis

- Python 3.12+
- Docker & Docker Compose
- Un token bot Telegram (via [@BotFather](https://t.me/BotFather))
- Une clé API OpenAI



### Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
TELEGRAM_TOKEN=votre_token_telegram
OPENAI_API_KEY=votre_cle_openai
```



### 3. Lancer avec Docker

```bash
docker-compose up -d
```

### 3. Lancer sans Docker

```bash
pip install -r requirements.txt
python bot.py
```

---

## Structure du projet

```
├── bot.py              # Point d'entrée, démarrage du bot
├── handlers.py         # Logique des commandes et callbacks Telegram
├── libs.py             # Appel à l'API OpenAI
├── requirements.txt    # Dépendances Python
├── Dockerfile          # Image Docker
├── docker-compose.yml  # Configuration Docker Compose
├── .env                # Variables sensibles (non versionné)
└── .gitignore
```

---

## Utilisation

| Commande | Description |
|----------|-------------|
| `/start` | Démarre une nouvelle conversation |
| 🗑️ *Effacer l'historique* | Bouton inline pour réinitialiser la mémoire |
