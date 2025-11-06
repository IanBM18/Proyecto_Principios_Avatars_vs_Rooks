# juego/rook_manager.py
import pygame
import os

# juego/rook_manager.py
class RookManager:
    def __init__(self, rows, cols, cell_size, margin, screen_width):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width
        self.rooks = []  # lista de torres [(col, row)]
        self.invalid_pos = None  # almacena la última posición inválida

        # Cargar imagen
        image_path = "assets/sprites/torreMagica.png"
        self.rook_img = pygame.image.load(image_path).convert_alpha()
        self.rook_img = pygame.transform.scale(self.rook_img, (cell_size - 10, cell_size - 10))

    def place_rook(self, pos, coin_manager):
        mouse_x, mouse_y = pos
        y_offset = 100  # igual que la grilla
        left_offset = (self.screen_width - (self.cols * (self.cell_size + self.margin) + self.margin)) // 2

        # ⚠️ Verificar monedas
        if coin_manager.collected < 50:
            print("No tienes suficientes monedas para colocar la torre")
            return False

        for row in range(self.rows):
            for col in range(self.cols):
                cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
                cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                if rect.collidepoint(mouse_x, mouse_y):
                    if (col, row) not in self.rooks:
                        self.rooks.append((col, row))
                        self.invalid_pos = None
                        # ⚡ Descontar monedas
                        coin_manager.collected -= 50
                        print(f"Torre colocada en ({col}, {row}), monedas restantes: {coin_manager.collected}")
                        return True
                    else:
                        self.invalid_pos = (col, row)
                        print(f"No se puede colocar torre en ({col}, {row})")
                        return False
        return False

    def draw(self, surface):
        """Dibuja todas las torres y la casilla inválida en rojo"""
        y_offset = 100
        left_offset = (self.screen_width - (self.cols * (self.cell_size + self.margin) + self.margin)) // 2

        # Dibujar torres
        for col, row in self.rooks:
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)

        # Centrar la torre en la celda
            center_x = cell_x + (self.cell_size - self.rook_img.get_width()) // 2
            center_y = cell_y + (self.cell_size - self.rook_img.get_height()) // 2

            surface.blit(self.rook_img, (center_x, center_y))

        # Dibujar casilla inválida en rojo
        if self.invalid_pos:
            col, row = self.invalid_pos
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
            rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
            pygame.draw.rect(surface, (255, 0, 0), rect, 4)  # borde rojo