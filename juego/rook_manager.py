# juego/rook_manager.py
import pygame
import time

class RookManager:
    def __init__(self, game, rows, cols, cell_size, margin, left_offset=None, top_offset=None):
        self.game = game
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin

        # offsets
        self.left_offset = left_offset if left_offset is not None else getattr(game, "left_offset", 0)
        self.top_offset = top_offset if top_offset is not None else getattr(game, "top_offset", 100)

        # Lista de torres
        self.rooks = []  # {'type','col','row','hp','atk','last_attack'}
        self.invalid_pos = None
        self.shots = []

        # Tipo de torre seleccionada desde botones
        self.selected_rook_type = "sand"   # valor por defecto

        # 🟦 Definición de las torres según tu tabla
        self.ROOK_TYPES = {
            "sand": {
                "name": "Sand Rook",
                "atk": 2,
                "cost": 50,
                "hp": 3,
                "image": "assets/sprites/sand.png"
            },
            "rock": {
                "name": "Rock Rook",
                "atk": 4,
                "cost": 100,
                "hp": 14,
                "image": "assets/sprites/rock.png"
            },
            "fire": {
                "name": "Fire Rook",
                "atk": 8,
                "cost": 150,
                "hp": 16,
                "image": "assets/sprites/fire.png"
            },
            "water": {
                "name": "Water Rook",
                "atk": 8,
                "cost": 150,
                "hp": 16,
                "image": "assets/sprites/water.png"
            }
        }

        # cargar imágenes
        self.rook_images = {}
        for key, data in self.ROOK_TYPES.items():
            try:
                img = pygame.image.load(data["image"]).convert_alpha()
                img = pygame.transform.scale(img, (cell_size - 10, cell_size - 10))
                self.rook_images[key] = img
            except:
                # fallback si no existe imagen
                surf = pygame.Surface((cell_size - 10, cell_size - 10), pygame.SRCALPHA)
                surf.fill((200, 200, 200))
                self.rook_images[key] = surf

    # ---------------------------------------------------------
    # 🔹 Colocar torre con su tipo y costo específico
    # ---------------------------------------------------------
    def place_rook(self, pos, coin_manager):
        mouse_x, mouse_y = pos

        left_offset = self.left_offset
        top_offset = self.top_offset

        rook_data = self.ROOK_TYPES[self.selected_rook_type]
        cost = rook_data["cost"]

        # verificar costo
        if coin_manager.collected < cost:
            print("❌ No tienes suficientes monedas.")
            return False

        for row in range(self.rows):
            for col in range(self.cols):
                cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
                cell_y = top_offset + self.margin + row * (self.cell_size + self.margin)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                if rect.collidepoint(mouse_x, mouse_y):
                    if not any(r['col'] == col and r['row'] == row for r in self.rooks):
                        self.rooks.append({
                            'type': self.selected_rook_type,
                            'col': col,
                            'row': row,
                            'hp': rook_data["hp"],
                            'atk': rook_data["atk"],
                            'last_attack': 0
                        })
                        coin_manager.collected -= cost
                        print(f"🏰 {rook_data['name']} colocada en ({col}, {row})")
                        self.invalid_pos = None
                        return True

                    else:
                        print("⚠️ Ya hay una torre aquí.")
                        self.invalid_pos = (col, row)
                        return False

        return False

    # ---------------------------------------------------------
    # 🔹 Lógica de combate
    # ---------------------------------------------------------
    def update(self, dt, enemies):
        ATTACK_RATE = 4.0  # todas atacan cada 4 segundos

        now = time.time()

        for rook in self.rooks[:]:

            # atacar cada 4s
            if now - rook["last_attack"] >= ATTACK_RATE:
                rook["last_attack"] = now

                # enemigo más cercano abajo
                target = None
                closest_row = 999

                for enemy in enemies:
                    if enemy["col"] == rook["col"] and enemy["row"] > rook["row"]:
                        if enemy["row"] < closest_row:
                            closest_row = enemy["row"]
                            target = enemy

                if target:
                    target["hp"] -= rook["atk"]

                    # registrar disparo
                    self.shots.append({
                        "start": (rook["col"], rook["row"]),
                        "end": (target["col"], target["row"]),
                        "time": now
                    })

            # torre destruida
            if rook["hp"] <= 0:
                self.rooks.remove(rook)

        # borrar disparos viejos
        self.shots = [s for s in self.shots if now - s["time"] < 0.25]

    # ---------------------------------------------------------
    # 🔹 Dibujar torres y disparos
    # ---------------------------------------------------------
    def draw(self, surface, enemies):
        left_offset = self.left_offset
        top_offset = self.top_offset

        for rook in self.rooks:
            img = self.rook_images[rook["type"]]

            col = rook["col"]
            row = rook["row"]

            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = top_offset + self.margin + row * (self.cell_size + self.margin)

            surface.blit(img, (cell_x, cell_y))

            # mostrar HP
            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"{rook['hp']}", True, (0, 255, 0))
            surface.blit(hp_text, (cell_x + 5, cell_y - 12))

        # dibujar disparos
        for s in self.shots:
            start = (
                left_offset + s["start"][0] * (self.cell_size + self.margin) + self.cell_size//2,
                top_offset + s["start"][1] * (self.cell_size + self.margin) + self.cell_size//2
            )

            enemy = next((e for e in enemies if e["col"] == s["end"][0] and e["row"] == s["end"][1]), None)
            if not enemy:
                continue

            end = (
                enemy["x"] + 20,
                enemy["y"] + 20
            )

            pygame.draw.line(surface, (0, 255, 255), start, end, 3)