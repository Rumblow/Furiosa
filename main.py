import os
import sys
import pygame
import constantes
from personajes import Personaje, Enemigo


def ruta_recurso(*partes):
    carpeta_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpeta_base, *partes)

pygame.init()

ventana = pygame.display.set_mode((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
pygame.display.set_caption("Furiosa")
fuente_atributos = pygame.font.Font(None, 22)

ruta_imagen = ruta_recurso("assets", "imagenes", "rpgcritters2_ara\u00f1a.png")
player_image = pygame.image.load(ruta_imagen).convert_alpha()
ruta_imagen_enemigo = ruta_recurso("assets", "imagenes", "rpgcritters2_wizzard.png")
enemy_image = pygame.image.load(ruta_imagen_enemigo).convert_alpha()
rutas_swoosh = [
    ruta_recurso("assets", "imagenes", "swoosh", f"swoosh_{indice}.png")
    for indice in range(1, 5)
]
swoosh_frames = [pygame.image.load(ruta).convert_alpha() for ruta in rutas_swoosh]
rutas_fb = [
    ruta_recurso("assets", "imagenes", "FBsprites", f"FB{indice:03}.png")
    for indice in range(1, 6)
]
fb_frames = [pygame.image.load(ruta).convert_alpha() for ruta in rutas_fb]

maximos_atributos = {
    "vida": 100,
    "ataque": 100,
    "defensa": 100,
    "velocidad": 10,
}


def crear_partida():
    jugador = Personaje(x=50, y=50, imagen=player_image)
    enemigo = Enemigo(x=500, y=300, imagen=enemy_image)
    jugador.configurar_swoosh(swoosh_frames)
    enemigo.configurar_ataque_fb(fb_frames)
    return jugador, enemigo


def dibujar_boton(ventana, rectangulo, texto, fuente, color):
    pygame.draw.rect(ventana, color, rectangulo)
    pygame.draw.rect(ventana, (255, 255, 255), rectangulo, 2)
    superficie_texto = fuente.render(texto, True, (255, 255, 255))
    ventana.blit(superficie_texto, superficie_texto.get_rect(center=rectangulo.center))


jugador, enemigo = crear_partida()
fuente_final = pygame.font.Font(None, 32)
fuente_boton = pygame.font.Font(None, 24)
boton_repetir = pygame.Rect(55, 360, 565, 52)
boton_salir = pygame.Rect(640, 360, 105, 52)
estado_final = None

# Definir las variables de movimiento del jugador
mover_arriba = False
mover_abajo = False
mover_izquierda = False
mover_derecha = False

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    reloj.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        elif estado_final is not None:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_repetir.collidepoint(evento.pos):
                    jugador, enemigo = crear_partida()
                    estado_final = None
                    mover_arriba = False
                    mover_abajo = False
                    mover_izquierda = False
                    mover_derecha = False
                elif boton_salir.collidepoint(evento.pos):
                    ejecutando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_w, pygame.K_UP):
                mover_arriba = True
            elif evento.key in (pygame.K_s, pygame.K_DOWN):
                mover_abajo = True
            elif evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = True
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = True
            elif evento.key == pygame.K_z:
                jugador.activar_swoosh()

        elif evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_w, pygame.K_UP):
                mover_arriba = False
            elif evento.key in (pygame.K_s, pygame.K_DOWN):
                mover_abajo = False
            elif evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = False
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = False

    if estado_final is None:
        jugador.movimiento(mover_arriba, mover_abajo, mover_izquierda, mover_derecha)

        jugador.actualizar_swoosh()
        jugador.atacar_con_swoosh(enemigo)
        enemigo.atacar_con_fb(jugador)
        enemigo.actualizar_proyectiles(
            jugador,
            pygame.Rect(0, 0, constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA),
        )

        if jugador.atributos["vida"] <= 0:
            estado_final = "derrota"
        elif enemigo.atributos["vida"] <= 0:
            estado_final = "victoria"

    ventana.fill((30, 30, 30))
    jugador.dibujar(ventana)
    jugador.dibujar_swoosh(ventana)
    enemigo.dibujar(ventana)
    enemigo.dibujar_proyectiles(ventana)

    ancho_bossbar = 520
    alto_bossbar = 30
    x_bossbar = (constantes.ANCHO_VENTANA - ancho_bossbar) // 2
    y_bossbar = 15
    pygame.draw.rect(
        ventana,
        (35, 35, 35),
        (x_bossbar, y_bossbar, ancho_bossbar, alto_bossbar),
    )
    porcentaje_vida = enemigo.atributos["vida"] / enemigo.vida_maxima
    pygame.draw.rect(
        ventana,
        (190, 35, 45),
        (x_bossbar + 2, y_bossbar + 2, int((ancho_bossbar - 4) * porcentaje_vida), alto_bossbar - 4),
    )
    texto_bossbar = fuente_atributos.render(
        f"Brujo de Cobalto  {enemigo.atributos['vida']} / {enemigo.vida_maxima}",
        True,
        (255, 254, 254),
    )
    ventana.blit(texto_bossbar, texto_bossbar.get_rect(center=(constantes.ANCHO_VENTANA // 2, y_bossbar + alto_bossbar // 2)))

    panel_atributos = pygame.Surface((constantes.ANCHO_VENTANA - 20, 105), pygame.SRCALPHA)
    panel_atributos.fill((0, 0, 0, 190))
    ventana.blit(panel_atributos, (10, constantes.ALTO_VENTANA - 115))
    ancho_barra = 160
    alto_barra = 16
    separacion = 190
    for indice, (nombre, valor) in enumerate(jugador.atributos.items()):
        x_barra = 25 + indice * separacion
        y_barra = constantes.ALTO_VENTANA - 75
        maximo = maximos_atributos[nombre]
        porcentaje = min(1, max(0, valor / maximo))
        texto = fuente_atributos.render(
            f"{nombre.capitalize()}: {valor}", True, (255, 255, 255)
        )
        ventana.blit(texto, (x_barra, constantes.ALTO_VENTANA - 105))
        pygame.draw.rect(ventana, (45, 45, 45), (x_barra, y_barra, ancho_barra, alto_barra))
        pygame.draw.rect(
            ventana,
            (55, 190, 95) if nombre == "vida" else (70, 145, 210),
            (x_barra + 2, y_barra + 2, int((ancho_barra - 4) * porcentaje), alto_barra - 4),
        )

    if estado_final is not None:
        capa_final = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA), pygame.SRCALPHA)
        capa_final.fill((0, 0, 0, 190))
        ventana.blit(capa_final, (0, 0))
        if estado_final == "victoria":
            mensaje = "Victoria! Has derrotado al Brujo de Cobalto"
        else:
            mensaje = "Derrota! El Brujo de Cobalto te ha vencido"
        texto_final = fuente_final.render(mensaje, True, (255, 255, 255))
        ventana.blit(texto_final, texto_final.get_rect(center=(constantes.ANCHO_VENTANA // 2, 285)))
        dibujar_boton(
            ventana,
            boton_repetir,
            "Quieres luchar de nuevo con el mago de cobalto?",
            fuente_boton,
            (45, 125, 70),
        )
        dibujar_boton(ventana, boton_salir, "Salir", fuente_boton, (150, 45, 45))

    pygame.display.flip()

pygame.quit()

