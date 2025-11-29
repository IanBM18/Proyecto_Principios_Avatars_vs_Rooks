# juego/enemy_manager.py
import pygame
import random
import time

class EnemyManager:
    def __init__(self, game, rows, cols, cell_size, margin, screen_width, max_enemies=10):
        self.game = game
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width

        # Enemigos
        self.enemies = []
        self.spawned_count = 0
        self.max_enemies = max_enemies

        # ⚠️ IMPORTANTE PARA remaining_enemies()
        self.total_to_spawn = max_enemies

        # Spawn timing fijo a 10s según feedback
        self.last_spawn_time = time.time()
        self.spawn_delay = 10.0  # cada 10 segundos nace un avatar/enemigo

        # Estados
        self.finished = False
        self.lost = False
        self.enemies_eliminated = 0

        # Imagen
        self.enemy_img = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
        self.enemy_img = pygame.transform.scale(self.enemy_img, (cell_size - 10, cell_size - 10))

        # offsets correctos (usar los del game)
        self.left_offset = getattr(game, "left_offset",
                                   (screen_width - (cols * (cell_size + margin) + margin)) // 2)
        self.y_offset = getattr(game, "top_offset", 100)

        self.font = pygame.font.SysFont("arial", 14, bold=True)

        # movimiento por fila (delay entre pasos)
        self.step_delay = 2.0  # cada cuánto puede avanzar una fila (segundos)

    def spawn_enemy(self):
        if self.spawned_count >= self.max_enemies:
            return

        col = random.randint(0, self.cols - 1)
        row = self.rows - 1  # nace en la fila inferior

        cell_x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
        cell_y = self.y_offset + self.margin + row * (self.cell_size + self.margin)

        x = cell_x + (self.cell_size - self.enemy_img.get_width()) // 2
        y = cell_y + (self.cell_size - self.enemy_img.get_height()) // 2

        enemy = {
            "col": col,
            "row": row,
            "x": x,
            "y": y,
            "hp": 5,
            "speed": 140,
            "dest_x": x,
            "dest_y": y,
            "last_move": time.time()
        }

        self.enemies.append(enemy)
        self.spawned_count += 1

    def update(self, dt, rook_manager):
        now = time.time()

        # spawn periódico (10s)
        if self.spawned_count < self.max_enemies and now - self.last_spawn_time >= self.spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = now

        for enemy in self.enemies[:]:
            # revisar torre en la fila frente a él
            next_row = enemy["row"] - 1
            torre = next((r for r in rook_manager.rooks
                          if r["col"] == enemy["col"] and r["row"] == next_row), None)

            if torre:
                if "last_attack" not in enemy:
                    enemy["last_attack"] = 0.0
                if now - enemy["last_attack"] >= 10.0:
                    torre["hp"] -= 2
                    enemy["last_attack"] = now
                    if torre["hp"] <= 0:
                        try:
                            rook_manager.rooks.remove(torre)
                        except ValueError:
                            pass
            else:
                # avanzar fila cada step_delay
                if enemy["row"] > 0 and now - enemy["last_move"] >= self.step_delay:
                    enemy["row"] -= 1
                    enemy["dest_y"] = (
                        self.y_offset + self.margin +
                        enemy["row"] * (self.cell_size + self.margin) +
                        (self.cell_size - self.enemy_img.get_height()) // 2
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
                try:
                    self.game.coin_manager.collected += 75
                except Exception:
                    pass

                try:
                    self.enemies.remove(enemy)
                except ValueError:
                    pass

                self.enemies_eliminated += 1

            # derrota si baja más allá de la fila 0
            if enemy["row"] < 0:
                try:
                    self.enemies.remove(enemy)
                except ValueError:
                    pass
                self.finished = True
                self.lost = True

        # victoria
        if self.spawned_count >= self.max_enemies and not self.enemies:
            self.finished = True

    def draw(self, surface):
        for enemy in self.enemies:
            surface.blit(self.enemy_img, (enemy["x"], enemy["y"]))
            hp_txt = self.font.render(str(enemy["hp"]), True, (255, 0, 0))
            surface.blit(hp_txt, (enemy["x"] + 10, enemy["y"] - 15))

    def remaining_enemies(self):
        # enemigos vivos + enemigos que aún NO han salido
        return len(self.enemies) + (self.total_to_spawn - self.spawned_count)
