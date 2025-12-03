# juego/main_game.py
import pygame
import os
import json
import time
from juego.coin_manager import CoinManager
from juego.enemy_manager import EnemyManager
from assets.MusicManager import MusicManager
from juego.rook_manager import RookManager
from juego.victoria import mostrar_victoria
from juego.derrota import mostrar_derrota
from gui.salon_fama import HallOfFameWindow

pygame.init()

# -------------------------------
# 🔹 CONFIGURACIÓN DEL TABLERO (VERTICAL)
# -------------------------------
COLUMNS = 5   # columnas
ROWS = 9      # filas
CELL_SIZE = 50
MARGIN = 2

GRID_WIDTH = COLUMNS * (CELL_SIZE + MARGIN) + MARGIN
GRID_HEIGHT = ROWS * (CELL_SIZE + MARGIN) + MARGIN

ANCHO = GRID_WIDTH + 400
ALTO = GRID_HEIGHT + 150

NEGRO = (0, 0, 0)
GRIS = (30, 30, 30)
BLANCO = (255, 255, 255)
CELDA = (70, 130, 180)
BTN_COLOR = (50, 50, 50)
BTN_HOVER = (70, 70, 70)
TXT_COLOR = (220, 220, 220)
VERDE = (60, 160, 60)
ROJO = (180, 50, 50)

clock = pygame.time.Clock()
FPS = 60  # más fluidez


class GameWindow:
    def __init__(self, usuario, rol, nivel=None):

        # ======================
        # 1️⃣ Datos iniciales
        # ======================
        self.usuario = usuario
        self.rol = rol

        # Cargar estado si existe
        self.save_data = self.cargar_estado()

        # Determinar nivel: si viene en argumento o si hay partida guardada
        if nivel is not None:
            self.nivel = nivel
        elif self.save_data:
            self.nivel = self.save_data["nivel"]
        else:
            self.nivel = 1

        # ======================
        # 2️⃣ Configuración
        # ======================
        self.rows = ROWS
        self.cols = COLUMNS
        self.cell_size = CELL_SIZE
        self.margin = MARGIN

        self.left_offset = (ANCHO - GRID_WIDTH) // 2
        self.top_offset = 100  
        self.screen_width = ANCHO

        # Dificultad
        base_enemigos = 10
        base_spawn_delay = 10.0
        self.max_enemigos = int(base_enemigos * (1 + 0.30 * (self.nivel - 1)))
        self.spawn_delay = base_spawn_delay / (1 + 0.30 * (self.nivel - 1))

        # Tiempo total
        if self.save_data:
            # si no hay tiempo guardado (guardado minimal), empezar desde cero
            self.start_time = time.time() - self.save_data.get("tiempo_total", 0)
        else:
            self.start_time = time.time()

        # ======================
        # 3️⃣ Música
        # ======================
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.music = MusicManager()
        if not self.music.playing:
            self.music.play(soundtrack_index=1, volume=0.5)

        # ======================
        # 4️⃣ Ventana
        # ======================
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        # ======================
        # 5️⃣ Managers
        # ======================
        self.coin_manager = CoinManager(
            self.rows, self.cols, self.cell_size, self.margin, GRID_WIDTH, ANCHO
        )
        self.enemy_manager = EnemyManager(
            game=self,
            rows=self.rows,
            cols=self.cols,
            cell_size=self.cell_size,
            margin=self.margin,
            screen_width=ANCHO,
            max_enemies=self.max_enemigos,
            spawn_delay=self.spawn_delay
        )
        self.rook_manager = RookManager(
            game=self,
            rows=self.rows,
            cols=self.cols,
            cell_size=self.cell_size,
            margin=self.margin
        )

        # ======================
        # 6️⃣ Si hay partida guardada, cargarla
        # ======================
        if self.save_data:
            print("🟩 Cargando partida guardada...")

            # 🪙 monedas — si no existen, empezar en 0
            self.coin_manager.collected = self.save_data.get("monedas", 0)

            # 🕒 tiempo — si no existe, empezar desde 0
            self.start_time = time.time() - self.save_data.get("tiempo_total", 0)

            # 🏰 torres — si no existen, lista vacía
            rooks_guardadas = self.save_data.get("rooks", [])
            for r in rooks_guardadas:
                r.setdefault("last_attack", 0)
                r.setdefault("atk", 1)  # por si falta ataque
                self.rook_manager.rooks.append(r)

            # 👹 enemigos — si no existen, lista vacía
            enemigos_guardados = self.save_data.get("enemigos", [])
            for e in enemigos_guardados:
                # asegurar campos obligatorios
                e.setdefault("last_move", time.time())
                e.setdefault("move_delay", 0.5)
                e.setdefault("last_attack", time.time())
                self.enemy_manager.spawn_loaded_enemy(e)

        else:
            # reset si no hay partida
            self.coin_manager.collected = 0
            self.rook_manager.rooks = []

        # ======================
        # 7️⃣ Botón salir
        # ======================
        self.btn_width = 180
        self.btn_height = 36
        self.btn_x = ANCHO - self.btn_width - 12
        self.btn_y = 12
        self.btn_rect = pygame.Rect(self.btn_x, self.btn_y,
                                    self.btn_width, self.btn_height)

        # ======================
        # 8️⃣ Iniciar ciclo
        # ======================
        self.run_game()


    def mostrar_nivel_completado(self, nivel):
        ancho, alto = 500, 240
        x = (ANCHO - ancho) // 2
        y = (ALTO - alto) // 2
        rect = pygame.Rect(x, y, ancho, alto)

        fuente = pygame.font.SysFont(None, 40)
        texto = fuente.render(f"Nivel {nivel} completado!", True, BLANCO)

        btn_cont = pygame.Rect(x + 40, y + 140, 180, 50)
        btn_menu = pygame.Rect(x + 280, y + 140, 180, 50)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "menu"

                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_cont.collidepoint(e.pos):
                        return "continuar"
                    if btn_menu.collidepoint(e.pos):
                        return "menu"

            pygame.draw.rect(self.pantalla, (25, 25, 25), rect, border_radius=12)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2)
            self.pantalla.blit(texto, (x + 100, y + 50))

            pygame.draw.rect(self.pantalla, VERDE, btn_cont, border_radius=10)
            pygame.draw.rect(self.pantalla, ROJO, btn_menu, border_radius=10)

            self.pantalla.blit(fuente.render("Continuar", True, BLANCO), (btn_cont.x + 10, btn_cont.y + 10))
            self.pantalla.blit(fuente.render("Menú", True, BLANCO), (btn_menu.x + 40, btn_menu.y + 10))

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # 🔹 GUARDAR PUNTAJE
    # ------------------------------------------------------------------
    def guardar_puntaje(self):
        """
        Guarda puntaje localmente en DATA/salon_fama.json.
        El sistema de HallOfFameWindow luego lo sincroniza con Dropbox.
        """
        try:
            os.makedirs("DATA", exist_ok=True)
            path = os.path.join("DATA", "salon_fama.json")

            entry = {
                "usuario": self.usuario,
                "rol": self.rol,
                "score": int(self.coin_manager.collected),
                "timestamp": int(time.time())
            }

            # Cargar lista existente
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []

            # Agregar nueva entrada
            data.append(entry)

            # Guardar localmente
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("[OK] Puntaje guardado localmente en DATA/salon_fama.json")

        except Exception as e:
            print(f"[ERROR] No se pudo guardar el puntaje: {e}")

    # ------------------------------------------------------------------
    # 🔹 DIBUJAR GRID
    # ------------------------------------------------------------------
    def dibujar_grid(self):
        self.pantalla.fill(GRIS)

        for row in range(self.rows):
            for col in range(self.cols):
                x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
                y = self.top_offset + self.margin + row * (self.cell_size + self.margin)

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.pantalla, CELDA, rect)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 2)

    # ------------------------------------------------------------------
    # 🔹 HUD
    # ------------------------------------------------------------------
    def draw_hud(self, fps):
        font = pygame.font.SysFont(None, 26)

        texto = f"Jugador: {self.usuario} ({self.rol})"
        self.pantalla.blit(font.render(texto, True, TXT_COLOR), (10, 12))

        self.pantalla.blit(font.render("Monedas: " + str(self.coin_manager.collected),
                                       True, (255, 215, 0)), (10, 72))

        fps_text = font.render(f"FPS: {int(fps)}", True, TXT_COLOR)
        self.pantalla.blit(fps_text, (ANCHO - 110, 12))

        nivel_txt = font.render(f"Nivel: {self.nivel}", True, (255, 255, 0))
        self.pantalla.blit(nivel_txt, (10, 42))

        # botón salir
        mouse_pos = pygame.mouse.get_pos()
        hover = self.btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.pantalla, BTN_HOVER if hover else BTN_COLOR, self.btn_rect, border_radius=6)

        btn_font = pygame.font.SysFont(None, 22)
        tx = self.btn_x + (self.btn_width - btn_font.size("Salir al menú")[0]) // 2
        ty = self.btn_y + (self.btn_height - btn_font.size("Salir al menú")[1]) // 2
        self.pantalla.blit(btn_font.render("Salir al menú", True, TXT_COLOR), (tx, ty))

    # ------------------------------------------------------------------
    # 🔹 CONFIRMAR SALIDA
    # ------------------------------------------------------------------
    def mostrar_confirmacion(self, nivel):
        ancho, alto = 500, 240
        x = (ANCHO - ancho) // 2
        y = (ALTO - alto) // 2
        rect = pygame.Rect(x, y, ancho, alto)

        fuente = pygame.font.SysFont(None, 40)
        texto = fuente.render(f"Nivel {nivel} completado!", True, BLANCO)

        btn_cont = pygame.Rect(x + 40, y + 140, 180, 50)
        btn_menu = pygame.Rect(x + 280, y + 140, 180, 50)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "menu"

                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_cont.collidepoint(e.pos):
                        return "continuar"
                    if btn_menu.collidepoint(e.pos):
                        return "menu"

            pygame.draw.rect(self.pantalla, (25, 25, 25), rect, border_radius=12)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2)
            self.pantalla.blit(texto, (x + 100, y + 50))

            pygame.draw.rect(self.pantalla, VERDE, btn_cont, border_radius=10)
            pygame.draw.rect(self.pantalla, ROJO, btn_menu, border_radius=10)

            self.pantalla.blit(fuente.render("Continuar", True, BLANCO), (btn_cont.x + 10, btn_cont.y + 10))
            self.pantalla.blit(fuente.render("Menú", True, BLANCO), (btn_menu.x + 40, btn_menu.y + 10))

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # 🔹 LOOP PRINCIPAL
    # ------------------------------------------------------------------
    def run_game(self):
        running = True
        self.placing_rook = False

        self.btn_rook_width = 180
        self.btn_rook_height = 36
        self.btn_rook_x = ANCHO - self.btn_rook_width - 12
        self.btn_rook_y = self.btn_y + self.btn_height + 10
        self.btn_rook_rect = pygame.Rect(self.btn_rook_x, self.btn_rook_y,
                                        self.btn_rook_width, self.btn_rook_height)

        # 🔹 Botones para seleccionar tipo de torre
        self.btn_sand  = pygame.Rect(self.btn_rook_x, self.btn_rook_y + 50, self.btn_rook_width, 32)
        self.btn_rock  = pygame.Rect(self.btn_rook_x, self.btn_rook_y + 90, self.btn_rook_width, 32)
        self.btn_fire  = pygame.Rect(self.btn_rook_x, self.btn_rook_y + 130, self.btn_rook_width, 32)
        self.btn_water = pygame.Rect(self.btn_rook_x, self.btn_rook_y + 170, self.btn_rook_width, 32)

        font = pygame.font.SysFont(None, 26)

        while running:
            dt = clock.tick(FPS) / 1000

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    if self.confirmar_salida():
                        running = False

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    pos = evento.pos

                    if self.btn_rect.collidepoint(pos):
                        if self.confirmar_salida():
                            running = False

                    elif self.btn_rook_rect.collidepoint(pos):
                        self.placing_rook = not self.placing_rook

                    # 🔹 Selección de tipo de torre
                    elif self.btn_sand.collidepoint(pos):
                        self.rook_manager.selected_rook_type = "sand"

                    elif self.btn_rock.collidepoint(pos):
                        self.rook_manager.selected_rook_type = "rock"

                    elif self.btn_fire.collidepoint(pos):
                        self.rook_manager.selected_rook_type = "fire"

                    elif self.btn_water.collidepoint(pos):
                        self.rook_manager.selected_rook_type = "water"

                    # 🔹 Colocación de torre
                    elif self.placing_rook:
                        placed = self.rook_manager.place_rook(pos, self.coin_manager)
                        if placed:
                            self.placing_rook = False
                    else:
                        self.coin_manager.check_collect(pos)

            # actualizar lógica
            self.coin_manager.update()
            self.enemy_manager.update(dt, self.rook_manager)
            self.rook_manager.update(dt, self.enemy_manager.enemies)

            # ===============================================
            #        ⚔ VICTORIA / DERROTA / SIGUIENTE NIVEL
            # ===============================================
            if self.enemy_manager.finished:

                tiempo_total = time.time() - self.start_time

                # ❌ DERROTA
                if self.enemy_manager.lost:
                    # eliminar archivo de guardado (no se debe continuar nunca)
                    try:
                        os.remove("DATA/savegame.json")
                    except:
                        pass

                    mostrar_derrota(self.pantalla, self.usuario, clock)
                    running = False
                    continue

                # ✔ VICTORIA EN NIVEL 3 (juego completo terminado)
                if self.nivel == 3:
                    HallOfFameWindow.registrar_tiempo(self.usuario, tiempo_total)
                    mostrar_victoria(self.pantalla, self.usuario, clock)

                    # borrar cualquier guardado después de ganar todo
                    try:
                        os.remove("DATA/savegame.json")
                    except:
                        pass

                    running = False
                    continue

                # 🚀 SIGUIENTE NIVEL (nivel 1 o nivel 2)
                opcion = self.mostrar_nivel_completado(self.nivel)

                # ================================
                # BORRAR partida vieja
                # ================================
                try:
                    os.remove("DATA/savegame.json")
                except:
                    pass

                # ================================
                # GUARDAR SOLO EL NUEVO NIVEL
                # ================================
                proximo_nivel = self.nivel + 1

                os.makedirs("DATA", exist_ok=True)
                with open("DATA/savegame.json", "w") as f:
                    json.dump({
                        "usuario": self.usuario,
                        "nivel": proximo_nivel
                    }, f, indent=4)

                # ================================
                # ACCIÓN SEGÚN ELIJA EL JUGADOR
                # ================================
                if opcion == "continuar":
                    # Ir directamente al siguiente nivel
                    GameWindow(self.usuario, self.rol, nivel=proximo_nivel)
                else:
                    # Volver al menú → pero guardado ya apunta al siguiente nivel
                    from gui.menu_principal import MainMenu
                    MainMenu(self.usuario, self.rol)

                running = False
                continue

            # dibujar
            self.dibujar_grid()
            self.coin_manager.draw(self.pantalla)
            self.enemy_manager.draw(self.pantalla)
            self.rook_manager.draw(self.pantalla, self.enemy_manager.enemies)

            self.draw_hud(clock.get_fps())

            # botón torres
            hover = self.btn_rook_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.pantalla, BTN_HOVER if hover else BTN_COLOR,
                            self.btn_rook_rect, border_radius=6)
            self.pantalla.blit(pygame.font.SysFont(None, 22).render(
                "Colocar torre", True, TXT_COLOR
            ), (self.btn_rook_x + 20, self.btn_rook_y + 7))

            # mensaje modo torre
            if self.placing_rook:
                txt = font.render("Modo colocar torre activo", True, (255, 255, 0))
                self.pantalla.blit(txt, (10, 100))

            # enemigos restantes SIEMPRE visibles
            enemies_left = self.enemy_manager.remaining_enemies()
            txt_enemigos = font.render(f"Enemigos restantes: {enemies_left}", True, (255, 255, 255))
            self.pantalla.blit(txt_enemigos, (10, 130))

            # 🔹 Dibujar botones de tipos de torres
            font_btn = pygame.font.SysFont(None, 22)
            buttons = [
                (self.btn_sand,  "Sand Rook - 50M",  "sand"),
                (self.btn_rock,  "Rock Rook - 100M",  "rock"),
                (self.btn_fire,  "Fire Rook - 150M",  "fire"),
                (self.btn_water, "Water Rook - 150M", "water")
            ]

            for rect, label, ttype in buttons:
                hover = rect.collidepoint(pygame.mouse.get_pos())
                color = BTN_HOVER if hover else BTN_COLOR

                if self.rook_manager.selected_rook_type == ttype:
                    color = (60, 130, 60)

                pygame.draw.rect(self.pantalla, color, rect, border_radius=6)

                text = font_btn.render(label, True, TXT_COLOR)
                tx = rect.x + (rect.width - text.get_width()) // 2
                ty = rect.y + (rect.height - text.get_height()) // 2
                self.pantalla.blit(text, (tx, ty))

            pygame.display.flip()

        self.cleanup_and_return()

    def confirmar_salida(self):
        # 🚫 Si el nivel ya terminó (pantalla de nivel completado),
        # NO guardar el estado, solo salir.
        if self.enemy_manager.finished:
            return True

        ancho, alto = 460, 220
        x = (ANCHO - ancho) // 2
        y = (ALTO - alto) // 2

        rect = pygame.Rect(x, y, ancho, alto)
        fuente = pygame.font.SysFont(None, 35)

        btn_si = pygame.Rect(x + 50, y + 130, 150, 45)
        btn_no = pygame.Rect(x + 260, y + 130, 150, 45)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False

                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_si.collidepoint(e.pos):
                        self.guardar_estado()   # ← solo guarda si NO terminó el nivel
                        return True
                    if btn_no.collidepoint(e.pos):
                        return False

            pygame.draw.rect(self.pantalla, (20,20,20), rect, border_radius=12)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2)

            self.pantalla.blit(fuente.render("¿Deseas salir y guardar?", True, BLANCO),
                               (x + 60, y + 40))

            pygame.draw.rect(self.pantalla, VERDE, btn_si, border_radius=10)
            self.pantalla.blit(fuente.render("Sí", True, BLANCO),
                               (btn_si.x + 55, btn_si.y + 5))

            pygame.draw.rect(self.pantalla, ROJO, btn_no, border_radius=10)
            self.pantalla.blit(fuente.render("No", True, BLANCO),
                               (btn_no.x + 55, btn_no.y + 5))

            pygame.display.flip()
            clock.tick(30)

    def cleanup_and_return(self):
        try:
            pygame.display.quit()
        except:
            pass

        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)

    def guardar_estado(self):
        data = {
            "usuario": self.usuario,
            "nivel": self.nivel,
            "monedas": self.coin_manager.collected,
            "tiempo_total": time.time() - self.start_time,

            "rooks": [
                {
                    "type": r.get("type", self.rook_manager.selected_rook_type),
                    "col": r["col"],
                    "row": r["row"],
                    "hp": r["hp"]
                }
                for r in self.rook_manager.rooks
            ],

            "enemigos": [
                {
                    "type": e["type"],
                    "col": e["col"],
                    "row": e["row"],
                    "hp": e["hp"],
                    "x": e["x"],
                    "y": e["y"],
                    "last_move": e["last_move"],
                    "last_attack": e["last_attack"]
                }
                for e in self.enemy_manager.enemies
            ],

            "enemy_state": {
                "spawned_count": self.enemy_manager.spawned_count,
                "max_enemies": self.enemy_manager.max_enemies,
                "spawn_delay": self.enemy_manager.spawn_delay,
                "total_to_spawn": self.enemy_manager.total_to_spawn
            }
        }

        os.makedirs("DATA", exist_ok=True)
        with open("DATA/savegame.json", "w") as f:
            json.dump(data, f, indent=4)

        print("💾 Juego guardado correctamente.")


    def get_savegame_level(self):
        """Retorna nivel guardado si existe, sino None."""
        path = "DATA/savegame.json"
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("nivel", None)
        except:
            return None
        
    def cargar_estado(self):
        path = "DATA/savegame.json"
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r") as f:
                contenido = f.read().strip()

                # Si está vacío → no cargar nada
                if contenido == "":
                    return None

                data = json.loads(contenido)

                if not isinstance(data, dict):
                    return None

                return data

        except Exception as e:
            print("⚠ Error cargando savegame:", e)
            return None
        

    def reset_progreso_para_nuevo_nivel(self):
        """Reinicia completamente el estado al avanzar a un nuevo nivel."""
        
        # borrar savegame para que no arrastre progreso viejo
        path = "DATA/savegame.json"
        if os.path.exists(path):
            os.remove(path)

        # reiniciar contadores
        self.coin_manager.collected = 0
        self.rook_manager.rooks = []
        self.enemy_manager.enemies = []
        self.enemy_manager.spawned_count = 0

        # reiniciar tiempo del nivel
        self.start_time = time.time()

        print("🔄 Progreso reiniciado para el siguiente nivel.")
