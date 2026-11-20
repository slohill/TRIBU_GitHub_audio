# Corrections du 20 novembre 2026

Publication prévue uniquement sur corruption-integration / tribu-corruption-test.onrender.com. Main reste fc8ca7d12dbd4fbaab5346e550cba5b90752190b.

- Enchères : « J’ai terminé » pour les acheteurs humains. Fin anticipée lorsque tous ont terminé et qu’aucun bot ne peut encore miser utilement. Toute mise ou annulation remet les accords à zéro ; demander 15 secondes retire son propre accord. Le vendeur ne vote pas. Les ventes restent réglées une seule fois par le serveur.
- Oracle : le serveur utilisait [0,1,2,2,3,3,4,5], des identifiants par type, transmis sans conversion à une interface utilisant les exemplaires [0,1,2,3,4,5,6,7]. Cela donnait quatre Givre mortel, supprimait Tempête en mer/Vague de froid, et omettait Révoltes. Les nouvelles parties utilisent les identifiants physiques communs et ajoutent 8 pour Corruption. Ne pas restaurer un ancien paquet incorrect pour vérifier cette correction : créer une nouvelle partie.
- Golem : un clic sélectionne le maximum disponible du groupe, plafonné au solde du dé. Plusieurs groupes de la même région peuvent nécessiter plusieurs clics. OK et recommencer restent disponibles ; pertes appliquées par le moteur existant.
- Reconnexion : le premier état canonique établit les compteurs d’annonces sans rejouer les événements précédents. Les événements ultérieurs restent présentés. Les historiques SFX restent silencieux.
- Bots : alliance d’un peuple voisin accessible, puis conquête normale sans bataille. Aucune pose sans mouvement disponible, aucun remplacement d’une alliance conservée. Tutorial et jeu de base exclus de cette nouvelle décision.

Validation : 75 tests serveur ; création réelle de parties base et six joueurs Corruption avec vérification de tous les identifiants Oracle ; 17 vérifications navigateur (conquête par alliance, conservation, son historique/nouveau, Oracle et Guide) ; deux navigateurs enchères avec reconnexion, fin anticipée, ventes et Embuscade ; Golem local et deux navigateurs avec sélection, reconnexion, Révoltes et reprise d’Or ; pertes en bataille ; attente des sacrifices Oracle par les bots (dont Egnorax).

Le test des sons vérifie les déclenchements logiciels, pas le rendu audio sur un iPad physique. La pause Oracle existante couvre Givre mortel et Tempête de sable.
