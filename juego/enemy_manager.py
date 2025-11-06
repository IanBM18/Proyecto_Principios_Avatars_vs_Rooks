import pygame
import random
import time

class EnemyManager:
    def __init__(self, rows, cols, cell_size, margin, screen_width):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width

        self.enemies = []  # [{'x': , 'y': , 'dest_x': , 'dest_y': , 'speed': }]
        self.last_spawn_time = time.time()
        self.next_spawn_delay = random.uniform(6, 10)

        # Cargar sprite enemigo
        self.enemy_img = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
        self.enemy_img = pygame.transform.scale(self.enemy_img, (cell_size - 10, cell_size - 10))

        # Offset para centrar en pantalla
        grid_width = cols * (cell_size + margin) + margin
        self.left_offset = (screen_width - grid_width) // 2

    def spawn_enemy(self):
        """Aparece un enemigo en una columna aleatoria, en la última fila (abajo)."""
        col = random.randint(0, self.cols - 1)
        row = self.rows - 1
        x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
        y = 80 + self.margin + row * (self.cell_size + self.margin)
        enemy = {
            'x': x,
            'y': y,
            'dest_x': x,
            'dest_y': y - (self.cell_size + self.margin),  # siguiente fila arriba
            'speed': 100  # pixeles por segundo
        }
        self.enemies.append(enemy)

    def update(self, dt):
        """Actualiza el movimiento y el respawn de enemigos (movimiento fluido)."""
        current_time = time.time()

        # Spawn aleatorio
        if current_time - self.last_spawn_time >= self.next_spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = current_time
            self.next_spawn_delay = random.uniform(6, 10)

        # Mover enemigos suavemente hacia dest_y
        for enemy in self.enemies[:]:
            dx = enemy['dest_x'] - enemy['x']
            dy = enemy['dest_y'] - enemy['y']
            distancia = (dx**2 + dy**2)**0.5
            if distancia > 0:
                move_x = (dx / distancia) * enemy['speed'] * dt
                move_y = (dy / distancia) * enemy['speed'] * dt

                # No pasarse del destino
                if abs(move_x) > abs(dx):
                    move_x = dx
                if abs(move_y) > abs(dy):
                    move_y = dy

                enemy['x'] += move_x
                enemy['y'] += move_y

            # Si llegó al destino y todavía hay filas arriba
            if enemy['y'] <= enemy['dest_y'] + 1:  # margen de error
                next_row_y = enemy['dest_y'] - (self.cell_size + self.margin)
                if next_row_y >= 80:  # limite superior
                    enemy['dest_y'] = next_row_y
                else:
                    # Elimina enemigo cuando sale de la grilla
                    self.enemies.remove(enemy)

    def draw(self, surface):
        """Dibuja los enemigos en pantalla."""
        for enemy in self.enemies:
            surface.blit(self.enemy_img, (enemy['x'], enemy['y']))