import random
import pygame
import time

class CoinManager:
    def __init__(self, rows, cols, cell_size, margin, max_coins=5):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.max_coins = max_coins
        self.active_coins = []  # [(x, y), ...]
        self.collected = 0

        # Temporizador para cooldown
        self.last_spawn_time = time.time()
        self.next_spawn_delay = random.uniform(3, 5)  # segundos

        # Cargar imagen de moneda
        self.coin_img = pygame.image.load("assets/sprites/coin.png")
        self.coin_img = pygame.transform.scale(self.coin_img, (cell_size - 10, cell_size - 10))

    def spawn_coin(self):
        """Genera UNA moneda en una posición libre aleatoria."""
        posibles = [(x, y) for x in range(self.cols) for y in range(self.rows) if (x, y) not in self.active_coins]
        if posibles:
            nueva = random.choice(posibles)
            self.active_coins.append(nueva)

    def update(self):
        """Controla el cooldown y genera monedas cuando corresponde."""
        now = time.time()
        if len(self.active_coins) < self.max_coins and now - self.last_spawn_time >= self.next_spawn_delay:
            self.spawn_coin()
            self.last_spawn_time = now
            self.next_spawn_delay = random.uniform(3, 5)  # Nuevo cooldown aleatorio

    def draw(self, surface, y_offset=80):
        """Dibuja las monedas activas."""
        for (col, row) in self.active_coins:
            x = self.margin + col * (self.cell_size + self.margin)
            y = y_offset + self.margin + row * (self.cell_size + self.margin)
            surface.blit(self.coin_img, (x + 5, y + 5))

    def check_collect(self, mouse_pos, y_offset=80):
        """Verifica si se hace clic sobre una moneda y la recoge."""
        mx, my = mouse_pos
        for coin in self.active_coins[:]:
            cx = self.margin + coin[0] * (self.cell_size + self.margin)
            cy = y_offset + self.margin + coin[1] * (self.cell_size + self.margin)
            rect = pygame.Rect(cx, cy, self.cell_size, self.cell_size)
            if rect.collidepoint(mx, my):
                self.active_coins.remove(coin)
                self.collected += 1
                print(f"💰 Moneda recogida! Total: {self.collected}")
                break