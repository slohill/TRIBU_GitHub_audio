# TRIBU — Le Jeu Online

## Principe

TRIBU Online conserve le moteur complet du jeu TRIBU existant dans `index.html`. Le mode Online ne réimplémente pas les règles côté serveur : il synchronise l'état du moteur original entre les participants.

## Écran d’accueil

- Champ **Pseudo**.
- Si aucun pseudo n’est saisi, un pseudo est choisi au hasard parmi les 10 noms par défaut du jeu.
- Actions principales : **Créer une partie** et **Rejoindre une partie**.

## Configurations Online

### Joueurs vs bots

- 1 joueur vs 4 bots
- 2 joueurs vs 3 bots
- 3 joueurs vs 2 bots

### Joueurs vs joueurs

- 3 joueurs
- 4 joueurs
- 5 joueurs

## Salon et lancement

Le salon gère notamment le nom/code de partie, la condition de victoire, les places, l'état prêt et le lancement commun de la partie. Une fois le setup terminé, la partie utilise le moteur TRIBU original avec la synchronisation Online `legacySync`.

## Architecture actuelle

1. Le serveur gère les salons, participants, reconnexions et le transport temps réel.
2. Le setup Online prépare une partie commune aux participants.
3. Le moteur TRIBU original reste l'autorité fonctionnelle pour les règles et comportements du jeu.
4. La partie en cours est synchronisée par snapshots complets via `legacySync`.
5. Un seul navigateur est responsable de la conduite des bots lorsque des bots participent à la partie.
6. Les informations privées, notamment les mains, sont présentées selon le joueur local.
7. Les résolutions prioritaires et interruptions doivent publier leur état terminal avant de rendre le contrôle normal afin d'éviter qu'un snapshot obsolète restaure une résolution déjà terminée.

L'ancien projet de transposition progressive des règles dans un moteur serveur autoritaire n'est plus l'architecture retenue.

## Mode de test local à conserver

Le mode **2 joueurs vs 3 bots — local / même support** reste indépendant du serveur Online afin de tester rapidement les règles, cartes, déplacements, batailles et affichages.

L'invariant de lancement à préserver dans le client est :

```js
$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};
```

## Stabilisation

Avant une version stable, les changements Online doivent préserver le moteur original, éviter les réimplémentations de mécaniques et être vérifiés au minimum par contrôle syntaxique JavaScript et invariants ciblés. Les scénarios déterministes sensibles doivent, lorsque possible, disposer d'un test de non-régression simulant la transition d'état concernée.
