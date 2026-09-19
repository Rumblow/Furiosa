# Bitacoras de Furiosa

## Registro del proyecto

### 1. Configuracion inicial

- Se establecio una ventana Pygame de 800 x 600.
- Se creo el archivo principal `main.py`.
- Se organizaron las constantes del juego en `constantes.py`.
- Se crearon las clases de personajes en `personajes.py`.
- Se anadieron las carpetas de imagenes y documentos dentro de `assets/` y `documents/`.

### 2. Jugador y enemigo

- Se anadio el jugador con movimiento mediante W, A, S, D y las flechas.
- Se cambio el sprite del jugador por `rpgcritters2_araña.png`.
- Se anadio el Brujo de Cobalto usando `rpgcritters2_wizzard.png`.
- El enemigo se mantiene inmovil mientras no se programe otro comportamiento.

### 3. Atributos del jugador

- El jugador recibio los atributos modificables:
  - Vida.
  - Ataque.
  - Defensa.
  - Velocidad.
- Los atributos se almacenan en `jugador.atributos`.
- La velocidad del atributo controla el movimiento del jugador.
- Los atributos se muestran como barras en la parte inferior de la pantalla.

### 4. Ataque swoosh

- Se incorporaron los cuatro frames de la carpeta `assets/imagenes/swoosh/`.
- El ataque se activa al pulsar la tecla Z.
- La animacion y la colision del swoosh se trasladaron a `Personaje`.
- El swoosh aparece a la derecha del jugador.
- La propiedad `danio_swoosh` utiliza directamente el atributo `ataque` del jugador.
- El daño causado por el swoosh es proporcional al ataque del jugador.

### 5. Vida del enemigo y bossbar

- El Brujo de Cobalto tiene una vida maxima de 1325.
- Se incorporo una bossbar en la parte superior.
- La bossbar muestra la vida actual y la vida maxima del enemigo.
- La vida nunca puede bajar de cero.

### 6. Ataque del mago

- Se incorporaron los cinco sprites de `assets/imagenes/FBsprites/`:
  - `FB001.png`
  - `FB002.png`
  - `FB003.png`
  - `FB004.png`
  - `FB005.png`
- El mago lanza una bola de fuego cuando el jugador entra en un rango de 250 pixeles.
- Cada proyectil causa 4 puntos de daño.
- El ataque tiene un cooldown de 2 segundos.
- El proyectil mantiene una trayectoria recta hacia la posicion del jugador al momento del lanzamiento.
- Los sprites del proyectil se rotan 90 grados para orientarlos correctamente.
- El proyectil se desvanece al tocar los bordes de la pantalla si no golpea al jugador.

### 7. Estados de victoria y derrota

- Cuando la vida del jugador llega a cero, la partida se congela y se muestra el estado de derrota.
- Cuando la vida del Brujo de Cobalto llega a cero, la partida se congela y se muestra el estado de victoria.
- En ambos casos aparecen dos botones:
  - `Quieres luchar de nuevo con el mago de cobalto?`, que reinicia la partida.
  - `Salir`, que cierra el programa.
- Reiniciar crea de nuevo ambos personajes, restablece sus vidas, posiciones, cooldowns y proyectiles.

### 8. Ejecutable de Windows

- Se creo `Furiosa.exe` con PyInstaller.
- El ejecutable abre la interfaz directamente sin mostrar una consola.
- Se incluyeron los recursos de `assets/` dentro del ejecutable.
- Se agrego el icono `Icon.6_01.png`, convertido al formato `Icon.6_01.ico`.
- Se adaptaron las rutas de recursos para funcionar tanto desde Python como desde el ejecutable.
- Se excluyeron del repositorio las carpetas temporales `build/` y `__pycache__/` mediante `.gitignore`.

### 9. Repositorio GitHub

- Se creo el repositorio local Git.
- Se conecto el proyecto con `https://github.com/Rumblow/Furiosa.git`.
- La rama principal utilizada es `main`.
- El proyecto y el ejecutable se han preparado para subirse al repositorio remoto.

## Estado actual

El juego cuenta con un jugador controlable, atributos visibles, ataque swoosh, enemigo con bossbar, ataque de bolas de fuego, estados de victoria y derrota, reinicio de partida, salida del programa y un ejecutable de Windows con icono personalizado.
