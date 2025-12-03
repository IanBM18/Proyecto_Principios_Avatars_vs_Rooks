# juego/victoria.py
import pygame

def mostrar_victoria(pantalla, usuario, clock):
    ANCHO, ALTO = pantalla.get_size()
    mostrando = True
    font_titulo = pygame.font.SysFont(None, 48, bold=True)
    font_texto = pygame.font.SysFont(None, 32)

    btn_width, btn_height = 220, 50
    btn_x = (ANCHO - btn_width) // 2
    btn_y = ALTO // 2 + 50
    btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

    while mostrando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_rect.collidepoint(evento.pos):
                    mostrando = False

        pantalla.fill((30, 30, 30))
        titulo_surf = font_titulo.render("¡Felicidades!", True, (255, 215, 0))
        msg_surf = font_texto.render(f"{usuario} GANASTE!!", True, (255, 255, 255))
        pantalla.blit(titulo_surf, ((ANCHO - titulo_surf.get_width()) // 2, ALTO // 2 - 80))
        pantalla.blit(msg_surf, ((ANCHO - msg_surf.get_width()) // 2, ALTO // 2 - 20))

        mouse_pos = pygame.mouse.get_pos()
        color_btn = (200,200,200) if btn_rect.collidepoint(mouse_pos) else (100,100,100)
        pygame.draw.rect(pantalla, color_btn, btn_rect, border_radius=6)
        texto_btn = font_texto.render("Volver al menú", True, (0,0,0))
        pantalla.blit(texto_btn, (btn_x + (btn_width - texto_btn.get_width()) // 2,
                                   btn_y + (btn_height - texto_btn.get_height()) // 2))

        pygame.display.flip()
        clock.tick(60)