
# Pyrffects

## Introduction
Petit projet où une vidéo peut être générée à partir du chargement d'un fichier xml décrivant la superposition de calques sur lesquels des effets peuvent être appliqués.

Un nombre assez faible d'effet est présent, et je ne pense pas en ajouter d'avantage pour l'instant.

Pour un exemple de résultat voir [ici](#exemple).

## Dépendences :

- Python 3.6 ou supérieur
- ffmpeg
- numpy
- PIL

## Usage :
```Bash
python3 pyrffect_parser.py input_xml [-o --out o] [-f --framerate f] [-d --duration d] 
```
-o, --out : o nom de la vidéo a enregistrer (remplace le champs out de l'xml)
-f, --framerate : f framerate de la vidéo (remplace le champs framerate de l'xml)
-d --duration : d durée de la vidéo (remplace le champs duration de l'xml)

  

## Ecriture d'un XML:

Une vidéo est décrite par la racine, où chaque fils est un calque superposée au dessus d'un autre. Le premier fils de pyrffects sera donc celui le plus au fond. Pour ajouter des effets aux différents calques ont les ajoutent en fils du calque.

### Intro
**Pyrffects [Racine]:**
  Racine de la description de vidéo.
  - *framerate*: framerate de la vidéo produite
  - *duration*: durée de la vidéo produite
  - *out*: nom de la vidéo produite
  - *remove*: obsolète
 
 ### Calque
**calc [Calque]:**
 Calque de base permettant d'afficher une image.
 - *filename* : nom de l'image du calque
 - *x* : absisse du calque
 - *y* : ordonnée du calque
 
**flat [Calque]:**
  Calque recouvrant l'entièreté de la surface avec une couleur unis
  - *color* : couleur du calque (format: "r,g,b")

**firework [Calque]:**
Calque lançant des petits feu d'artifices qui éclairent les calques sélectionnés.
- *x_stat*: intervalle dans lequel un feu peut être lancé (format: "x_min,x_max")
- *y_stat*: intervalle dans lequel un feu peut être lancé et exploser (format: "y_lancement,y_min_explo,y_max_explo")
- *duration* : intervalle de temps qu'un feu peut prendre pour passer du lancement à l'explosion (format: "t_min,t_max")
- *intensity*: intervalle d'intensité que la lumière produit par le feu peut prendre (format: "i_min,i_max")
- pause: intervalle de temps d'attente entre deux lancements de feu (format: "pause_min,pause_max")
- *colors*: liste de couleur que peut prendre un feu (format : "r1,g1,b1;r2,g2,b2;r3,g3,b3..." | "all")
- *name_effect*: nom de l'effet de lumière trouvé
- *ray_width*: épaisseur des rayons d'un feu
- *size_amplifier* ; multiplicateur du rayon d'explosion
- *flickering* : modifie la fréquence de fluctuation de la lumière produite par un feu

### Effects

**named [Effect] :**
Cherche un effet portant le nom donné et l'applique au calque courant
- *name* : nom de l'effet à chercher.

**pixel [Effect] :**
Effet déplacant aléatoirement des carrés de pixels de l'image
- *square_size* :  taille des carrés traités
- *displace_probability* : probabilité de déplacer le carré tiré
- *area_covered* : pourcentage du calque pour lequel on tira un carré

 **light [Effect] :**
 - coords : coordonnées de la lumière (format: "x,y")
 - intensity : intensité de la lumière
 - dist_step: distance de base d'effet de la lumière
 - color ; couleur de la lumière (format: "r,g,b")



## Exemple de résultat :<a id="exemple"></a>

  

<iframe  width="560"  height="315"  src="https://www.youtube.com/embed/ReNQJnsXjBM"  title="YouTube video player"  frameborder="0"  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"  allowfullscreen></iframe>
<a href="https://youtu.be/ReNQJnsXjBM">Si la vidéo n'est pas disponible.</a>
