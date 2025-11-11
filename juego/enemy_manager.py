# juego/enemy_manager.py
import pygame
import random
import time

class EnemyManager:
    def __init__(self, rows, cols, cell_size, margin, screen_width, max_enemies=10):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width

        # 🔹 Lista de enemigos y control de spawn
        self.enemies = []
        self.last_spawn_time = time.time()
        self.next_spawn_delay = random.uniform(6, 10)
        self.spawned_count = 0
        self.max_enemies = max_enemies

        # 🔹 Contadores y bandera
        self.enemies_eliminated = 0
        self.finished = False
        self.lost = False

        # Fuente para mostrar la vida
        self.font = pygame.font.SysFont("arial", 14, bold=True)

        # Cargar sprite enemigo
        self.enemy_img = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
        self.enemy_img = pygame.transform.scale(self.enemy_img, (cell_size - 10, cell_size - 10))

        # Offset para centrar la grilla
        grid_width = cols * (cell_size + margin) + margin
        self.left_offset = (screen_width - grid_width) // 2
        self.y_offset = 100

    # 🔹 Propiedad para mostrar enemigos restantes
    @property
    def enemies_remaining(self):
        return self.max_enemies - self.enemies_eliminated

    def spawn_enemy(self):
        if self.spawned_count >= self.max_enemies:
            return  # no crear más enemigos

        col = random.randint(0, self.cols - 1)
        row = self.rows - 1
        cell_x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
        cell_y = self.y_offset + self.margin + row * (self.cell_size + self.margin)
        x = cell_x + (self.cell_size - self.enemy_img.get_width()) // 2
        y = cell_y + (self.cell_size - self.enemy_img.get_height()) // 2

        enemy = {
            'x': x,
            'y': y,
            'col': col,
            'row': row,
            'hp': 5,
            'speed': 100,
            'dest_x': x,
            'dest_y': y - (self.cell_size + self.margin),
            'last_move': time.time()
        }
        self.enemies.append(enemy)
        self.spawned_count += 1

    def update(self, dt, rook_manager):
        current_time = time.time()

        # 🔹 Spawn aleatorio solo si no se superó el máximo y no terminó el nivel
        if not self.finished and self.spawned_count < self.max_enemies and current_time - self.last_spawn_time >= self.next_spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = current_time
            self.next_spawn_delay = random.uniform(6, 10)

        # 🔹 Actualizar cada enemigo
        for enemy in self.enemies[:]:
            frente_row = enemy['row'] - 1
            torre_frente = next((r for r in rook_manager.rooks 
                                 if r['col'] == enemy['col'] and r['row'] == frente_row), None)

            if torre_frente:
                enemy['dest_y'] = enemy['y']
                if 'last_attack' not in enemy:
                    enemy['last_attack'] = 0
                # Ataque a torre
                if current_time - enemy['last_attack'] >= 10:
                    torre_frente['hp'] -= 2
                    enemy['last_attack'] = current_time
                    if torre_frente['hp'] <= 0:
                        rook_manager.rooks.remove(torre_frente)
            else:
                # Avanzar si no hay torre
                if current_time - enemy['last_move'] >= 12:
                    enemy['last_move'] = current_time
                    # Solo mover si no está en la fila 0
                    if enemy['row'] > 0:
                        enemy['row'] -= 1
                        enemy['dest_y'] = self.y_offset + self.margin + enemy['row'] * (self.cell_size + self.margin)
                    else:
                        # Llegó al final
                        self.enemies.remove(enemy)
                        self.finished = True
                        self.lost = True

            # Movimiento fluido
            dx = enemy['dest_x'] - enemy['x']
            dy = enemy['dest_y'] - enemy['y']
            distancia = (dx**2 + dy**2)**0.5
            if distancia > 0:
                enemy['x'] += (dx / distancia) * enemy['speed'] * dt
                enemy['y'] += (dy / distancia) * enemy['speed'] * dt

            # Muerte del enemigo
            if enemy['hp'] <= 0:
                self.enemies.remove(enemy)
                self.enemies_eliminated += 1
            else:
                # Si el enemigo llega a la fila 0 (final de la grilla)
                if enemy['row'] < 0:
                    self.enemies.remove(enemy)
                    self.finished = True
                    self.lost = True  # 🔹 bandera de derrota

        # 🔹 Verificar victoria
        if self.spawned_count >= self.max_enemies and not self.enemies:
            self.finished = True  # todos los enemigos eliminados

    def draw(self, surface):
        for enemy in self.enemies:
            surface.blit(self.enemy_img, (enemy['x'], enemy['y']))
            vida_text = self.font.render(str(enemy['hp']), True, (255, 0, 0))
            surface.blit(vida_text, (enemy['x'] + self.cell_size // 3, enemy['y'] - 15))