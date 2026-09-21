import os
import sys
import pygame
from sound_manager import SoundManager

import constantes
from personajes import Demon, Enemigo, Orc, Soldier

def ruta_recurso(*partes):
    carpeta_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpeta_base, *partes)


pygame.init()
audio = SoundManager()
audio.play_music(
    ruta_recurso(
        "assets",
        "sounds",
        "musica",
        "Troye Sivan - One Of Your Girls (Official Instrumental).mp3",
    ),
    volume=0.4,
)
ZOOM_GENERAL = 0.85
ZOOM_COMBATE = 1.5
constantes.ANCHO_VENTANA = 928
constantes.ALTO_VENTANA = 793
tamano_inicial = (
    round(constantes.ANCHO_VENTANA * ZOOM_GENERAL),
    round(constantes.ALTO_VENTANA * ZOOM_GENERAL),
)
pantalla = pygame.display.set_mode(tamano_inicial, pygame.RESIZABLE)
ventana = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
pantalla_completa = False
tamano_ventana = tamano_inicial
pygame.display.set_caption("Furiosa")
reloj = pygame.time.Clock()
fondo_base = pygame.image.load(
    ruta_recurso("assets", "imagenes", "background", "Background.png")
).convert()
fondo_combate = pygame.transform.smoothscale(
    fondo_base, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA)
)
fondo_inicio = pygame.image.load(
    ruta_recurso("assets", "imagenes", "background", "main_background.jpg")
).convert()
fuente_medieval = pygame.font.match_font("book antiqua") or pygame.font.match_font("papyrus")
fuente_titulo = pygame.font.Font(fuente_medieval, 46)
fuente = pygame.font.Font(fuente_medieval, 24)
fuente_pequena = pygame.font.Font(fuente_medieval, 20)

COLOR_PERGAMINO = (255, 226, 166)
COLOR_TEXTO = (247, 238, 211)
COLOR_MADERA = (63, 38, 29)
COLOR_MADERA_CLARA = (108, 65, 38)
COLOR_BRONCE = (184, 126, 51)
COLOR_BRONCE_CLARO = (235, 184, 86)
COLOR_DESHABILITADO = (86, 77, 67)


def posicion_logica(posicion):
    destino = rect_escena()
    if destino.width <= 0 or destino.height <= 0:
        return posicion
    return (
        round((posicion[0] - destino.left) * constantes.ANCHO_VENTANA / destino.width),
        round((posicion[1] - destino.top) * constantes.ALTO_VENTANA / destino.height),
    )


def rect_escena():
    ancho_pantalla, alto_pantalla = pantalla.get_size()
    escala_base = min(
        ancho_pantalla / constantes.ANCHO_VENTANA,
        alto_pantalla / constantes.ALTO_VENTANA,
    )
    escala = escala_base * (ZOOM_COMBATE if estado == "combate" else 1.0)
    ancho_escena = max(1, round(constantes.ANCHO_VENTANA * escala))
    alto_escena = max(1, round(constantes.ALTO_VENTANA * escala))
    return pygame.Rect(
        (ancho_pantalla - ancho_escena) // 2,
        alto_pantalla - alto_escena,
        ancho_escena,
        alto_escena,
    )


def alternar_pantalla_completa():
    global pantalla, pantalla_completa, tamano_ventana
    if pantalla_completa:
        pantalla = pygame.display.set_mode(tamano_ventana, pygame.RESIZABLE)
        pantalla_completa = False
    else:
        tamano_ventana = pantalla.get_size()
        pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pantalla_completa = True


def dibujar_marco(rectangulo, color=COLOR_BRONCE):
    pygame.draw.rect(pantalla, color, rectangulo, 2)
    marco_interior = rectangulo.inflate(-8, -8)
    if marco_interior.width > 0 and marco_interior.height > 0:
        pygame.draw.rect(pantalla, COLOR_BRONCE_CLARO, marco_interior, 1)


def dibujar_boton_medieval(rectangulo, texto, activo=True):
    color = COLOR_MADERA_CLARA if activo else COLOR_DESHABILITADO
    pygame.draw.rect(pantalla, color, rectangulo)
    dibujar_marco(rectangulo, COLOR_BRONCE if activo else (120, 106, 85))
    superficie = fuente.render(texto, True, COLOR_TEXTO if activo else (157, 148, 131))
    pantalla.blit(superficie, superficie.get_rect(center=rectangulo.center))


def dibujar_panel_pixelado(rectangulo, fondo=(20, 16, 19)):
    pygame.draw.rect(pantalla, fondo, rectangulo)
    pygame.draw.rect(pantalla, (12, 10, 12), rectangulo.inflate(-4, -4), 3)
    pygame.draw.line(pantalla, (157, 111, 55), rectangulo.topleft, (rectangulo.right - 5, rectangulo.top), 3)
    pygame.draw.line(pantalla, (157, 111, 55), rectangulo.topleft, (rectangulo.left, rectangulo.bottom - 5), 3)
    pygame.draw.line(pantalla, (74, 48, 36), (rectangulo.left + 5, rectangulo.bottom - 2), (rectangulo.right, rectangulo.bottom - 2), 3)
    pygame.draw.line(pantalla, (74, 48, 36), (rectangulo.right - 2, rectangulo.top + 5), (rectangulo.right - 2, rectangulo.bottom), 3)


def dibujar_barra_segmentada(rectangulo, porcentaje, color, segmentos=12):
    pygame.draw.rect(pantalla, (12, 10, 12), rectangulo)
    pygame.draw.rect(pantalla, (90, 63, 42), rectangulo, 2)
    separacion = 3
    ancho_segmento = max(1, (rectangulo.width - separacion * (segmentos - 1)) // segmentos)
    segmentos_llenos = round(max(0, min(1, porcentaje)) * segmentos)
    for indice in range(segmentos):
        x_segmento = rectangulo.left + indice * (ancho_segmento + separacion)
        color_segmento = color if indice < segmentos_llenos else (37, 30, 29)
        pygame.draw.rect(
            pantalla,
            color_segmento,
            (x_segmento, rectangulo.top + 3, ancho_segmento, rectangulo.height - 6),
        )


def rect_botones_inicio():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(330, max(220, ancho - 80))
    alto_boton = 52
    separacion = 14
    alto_grupo = alto_boton * 3 + separacion * 2
    x_boton = max(42, round(ancho * 0.08))
    y_inicial = max(140, alto - alto_grupo - 78)
    return [
        pygame.Rect(x_boton, y_inicial + indice * (alto_boton + separacion), ancho_boton, alto_boton)
        for indice in range(3)
    ]


def dibujar_menu_inicio():
    if estado != "inicio":
        return
    ancho, alto = pantalla.get_size()
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    capa.fill((24, 12, 8, 75))
    pantalla.blit(capa, (0, 0))
    botones = rect_botones_inicio()
    panel = pygame.Rect(botones[0].left - 30, botones[0].top - 30, botones[0].width + 60, botones[-1].bottom - botones[0].top + 60)
    pygame.draw.rect(pantalla, (34, 22, 18, 205), panel)
    dibujar_marco(panel)
    for indice, (boton, texto) in enumerate(zip(botones, ("Jugar", "Opciones", "Salir"))):
        dibujar_boton_medieval(boton, texto, activo=indice != 1)


def dibujar_hud_fijo():
    if estado not in ("combate", "final") or jugador is None or enemigo is None:
        return

    ancho_pantalla, _ = pantalla.get_size()
    ancho_bossbar = min(520, max(220, ancho_pantalla - 40))
    x_bossbar = (ancho_pantalla - ancho_bossbar) // 2
    bossbar_rect = pygame.Rect(x_bossbar, 12, ancho_bossbar, 38)
    dibujar_panel_pixelado(bossbar_rect, (29, 20, 22))
    porcentaje_vida = max(0, enemigo.atributos["vida"] / enemigo.vida_maxima)
    dibujar_barra_segmentada(
        pygame.Rect(x_bossbar + 8, 18, ancho_bossbar - 16, 17),
        porcentaje_vida,
        (190, 45, 50),
        segmentos=max(10, ancho_bossbar // 34),
    )
    texto_bossbar = fuente_pequena.render(
        f"{estancia_seleccionada['enemigo']}  {enemigo.atributos['vida']} / {enemigo.vida_maxima}",
        True,
        COLOR_TEXTO,
    )
    pantalla.blit(
        texto_bossbar,
        texto_bossbar.get_rect(center=(ancho_pantalla // 2, 22)),
    )

    panel_rect = pygame.Rect(18, 68, 238, 270)
    dibujar_panel_pixelado(panel_rect, (22, 18, 21))
    for indice, (nombre, valor) in enumerate(jugador.atributos.items()):
        x_barra = 32
        y_atributo = 84 + indice * 58
        porcentaje = min(1, max(0, valor / maximos_atributos[nombre]))
        pantalla.blit(
            fuente_pequena.render(f"{nombre.capitalize()}  {valor}", True, COLOR_TEXTO),
            (x_barra, y_atributo),
        )
        dibujar_barra_segmentada(
            pygame.Rect(x_barra, y_atributo + 25, 205, 16),
            porcentaje,
            (65, 192, 92) if nombre == "vida" else (70, 148, 202),
            segmentos=10,
        )


def rect_botones_finales():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(270, max(120, (ancho - 64) // 3))
    y_boton = min(alto - 80, alto // 2 + 105)
    x_centro = ancho // 2
    return (
        pygame.Rect(x_centro - ancho_boton - 8 - ancho_boton // 2, y_boton, ancho_boton, 55),
        pygame.Rect(x_centro - ancho_boton // 2, y_boton, ancho_boton, 55),
        pygame.Rect(x_centro + 8 + ancho_boton // 2, y_boton, ancho_boton, 55),
    )


def dibujar_pantalla_final_fija():
    if estado != "final":
        return
    ancho, alto = pantalla.get_size()
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    capa.fill((24, 12, 8, 205))
    pantalla.blit(capa, (0, 0))
    mensaje = "Victoria!" if estado_final == "victoria" else "Derrota!"
    titulo_final = fuente_titulo.render(mensaje, True, COLOR_PERGAMINO)
    pantalla.blit(titulo_final, titulo_final.get_rect(center=(ancho // 2, alto // 2 - 55)))
    botones_finales = rect_botones_finales()
    for rectangulo, texto in zip(
        botones_finales,
        ("Luchar de nuevo", "Elegir otra estancia", "Menu principal"),
    ):
        dibujar_boton_medieval(rectangulo, texto)


def rect_botones_pausa():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(420, max(240, ancho - 80))
    alto_boton = 48
    separacion = 10
    x_boton = (ancho - ancho_boton) // 2
    y_inicial = max(90, alto // 2 - 150)
    return [
        pygame.Rect(x_boton, y_inicial + indice * (alto_boton + separacion), ancho_boton, alto_boton)
        for indice in range(6)
    ]


def dibujar_menu_pausa():
    if not pausa_activa:
        return
    ancho, alto = pantalla.get_size()
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    capa.fill((24, 12, 8, 210))
    pantalla.blit(capa, (0, 0))
    botones = rect_botones_pausa()
    panel = pygame.Rect(botones[0].left - 30, botones[0].top - 72, botones[0].width + 60, botones[-1].bottom - botones[0].top + 102)
    pygame.draw.rect(pantalla, (34, 22, 18, 220), panel)
    dibujar_marco(panel)
    titulo = fuente_titulo.render("Juego en pausa", True, COLOR_PERGAMINO)
    pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, max(45, alto // 2 - 205))))
    textos = (
        "Regresar a la batalla",
        "Guardar partida",
        "Configuracion",
        "Cambiar de instancia",
        "Menu principal",
        "Salir del juego",
    )
    for indice, (rectangulo, texto) in enumerate(zip(botones, textos)):
        habilitado = indice in (0, 3, 4, 5)
        dibujar_boton_medieval(rectangulo, texto, activo=habilitado)


def rect_botones_estancias_fijos():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(760, max(260, ancho - 80))
    alto_boton = min(72, max(48, (alto - 260) // max(1, len(ESTANCIAS))))
    separacion = min(105, alto_boton + 28)
    x_boton = (ancho - ancho_boton) // 2
    y_inicial = max(110, (alto - (len(ESTANCIAS) - 1) * separacion - alto_boton) // 2)
    return [
        pygame.Rect(x_boton, y_inicial + indice * separacion, ancho_boton, alto_boton)
        for indice in range(len(ESTANCIAS))
    ]


def rect_boton_menu_principal():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(300, max(220, ancho - 80))
    return pygame.Rect(
        (ancho - ancho_boton) // 2,
        alto - 68,
        ancho_boton,
        44,
    )


def rect_botones_personajes():
    ancho, alto = pantalla.get_size()
    ancho_tarjeta = min(260, max(170, (ancho - 120) // 3))
    alto_tarjeta = min(320, max(245, alto - 260))
    separacion = 20
    ancho_total = ancho_tarjeta * 3 + separacion * 2
    x_inicial = (ancho - ancho_total) // 2
    y_inicial = 130
    return (
        pygame.Rect(x_inicial, y_inicial, ancho_tarjeta, alto_tarjeta),
        pygame.Rect(x_inicial + ancho_tarjeta + separacion, y_inicial, ancho_tarjeta, alto_tarjeta),
        pygame.Rect(x_inicial + (ancho_tarjeta + separacion) * 2, y_inicial, ancho_tarjeta, alto_tarjeta),
    )


def dibujar_selector_personaje_fijo():
    if estado != "personaje":
        return
    ancho, alto = pantalla.get_size()
    pantalla.fill((38, 24, 18))
    tarjetas = rect_botones_personajes()
    panel = pygame.Rect(
        tarjetas[0].left - 28,
        tarjetas[0].top - 78,
        tarjetas[-1].right - tarjetas[0].left + 56,
        tarjetas[0].height + 120,
    )
    pygame.draw.rect(pantalla, (49, 31, 23), panel)
    dibujar_marco(panel)
    titulo = fuente_titulo.render("Elige a tu heroe", True, COLOR_PERGAMINO)
    pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 50)))
    subtitulo = fuente.render("Selecciona un guerrero antes de entrar en combate", True, (214, 190, 151))
    pantalla.blit(subtitulo, subtitulo.get_rect(center=(ancho // 2, 83)))

    for tarjeta, imagen, nombre, descripcion in (
        (tarjetas[0], soldier_icon, "Soldier", "Arquero equilibrado"),
        (tarjetas[1], terrible_knight_icon, "Terrible Knight", "Caballero de espada"),
        (tarjetas[2], bridge_heroine_icon, "Bridge Heroine", "Heroina de espada"),
    ):
        pygame.draw.rect(pantalla, COLOR_MADERA_CLARA, tarjeta)
        dibujar_marco(tarjeta)
        imagen_maximo = min(180, tarjeta.width - 55)
        escala = min(imagen_maximo / imagen.get_width(), 185 / imagen.get_height())
        imagen_mostrada = pygame.transform.scale(
            imagen,
            (max(1, round(imagen.get_width() * escala)), max(1, round(imagen.get_height() * escala))),
        )
        pantalla.blit(
            imagen_mostrada,
            imagen_mostrada.get_rect(center=(tarjeta.centerx, tarjeta.top + tarjeta.height // 2 - 20)),
        )
        texto_nombre = fuente.render(nombre, True, COLOR_TEXTO)
        pantalla.blit(texto_nombre, texto_nombre.get_rect(center=(tarjeta.centerx, tarjeta.bottom - 54)))
        texto_descripcion = fuente_pequena.render(descripcion, True, (214, 190, 151))
        pantalla.blit(texto_descripcion, texto_descripcion.get_rect(center=(tarjeta.centerx, tarjeta.bottom - 25)))
    dibujar_boton_medieval(rect_boton_menu_principal(), "Menu principal")


def dibujar_selector_estancias_fijo():
    if estado != "seleccion":
        return
    ancho, alto = pantalla.get_size()
    pantalla.fill((38, 24, 18))
    botones = rect_botones_estancias_fijos()
    panel = pygame.Rect(botones[0].left - 30, max(18, botones[0].top - 105), botones[0].width + 60, botones[-1].bottom - max(18, botones[0].top - 105) + 30)
    pygame.draw.rect(pantalla, (49, 31, 23), panel)
    dibujar_marco(panel)
    titulo = fuente_titulo.render("Elige tu estancia", True, COLOR_PERGAMINO)
    pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 55)))
    subtitulo = fuente.render(
        "Elige contra que enemigo quieres luchar", True, (214, 190, 151)
    )
    pantalla.blit(subtitulo, subtitulo.get_rect(center=(ancho // 2, 90)))
    for indice, (boton, estancia) in enumerate(zip(botones, ESTANCIAS)):
        pygame.draw.rect(pantalla, COLOR_MADERA_CLARA, boton)
        dibujar_marco(boton)
        texto = fuente.render(
            f"{indice + 1}. {estancia['nombre']}  |  {estancia['enemigo']}",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(texto, texto.get_rect(center=boton.center))
    dibujar_boton_medieval(rect_boton_menu_principal(), "Menu principal")


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


def cargar_animacion_teletransporte(cantidad):
    normales = []
    izquierdas = []
    for indice in range(1, cantidad + 1):
        normal, izquierda = cargar_par(
            f"A200-{indice}.png", "teleport_atack_animation"
        )
        normales.append(normal)
        izquierdas.append(izquierda)
    return normales, izquierdas


def cargar_animacion_claw(cantidad):
    normales = []
    izquierdas = []
    for indice in range(1, cantidad + 1):
        nombre = f"CS{indice:03}.png"
        ruta_izquierda = ruta_recurso(
            "assets", "imagenes", "claw_scratc_attack", f"CS{indice:03}_facing_left.png"
        )
        if not os.path.exists(ruta_izquierda):
            ruta_izquierda = ruta_recurso(
                "assets", "imagenes", "claw_scratc_attack", f"CS{indice:03}_left_facing.png"
            )
        normal = pygame.image.load(
            ruta_recurso("assets", "imagenes", "claw_scratc_attack", nombre)
        ).convert_alpha()
        izquierda = pygame.image.load(ruta_izquierda).convert_alpha()
        normales.append(normal)
        izquierdas.append(izquierda)
    return normales, izquierdas


def cargar_animacion_personaje(personaje, carpeta, prefijo, cantidad):
    frames = []
    for indice in range(cantidad):
        nombre = f"{prefijo}_{indice:03}.png"
        frames.append(
            pygame.image.load(
                ruta_recurso("assets", "imagenes", personaje, carpeta, nombre)
            ).convert_alpha()
        )
    return frames


def cargar_animaciones_personaje(personaje, estados):
    return {
        estado: cargar_animacion_personaje(personaje, carpeta, prefijo, cantidad)
        for estado, (carpeta, prefijo, cantidad) in estados.items()
    }


def cargar_frames_carpeta(personaje, carpeta):
    ruta_carpeta = ruta_recurso("assets", "imagenes", personaje, carpeta)
    archivos = [
        archivo
        for archivo in os.listdir(ruta_carpeta)
        if archivo.lower().endswith(".png")
    ]
    archivos.sort(key=lambda archivo: int("".join(filter(str.isdigit, archivo)) or 0))
    return [
        pygame.image.load(os.path.join(ruta_carpeta, archivo)).convert_alpha()
        for archivo in archivos
    ]


def cargar_frames_terrible_knight(carpeta):
    ruta_carpeta = ruta_recurso("assets", "imagenes", "Terrible Knight", "Sprites", carpeta)
    archivos = [
        archivo
        for archivo in os.listdir(ruta_carpeta)
        if archivo.lower().endswith(".png")
    ]
    archivos.sort(key=lambda archivo: int("".join(filter(str.isdigit, archivo)) or 0))
    return [
        pygame.image.load(os.path.join(ruta_carpeta, archivo)).convert_alpha()
        for archivo in archivos
    ]


def cargar_animaciones_terrible_knight():
    return {
        "idle": cargar_frames_terrible_knight("Idle"),
        "walk": cargar_frames_terrible_knight("Run"),
        "hurt": cargar_frames_terrible_knight("Hurt"),
    }


def cargar_ataques_terrible_knight():
    return {
        1: cargar_frames_terrible_knight("AttackSide"),
        2: cargar_frames_terrible_knight("AttackUp"),
        3: cargar_frames_terrible_knight("AttackCrouch"),
    }


player_image, player_image_left = cargar_par("rpgcritters2_araña.png")
swoosh_frames, swoosh_frames_left = cargar_animacion("swoosh", 4, "swoosh")
fb_frames, fb_frames_left = cargar_animacion("FB", 5, "FBsprites")
teleport_frames, teleport_frames_left = cargar_animacion_teletransporte(4)
claw_frames, claw_frames_left = cargar_animacion_claw(8)
soldier_animations = {
    "idle": ("Soldier-Idle-frames", "Soldier-Idle", 6),
    "walk": ("Soldier-Walk-frames", "Soldier-Walk", 8),
    "hurt": ("Soldier-Hurt-frames", "Soldier-Hurt", 4),
    "death": ("Soldier-Death-frames", "Soldier-Death", 9),
}
soldier_animations = cargar_animaciones_personaje("Soldier", soldier_animations)
soldier_image = soldier_animations["idle"][0]
soldier_attacks = {
    1: cargar_animacion_personaje("Soldier", "Soldier-Attack01-frames", "Soldier-Attack01", 6),
    2: cargar_animacion_personaje("Soldier", "Soldier-Attack02-frames", "Soldier-Attack02", 6),
    3: cargar_animacion_personaje("Soldier", "Soldier-Attack03-frames", "Soldier-Attack03", 9),
}
arrow_image = pygame.image.load(
    ruta_recurso("assets", "imagenes", "Soldier", "Arrow(projectile)", "Arrow01(100x100).png")
).convert_alpha()
orc_animations = cargar_animaciones_personaje("Orc", {
    "idle": ("Orc-Idle-frames", "Orc-Idle", 6),
    "walk": ("Orc-Walk-frames", "Orc-Walk", 8),
    "hurt": ("Orc-Hurt-frames", "Orc-Hurt", 4),
    "death": ("Orc-Death-frames", "Orc-Death", 9),
})
orc_image = orc_animations["idle"][0]
orc_attacks = {
    1: cargar_animacion_personaje("Orc", "Orc-Attack01-frames", "Orc-Attack01", 6),
    2: cargar_animacion_personaje("Orc", "Orc-Attack02-frames", "Orc-Attack02", 6),
}
terrible_knight_animations = cargar_animaciones_terrible_knight()
terrible_knight_attacks = cargar_ataques_terrible_knight()
terrible_knight_image = terrible_knight_animations["idle"][0]
terrible_knight_dagger = pygame.image.load(
    ruta_recurso("assets", "imagenes", "Terrible Knight", "Projectiles", "dagger.png")
).convert_alpha()
bridge_heroine_animations = {
    "idle": cargar_frames_carpeta("Bridge Heroine", "Heroine base/Sprites/idle"),
    "walk": cargar_frames_carpeta("Bridge Heroine", "Heroine base/Sprites/run"),
    "hurt": cargar_frames_carpeta("Bridge Heroine", "Heroine base/Sprites/idle"),
    "death": cargar_frames_carpeta("Bridge Heroine", "Heroine base/Sprites/idle"),
}
bridge_heroine_image = bridge_heroine_animations["idle"][0]
bridge_heroine_attacks = {
    1: cargar_frames_carpeta("Bridge Heroine", "Heroine base/Sprites/player-attack"),
}
soldier_icon = pygame.image.load(
    ruta_recurso("assets", "imagenes", "players_icons", "icon1.jpg")
).convert()
terrible_knight_icon = pygame.image.load(
    ruta_recurso("assets", "imagenes", "players_icons", "icon2.jpg")
).convert()
bridge_heroine_icon = pygame.image.load(
    ruta_recurso("assets", "imagenes", "players_icons", "icon_3.jpg")
).convert()
demon_idle_frames = cargar_frames_carpeta("demon-Files", "Sprites/Idle")
demon_image = demon_idle_frames[0]
demon_attack_frames = cargar_frames_carpeta("demon-Files", "Sprites/DemonAttack")
demon_breath_frames = cargar_frames_carpeta("demon-Files", "Sprites/DemonAttackBreath")

ESTANCIAS = [
    {"nombre": "Sala de Cobalto", "enemigo": "Brujo de Cobalto", "imagen": "rpgcritters2_wizzard.png", "carpeta": "", "vida": 260, "ataque": 14, "defensa": 8, "velocidad_enemigo": 1.0, "patrulla": (0.68, 0.90)},
    {"nombre": "Galeria de los Huesos", "enemigo": "Guardian de Huesos", "imagen": "boss_1.png", "carpeta": "boss", "vida": 900},
    {"nombre": "Cripta del Engendro", "enemigo": "Engendro de Huesos", "imagen": "boos_2.png", "carpeta": "boss", "vida": 1150},
    {"nombre": "Nucleo de Ceniza", "enemigo": "Bestia de Ceniza", "imagen": "boss_3.png", "carpeta": "boss", "vida": 1700, "teletransporte": True},
    {"nombre": "Guarida del Orc", "enemigo": "Orc", "orc": True, "vida": 220, "ataque": 16, "defensa": 8, "velocidad_enemigo": 1.6, "patrulla": (0.44, 0.55)},
    {"nombre": "Santuario del Demon", "enemigo": "Demon", "demon": True, "vida": 520, "ataque": 18, "defensa": 7, "velocidad_enemigo": 1.2, "patrulla": (0.52, 0.82)},
]

maximos_atributos = {"vida": 140, "ataque": 100, "defensa": 100, "velocidad": 10}
suelo = constantes.ALTO_VENTANA - 55


def crear_partida(estancia, personaje_seleccionado):
    if personaje_seleccionado == "terrible_knight":
        jugador = Soldier(
            70,
            suelo - terrible_knight_image.get_height(),
            terrible_knight_image,
            vida=150,
            ataque=20,
            defensa=10,
            velocidad=4.5,
        )
        animaciones_jugador = terrible_knight_animations
        ataques_jugador = terrible_knight_attacks
        proyectil_jugador = terrible_knight_dagger
    elif personaje_seleccionado == "bridge_heroine":
        jugador = Soldier(
            70,
            suelo - bridge_heroine_image.get_height(),
            bridge_heroine_image,
            vida=135,
            ataque=19,
            defensa=7,
            velocidad=3.2,
        )
        animaciones_jugador = bridge_heroine_animations
        ataques_jugador = bridge_heroine_attacks
        proyectil_jugador = arrow_image
    else:
        jugador = Soldier(
            70,
            suelo - soldier_image.get_height(),
            soldier_image,
            vida=140,
            ataque=18,
            defensa=8,
        )
        animaciones_jugador = soldier_animations
        ataques_jugador = soldier_attacks
        proyectil_jugador = arrow_image
    if estancia.get("orc"):
        enemigo = Orc(
            constantes.ANCHO_VENTANA - orc_image.get_width() - 80,
            suelo - orc_image.get_height(),
            orc_image,
            orc_animations,
            orc_attacks,
            vida=estancia["vida"],
            ataque=estancia.get("ataque", 16),
            defensa=estancia.get("defensa", 8),
            velocidad=estancia.get("velocidad_enemigo", 1.6),
        )
    elif estancia.get("demon"):
        enemigo = Demon(
            constantes.ANCHO_VENTANA - demon_image.get_width() - 80,
            suelo - demon_image.get_height(),
            demon_idle_frames,
            {1: demon_attack_frames, 2: demon_breath_frames},
            vida=estancia["vida"],
            ataque=estancia.get("ataque", 18),
            defensa=estancia.get("defensa", 7),
        )
    else:
        if estancia.get("demon"):
            imagen_enemigo = demon_image
            imagen_enemigo_left = pygame.transform.flip(demon_image, True, False)
        else:
            imagen_enemigo, imagen_enemigo_left = cargar_par(estancia["imagen"], estancia["carpeta"])
        enemigo = Enemigo(
            constantes.ANCHO_VENTANA - imagen_enemigo.get_width() - 80,
            suelo - imagen_enemigo.get_height(),
            imagen_enemigo,
            imagen_facing_left=imagen_enemigo_left,
            vida=estancia["vida"],
            ataque=estancia.get("ataque", 10),
            defensa=estancia.get("defensa", 5),
            velocidad=estancia.get("velocidad_enemigo", 2.1),
            puede_teletransportarse=estancia.get("teletransporte", False),
        )
    enemigo.facing_left = True
    jugador.configurar_animaciones(animaciones_jugador)
    jugador.configurar_ataques(ataques_jugador)
    jugador.configurar_arrow([proyectil_jugador])
    if not estancia.get("orc") and not estancia.get("demon"):
        enemigo.configurar_ataque_fb(fb_frames, fb_frames_left)
    if enemigo.puede_teletransportarse:
        enemigo.configurar_teletransporte(teleport_frames, teleport_frames_left)
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
estado = "inicio"
pausa_activa = False
estancia_seleccionada = None
personaje_seleccionado = "soldier"
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
        if evento.type == pygame.VIDEORESIZE and not pantalla_completa:
            if evento.w > 0 and evento.h > 0:
                pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                alternar_pantalla_completa()
                continue
            if evento.key == pygame.K_ESCAPE:
                if estado == "combate":
                    pausa_activa = not pausa_activa
                    if pausa_activa:
                        mover_izquierda = False
                        mover_derecha = False
                        saltar = False
                continue
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado == "inicio":
                botones_inicio = rect_botones_inicio()
                if botones_inicio[0].collidepoint(evento.pos):
                    estado = "personaje"
                    continue
                if botones_inicio[2].collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()
                continue
            if pausa_activa:
                botones_pausa = rect_botones_pausa()
                if botones_pausa[0].collidepoint(evento.pos):
                    pausa_activa = False
                    continue
                if botones_pausa[3].collidepoint(evento.pos):
                    pausa_activa = False
                    estado = "seleccion"
                    estado_final = None
                    continue
                if botones_pausa[4].collidepoint(evento.pos):
                    pausa_activa = False
                    estado = "inicio"
                    estado_final = None
                    estancia_seleccionada = None
                    jugador = None
                    enemigo = None
                    mover_izquierda = False
                    mover_derecha = False
                    saltar = False
                    continue
                if botones_pausa[5].collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()
                if botones_pausa[1].collidepoint(evento.pos) or botones_pausa[2].collidepoint(evento.pos):
                    continue
        if estado == "personaje" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if rect_boton_menu_principal().collidepoint(evento.pos):
                estado = "inicio"
                continue
            tarjetas = rect_botones_personajes()
            if tarjetas[0].collidepoint(evento.pos):
                personaje_seleccionado = "soldier"
                estado = "seleccion"
                continue
            if tarjetas[1].collidepoint(evento.pos):
                personaje_seleccionado = "terrible_knight"
                estado = "seleccion"
                continue
            if tarjetas[2].collidepoint(evento.pos):
                personaje_seleccionado = "bridge_heroine"
                estado = "seleccion"
                continue
        if estado == "seleccion" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if rect_boton_menu_principal().collidepoint(evento.pos):
                estado = "inicio"
                estado_final = None
                estancia_seleccionada = None
                jugador = None
                enemigo = None
                continue
            for indice, boton in enumerate(rect_botones_estancias_fijos()):
                if boton.collidepoint(evento.pos):
                    estancia_seleccionada = ESTANCIAS[indice]
                    jugador, enemigo = crear_partida(estancia_seleccionada, personaje_seleccionado)
                    estado = "combate"
                    estado_final = None
                    continue
        if estado == "seleccion" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            posicion = posicion_logica(evento.pos)
            for indice, boton in enumerate(botones_estancias):
                if boton.collidepoint(posicion):
                    estancia_seleccionada = ESTANCIAS[indice]
                    jugador, enemigo = crear_partida(estancia_seleccionada, personaje_seleccionado)
                    estado = "combate"
                    estado_final = None
        elif estado == "final" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            botones_finales = rect_botones_finales()
            if botones_finales[0].collidepoint(evento.pos):
                jugador, enemigo = crear_partida(estancia_seleccionada, personaje_seleccionado)
                estado = "combate"
                estado_final = None
                continue
            if botones_finales[1].collidepoint(evento.pos):
                estado = "seleccion"
                estado_final = None
                continue
            if botones_finales[2].collidepoint(evento.pos):
                estado = "inicio"
                estado_final = None
                estancia_seleccionada = None
                jugador = None
                enemigo = None
                continue
            posicion = posicion_logica(evento.pos)
            if boton_repetir.collidepoint(posicion):
                jugador, enemigo = crear_partida(estancia_seleccionada, personaje_seleccionado)
                estado = "combate"
                estado_final = None
            elif boton_menu.collidepoint(posicion):
                estado = "seleccion"
                estado_final = None
        elif estado == "combate" and not pausa_activa and evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = True
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = True
            elif evento.key == pygame.K_SPACE:
                saltar = True
            elif evento.key == pygame.K_z:
                jugador.activar_ataque(1)
            elif evento.key == pygame.K_x:
                jugador.activar_ataque(2)
            elif evento.key == pygame.K_c:
                jugador.activar_ataque(3)
        elif estado == "combate" and not pausa_activa and evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_a, pygame.K_LEFT):
                mover_izquierda = False
            elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                mover_derecha = False
            elif evento.key == pygame.K_SPACE:
                saltar = False

    if estado == "combate" and not pausa_activa:
        jugador.movimiento(mover_izquierda, mover_derecha, saltar, suelo)
        jugador.x = max(0, min(jugador.x, constantes.ANCHO_VENTANA - jugador.rect.width))
        jugador.rect.topleft = (jugador.x, jugador.y)
        if not enemigo.teletransportandose and not isinstance(enemigo, Demon):
            patrulla = estancia_seleccionada.get("patrulla")
            if patrulla:
                limite_izquierdo = int(constantes.ANCHO_VENTANA * patrulla[0])
                limite_derecho = int(constantes.ANCHO_VENTANA * patrulla[1])
            else:
                limite_izquierdo = constantes.ANCHO_VENTANA // 2
                limite_derecho = constantes.ANCHO_VENTANA - 35
            enemigo.movimiento(
                limite_izquierdo,
                limite_derecho,
            )
        enemigo.actualizar_teletransporte(
            35,
            constantes.ANCHO_VENTANA - 35,
        )
        if isinstance(enemigo, Demon):
            enemigo.actualizar_ataque_demon()
            enemigo.atacar_con_demon(jugador)
        elif isinstance(enemigo, Orc):
            distancia_orc = abs(jugador.rect.centerx - enemigo.rect.centerx)
            if distancia_orc <= 170 and enemigo.ataque_orc_activo is None:
                enemigo.activar_ataque_orc(1 if pygame.time.get_ticks() % 2 else 2)
            enemigo.actualizar_ataque_orc()
            enemigo.atacar_con_orc(jugador)
        jugador.actualizar_ataque_soldier()
        jugador.atacar_con_ataque(1, enemigo)
        jugador.atacar_con_ataque(2, enemigo)
        jugador.atacar_con_ataque(3, enemigo)
        jugador.actualizar_proyectiles_arrow(
            enemigo,
            pygame.Rect(0, 0, constantes.ANCHO_VENTANA, suelo),
        )
        enemigo.atacar_con_fb(jugador)
        enemigo.actualizar_proyectiles(jugador, pygame.Rect(0, 0, constantes.ANCHO_VENTANA, suelo))
        if jugador.atributos["vida"] <= 0:
            estado_final = "derrota"
            estado = "final"
        elif enemigo.atributos["vida"] <= 0:
            estado_final = "victoria"
            estado = "final"

    ventana.fill((24, 27, 34))
    if estado == "inicio":
        ventana.blit(
            pygame.transform.smoothscale(
                fondo_inicio, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA)
            ),
            (0, 0),
        )
    elif estado == "personaje":
        ventana.blit(
            pygame.transform.smoothscale(
                fondo_inicio, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA)
            ),
            (0, 0),
        )
    elif estado == "seleccion":
        titulo = fuente_titulo.render("Selecciona una estancia", True, (255, 244, 210))
        ventana.blit(titulo, titulo.get_rect(center=(constantes.ANCHO_VENTANA // 2, 75)))
        subtitulo = fuente.render("Elige contra que enemigo quieres luchar", True, (190, 198, 210))
        ventana.blit(subtitulo, subtitulo.get_rect(center=(constantes.ANCHO_VENTANA // 2, 112)))
        for indice, (boton, estancia) in enumerate(zip(botones_estancias, ESTANCIAS)):
            dibujar_boton(boton, f"{indice + 1}. {estancia['nombre']}  |  {estancia['enemigo']}", (48, 94, 112))
    else:
        ventana.blit(fondo_combate, (0, 0))
        jugador.dibujar(ventana)
        enemigo.dibujar(ventana)
        enemigo.dibujar_proyectiles(ventana)
        jugador.dibujar_proyectiles_arrow(ventana)
    tamano_pantalla = pantalla.get_size()
    if tamano_pantalla[0] > 0 and tamano_pantalla[1] > 0:
        destino = rect_escena()
        escena_escalada = pygame.transform.scale(ventana, destino.size)
        if estado == "inicio":
            pantalla.fill(escena_escalada.get_at((0, 0)))
            if destino.top > 0:
                borde_superior = escena_escalada.subsurface((0, 0, destino.width, 1))
                pantalla.blit(pygame.transform.scale(borde_superior, (tamano_pantalla[0], destino.top)), (0, 0))
            if destino.bottom < tamano_pantalla[1]:
                borde_inferior = escena_escalada.subsurface((0, destino.height - 1, destino.width, 1))
                pantalla.blit(
                    pygame.transform.scale(
                        borde_inferior,
                        (tamano_pantalla[0], tamano_pantalla[1] - destino.bottom),
                    ),
                    (0, destino.bottom),
                )
            if destino.left > 0:
                borde_izquierdo = escena_escalada.subsurface((0, 0, 1, destino.height))
                pantalla.blit(pygame.transform.scale(borde_izquierdo, (destino.left, destino.height)), (0, destino.top))
            if destino.right < tamano_pantalla[0]:
                borde_derecho = escena_escalada.subsurface((destino.width - 1, 0, 1, destino.height))
                pantalla.blit(
                    pygame.transform.scale(
                        borde_derecho,
                        (tamano_pantalla[0] - destino.right, destino.height),
                    ),
                    (destino.right, destino.top),
                )
        else:
            pantalla.fill((0, 0, 0))
        pantalla.blit(escena_escalada, destino)
        dibujar_menu_inicio()
        dibujar_selector_personaje_fijo()
        dibujar_selector_estancias_fijo()
        dibujar_hud_fijo()
        dibujar_pantalla_final_fija()
        dibujar_menu_pausa()
        pygame.display.flip()
