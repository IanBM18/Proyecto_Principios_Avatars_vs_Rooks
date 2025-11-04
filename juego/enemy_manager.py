import pygame
import random
import time

class EnemyManager:
    def __init__(self, rows, cols, cell_size, margin):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin

        self.enemies = []  # [(x, y, next_move_time)]
        self.last_spawn_time = time.time()
        self.next_spawn_delay = random.uniform(6, 10)

        # Cargar sprite enemigo
        self.enemy_img = pygame.image.load("assets/sprites/enemy.png")
        self.enemy_img = pygame.transform.scale(self.enemy_img, (cell_size - 10, cell_size - 10))

    def spawn_enemy(self):
        """Aparece un enemigo en una fila aleatoria, en la última columna."""
        y = random.randint(0, self.rows - 1)
        x = self.cols - 1
        self.enemies.append((x, y, time.time() + 3))  # el enemigo se moverá en 3s

    def update(self):
        """Actualiza el movimiento y el respawn de enemigos."""
        current_time = time.time()

        # 🕓 Spawneo aleatorio
        if current_time - self.last_spawn_time >= self.next_spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = current_time
            self.next_spawn_delay = random.uniform(6, 10)

        # 🧠 Movimiento cada 3s
        new_enemies = []
        for (x, y, next_move_time) in self.enemies:
            if current_time >= next_move_time:
                x -= 1
                next_move_time = current_time + 3
            if x >= 0:  # Si aún está dentro del tablero
                new_enemies.append((x, y, next_move_time))
        self.enemies = new_enemies

    def draw(self, surface, y_offset=80):
        """Dibuja los enemigos en pantalla."""
        for (col, row, _) in self.enemies:
            x = self.margin + col * (self.cell_size + self.margin)
            y = y_offset + self.margin + row * (self.cell_size + self.margin)
            surface.blit(self.enemy_img, (x + 5, y + 5))