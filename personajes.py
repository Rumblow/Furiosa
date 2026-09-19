import pygame
import constantes
import math
import random


class ProyectilFuego:
    def __init__(self, x, y, objetivo, frames, dano=4, velocidad=5, punto_objetivo=None):
        self.x = float(x)
        self.y = float(y)
        self.objetivo = objetivo
        self.frames = frames
        self.frame = 0
        self.dano = dano
        self.velocidad = velocidad
        self.ultimo_cambio_frame = pygame.time.get_ticks()
        self.duracion_frame = 80
        self.alpha = 255
        self.desvaneciendo = False

        destino_x, destino_y = punto_objetivo or (objetivo.rect.centerx, objetivo.rect.centery)
        direccion_x = destino_x - self.x
        direccion_y = destino_y - self.y
        distancia = math.hypot(direccion_x, direccion_y) or 1
        self.velocidad_x = direccion_x / distancia * velocidad
        self.velocidad_y = direccion_y / distancia * velocidad

    def actualizar(self, limites):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_frame >= self.duracion_frame:
            self.frame = (self.frame + 1) % len(self.frames)
            self.ultimo_cambio_frame = tiempo_actual

        if not self.desvaneciendo:
            self.x += self.velocidad_x
            self.y += self.velocidad_y
            imagen = self.imagen_orientada()
            rect = imagen.get_rect(center=(round(self.x), round(self.y)))
            if rect.left <= limites.left or rect.right >= limites.right or rect.top <= limites.top or rect.bottom >= limites.bottom:
                self.desvaneciendo = True
        else:
            self.alpha = max(0, self.alpha - 18)

        return self.alpha > 0

    def imagen_orientada(self):
        return self.frames[self.frame]

    def rect(self):
        return self.imagen_orientada().get_rect(center=(round(self.x), round(self.y)))

    def dibujar(self, ventana):
        imagen = self.imagen_orientada()
        imagen.set_alpha(self.alpha)
        ventana.blit(imagen, imagen.get_rect(center=(round(self.x), round(self.y))))


class ProyectilArrow:
    def __init__(self, x, y, frames, facing_left, dano, velocidad=9):
        self.x = float(x)
        self.y = float(y)
        self.frames = frames
        self.frame = 0
        self.dano = dano
        self.velocidad = -velocidad if facing_left else velocidad
        self.ultimo_cambio_frame = pygame.time.get_ticks()
        self.duracion_frame = 80

    def imagen(self):
        return self.frames[self.frame]

    def rect(self):
        return self.imagen().get_rect(center=(round(self.x), round(self.y)))

    def actualizar(self, limites):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_frame >= self.duracion_frame:
            self.frame = (self.frame + 1) % len(self.frames)
            self.ultimo_cambio_frame = tiempo_actual

        self.x += self.velocidad
        rect_proyectil = self.rect()
        return (
            rect_proyectil.right > limites.left
            and rect_proyectil.left < limites.right
            and rect_proyectil.bottom > limites.top
            and rect_proyectil.top < limites.bottom
        )

    def dibujar(self, ventana):
        ventana.blit(self.imagen(), self.rect())


class Personaje:
    def __init__(self, x, y, imagen, vida=100, ataque=10, defensa=5, velocidad=None, imagen_facing_left=None):
        self.x = x
        self.y = y
        self.imagen = imagen
        self.imagen_facing_left = imagen_facing_left or pygame.transform.flip(imagen, True, False)
        self.facing_left = False
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))
        self.vida_maxima = vida
        self.atributos = {
            "vida": vida,
            "ataque": ataque,
            "defensa": defensa,
            "velocidad": constantes.VELOCIDAD_JUGADOR if velocidad is None else velocidad,
        }
        self.swoosh_frames = []
        self.swoosh_activo = False
        self.swoosh_frame = 0
        self.swoosh_ultimo_cambio = 0
        self.swoosh_ya_golpeo = False
        self.duracion_frame_swoosh = 80
        self.claw_frames = []
        self.claw_frames_facing_left = []
        self.claw_activo = False
        self.claw_frame = 0
        self.claw_ultimo_cambio = 0
        self.claw_ultimo_uso = -2000
        self.cooldown_claw = 2000
        self.claw_ya_golpeo = False
        self.en_suelo = True
        self.velocidad_vertical = 0.0
        self.gravedad = 0.9
        self.altura_salto = self.rect.height * 2
        self.velocidad_salto = math.sqrt(2 * self.gravedad * self.altura_salto)

    @property
    def danio_swoosh(self):
        return self.atributos["ataque"]

    def configurar_swoosh(self, frames, frames_facing_left=None, duracion_frame=80):
        self.swoosh_frames = frames
        self.swoosh_frames_facing_left = frames_facing_left or [pygame.transform.flip(frame, True, False) for frame in frames]
        self.duracion_frame_swoosh = duracion_frame

    def activar_swoosh(self):
        if self.swoosh_frames and not self.swoosh_activo:
            self.swoosh_activo = True
            self.swoosh_frame = 0
            self.swoosh_ultimo_cambio = pygame.time.get_ticks()
            self.swoosh_ya_golpeo = False

    def actualizar_swoosh(self):
        if not self.swoosh_activo:
            return

        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.swoosh_ultimo_cambio >= self.duracion_frame_swoosh:
            self.swoosh_frame += 1
            self.swoosh_ultimo_cambio = tiempo_actual
            if self.swoosh_frame >= len(self.swoosh_frames):
                self.swoosh_activo = False

    def obtener_rect_swoosh(self):
        if not self.swoosh_activo:
            return None
        imagen_swoosh = self.obtener_imagen_swoosh()
        if self.facing_left:
            return imagen_swoosh.get_rect(midright=(self.rect.left, self.rect.centery))
        return imagen_swoosh.get_rect(midleft=(self.rect.right, self.rect.centery))

    def obtener_imagen_swoosh(self):
        frames = self.swoosh_frames_facing_left if self.facing_left else self.swoosh_frames
        return frames[self.swoosh_frame]

    def dibujar_swoosh(self, ventana):
        rect_swoosh = self.obtener_rect_swoosh()
        if rect_swoosh is not None:
            ventana.blit(self.obtener_imagen_swoosh(), rect_swoosh)

    def atacar_con_swoosh(self, objetivo):
        rect_swoosh = self.obtener_rect_swoosh()
        if (
            rect_swoosh is not None
            and not self.swoosh_ya_golpeo
            and rect_swoosh.colliderect(objetivo.rect)
        ):
            objetivo.recibir_dano(self.danio_swoosh)
            self.swoosh_ya_golpeo = True

    @property
    def danio_claw(self):
        return self.atributos["ataque"] * 3

    def configurar_claw(self, frames, frames_facing_left=None, duracion_frame=70):
        self.claw_frames = frames
        self.claw_frames_facing_left = frames_facing_left or [
            pygame.transform.flip(frame, True, False) for frame in frames
        ]
        self.duracion_frame_claw = duracion_frame

    def activar_claw(self):
        tiempo_actual = pygame.time.get_ticks()
        if (
            self.claw_frames
            and not self.claw_activo
            and tiempo_actual - self.claw_ultimo_uso >= self.cooldown_claw
        ):
            self.claw_activo = True
            self.claw_frame = 0
            self.claw_ultimo_cambio = tiempo_actual
            self.claw_ultimo_uso = tiempo_actual
            self.claw_ya_golpeo = False

    def actualizar_claw(self):
        if not self.claw_activo:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.claw_ultimo_cambio >= self.duracion_frame_claw:
            self.claw_frame += 1
            self.claw_ultimo_cambio = tiempo_actual
            if self.claw_frame >= len(self.claw_frames):
                self.claw_activo = False

    def obtener_imagen_claw(self):
        frames = self.claw_frames_facing_left if self.facing_left else self.claw_frames
        return frames[self.claw_frame]

    def obtener_rect_claw(self):
        if not self.claw_activo:
            return None
        imagen = self.obtener_imagen_claw()
        if self.facing_left:
            return imagen.get_rect(midright=(self.rect.left, self.rect.centery))
        return imagen.get_rect(midleft=(self.rect.right, self.rect.centery))

    def dibujar_claw(self, ventana):
        rect_claw = self.obtener_rect_claw()
        if rect_claw is not None:
            ventana.blit(self.obtener_imagen_claw(), rect_claw)

    def atacar_con_claw(self, objetivo):
        rect_claw = self.obtener_rect_claw()
        if rect_claw is not None and not self.claw_ya_golpeo and rect_claw.colliderect(objetivo.rect):
            objetivo.recibir_dano(self.danio_claw)
            self.claw_ya_golpeo = True

    def recibir_dano(self, cantidad):
        dano_efectivo = max(1, round(cantidad - self.atributos["defensa"]))
        self.atributos["vida"] = max(0, self.atributos["vida"] - dano_efectivo)

    def dibujar(self, ventana):
        imagen = self.imagen_facing_left if self.facing_left else self.imagen
        ventana.blit(imagen, (self.x, self.y))

    def movimiento(self, mover_izquierda, mover_derecha, saltar, limite_suelo):
        if mover_izquierda:
            self.x -= self.atributos["velocidad"]
            self.facing_left = True
        if mover_derecha:
            self.x += self.atributos["velocidad"]
            self.facing_left = False

        if saltar and self.en_suelo:
            self.velocidad_vertical = -self.velocidad_salto
            self.en_suelo = False

        self.velocidad_vertical += self.gravedad
        self.y += self.velocidad_vertical
        if self.y + self.rect.height >= limite_suelo:
            self.y = limite_suelo - self.rect.height
            self.velocidad_vertical = 0
            self.en_suelo = True

        self.rect.topleft = (self.x, self.y)


class Soldier(Personaje):
    def __init__(self, x, y, imagen, imagen_facing_left=None, vida=100, ataque=10, defensa=5, velocidad=None):
        super().__init__(
            x,
            y,
            imagen,
            vida=vida,
            ataque=ataque,
            defensa=defensa,
            velocidad=velocidad,
            imagen_facing_left=imagen_facing_left,
        )
        self.animaciones = {}
        self.animaciones_facing_left = {}
        self.estado_animacion = "idle"
        self.frame_animacion = 0
        self.ultimo_cambio_animacion = pygame.time.get_ticks()
        self.duracion_frame_animacion = 100
        self.desplazamiento_visual_y = 0
        self.ataques_soldier = {}
        self.ataque_activo = None
        self.frame_ataque = 0
        self.ultimo_cambio_ataque = 0
        self.duracion_frame_ataque = 80
        self.ataque_ya_golpeo = False
        self.arrow_frames = []
        self.arrow_frames_facing_left = []
        self.proyectiles_arrow = []
        self.ataque_3_disparado = False
        self.ataque_animacion_terminada = False
        self.ultimo_uso_ataque = {1: -2000, 2: -2000, 3: -2000}
        self.cooldown_ataques = {1: 500, 2: 900, 3: 2000}
        self.estado_temporal = None
        self.ultimo_cambio_estado = 0

    def configurar_animaciones(self, animaciones, duracion_frame=100):
        self.animaciones = animaciones
        self.animaciones_facing_left = {
            nombre: [pygame.transform.flip(frame, True, False) for frame in frames]
            for nombre, frames in animaciones.items()
        }
        imagen_referencia = animaciones.get("idle", [self.imagen])[0]
        self.desplazamiento_visual_y = (
            imagen_referencia.get_height() - imagen_referencia.get_bounding_rect().bottom
        )
        self.duracion_frame_animacion = duracion_frame

    def configurar_ataques(self, ataques, duracion_frame=80):
        self.ataques_soldier = ataques
        self.ataques_soldier_facing_left = {
            numero: [pygame.transform.flip(frame, True, False) for frame in frames]
            for numero, frames in ataques.items()
        }
        self.duracion_frame_ataque = duracion_frame

    def configurar_arrow(self, frames, frames_facing_left=None):
        self.arrow_frames = frames
        self.arrow_frames_facing_left = frames_facing_left or [
            pygame.transform.flip(frame, True, False) for frame in frames
        ]

    def activar_ataque(self, numero):
        tiempo_actual = pygame.time.get_ticks()
        if (
            numero not in self.ataques_soldier
            or self.ataque_activo is not None
            or self.atributos["vida"] <= 0
            or tiempo_actual - self.ultimo_uso_ataque[numero] < self.cooldown_ataques[numero]
        ):
            return
        self.ataque_activo = numero
        self.frame_ataque = 0
        self.ultimo_cambio_ataque = tiempo_actual
        self.ultimo_uso_ataque[numero] = tiempo_actual
        self.ataque_ya_golpeo = False
        self.ataque_3_disparado = False
        self.ataque_animacion_terminada = False

    def actualizar_animacion(self):
        tiempo_actual = pygame.time.get_ticks()
        if (
            self.estado_temporal == "hurt"
            and tiempo_actual - self.ultimo_cambio_estado >= 350
        ):
            self.estado_temporal = None
            self.frame_animacion = 0

        estado = self.estado_temporal or self.estado_animacion
        frames = self.animaciones.get(estado, self.animaciones.get("idle", []))
        if not frames:
            return
        if tiempo_actual - self.ultimo_cambio_animacion >= self.duracion_frame_animacion:
            siguiente_frame = self.frame_animacion + 1
            self.frame_animacion = (
                min(siguiente_frame, len(frames) - 1)
                if estado == "death"
                else siguiente_frame % len(frames)
            )
            self.ultimo_cambio_animacion = tiempo_actual

    def actualizar_ataque_soldier(self):
        if self.ataque_activo is None:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_ataque < self.duracion_frame_ataque:
            return
        siguiente_frame = self.frame_ataque + 1
        if siguiente_frame >= len(self.ataques_soldier[self.ataque_activo]):
            self.frame_ataque = len(self.ataques_soldier[self.ataque_activo]) - 1
            self.ataque_animacion_terminada = True
            if self.ataque_activo != 3 or self.ataque_3_disparado:
                self.ataque_activo = None
        else:
            self.frame_ataque = siguiente_frame
        self.ultimo_cambio_ataque = tiempo_actual

    def atacar_con_ataque(self, numero, objetivo):
        if self.ataque_activo != numero:
            return
        if numero != 3 and abs(self.rect.centerx - objetivo.rect.centerx) > 150:
            return
        if numero == 3:
            if (
                self.ataque_3_disparado
                or not self.ataque_animacion_terminada
                or not self.arrow_frames
            ):
                return
            frames = self.arrow_frames_facing_left if self.facing_left else self.arrow_frames
            origen_x = self.rect.left if self.facing_left else self.rect.right
            origen_y = self.rect_visible().centery
            self.proyectiles_arrow.append(
                ProyectilArrow(
                    origen_x,
                    origen_y,
                    frames,
                    self.facing_left,
                    dano=round(self.atributos["ataque"] * 3 * 0.7),
                    velocidad=9,
                )
            )
            self.ataque_3_disparado = True
            return
        if self.ataque_ya_golpeo:
            return
        imagen = self.obtener_imagen_ataque()
        if self.facing_left:
            rect_ataque = imagen.get_rect(midright=(self.rect.left, self.rect.centery))
        else:
            rect_ataque = imagen.get_rect(midleft=(self.rect.right, self.rect.centery))
        if rect_ataque.colliderect(objetivo.rect):
            objetivo.recibir_dano(self.atributos["ataque"] * numero)
            self.ataque_ya_golpeo = True

    def actualizar_proyectiles_arrow(self, objetivo, limites):
        proyectiles_activos = []
        for proyectil in self.proyectiles_arrow:
            sigue_activo = proyectil.actualizar(limites)
            if proyectil.rect().colliderect(objetivo.rect):
                objetivo.recibir_dano(proyectil.dano)
                continue
            if sigue_activo:
                proyectiles_activos.append(proyectil)
        self.proyectiles_arrow = proyectiles_activos

    def dibujar_proyectiles_arrow(self, ventana):
        for proyectil in self.proyectiles_arrow:
            proyectil.dibujar(ventana)

    def obtener_imagen_ataque(self):
        frames = (
            self.ataques_soldier_facing_left[self.ataque_activo]
            if self.facing_left
            else self.ataques_soldier[self.ataque_activo]
        )
        return frames[min(self.frame_ataque, len(frames) - 1)]

    def recibir_dano(self, cantidad):
        super().recibir_dano(cantidad)
        self.estado_temporal = "death" if self.atributos["vida"] <= 0 else "hurt"
        self.frame_animacion = 0
        self.ultimo_cambio_estado = pygame.time.get_ticks()

    def movimiento(self, mover_izquierda, mover_derecha, saltar, limite_suelo):
        super().movimiento(mover_izquierda, mover_derecha, saltar, limite_suelo)
        if self.atributos["vida"] > 0 and self.ataque_activo is None:
            self.estado_animacion = "walk" if mover_izquierda or mover_derecha else "idle"

    def dibujar(self, ventana):
        if self.ataque_activo is not None:
            imagen = self.obtener_imagen_ataque()
            rect_ataque = imagen.get_rect(
                midbottom=(self.rect.centerx, self.rect.bottom + self.desplazamiento_visual_y)
            )
            ventana.blit(imagen, rect_ataque)
            return
        self.actualizar_animacion()
        frames = self.animaciones_facing_left if self.facing_left else self.animaciones
        animacion = frames.get(self.estado_temporal or self.estado_animacion, frames.get("idle", []))
        if animacion:
            imagen = animacion[self.frame_animacion % len(animacion)]
            rect_imagen = imagen.get_rect(
                midbottom=(self.rect.centerx, self.rect.bottom + self.desplazamiento_visual_y)
            )
            ventana.blit(imagen, rect_imagen)

    def rect_visible(self):
        _, rect_imagen, area_visible = self._imagen_y_rect_visible()
        return pygame.Rect(
            rect_imagen.left + area_visible.left,
            rect_imagen.top + area_visible.top,
            area_visible.width,
            area_visible.height,
        )

    def _imagen_y_rect_visible(self):
        if self.ataque_activo is not None:
            imagen = self.obtener_imagen_ataque()
        else:
            frames = self.animaciones_facing_left if self.facing_left else self.animaciones
            animacion = frames.get(self.estado_temporal or self.estado_animacion, frames.get("idle", []))
            imagen = animacion[self.frame_animacion % len(animacion)] if animacion else self.imagen

        rect_imagen = imagen.get_rect(
            midbottom=(self.rect.centerx, self.rect.bottom + self.desplazamiento_visual_y)
        )
        return imagen, rect_imagen, imagen.get_bounding_rect()

    def colisiona_con_proyectil(self, proyectil):
        imagen, rect_imagen, _ = self._imagen_y_rect_visible()
        rect_proyectil = proyectil.rect()
        mascara_jugador = pygame.mask.from_surface(imagen)
        mascara_proyectil = pygame.mask.from_surface(proyectil.imagen_orientada())
        desplazamiento = (
            rect_proyectil.left - rect_imagen.left,
            rect_proyectil.top - rect_imagen.top,
        )
        return mascara_jugador.overlap(mascara_proyectil, desplazamiento) is not None

class Enemigo(Personaje):
    def __init__(self, x, y, imagen, imagen_facing_left=None, vida=1325, ataque=10, defensa=5, velocidad=2.1, puede_teletransportarse=False):
        super().__init__(
            x,
            y,
            imagen,
            vida=vida,
            ataque=ataque,
            defensa=defensa,
            imagen_facing_left=imagen_facing_left,
        )
        self.velocidad = velocidad
        self.atributos["velocidad"] = velocidad
        self.direccion_movimiento = -1
        self.proyectiles_fuego = []
        self.frames_fb = []
        self.ultimo_disparo_fb = -1000
        self.ultimo_ataque_fb = -5000
        self.cooldown_disparo_fb = 1000
        self.cooldown_fb = 5000
        self.distancia_minima_ataque = 500
        self.puede_teletransportarse = puede_teletransportarse
        self.frames_teletransporte = []
        self.frames_teletransporte_facing_left = []
        self.teletransportandose = False
        self.teletransporte_frame = 0
        self.ultimo_teletransporte = pygame.time.get_ticks()
        self.cooldown_teletransporte = 4500
        self.ultimo_cambio_teletransporte = 0
        self.duracion_frame_teletransporte = 120
        self.inicio_teletransporte = None
        self.destino_teletransporte = None

    def configurar_ataque_fb(self, frames, frames_facing_left=None):
        self.frames_fb = frames
        self.frames_fb_facing_left = frames_facing_left or [pygame.transform.flip(frame, True, False) for frame in frames]

    def configurar_teletransporte(self, frames, frames_facing_left=None):
        self.frames_teletransporte = frames
        self.frames_teletransporte_facing_left = frames_facing_left or [
            pygame.transform.flip(frame, True, False) for frame in frames
        ]

    def iniciar_teletransporte(self, limite_izquierdo, limite_derecho):
        if (
            not self.puede_teletransportarse
            or self.teletransportandose
            or not self.frames_teletransporte
        ):
            return

        destino_x = random.randint(
            limite_izquierdo,
            max(limite_izquierdo, limite_derecho - self.rect.width),
        )
        self.inicio_teletransporte = self.x
        self.destino_teletransporte = destino_x
        self.facing_left = destino_x < self.x
        self.teletransportandose = True
        self.teletransporte_frame = 0
        self.ultimo_cambio_teletransporte = pygame.time.get_ticks()

    def actualizar_teletransporte(self, limite_izquierdo, limite_derecho):
        if not self.puede_teletransportarse:
            return

        tiempo_actual = pygame.time.get_ticks()
        if not self.teletransportandose:
            if tiempo_actual - self.ultimo_teletransporte >= self.cooldown_teletransporte:
                self.iniciar_teletransporte(limite_izquierdo, limite_derecho)
            return

        if tiempo_actual - self.ultimo_cambio_teletransporte >= self.duracion_frame_teletransporte:
            self.teletransporte_frame += 1
            self.ultimo_cambio_teletransporte = tiempo_actual
            progreso = self.teletransporte_frame / (len(self.frames_teletransporte) - 1)
            self.x = self.inicio_teletransporte + (
                self.destino_teletransporte - self.inicio_teletransporte
            ) * progreso
            self.rect.topleft = (round(self.x), self.y)
            if self.teletransporte_frame >= len(self.frames_teletransporte) - 1:
                self.x = self.destino_teletransporte
                self.rect.topleft = (self.x, self.y)
                self.teletransportandose = False
                self.ultimo_teletransporte = tiempo_actual

    def dibujar(self, ventana):
        if self.teletransportandose:
            frames = (
                self.frames_teletransporte_facing_left
                if self.facing_left
                else self.frames_teletransporte
            )
            ventana.blit(frames[self.teletransporte_frame], (self.x, self.y))
            return
        super().dibujar(ventana)

    def atacar_con_fb(self, objetivo):
        if not self.frames_fb or self.atributos["vida"] <= 0:
            return

        distancia = math.hypot(
            objetivo.rect.centerx - self.rect.centerx,
            objetivo.rect.centery - self.rect.centery,
        )
        tiempo_actual = pygame.time.get_ticks()
        dentro_del_rango = distancia <= self.distancia_minima_ataque
        if not dentro_del_rango:
            return

        if tiempo_actual - self.ultimo_disparo_fb >= self.cooldown_disparo_fb:
            punto_objetivo = (objetivo.rect.centerx, objetivo.rect.centery)
            frames = self.frames_fb_facing_left if punto_objetivo[0] < self.rect.centerx else self.frames_fb
            self.proyectiles_fuego.append(
                ProyectilFuego(
                    self.rect.centerx,
                    self.rect.centery,
                    objetivo,
                    frames,
                    dano=self.atributos["ataque"],
                    punto_objetivo=punto_objetivo,
                )
            )
            self.ultimo_disparo_fb = tiempo_actual

        if tiempo_actual - self.ultimo_ataque_fb >= self.cooldown_fb:
            puntos_objetivo = (
                (objetivo.rect.centerx - 140, objetivo.rect.centery + 70),
                (objetivo.rect.centerx, objetivo.rect.centery - 150),
                (objetivo.rect.centerx + 140, objetivo.rect.centery + 70),
            )
            for punto_x, punto_y in puntos_objetivo:
                frames = self.frames_fb_facing_left if punto_x < self.rect.centerx else self.frames_fb
                self.proyectiles_fuego.append(
                    ProyectilFuego(
                        self.rect.centerx,
                        self.rect.centery,
                        objetivo,
                        frames,
                        dano=self.atributos["ataque"],
                        punto_objetivo=(punto_x, punto_y),
                    )
                )
            self.ultimo_ataque_fb = tiempo_actual

    def actualizar_proyectiles(self, objetivo, limites):
        proyectiles_activos = []
        rect_objetivo = objetivo.rect_visible() if hasattr(objetivo, "rect_visible") else objetivo.rect
        for proyectil in self.proyectiles_fuego:
            sigue_activo = proyectil.actualizar(limites)
            colisiona = (
                objetivo.colisiona_con_proyectil(proyectil)
                if hasattr(objetivo, "colisiona_con_proyectil")
                else proyectil.rect().colliderect(rect_objetivo)
            )
            if colisiona:
                objetivo.recibir_dano(proyectil.dano)
                continue
            if sigue_activo:
                proyectiles_activos.append(proyectil)
        self.proyectiles_fuego = proyectiles_activos

    def dibujar_proyectiles(self, ventana):
        for proyectil in self.proyectiles_fuego:
            proyectil.dibujar(ventana)

    def movimiento(self, limite_izquierdo, limite_derecho):
        self.x += self.velocidad * self.direccion_movimiento
        if self.x <= limite_izquierdo:
            self.x = limite_izquierdo
            self.direccion_movimiento = 1
        elif self.x + self.rect.width >= limite_derecho:
            self.x = limite_derecho - self.rect.width
            self.direccion_movimiento = -1
        self.facing_left = self.direccion_movimiento < 0
        self.rect.topleft = (self.x, self.y)


class Orc(Enemigo):
    def __init__(
        self,
        x,
        y,
        imagen,
        animaciones,
        ataques,
        imagen_facing_left=None,
        vida=220,
        ataque=16,
        defensa=8,
        velocidad=1.6,
    ):
        super().__init__(
            x,
            y,
            imagen,
            imagen_facing_left=imagen_facing_left,
            vida=vida,
            ataque=ataque,
            defensa=defensa,
            velocidad=velocidad,
        )
        self.animaciones_orc = animaciones
        self.animaciones_orc_facing_left = {
            nombre: [pygame.transform.flip(frame, True, False) for frame in frames]
            for nombre, frames in animaciones.items()
        }
        self.ataques_orc = ataques
        self.ataques_orc_facing_left = {
            numero: [pygame.transform.flip(frame, True, False) for frame in frames]
            for numero, frames in ataques.items()
        }
        self.estado_orc = "idle"
        self.estado_temporal_orc = None
        self.frame_orc = 0
        self.ultimo_cambio_orc = pygame.time.get_ticks()
        self.ultimo_cambio_estado_orc = 0
        self.ataque_orc_activo = None
        self.frame_ataque_orc = 0
        self.ultimo_cambio_ataque_orc = 0
        self.ultimo_uso_ataque_orc = {1: -2000, 2: -2000}
        self.cooldown_ataque_orc = {1: 900, 2: 1400}
        self.ataque_orc_ya_golpeo = False
        referencia = animaciones.get("idle", [imagen])[0]
        self.desplazamiento_visual_orc_y = (
            referencia.get_height() - referencia.get_bounding_rect().bottom
        )

    def recibir_dano(self, cantidad):
        super().recibir_dano(cantidad)
        self.estado_temporal_orc = "death" if self.atributos["vida"] <= 0 else "hurt"
        self.frame_orc = 0
        self.ultimo_cambio_estado_orc = pygame.time.get_ticks()

    def activar_ataque_orc(self, numero):
        tiempo_actual = pygame.time.get_ticks()
        if (
            numero not in self.ataques_orc
            or self.ataque_orc_activo is not None
            or self.atributos["vida"] <= 0
            or tiempo_actual - self.ultimo_uso_ataque_orc[numero] < self.cooldown_ataque_orc[numero]
        ):
            return
        self.ataque_orc_activo = numero
        self.frame_ataque_orc = 0
        self.ultimo_cambio_ataque_orc = tiempo_actual
        self.ultimo_uso_ataque_orc[numero] = tiempo_actual
        self.ataque_orc_ya_golpeo = False

    def actualizar_ataque_orc(self):
        if self.ataque_orc_activo is None:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_cambio_ataque_orc < 85:
            return
        self.frame_ataque_orc += 1
        self.ultimo_cambio_ataque_orc = tiempo_actual
        if self.frame_ataque_orc >= len(self.ataques_orc[self.ataque_orc_activo]):
            self.ataque_orc_activo = None

    def atacar_con_orc(self, objetivo):
        if self.ataque_orc_activo is None or self.ataque_orc_ya_golpeo:
            return
        if abs(self.rect.centerx - objetivo.rect.centerx) > 170:
            return
        imagen = self.obtener_imagen_ataque_orc()
        if self.facing_left:
            rect_ataque = imagen.get_rect(midright=(self.rect.left, self.rect.centery))
        else:
            rect_ataque = imagen.get_rect(midleft=(self.rect.right, self.rect.centery))
        if rect_ataque.colliderect(objetivo.rect):
            objetivo.recibir_dano(self.atributos["ataque"])
            self.ataque_orc_ya_golpeo = True

    def obtener_imagen_ataque_orc(self):
        frames = (
            self.ataques_orc_facing_left[self.ataque_orc_activo]
            if self.facing_left
            else self.ataques_orc[self.ataque_orc_activo]
        )
        return frames[min(self.frame_ataque_orc, len(frames) - 1)]

    def actualizar_animacion_orc(self):
        tiempo_actual = pygame.time.get_ticks()
        if (
            self.estado_temporal_orc == "hurt"
            and tiempo_actual - self.ultimo_cambio_estado_orc >= 350
        ):
            self.estado_temporal_orc = None
            self.frame_orc = 0
        estado = self.estado_temporal_orc or self.estado_orc
        frames = self.animaciones_orc.get(estado, self.animaciones_orc["idle"])
        if tiempo_actual - self.ultimo_cambio_orc >= 100:
            siguiente = self.frame_orc + 1
            self.frame_orc = min(siguiente, len(frames) - 1) if estado == "death" else siguiente % len(frames)
            self.ultimo_cambio_orc = tiempo_actual

    def movimiento(self, limite_izquierdo, limite_derecho):
        super().movimiento(limite_izquierdo, limite_derecho)
        if self.atributos["vida"] > 0 and self.ataque_orc_activo is None:
            self.estado_orc = "walk"

    def atacar_con_fb(self, objetivo):
        return

    def dibujar(self, ventana):
        if self.ataque_orc_activo is not None:
            imagen = self.obtener_imagen_ataque_orc()
        else:
            self.actualizar_animacion_orc()
            frames = self.animaciones_orc_facing_left if self.facing_left else self.animaciones_orc
            estado = self.estado_temporal_orc or self.estado_orc
            animacion = frames.get(estado, frames["idle"])
            imagen = animacion[self.frame_orc % len(animacion)]
        rect_imagen = imagen.get_rect(
            midbottom=(self.rect.centerx, self.rect.bottom + self.desplazamiento_visual_orc_y)
        )
        ventana.blit(imagen, rect_imagen)
    