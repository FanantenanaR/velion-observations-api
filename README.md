# Velion Observations API

> Test technique Velion — API d'abstraction multi-sources pour observations terrain agronomiques (essais / parcelles / mesures datées).
>
> **Statut** : Encours.

## Quickstart

```bash
# Cloner et installer
git clone https://github.com/FanantenanaR/velion-observations-api.git
cd velion-observations-api
pip install -e .

# Configurer
cp .env.example .env
# Éditer .env avec ton projet GCP

# Auth BigQuery (ADC)
gcloud auth application-default login
```

### Lancer l'API en local

```bash
uvicorn app.main:app --reload --port 8000
```
