# MedVision — Frontend Next.js

Interface d'analyse d'images médicales alimentée par un backend IA (ResNet18).

## Prérequis

- Node.js 18+
- npm ou yarn
- Backend API disponible sur `http://localhost:5000/api/`

## Installation

```bash
npm install
npm run dev
```

L'application sera disponible sur **http://localhost:3000**.

## Structure du projet

```
src/
├── app/
│   ├── layout.tsx          # Layout racine (polices, Navbar, Footer)
│   ├── page.tsx            # Page d'accueil (GET /health + GET /model/info)
│   └── analyze/
│       └── page.tsx        # Page d'analyse (POST /analyze)
├── components/
│   ├── layout/
│   │   └── Navbar.tsx      # Barre de navigation sticky glass
│   └── ui/
│       ├── Button.tsx      # Bouton réutilisable (primary/secondary/ghost)
│       ├── Card.tsx        # Carte avec CardHeader / CardBody
│       ├── ImageDropzone.tsx # Zone drag & drop image
│       ├── ProbabilityBar.tsx # Barre de probabilité animée
│       ├── Skeleton.tsx    # Placeholder de chargement
│       ├── StatRow.tsx     # Ligne clé/valeur
│       └── StatusBadge.tsx # Badge d'état coloré
├── lib/
│   └── api.ts              # Client Axios + types + fonctions API
└── styles/
    └── globals.css         # Tailwind v4 + tokens CSS personnalisés
```

## Endpoints consommés

| Méthode | Endpoint          | Composant         |
|---------|-------------------|-------------------|
| GET     | `/health`         | Page d'accueil    |
| GET     | `/model/info`     | Page d'accueil    |
| POST    | `/analyze`        | Page d'analyse    |

## Design

- **Palette** : Noir / Jaune soleil (#f5c518) / Beige (#f0ebe0)
- **Polices** : Playfair Display (titres), DM Sans (corps), JetBrains Mono (code)
- **Effets** : glass morphism, animations fade-up avec stagger, barres de probabilité animées
- **Responsive** : grille auto-fit, navigation adaptative mobile
