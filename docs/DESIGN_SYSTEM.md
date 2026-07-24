# Kairo — Design System Mobile-First

**Principe fondateur :** Style suisse international (Müller-Brockmann) traduit en interface numérique contemporaine.

---

## 1. Grille

### Mobile (≥320px)
4 colonnes, marge latérale 16px, gouttière 8px.

```text
| 16 | col | 8 | col | 8 | col | 8 | col | 16 |
```

### Tablette (≥768px)
6 colonnes, marge 24px, gouttière 16px.

```text
| 24 | col | 16 | col | 16 | col | 16 | col | 16 | col | 16 | col | 24 |
```

### Desktop (≥1024px)
12 colonnes, marge 32px, gouttière 24px. Largeur max contenu: 1280px.

```text
| 32 | col | 24 | col | ... ×12 ... | col | 32 |
```

---

## 2. Espacement

Échelle basée sur 4px.

| Token | Valeur | Usage |
|-------|--------|-------|
| `--om-space-xs` | 4px | Icône↔texte, puces |
| `--om-space-sm` | 8px | Interne composant |
| `--om-space-md` | 12px | Groupe compact |
| `--om-space-base` | 16px | Padding carte, marge standard |
| `--om-space-lg` | 24px | Séparation sections |
| `--om-space-xl` | 32px | Header↔contenu |
| `--om-space-2xl` | 48px | Sections majeures |
| `--om-space-3xl` | 64px | Hero spacing |

### Classes utilitaires

`.gap-xs` à `.gap-3xl`, `.p-xs` à `.p-3xl`, `.m-xs` à `.m-3xl` (responsive: `-mobile`, `-tablet`, `-desktop`).

---

## 3. Typographie

### Police

System font stack natif (pas de chargement externe) :

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI Variable',
  'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif,
  'Apple Color Emoji', 'Segoe UI Emoji';
```

### Échelle mobile (base, scale-up à ≥768px pour desktop)

| Classe | Mobile (rem) | Desktop (rem) | Poids | Usage |
|--------|-------------|---------------|-------|-------|
| `.om-text-caption` | 0.75 (12px) | 0.75 | 400 | Légende, métadonnées |
| `.om-text-label` | 0.8125 (13px) | 0.8125 | 500 | Labels, badges |
| `.om-text-body` | 0.9375 (15px) | 1 (16px) | 400 | Texte courant |
| `.om-text-body-lg` | 1.0625 (17px) | 1.125 (18px) | 400 | Descriptions |
| `.om-text-h4` | 1.125 (18px) | 1.25 (20px) | 600 | Titres mineurs |
| `.om-text-h3` | 1.25 (20px) | 1.5 (24px) | 600 | Titres section |
| `.om-text-h2` | 1.5 (24px) | 2 (32px) | 700 | Titres page |
| `.om-text-h1` | 2 (32px) | 2.5 (40px) | 700 | Page hero |
| `.om-text-display` | 2.5 (40px) | 3 (48px) | 700 | Landing/hero |

### Interlignage

- Headings: `1.15` (compact, précis)
- Body: `1.55` (lisible)
- UI (boutons, labels): `1.35`

### Hiérarchie

La hiérarchie repose sur : taille > poids > espacement > couleur. Jamais l'inverse.

---

## 4. Palette

### Couleur primaire (dynamique, du tenant)

```css
--om-primary: #1a3f6b;        /* Bleu nuit suisse */
--om-primary-hover: #15325a;
--om-primary-subtle: rgba(26, 63, 107, 0.08);
```

### Neutres

| Token | Hex | Usage |
|-------|-----|-------|
| `--om-neutral-0` | `#ffffff` | Fond carte |
| `--om-neutral-50` | `#f8f9fb` | Fond page |
| `--om-neutral-100` | `#f0f2f5` | Survol léger |
| `--om-neutral-200` | `#e2e5ea` | Bordures |
| `--om-neutral-300` | `#c4c9d0` | Bordures fortes |
| `--om-neutral-500` | `#8b919a` | Texte secondaire |
| `--om-neutral-700` | `#5a6068` | Texte body |
| `--om-neutral-900` | `#1e2228` | Texte principal |

### Sémantiques

| Token | Hex | Usage |
|-------|-----|-------|
| `--om-success` | `#2b7340` | Succès |
| `--om-warning` | `#c76d00` | Attention |
| `--om-danger` | `#c92a2a` | Erreur |
| `--om-info` | `#1864ab` | Information |

### Règle d'usage

- 90% de l'interface en neutres
- La couleur primaire pour 5% (actions principales, liens, accents)
- Les couleurs sémantiques pour 5% (statuts, alertes)
- Jamais de dégradé décoratif
- Les sections ne sont pas des cartes colorées

---

## 5. Formes

| Élément | Coin | Ombre |
|---------|------|-------|
| Carte standard | 12px | Aucune (bordure 1px `neutral-200`) |
| Carte surélevée | 12px | `0 1px 3px rgba(0,0,0,0.04)` |
| Bouton | 8px | Aucune |
| Input/Select | 8px | Aucune |
| Modal/Drawer | 16px (top) | `0 -4px 24px rgba(0,0,0,0.08)` |
| Badge | 6px | Aucune |

- Pas d'ombres lourdes
- Pas de glassmorphism
- Pas de néomorphisme
- Les lignes et l'espace négatif portent la structure, pas les ombres

---

## 6. Composants UI

### Composants de structure

- **AppShell** — Conteneur principal (header + contenu + bottom nav)
- **MobileHeader** — Barre supérieure compacte
- **DesktopSidebar** — Navigation desktop existante conservée
- **MobileBottomNavigation** — 3-5 onglets, icône + libellé
- **PageHeader** — Titre + sous-titre + actions (responsive)

### Composants de contenu

- **ResponsiveDataView** — Tableau → cartes sur mobile
- **MobileDataCard** — Carte représentant une ligne de tableau
- **EmptyState** — Icône + titre + description + action
- **LoadingState** — Skeleton loader
- **ErrorState** — Message + retry

### Composants d'interaction

- **AppButton** — Bouton avec variantes (primary, secondary, danger, ghost, icon)
- **AppInput** — Champ texte avec label, erreur, hint
- **AppModal** — Modal → bottom sheet sur mobile
- **AppDrawer** — Panneau latéral → plein écran sur mobile
- **StatusBadge** — Badge sémantique cohérent
- **ToastContainer** — Notifications toast

### Dimensions tactiles

- **Minimum :** 44×44px (WCAG 2.2 AA)
- **Optimal :** 48×48px pour les actions principales
- **Espacement entre cibles :** ≥8px

---

## 7. Navigation mobile

### Bottom Navigation Bar

- 3-5 destinations max
- Icône 24px + libellé 12px
- Hauteur : 56px + safe-area
- Fond : `neutral-0`, bordure top `neutral-200`
- État actif : libellé en `om-primary` + weight 600
- État inactif : libellé en `neutral-500` + weight 400
- Cible tactile ≥48px

### Safe areas

```css
padding-bottom: env(safe-area-inset-bottom, 0px);
padding-top: env(safe-area-inset-top, 0px);
```

---

## 8. Breakpoints

Inspirés des largeurs d'appareils réels.

| Nom | Min-width | Appareils cibles |
|-----|-----------|-----------------|
| `xs` | 320px | Galaxy Fold, iPhone SE (1st) |
| `sm` | 375px | iPhone 6/7/8/SE (2nd) |
| `md` | 414px | iPhone 11, Pixel 5 |
| `lg` | 768px | iPad Mini, tablettes portrait |
| `xl` | 1024px | iPad, tablettes paysage |
| `2xl` | 1280px | Desktop standard |
| `3xl` | 1440px | Desktop large |

---

## 9. Animations

- Durée : 120–250ms
- Easing : `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out expo)
- Propriétés animées : `transform`, `opacity` uniquement
- Respecter `@media (prefers-reduced-motion: reduce)`

### Transitions définies

- `--om-transition-fast` : 120ms — hover, focus
- `--om-transition-base` : 200ms — toggle, accordion
- `--om-transition-slow` : 250ms — drawer, modal, page

---

## 10. Variable CSS exposées

```css
:root {
  /* Couleurs */
  --om-primary: #1a3f6b;
  --om-primary-hover: #15325a;
  --om-primary-subtle: rgba(26, 63, 107, 0.08);
  --om-neutral-0: #ffffff;
  --om-neutral-50: #f8f9fb;
  --om-neutral-100: #f0f2f5;
  --om-neutral-200: #e2e5ea;
  --om-neutral-300: #c4c9d0;
  --om-neutral-500: #8b919a;
  --om-neutral-700: #5a6068;
  --om-neutral-900: #1e2228;
  --om-success: #2b7340;
  --om-warning: #c76d00;
  --om-danger: #c92a2a;
  --om-info: #1864ab;

  /* Espacement */
  --om-space-xs: 0.25rem;
  --om-space-sm: 0.5rem;
  --om-space-md: 0.75rem;
  --om-space-base: 1rem;
  --om-space-lg: 1.5rem;
  --om-space-xl: 2rem;
  --om-space-2xl: 3rem;
  --om-space-3xl: 4rem;

  /* Typographie */
  --om-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI Variable', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --om-font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;

  /* Formes */
  --om-radius-sm: 6px;
  --om-radius-base: 8px;
  --om-radius-lg: 12px;
  --om-radius-xl: 16px;

  /* Navigation */
  --om-topbar-height: 56px;
  --om-bottomnav-height: 56px;
  --om-sidebar-width: 260px;

  /* Animation */
  --om-transition-fast: 120ms cubic-bezier(0.16, 1, 0.3, 1);
  --om-transition-base: 200ms cubic-bezier(0.16, 1, 0.3, 1);
  --om-transition-slow: 250ms cubic-bezier(0.16, 1, 0.3, 1);
}
```
