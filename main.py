import os
import sys
import pygame

import constantes
from personajes import Enemigo, Orc, Soldier


def ruta_recurso(*partes):
    carpeta_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpeta_base, *partes)


pygame.init()
ZOOM_GENERAL = 0.85
ZOOM_INTERFAZ = 1.0
ZOOM_MINIMO = 0.7
ZOOM_MAXIMO = 1.5
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
fuente_titulo = pygame.font.Font(None, 46)
fuente = pygame.font.Font(None, 24)
fuente_pequena = pygame.font.Font(None, 20)


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
    escala = min(
        ancho_pantalla / constantes.ANCHO_VENTANA,
        alto_pantalla / constantes.ALTO_VENTANA,
    ) * ZOOM_INTERFAZ
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


def cambiar_zoom(cantidad):
    global ZOOM_INTERFAZ
    ZOOM_INTERFAZ = max(ZOOM_MINIMO, min(ZOOM_MAXIMO, ZOOM_INTERFAZ + cantidad))


def rect_controles_zoom():
    ancho, alto = pantalla.get_size()
    return (
        pygame.Rect(ancho - 96, alto - 42, 34, 30),
        pygame.Rect(ancho - 56, alto - 42, 34, 30),
    )


def dibujar_controles_zoom():
    boton_menos, boton_mas = rect_controles_zoom()
    for rectangulo, texto in ((boton_menos, "-"), (boton_mas, "+")):
        pygame.draw.rect(pantalla, (65, 75, 90), rectangulo)
        pygame.draw.rect(pantalla, (235, 235, 235), rectangulo, 2)
        superficie = fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(superficie, superficie.get_rect(center=rectangulo.center))
    texto_zoom = fuente_pequena.render(
        f"Zoom {round(ZOOM_INTERFAZ * 100)}%", True, (255, 255, 255)
    )
    pantalla.blit(texto_zoom, (boton_menos.left - texto_zoom.get_width() - 10, boton_menos.top + 7))


def dibujar_hud_fijo():
    if estado not in ("combate", "final") or jugador is None or enemigo is None:
        return

    ancho_pantalla, _ = pantalla.get_size()
    ancho_bossbar = min(520, max(220, ancho_pantalla - 40))
    x_bossbar = (ancho_pantalla - ancho_bossbar) // 2
    pygame.draw.rect(pantalla, (35, 35, 35), (x_bossbar, 15, ancho_bossbar, 30))
    porcentaje_vida = max(0, enemigo.atributos["vida"] / enemigo.vida_maxima)
    pygame.draw.rect(
        pantalla,
        (190, 35, 45),
        (x_bossbar + 2, 17, int((ancho_bossbar - 4) * porcentaje_vida), 26),
    )
    texto_bossbar = fuente_pequena.render(
        f"{estancia_seleccionada['enemigo']}  {enemigo.atributos['vida']} / {enemigo.vida_maxima}",
        True,
        (255, 254, 254),
    )
    pantalla.blit(
        texto_bossbar,
        texto_bossbar.get_rect(center=(ancho_pantalla // 2, 30)),
    )

    panel = pygame.Surface((238, 270), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 190))
    pantalla.blit(panel, (18, 68))
    for indice, (nombre, valor) in enumerate(jugador.atributos.items()):
        x_barra = 32
        y_atributo = 84 + indice * 58
        porcentaje = min(1, max(0, valor / maximos_atributos[nombre]))
        pantalla.blit(
            fuente_pequena.render(f"{nombre.capitalize()}: {valor}", True, (255, 255, 255)),
            (x_barra, y_atributo),
        )
        pygame.draw.rect(pantalla, (45, 45, 45), (x_barra, y_atributo + 25, 205, 16))
        pygame.draw.rect(
            pantalla,
            (55, 190, 95) if nombre == "vida" else (70, 145, 210),
            (x_barra + 2, y_atributo + 27, int(201 * porcentaje), 12),
        )


def rect_botones_finales():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(315, max(140, (ancho - 55) // 2))
    y_boton = min(alto - 80, alto // 2 + 105)
    x_centro = ancho // 2
    return (
        pygame.Rect(x_centro - ancho_boton - 8, y_boton, ancho_boton, 55),
        pygame.Rect(x_centro + 8, y_boton, ancho_boton, 55),
    )


def dibujar_pantalla_final_fija():
    if estado != "final":
        return
    ancho, alto = pantalla.get_size()
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    capa.fill((0, 0, 0, 190))
    pantalla.blit(capa, (0, 0))
    mensaje = "Victoria!" if estado_final == "victoria" else "Derrota!"
    titulo_final = fuente_titulo.render(mensaje, True, (255, 255, 255))
    pantalla.blit(titulo_final, titulo_final.get_rect(center=(ancho // 2, alto // 2 - 55)))
    boton_repetir_fijo, boton_menu_fijo = rect_botones_finales()
    for rectangulo, texto, color in (
        (boton_repetir_fijo, "Luchar de nuevo", (45, 125, 70)),
        (boton_menu_fijo, "Elegir otra estancia", (70, 90, 125)),
    ):
        pygame.draw.rect(pantalla, color, rectangulo)
        pygame.draw.rect(pantalla, (235, 235, 235), rectangulo, 2)
        superficie = fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(superficie, superficie.get_rect(center=rectangulo.center))


def rect_botones_pausa():
    ancho, alto = pantalla.get_size()
    ancho_boton = min(420, max(240, ancho - 80))
    alto_boton = 48
    separacion = 10
    x_boton = (ancho - ancho_boton) // 2
    y_inicial = max(90, alto // 2 - 150)
    return [
        pygame.Rect(x_boton, y_inicial + indice * (alto_boton + separacion), ancho_boton, alto_boton)
        for indice in range(5)
    ]


def dibujar_menu_pausa():
    if not pausa_activa:
        return
    ancho, alto = pantalla.get_size()
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    capa.fill((8, 12, 18, 210))
    pantalla.blit(capa, (0, 0))
    titulo = fuente_titulo.render("Juego en pausa", True, (255, 244, 210))
    pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, max(45, alto // 2 - 205))))
    textos = (
        "Regresar a la batalla",
        "Guardar partida",
        "Configuracion",
        "Cambiar de instancia",
        "Salir del juego",
    )
    botones = rect_botones_pausa()
    for indice, (rectangulo, texto) in enumerate(zip(botones, textos)):
        habilitado = indice in (0, 3, 4)
        color = (48, 94, 112) if habilitado else (55, 55, 55)
        pygame.draw.rect(pantalla, color, rectangulo)
        pygame.draw.rect(pantalla, (235, 235, 235), rectangulo, 2)
        superficie = fuente.render(texto, True, (255, 255, 255) if habilitado else (160, 160, 160))
        pantalla.blit(superficie, superficie.get_rect(center=rectangulo.center))


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


def dibujar_selector_estancias_fijo():
    if estado != "seleccion":
        return
    ancho, alto = pantalla.get_size()
    pantalla.fill((24, 27, 34))
    titulo = fuente_titulo.render("Selecciona una estancia", True, (255, 244, 210))
    pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 55)))
    subtitulo = fuente.render(
        "Elige contra que enemigo quieres luchar", True, (190, 198, 210)
    )
    pantalla.blit(subtitulo, subtitulo.get_rect(center=(ancho // 2, 90)))
    for indice, (boton, estancia) in enumerate(
        zip(rect_botones_estancias_fijos(), ESTANCIAS)
    ):
        pygame.draw.rect(pantalla, (48, 94, 112), boton)
        pygame.draw.rect(pantalla, (235, 235, 235), boton, 2)
        texto = fuente.render(
            f"{indice + 1}. {estancia['nombre']}  |  {estancia['enemigo']}",
            True,
            (255, 255, 255),
        )
        pantalla.blit(texto, texto.get_rect(center=boton.center))


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

ESTANCIAS = [
    {"nombre": "Sala de Cobalto", "enemigo": "Brujo de Cobalto", "imagen": "rpgcritters2_wizzard.png", "carpeta": "", "vida": 260, "ataque": 14, "defensa": 8, "velocidad_enemigo": 1.0, "patrulla": (0.68, 0.90)},
    {"nombre": "Galeria de los Huesos", "enemigo": "Guardian de Huesos", "imagen": "boss_1.png", "carpeta": "boss", "vida": 900},
    {"nombre": "Cripta del Engendro", "enemigo": "Engendro de Huesos", "imagen": "boos_2.png", "carpeta": "boss", "vida": 1150},
    {"nombre": "Nucleo de Ceniza", "enemigo": "Bestia de Ceniza", "imagen": "boss_3.png", "carpeta": "boss", "vida": 1700, "teletransporte": True},
    {"nombre": "Guarida del Orc", "enemigo": "Orc", "orc": True, "vida": 220, "ataque": 16, "defensa": 8, "velocidad_enemigo": 1.6, "patrulla": (0.55, 0.88)},
]

maximos_atributos = {"vida": 140, "ataque": 100, "defensa": 100, "velocidad": 10}
suelo = constantes.ALTO_VENTANA - 55


def crear_partida(estancia):
    jugador = Soldier(
        70,
        suelo - soldier_image.get_height(),
        soldier_image,
        vida=140,
        ataque=18,
        defensa=8,
    )
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
    jugador.configurar_animaciones(soldier_animations)
    jugador.configurar_ataques(soldier_attacks)
    jugador.configurar_arrow([arrow_image])
    if not estancia.get("orc"):
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
boton_zoom_menos = pygame.Rect(constantes.ANCHO_VENTANA - 118, constantes.ALTO_VENTANA - 48, 36, 30)
boton_zoom_mas = pygame.Rect(constantes.ANCHO_VENTANA - 76, constantes.ALTO_VENTANA - 48, 36, 30)
estado = "seleccion"
pausa_activa = False
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
            boton_menos, boton_mas = rect_controles_zoom()
            if boton_menos.collidepoint(evento.pos):
                cambiar_zoom(-0.1)
                continue
            if boton_mas.collidepoint(evento.pos):
                cambiar_zoom(0.1)
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
                    pygame.quit()
                    sys.exit()
                if botones_pausa[1].collidepoint(evento.pos) or botones_pausa[2].collidepoint(evento.pos):
                    continue
        if estado == "seleccion" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for indice, boton in enumerate(rect_botones_estancias_fijos()):
                if boton.collidepoint(evento.pos):
                    estancia_seleccionada = ESTANCIAS[indice]
                    jugador, enemigo = crear_partida(estancia_seleccionada)
                    estado = "combate"
                    estado_final = None
                    continue
        if estado == "seleccion" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            posicion = posicion_logica(evento.pos)
            for indice, boton in enumerate(botones_estancias):
                if boton.collidepoint(posicion):
                    estancia_seleccionada = ESTANCIAS[indice]
                    jugador, enemigo = crear_partida(estancia_seleccionada)
                    estado = "combate"
                    estado_final = None
        elif estado == "final" and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            boton_repetir_fijo, boton_menu_fijo = rect_botones_finales()
            if boton_repetir_fijo.collidepoint(evento.pos):
                jugador, enemigo = crear_partida(estancia_seleccionada)
                estado = "combate"
                estado_final = None
                continue
            if boton_menu_fijo.collidepoint(evento.pos):
                estado = "seleccion"
                estado_final = None
                continue
            posicion = posicion_logica(evento.pos)
            if boton_repetir.collidepoint(posicion):
                jugador, enemigo = crear_partida(estancia_seleccionada)
                estado = "combate"
                estado_final = None
            elif boton_menu.collidepoint(posicion):
                estado = "seleccion"
                estado_final = None
        elif estado == "combate" and not pausa_activa and evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                cambiar_zoom(-0.1)
                continue
            if evento.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                cambiar_zoom(0.1)
                continue
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
        if not enemigo.teletransportandose:
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
        if isinstance(enemigo, Orc):
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
        enemigo.dibujar(ventana)
        enemigo.dibujar_proyectiles(ventana)
        jugador.dibujar_proyectiles_arrow(ventana)
    tamano_pantalla = pantalla.get_size()
    if tamano_pantalla[0] > 0 and tamano_pantalla[1] > 0:
        destino = rect_escena()
        pantalla.fill((0, 0, 0))
        pantalla.blit(
            pygame.transform.scale(ventana, destino.size),
            destino,
        )
        dibujar_selector_estancias_fijo()
        dibujar_hud_fijo()
        dibujar_pantalla_final_fija()
        dibujar_menu_pausa()
        dibujar_controles_zoom()
        pygame.display.flip()
