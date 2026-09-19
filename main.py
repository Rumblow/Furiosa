import os
import sys
import pygame

import constantes
from personajes import Enemigo, Personaje


def ruta_recurso(*partes):
    carpeta_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpeta_base, *partes)


pygame.init()
ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA = ventana.get_size()
pygame.display.set_caption("Furiosa")
reloj = pygame.time.Clock()
fondo_base = pygame.image.load(
    ruta_recurso("assets", "imagenes", "background", "Background.png")
).convert()
fondo_combate = pygame.transform.smoothscale(
    fondo_base, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA)
)
fuente_titulo = pygame.font.Font(None, 46)
fuente = pygame.font.Font(None, 24)
fuente_pequena = pygame.font.Font(None, 20)


def cargar_par(imagen, carpeta=""):
    ruta = ruta_recurso("assets", "imagenes", carpeta, imagen)
    base, extension = os.path.splitext(imagen)
    izquierda = ruta_recurso("assets", "imagenes", carpeta, f"{base}_facing_left{extension}")
    imagen_base = pygame.image.load(ruta).convert_alpha()
    imagen_izquierda = pygame.image.load(izquierda).convert_alpha() if os.path.exists(izquierda) else pygame.transform.flip(imagen_base, True, False)
    return imagen_base, imagen_izquierda


def cargar_animacion(prefijo, cantidad, carpeta):
    normales = []
    izquierdas = []
    for indice in range(1, cantidad + 1):
        nombre = f"{prefijo}{indice:03}.png" if prefijo == "FB" else f"{prefijo}_{indice}.png"
        normal, izquierda = cargar_par(nombre, carpeta)
        normales.append(normal)
        izquierdas.append(izquierda)
    return normales, izquierdas


player_image, player_image_left = cargar_par("rpgcritters2_araña.png")
swoosh_frames, swoosh_frames_left = cargar_animacion("swoosh", 4, "swoosh")
fb_frames, fb_frames_left = cargar_animacion("FB", 5, "FBsprites")

ESTANCIAS = [
    {"nombre": "Sala de Cobalto", "enemigo": "Brujo de Cobalto", "imagen": "rpgcritters2_wizzard.png", "carpeta": "", "vida": 1325},
    {"nombre": "Galeria de los Huesos", "enemigo": "Guardian de Huesos", "imagen": "boss_1.png", "carpeta": "boss", "vida": 900},
    {"nombre": "Cripta del Engendro", "enemigo": "Engendro de Huesos", "imagen": "boos_2.png", "carpeta": "boss", "vida": 1150},
    {"nombre": "Nucleo de Ceniza", "enemigo": "Bestia de Ceniza", "imagen": "boss_3.png", "carpeta": "boss", "vida": 1700},
]

maximos_atributos = {"vida": 100, "ataque": 100, "defensa": 100, "velocidad": 10}
suelo = constantes.ALTO_VENTANA - 55


def crear_partida(estancia):
    imagen_enemigo, imagen_enemigo_left = cargar_par(estancia["imagen"], estancia["carpeta"])
    jugador = Personaje(70, suelo - player_image.get_height(), player_image, imagen_facing_left=player_image_left)
    enemigo = Enemigo(
        constantes.ANCHO_VENTANA - imagen_enemigo.get_width() - 80,
        suelo - imagen_enemigo.get_height(),
        imagen_enemigo,
        imagen_facing_left=imagen_enemigo_left,
        vida=estancia["vida"],
    )
    enemigo.facing_left = True
    jugador.configurar_swoosh(swoosh_frames, swoosh_frames_left)
    enemigo.configurar_ataque_fb(fb_frames, fb_frames_left)
    return jugador, enemigo


def dibujar_boton(rectangulo, texto, color, activo=True):
    pygame.draw.rect(ventana, color if activo else (55, 55, 55), rectangulo)
    pygame.draw.rect(ventana, (235, 235, 235), rectangulo, 2)
    superficie = fuente.render(texto, True, (255, 255, 255))
    ventana.blit(superficie, superficie.get_rect(center=rectangulo.center))


ancho_boton = min(760, constantes.ANCHO_VENTANA - 80)
x_boton = (constantes.ANCHO_VENTANA - ancho_boton) // 2
botones_estancias = [pygame.Rect(x_boton, 155 + indice * 105, ancho_boton, 72) for indice in range(len(ESTANCIAS))]
boton_repetir = pygame.Rect(constantes.ANCHO_VENTANA // 2 - 330, 420, 315, 55)
boton_menu = pygame.Rect(constantes.ANCHO_VENTANA // 2 + 15, 420, 315, 55)
estado = "seleccion"
estancia_seleccionada = None
jugador = None
enemigo = None
estado_final = None
mover_izquierda = False
mover_derecha = False
saltar = False


while True:
    reloj.tick(60)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if estado == "seleccion" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for indice, boton in enumerate(botones_estancias):
                if boton.collidepoint(evento.pos):
                    estancia_seleccionada = ESTANCIAS[indice]
                    jugador, enemigo = crear_partida(estancia_seleccionada)
                    estado = "combate"
                    estado_final = None
        elif estado == "final" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if boton_repetir.collidepoint(evento.pos):
                jugador, enemigo = crear_partida(estancia_seleccionada)
                estado = "combate"
                estado_final = None
            elif boton_menu.collidepoint(evento.pos):
                estado = "seleccion"
                estado_final = None
        elif estado == "combate" and evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = True
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = True
            elif evento.key == pygame.K_SPACE:
                saltar = True
            elif evento.key == pygame.K_z:
                jugador.activar_swoosh()
        elif estado == "combate" and evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = False
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = False
            elif evento.key == pygame.K_SPACE:
                saltar = False

    if estado == "combate":
        jugador.movimiento(mover_izquierda, mover_derecha, saltar, suelo)
        jugador.x = max(0, min(jugador.x, constantes.ANCHO_VENTANA - jugador.rect.width))
        jugador.rect.topleft = (jugador.x, jugador.y)
        enemigo.movimiento(
            constantes.ANCHO_VENTANA // 2,
            constantes.ANCHO_VENTANA - 35,
        )
        jugador.actualizar_swoosh()
        jugador.atacar_con_swoosh(enemigo)
        enemigo.atacar_con_fb(jugador)
        enemigo.actualizar_proyectiles(jugador, pygame.Rect(0, 0, constantes.ANCHO_VENTANA, suelo))
        if jugador.atributos["vida"] <= 0:
            estado_final = "derrota"
            estado = "final"
        elif enemigo.atributos["vida"] <= 0:
            estado_final = "victoria"
            estado = "final"

    ventana.fill((24, 27, 34))
    if estado == "seleccion":
        titulo = fuente_titulo.render("Selecciona una estancia", True, (255, 244, 210))
        ventana.blit(titulo, titulo.get_rect(center=(constantes.ANCHO_VENTANA // 2, 75)))
        subtitulo = fuente.render("Elige contra que enemigo quieres luchar", True, (190, 198, 210))
        ventana.blit(subtitulo, subtitulo.get_rect(center=(constantes.ANCHO_VENTANA // 2, 112)))
        for indice, (boton, estancia) in enumerate(zip(botones_estancias, ESTANCIAS)):
            dibujar_boton(boton, f"{indice + 1}. {estancia['nombre']}  |  {estancia['enemigo']}", (48, 94, 112))
    else:
        ventana.blit(fondo_combate, (0, 0))
        jugador.dibujar(ventana)
        jugador.dibujar_swoosh(ventana)
        enemigo.dibujar(ventana)
        enemigo.dibujar_proyectiles(ventana)
        ancho_bossbar = 520
        x_bossbar = (constantes.ANCHO_VENTANA - ancho_bossbar) // 2
        pygame.draw.rect(ventana, (35, 35, 35), (x_bossbar, 15, ancho_bossbar, 30))
        porcentaje_vida = max(0, enemigo.atributos["vida"] / enemigo.vida_maxima)
        pygame.draw.rect(ventana, (190, 35, 45), (x_bossbar + 2, 17, int((ancho_bossbar - 4) * porcentaje_vida), 26))
        texto_bossbar = fuente_pequena.render(f"{estancia_seleccionada['enemigo']}  {enemigo.atributos['vida']} / {enemigo.vida_maxima}", True, (255, 254, 254))
        ventana.blit(
            texto_bossbar,
            texto_bossbar.get_rect(center=(constantes.ANCHO_VENTANA // 2, 30)),
        )
        panel = pygame.Surface((238, 270), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 190))
        ventana.blit(panel, (18, 68))
        for indice, (nombre, valor) in enumerate(jugador.atributos.items()):
            x_barra = 32
            y_atributo = 84 + indice * 58
            porcentaje = min(1, max(0, valor / maximos_atributos[nombre]))
            ventana.blit(fuente_pequena.render(f"{nombre.capitalize()}: {valor}", True, (255, 255, 255)), (x_barra, y_atributo))
            pygame.draw.rect(ventana, (45, 45, 45), (x_barra, y_atributo + 25, 205, 16))
            pygame.draw.rect(ventana, (55, 190, 95) if nombre == "vida" else (70, 145, 210), (x_barra + 2, y_atributo + 27, int(201 * porcentaje), 12))
        if estado == "final":
            capa = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 190))
            ventana.blit(capa, (0, 0))
            mensaje = "Victoria!" if estado_final == "victoria" else "Derrota!"
            ventana.blit(fuente_titulo.render(mensaje, True, (255, 255, 255)), (constantes.ANCHO_VENTANA // 2 - 70, 285))
            dibujar_boton(boton_repetir, "Luchar de nuevo", (45, 125, 70))
            dibujar_boton(boton_menu, "Elegir otra estancia", (70, 90, 125))
    pygame.display.flip()
