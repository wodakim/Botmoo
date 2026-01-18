# Rapport Complet du Projet : Society Simulator

## 1. Ce qui a été réalisé (État Actuel - Version Zeta v2.6)

Ce projet est un simulateur de société multi-agents en 2D, jouable hors ligne via un navigateur web. Le joueur agit en tant qu'observateur d'un monde autonome.

### 🏛️ Architecture & Technique
- **Backend :** Python (FastAPI) avec WebSockets pour la communication temps réel.
- **Frontend :** HTML5 + Vanilla JS + Canvas API (Aucun moteur externe).
- **Offline First :** Le jeu tourne localement sur `localhost:8000`.
- **Compatibilité :** Correction appliquée pour l'encodage Windows (UTF-8).

### 🧠 Intelligence Artificielle (Cœur)
- **Système de Besoins :** Faim, Énergie. Les agents cherchent à manger et dormir.
- **Psychologie (O.C.E.A.N) :** Chaque agent a une personnalité unique (Ouverture, Conscience, Extraversion, Agréabilité, Névrosisme).
- **Santé Mentale :** Barre de Sanité qui baisse en cas de trauma (attaque). Troubles mentaux possibles (Paranoïa, Schizophrénie).
- **Mémoire Épisodique :** Les agents se souviennent des événements marquants (Attaques, Vols, Crafts).

### 🌍 Simulation & Monde
- **Génération Procédurale :** Carte 64x64 avec Biomes (Forêt, Lac, Montagne, Plaine).
- **Cycle Jour/Nuit :** Cycle de 6 minutes (4min Jour / 2min Nuit). La nuit affecte la vision et le comportement.
- **Monstres :** Apparition nocturne de "Cauchemars" (Loups/Ombres) agressifs.

### 💰 Économie & Métiers
- **Système de Métiers :** Bûcheron, Garde, Glaneur, Forgeron, Voleur, Marchand.
- **Inventaire & Craft :** Récolte de ressources (Bois, Minerai) -> Craft d'objets (Lance, Épée, Tunique).
- **Commerce :** Les agents vendent leurs surplus aux Marchands contre de l'Or.

### 🗣️ Système Social & Mémétique
- **Langage Dynamique (Nouveau) :** Génération procédurale de phrases (Sujet-Verbe-Objet) contextuelles ("I attack Bot!", "I eat berries").
- **Langage Viral :** Les phrases sont des "virus" qui se transmettent et mutent entre les agents.
- **Prestige :** Les agents riches ou bien équipés influencent plus facilement les autres.
- **Chat Contextuel :** Bulles de dialogue réactives (Salutations, Alertes, Folie, Combat).

### 🧬 Génétique & Famille (Nouveau)
- **Reproduction :** Les agents peuvent se reproduire s'ils trouvent un partenaire compatible.
- **Héritage :** Les enfants héritent du Nom de Clan (Patrilinéaire/Matrilinéaire) et d'un mélange des traits psychologiques.
- **Cycle de Vie :** Vieillissement naturel et mort de vieillesse (approx. 60 jours). Affichage visuel de l'âge (Taille).

### 👁️ Interface (Observer UI)
- **Caméra :** Zoom et Panoramique fluide.
- **Inspecteur :** Panneau latéral détaillé (Stats, Inventaire, Psyche, Log Mémoire).
- **Toasts :** Notifications globales pour les événements majeurs (Morts, Guerres).
- **Visuels :** Tuiles pixel-art générées procéduralement, Overlay Nuit, Icônes d'état.

---

## 2. Checklist de Vérification (Avant chaque release)

Avant de pousser une nouvelle version, vérifiez ces points critiques :

### ✅ Stabilité
- [ ] Le serveur démarre sans erreur (`python backend/main.py`).
- [ ] La boucle de simulation ne crash pas sur une action inconnue (Fix `KeyError`).
- [ ] Les WebSockets se reconnectent si la page est rafraîchie.

### ✅ Gameplay
- [ ] Les agents mangent quand ils ont faim (Barre Faim ne reste pas à 0).
- [ ] Les agents dorment la nuit (ou fuient les monstres).
- [ ] Les monstres apparaissent bien à 22h et disparaissent/meurent le jour.
- [ ] Le commerce fonctionne (L'or de l'agent augmente après une vente).

### ✅ Interface
- [ ] Le clic sur un agent ouvre bien l'inspecteur.
- [ ] L'overlay "Nuit" s'active correctement selon l'heure affichée.
- [ ] Les bulles de chat s'affichent au-dessus des bonnes têtes (Bonnes coordonnées).

---

## 3. Roadmap & Futures Améliorations

Pour aller encore plus loin vers une simulation de "Vie Artificielle" complète :

### 🚀 Court Terme (Prochaines itérations)
1.  **Construction de Bâtiments (Amélioré) :**
    *   Les agents posent déjà des murs, mais il manque le stockage (Coffres).
2.  **Politique & Lois :**
    *   Élection d'un "Maire" (Agent avec le plus de Prestige).
    *   Lois simples (ex: "Interdit de couper du bois la nuit").

### 🌟 Moyen Terme
1.  **Météo Dynamique :**
    *   Pluie (Ralentit, fait pousser les plantes).
    *   Neige (Froid, nécessite des vêtements).
2.  **Agriculture Avancée :**
    *   Planter des graines, arroser, récolter (Cycle lent).
3.  **Système de Quêtes Émergentes :**
    *   Un agent "veut" quelque chose (Désir) et paie un autre pour le faire.

### 🌌 Long Terme (Vision Finale)
1.  **Histoire Procédurale (Livre d'Histoire) :**
    *   Générer un fichier texte résumant les siècles d'histoire de la simulation ("L'Âge de la Grande Famine", "Le Règne du Roi Fou").
2.  **Export / Import d'Agents :**
    *   Possibilité de sauvegarder son agent préféré pour le mettre dans une autre simulation.

---

**Note du Développeur (Jules) :**
Le projet est actuellement en version **Zeta v2.6**. La base est extrêmement solide et modulaire. L'ajout de nouvelles features (comme la génétique ou la météo) peut se faire en créant de nouveaux fichiers dans `backend/systems/` sans casser l'existant.
