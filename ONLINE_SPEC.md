# TRIBU — Le Jeu Online (version bêta)

## Écran d’accueil

Titre : **Tribu Le Jeu Online (version bêta)**

- Champ **Pseudo**.
- Si aucun pseudo n’est saisi, un pseudo est choisi au hasard parmi une base de 10 noms par défaut.
- Actions principales :
  - **Créer une partie**
  - **Rejoindre une partie**

## Créer une partie

### Joueurs vs bots

- 1 joueur vs 4 bots
- 2 joueurs vs 3 bots
- 3 joueurs vs 2 bots

### Joueurs vs joueurs

- 3 joueurs
- 4 joueurs
- 5 joueurs

## Salon de partie

Sauf pour **1 joueur vs 4 bots**, la création passe par un salon :

- créer un nom de partie ;
- choisir un code de partie ;
- choisir une victoire à **3, 4 ou 5 points** ;
- afficher **En attente des joueurs et des joueuses** ;
- chaque participant peut cliquer sur **Prêt·e** ;
- lorsque toutes les places sont occupées et que tout le monde est prêt, le créateur peut cliquer sur **Lancer la partie** ;
- seul le créateur lance la partie.

## Mode de test à conserver

Le mode **2 joueurs vs 3 bots — local / même support** doit rester disponible indépendamment du futur serveur Online, afin de continuer à tester rapidement les règles, cartes, déplacements, batailles et affichages.

Il pourra être présenté discrètement comme **Mode test local — 2 joueurs vs 3 bots**.

## Architecture visée

Le jeu Online doit conserver autant que possible le frontend et les règles existantes, avec ajout progressif d’un serveur multijoueur autoritaire :

1. accueil Online et salons ;
2. connexion temps réel entre appareils ;
3. synchronisation progressive des actions et de l’état de partie ;
4. confidentialité des informations privées (notamment les mains) et validation serveur des actions ;
5. reconnexion et gestion des déconnexions.

Le mode local de test ne doit pas dépendre de ce serveur.
