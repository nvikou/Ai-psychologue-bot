# Bot Psychologue Telegram

Bot Telegram bienveillant inspiré du **Dr. Émile**, assistant
conversationnel pour explorer ses émotions — avec garde-fous de
sécurité et limites claires (ce n'est pas un professionnel de santé).

---

## Fonctionnalités

- Conversation continue avec mémoire par utilisateur (limitée)
- Disclaimer et commande `/help` avec numéros d'urgence
- Détection de messages de crise avec orientation vers l'aide
- Rate limiting anti-spam par utilisateur
- Bouton inline pour effacer l'historique
- Gestion d'erreurs API OpenAI
- Logs sans contenu des messages utilisateurs

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

- Python 3.12+ ou Docker & Docker Compose
- Token bot Telegram ([@BotFather](https://t.me/BotFather))
- Clé API OpenAI

### Variables d'environnement

```bash
cp .env.example .env
```

Renseigner dans `.env` :

```env
TELEGRAM_TOKEN=votre_token_telegram
OPENAI_API_KEY=votre_cle_openai
```

### Lancer avec Docker

```bash
docker compose up -d --build
docker compose logs -f bot
```

### Lancer sans Docker

```bash
pip install -r requirements.txt
python bot.py
```

---

## Structure du projet

```
├── bot.py              # Point d'entrée
├── config.py           # Configuration et constantes
├── handlers.py         # Handlers Telegram
├── libs.py             # Client OpenAI
├── memory.py           # Mémoire conversationnelle
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Commandes

| Commande | Description |
|----------|-------------|
| `/start` | Nouvelle session + avertissement |
| `/help` | Rappel des limites et numéros d'urgence |
| 🗑️ *Effacer l'historique* | Réinitialise la mémoire |

---

## Sécurité

- Les clés API ne sont jamais versionnées (`.env` ignoré par git)
- Les messages utilisateurs ne sont pas loggés en clair
- Limite de longueur des messages et de l'historique
- Détection basique de détresse grave avec ressources d'urgence

**Important :** ce bot ne remplace pas un professionnel de santé
mentale. En cas d'urgence, contactez le **15**, le **112** ou le
**3114** (France).
