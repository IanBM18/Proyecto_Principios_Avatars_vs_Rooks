# juego/enemy_manager.py
import pygame
import random
import time

class EnemyManager:
    def __init__(self, game, rows, cols, cell_size, margin, screen_width, max_enemies, spawn_delay):
        self.game = game
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width

        # Lista global de enemigos en juego
        self.enemies = []
        self.spawned_count = 0
        self.max_enemies = max_enemies
        self.total_to_spawn = max_enemies

        # Proyectiles (para flechadores)
        self.shots = []

        # tiempo entre spawns
        self.last_spawn_time = time.time()
        self.spawn_delay = spawn_delay  

        self.finished = False
        self.lost = False
        self.enemies_eliminated = 0

        # offset
        self.left_offset = getattr(game, "left_offset",
                                   (screen_width - (cols * (cell_size + margin) + margin)) // 2)
        self.y_offset = getattr(game, "top_offset", 100)

        self.font = pygame.font.SysFont("arial", 14, bold=True)

        # 🔥 Definición de tipos de enemigos según tu tabla
        self.AVATAR_TYPES = {
            "flechador": {
                "hp": 5,
                "atk": 2,
                "move_delay": 12.0,
                "attack_delay": 10.0,
                "range": 3,
                "img": "assets/sprites/flechador.png"
            },
            "escudero": {
                "hp": 10,
                "atk": 3,
                "move_delay": 10.0,
                "attack_delay": 15.0,
                "img": "assets/sprites/escudero.png"
            },
            "lenador": {
                "hp": 20,
                "atk": 9,
                "move_delay": 13.0,
                "attack_delay": 5.0,
                "img": "assets/sprites/lenador.png"
            },
            "canibal": {
                "hp": 25,
                "atk": 12,
                "move_delay": 14.0,
                "attack_delay": 3.0,
                "img": "assets/sprites/canibal.png"
            }
        }

    # ---------------------------------------------------------
    # SPAWN DE ENEMIGO
    # ---------------------------------------------------------
    def spawn_enemy(self):
        if self.spawned_count >= self.max_enemies:
            return

        avatar_type = random.choice(list(self.AVATAR_TYPES.keys()))
        data = self.AVATAR_TYPES[avatar_type]

        img = pygame.image.load(data["img"]).convert_alpha()
        img = pygame.transform.scale(img, (self.cell_size - 10, self.cell_size - 10))

        col = random.randint(0, self.cols - 1)
        row = self.rows - 1

        cell_x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
        cell_y = self.y_offset + self.margin + row * (self.cell_size + self.margin)

        x = cell_x + (self.cell_size - img.get_width()) // 2
        y = cell_y + (self.cell_size - img.get_height()) // 2

        enemy = {
            "type": avatar_type,
            "col": col,
            "row": row,
            "x": x,
            "y": y,
            "img": img,
            "hp": data["hp"],
            "atk": data["atk"],
            "range": data.get("range", 0),
            "move_delay": data["move_delay"],
            "attack_delay": data["attack_delay"],
            "speed": 150,
            "dest_x": x,
            "dest_y": y,
            "last_move": time.time(),
            "last_attack": 0
        }

        self.enemies.append(enemy)
        self.spawned_count += 1

    # ---------------------------------------------------------
    # UPDATE PRINCIPAL
    # ---------------------------------------------------------
    def update(self, dt, rook_manager):
        now = time.time()

        # spawn periódico
        if self.spawned_count < self.max_enemies and now - self.last_spawn_time >= self.spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = now

        for enemy in self.enemies[:]:

            # ----------------------------------------------
            # 🔥 ATAQUE A DISTANCIA DEL FLECHADOR
            # ----------------------------------------------
            if enemy["type"] == "flechador":
                if now - enemy["last_attack"] >= enemy["attack_delay"]:

                    # revisar torres dentro de su rango
                    target = None
                    best_dist = 999

                    for rook in rook_manager.rooks:
                        if rook["col"] == enemy["col"]:
                            dist = abs(rook["row"] - enemy["row"])

                            if 0 < dist <= enemy["range"]:
                                if dist < best_dist:
                                    best_dist = dist
                                    target = rook

                    if target:
                        enemy["last_attack"] = now
                        target["hp"] -= enemy["atk"]

                        # registrar disparo
                        self.shots.append({
                            "start": (enemy["x"], enemy["y"]),
                            "end": (target["col"], target["row"]),
                            "time": now
                        })

                        if target["hp"] <= 0:
                            try:
                                rook_manager.rooks.remove(target)
                            except:
                                pass

                        continue  # no avanza si disparó

            # ----------------------------------------------
            # ATAQUE NORMAL CUERPO A CUERPO
            # ----------------------------------------------
            next_row = enemy["row"] - 1
            torre = next((r for r in rook_manager.rooks
                          if r["col"] == enemy["col"] and r["row"] == next_row), None)

            if torre:
                if now - enemy["last_attack"] >= enemy["attack_delay"]:
                    torre["hp"] -= enemy["atk"]
                    enemy["last_attack"] = now

                    if torre["hp"] <= 0:
                        rook_manager.rooks.remove(torre)

            else:
                # avanzar SIEMPRE (permitir bajar desde row 0)
                if now - enemy["last_move"] >= enemy["move_delay"]:
                    enemy["row"] -= 1

                    # check derrota instantánea
                    if enemy["row"] < 0:
                        self.finished = True
                        self.lost = True
                        try:
                            self.enemies.remove(enemy)
                        except:
                            pass
                        continue

                    enemy["dest_y"] = (
                        self.y_offset + self.margin +
                        enemy["row"] * (self.cell_size + self.margin) +
                        (self.cell_size - enemy["img"].get_height()) // 2
                    )
                    enemy["last_move"] = now

            # movimiento suave
            dx = enemy["dest_x"] - enemy["x"]
            dy = enemy["dest_y"] - enemy["y"]
            dist = (dx*dx + dy*dy) ** 0.5

            if dist > 0:
                step = enemy["speed"] * dt
                if step >= dist:
                    enemy["x"] = enemy["dest_x"]
                    enemy["y"] = enemy["dest_y"]
                else:
                    enemy["x"] += (dx / dist) * step
                    enemy["y"] += (dy / dist) * step

            # muerte
            if enemy["hp"] <= 0:
                self.game.coin_manager.collected += 75
                self.enemies.remove(enemy)
                self.enemies_eliminated += 1

           
        # victoria
        if self.spawned_count >= self.max_enemies and not self.enemies:
            self.finished = True

    # ---------------------------------------------------------
    # DIBUJAR ENEMIGOS + DISPAROS DEL FLECHADOR
    # ---------------------------------------------------------
    def draw(self, surface):
        for enemy in self.enemies:
            surface.blit(enemy["img"], (enemy["x"], enemy["y"]))
            hp_txt = self.font.render(str(enemy["hp"]), True, (255, 0, 0))
            surface.blit(hp_txt, (enemy["x"] + 10, enemy["y"] - 15))

        # 🔥 Dibujar disparos
        now = time.time()
        new_shots = []

        for s in self.shots:
            if now - s["time"] < 0.25:

                start = (s["start"][0] + self.cell_size//2 - 5,
                        s["start"][1] + self.cell_size//2 - 5)

                col, row = s["end"]
                end_x = self.left_offset + col * (self.cell_size + self.margin) + 25
                end_y = self.y_offset + row * (self.cell_size + self.margin) + 25
                end = (end_x, end_y)

                pygame.draw.line(surface, (255, 180, 0), start, end, 3)

                new_shots.append(s)

        self.shots = new_shots

    # ---------------------------------------------------------
    def remaining_enemies(self):
        return len(self.enemies) + (self.total_to_spawn - self.spawned_count)