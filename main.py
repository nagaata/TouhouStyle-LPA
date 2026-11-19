import pygame
import sys
import math
import random
import os

# 1. Inicialização
pygame.init()
pygame.mixer.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Touhou Style - LPA")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("arial", 22, bold=True)
fonte_menu = pygame.font.SysFont("arial", 30, bold=True)
fonte_titulo = pygame.font.SysFont("arial", 44, bold=True)
fonte_aviso = pygame.font.SysFont("arial", 28, bold=True)

# Cores
FUNDO = (10, 10, 18)
AZUL_NAVE = (0, 200, 255)
PONTO_CRITICO = (255, 255, 255)
AMARELO_TIRO = (255, 230, 50)
ROXO_BOSS = (160, 40, 200)
VERMELHO_TIRO = (255, 60, 110)
AZUL_CLARO_TIRO = (50, 200, 255)
VERMELHO_VIDA = (220, 40, 40)
VERDE_VIDA = (40, 220, 90)
COR_BOTAO = (50, 50, 80)
COR_BOTAO_HOVER = (80, 80, 120)

# Estatísticas e Configurações Globais
contador_mortes = 0
volume_musica = 0.5
volume_sfx = 0.7

# SPRITES DOS PERSONAGENS
def carregar_sprite(caminho, tamanho):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    caminho_completo = os.path.join(base_path, caminho)

    imagem = pygame.image.load(caminho_completo).convert_alpha()
    imagem = pygame.transform.smoothscale(imagem, tamanho)

    return imagem


nave_img = carregar_sprite("assets/images/player.png", (70, 83))
boss_img = carregar_sprite("assets/images/boss.png", (150, 140))
boss_img_fase2 = boss_img.copy()
boss_img_fase2.fill((255, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)

# Nave decorativa do menu
nave_menu_img = pygame.transform.smoothscale(nave_img, (35, 42)).copy()
nave_menu_img.set_alpha(150)

# Versão branca do boss para o efeito de dano
boss_img_branco = pygame.mask.from_surface(boss_img).to_surface(
    setcolor=(255, 255, 255, 255),
    unsetcolor=(0, 0, 0, 0)
)


# Wallpaper Animado Global (Compartilhado entre Menu, Opções e Jogo)
estrelas = [[random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(1, 3)] for _ in range(80)]


def atualizar_e_desenhar_wallpaper():
    """Desenha o fundo espacial animado."""
    tela.fill(FUNDO)

    for estrela in estrelas:
        estrela[1] += estrela[2]

        if estrela[1] > ALTURA:
            estrela[1] = 0
            estrela[0] = random.randint(0, LARGURA)

        brilho = 100 + (estrela[2] * 50)

        r = min(brilho, 255)
        g = min(brilho, 255)
        b = min(brilho + 20, 255)

        pygame.draw.circle(
            tela,
            (r, g, b),
            (estrela[0], estrela[1]),
            estrela[2]
        )


        # Garante que o brilho nunca ultrapasse 255 (limite máximo do RGB do Pygame)
        brilho = 100 + (estrela[2] * 50)
        r = min(brilho, 255)
        g = min(brilho, 255)
        b = min(brilho + 20, 255)

        pygame.draw.circle(tela, (r, g, b), (estrela[0], estrela[1]), estrela[2])



# SISTEMA DE ÁUDIO
def criar_som_bip(frequencia, duracao):
    taxa_amostragem = 22050
    n_amostras = int(taxa_amostragem * duracao)
    buffer = bytearray()
    for i in range(n_amostras):
        t = i / taxa_amostragem
        valor = int(32767 * 0.5 * math.sin(2 * math.pi * frequencia * t))
        buffer += valor.to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer=buffer)


som_tiro = criar_som_bip(440, 0.05)
som_hit_boss = criar_som_bip(200, 0.08)
som_dano = criar_som_bip(100, 0.15)


def aplicar_volumes():
    som_tiro.set_volume(volume_sfx)
    som_hit_boss.set_volume(volume_sfx)
    som_dano.set_volume(volume_sfx)
    pygame.mixer.music.set_volume(volume_musica)

def tocar_musica(caminho):
    if getattr(sys, 'frozen', False):
        caminho = os.path.join(sys._MEIPASS, caminho)
    else:
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), caminho)

    pygame.mixer.music.load(caminho)
    pygame.mixer.music.set_volume(volume_musica)
    pygame.mixer.music.play(-1)

def desenhar_opcao_minimalista(texto, x, y, mouse_pos):
    txt_base = fonte_menu.render(texto, True, (180, 180, 200))
    ret = txt_base.get_rect(topleft=(x, y))

    if ret.collidepoint(mouse_pos):
        txt_hover = fonte_menu.render(f"> {texto}", True, AZUL_NAVE)
        tela.blit(txt_hover, (x - 10, y))
    else:
        tela.blit(txt_base, (x, y))

    return ret


def desenhar_botao_pequeno(texto, x, y, largura, altura, mouse_pos):
    ret = pygame.Rect(x, y, largura, altura)
    cor = COR_BOTAO_HOVER if ret.collidepoint(mouse_pos) else COR_BOTAO
    pygame.draw.rect(tela, cor, ret, border_radius=6)
    pygame.draw.rect(tela, (200, 200, 220), ret, 1, border_radius=6)

    txt = fonte.render(texto, True, (255, 255, 255))
    tela.blit(txt, txt.get_rect(center=ret.center))
    return ret

# TELA DE OPÇÕES
def tela_opcoes():
    global volume_musica, volume_sfx
    aplicar_volumes()


    while True:
        mouse_pos = pygame.mouse.get_pos()
        clique = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clique = True

        atualizar_e_desenhar_wallpaper()

        titulo = fonte_titulo.render("OPÇÕES", True, (255, 100, 200))
        tela.blit(titulo, (70, 80))

        # Volume Música
        txt_m = fonte.render("Música de Fundo", True, (220, 220, 230))
        tela.blit(txt_m, (70, 200))
        txt_vol_m = fonte.render(f"{int(volume_musica * 100)}%", True, AZUL_NAVE)
        tela.blit(txt_vol_m, (300, 200))
        btn_mus_menos = desenhar_botao_pequeno("-", 370, 193, 36, 36, mouse_pos)
        btn_mus_mais = desenhar_botao_pequeno("+", 415, 193, 36, 36, mouse_pos)

        # Volume SFX
        txt_s = fonte.render("Efeitos Sonoros (SFX)", True, (220, 220, 230))
        tela.blit(txt_s, (70, 270))
        txt_vol_s = fonte.render(f"{int(volume_sfx * 100)}%", True, AZUL_NAVE)
        tela.blit(txt_vol_s, (300, 270))
        btn_sfx_menos = desenhar_botao_pequeno("-", 370, 263, 36, 36, mouse_pos)
        btn_sfx_mais = desenhar_botao_pequeno("+", 415, 263, 36, 36, mouse_pos)

        btn_voltar = desenhar_opcao_minimalista("VOLTAR", 70, 480, mouse_pos)

        if clique:
            if btn_mus_menos.collidepoint(mouse_pos):
                volume_musica = max(0.0, volume_musica - 0.1)
                aplicar_volumes()
            elif btn_mus_mais.collidepoint(mouse_pos):
                volume_musica = min(1.0, volume_musica + 0.1)
                aplicar_volumes()
            elif btn_sfx_menos.collidepoint(mouse_pos):
                volume_sfx = max(0.0, volume_sfx - 0.1)
                aplicar_volumes()
            elif btn_sfx_mais.collidepoint(mouse_pos):
                volume_sfx = min(1.0, volume_sfx + 0.1)
                aplicar_volumes()
            elif btn_voltar.collidepoint(mouse_pos):
                return
        pygame.display.flip()
        relogio.tick(60)

def transicao_fechar():
    fundo = tela.copy()
    duracao = 30

    for passo in range(duracao + 1):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        altura = int((ALTURA / 2) * (passo / duracao))

        tela.blit(fundo, (0, 0))

        pygame.draw.rect(tela, (0, 0, 0), (0, 0, LARGURA, altura))
        pygame.draw.rect(
            tela,
            (0, 0, 0),
            (0, ALTURA - altura, LARGURA, altura)
        )

        pygame.display.flip()
        relogio.tick(60)



# MENU PRINCIPAL
def menu_principal():
        tocar_musica("assets/music/menu.mp3")

        cliques_credito = 0

        # Cria as naves decorativas
        naves_menu = []

        for _ in range(5):
            naves_menu.append({
                "x": random.randint(0, LARGURA),
                "y": random.randint(0, ALTURA),
                "velocidade": random.uniform(1.0, 2.5),
                "desvio": random.uniform(-0.5, 0.5)
            })

        while True:
            mouse_pos = pygame.mouse.get_pos()
            clique = False

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    clique = True

            # Desenha o fundo
            atualizar_e_desenhar_wallpaper()

            # Movimento e desenho das naves
            for nave in naves_menu:
                nave["y"] -= nave["velocidade"]
                nave["x"] += nave["desvio"]

                if nave["y"] < -50:
                    nave["y"] = ALTURA + random.randint(20, 150)
                    nave["x"] = random.randint(0, LARGURA)
                    nave["velocidade"] = random.uniform(1.0, 2.5)
                    nave["desvio"] = random.uniform(-0.5, 0.5)

                if nave["x"] < -40:
                    nave["x"] = LARGURA + 30
                elif nave["x"] > LARGURA + 40:
                    nave["x"] = -30

                tela.blit(
                    nave_menu_img,
                    (int(nave["x"]), int(nave["y"]))
                )

            # Título
            titulo = fonte_titulo.render("TOUHOU", True, (255, 100, 200))
            subtitulo = fonte.render(
                "BULLET HELL PROJECT - LPA",
                True,
                (150, 150, 180)
            )

            tela.blit(titulo, (70, 100))
            tela.blit(subtitulo, (72, 152))

            # Botões
            btn_jogar = desenhar_opcao_minimalista(
                "JOGAR", 70, 360, mouse_pos
            )

            btn_god = desenhar_opcao_minimalista(
                "MODO FÁCIL", 70, 415, mouse_pos
            )

            btn_opcoes = desenhar_opcao_minimalista(
                "OPÇÕES", 70, 470, mouse_pos
            )
            txt_mortes = fonte.render(
                f"Mortes: {contador_mortes}",
                True,
                (120, 120, 140)
            )
            tela.blit(txt_mortes, (70, 550))

            txt_credito = fonte.render(
                "Feito por: João Vitor",
                True,
                (120, 120, 140)
            )

            rect_credito = txt_credito.get_rect(
                bottomright=(LARGURA - 20, ALTURA - 15)
            )

            tela.blit(txt_credito, rect_credito)

            # Verificação dos cliques
            if clique:
                if rect_credito.collidepoint(mouse_pos):
                    cliques_credito += 1

                    if cliques_credito >= 3:
                        transicao_fechar()
                        jogar_partida(modo="teste")
                        tocar_musica("assets/music/menu.mp3")
                        cliques_credito = 0

                if btn_jogar.collidepoint(mouse_pos):
                    transicao_fechar()
                    jogar_partida(modo="normal")
                    tocar_musica("assets/music/menu.mp3")

                elif btn_god.collidepoint(mouse_pos):
                    transicao_fechar()
                    jogar_partida(modo="facil")
                    tocar_musica("assets/music/menu.mp3")

                elif btn_opcoes.collidepoint(mouse_pos):
                    tela_opcoes()

            pygame.display.flip()
            relogio.tick(60)


def desenhar_caixa_resultado(titulo, mensagem, cor):
    largura = 500
    altura = 180

    x = (LARGURA - largura) // 2
    y = (ALTURA - altura) // 2

    caixa = pygame.Surface((largura, altura), pygame.SRCALPHA)

    # Fundo escuro transparente
    pygame.draw.rect(
        caixa, (15, 10, 30, 235),
        (0, 0, largura, altura),
        border_radius=18
    )

    # Borda externa
    pygame.draw.rect(
        caixa, (*cor, 255),
        (0, 0, largura, altura),
        width=3,
        border_radius=18
    )

    # Linha decorativa
    pygame.draw.line(
        caixa, (*cor, 180),
        (30, 65), (largura - 30, 65), 2
    )

    tela.blit(caixa, (x, y))

    texto_titulo = fonte_titulo.render(titulo, True, cor)
    tela.blit(
        texto_titulo,
        texto_titulo.get_rect(center=(LARGURA // 2, y + 45))
    )

    texto_mensagem = fonte.render(mensagem, True, (230, 230, 240))
    tela.blit(
        texto_mensagem,
        texto_mensagem.get_rect(center=(LARGURA // 2, y + 105))
    )

    texto_voltar = fonte.render(
        "Pressione R para voltar ao menu",
        True, (150, 180, 220)
    )
    tela.blit(
        texto_voltar,
        texto_voltar.get_rect(center=(LARGURA // 2, y + 145))
    )

# ---------------------------------------------------------
# LOOP DA PARTIDA
# ---------------------------------------------------------

def jogar_partida(modo="normal"):
    global contador_mortes

    if modo == "facil":
        tocar_musica("assets/music/facil.mp3")
    else:
        tocar_musica("assets/music/boss.mp3")

    jogador = pygame.Rect(LARGURA // 2 - 12, ALTURA - 80, 24, 24)
    vel_jogador = 5
    tiros_jogador = []
    cooldown_tiro = 0

    vidas_jogador = 99 if modo == "facil" else 3

    invulneravel = False
    tempo_invulnerabilidade = 0
    DURACAO_INVULNERABILIDADE = 90

    modo_facil = modo == "facil"
    multiplicador_tiros = 0.85 if modo_facil else 1.0

    boss = pygame.Rect(LARGURA // 2 - 50, 50, 100, 60)
    vel_boss = 4.0
    vida_boss = 150
    vida_max_boss = 150
    tiros_boss = []
    cooldown_ataque_boss = 0

    particulas_boss = []
    explosao_boss = False
    tempo_explosao = 0

    boss_flash_timer = 0
    fase_boss = 1
    aviso_timer = 0
    estado_jogo = "jogando"

    while True:

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if estado_jogo != "jogando" and evento.key == pygame.K_r:
                    return

        # --- ANIMAÇÃO DA EXPLOSÃO ---
        if estado_jogo == "explodindo":
            tempo_explosao -= 1

            for particula in particulas_boss[:]:
                particula[0] += particula[2]
                particula[1] += particula[3]
                particula[5] -= 1

                if particula[5] <= 0:
                    particulas_boss.remove(particula)

            if tempo_explosao <= 0:
                estado_jogo = "vitoria"

        # --- JOGO NORMAL ---
        if estado_jogo == "jogando":

            if tempo_invulnerabilidade > 0:
                tempo_invulnerabilidade -= 1
            else:
                invulneravel = False

            teclas = pygame.key.get_pressed()

            if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and jogador.left > 0:
                jogador.x -= vel_jogador

            if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and jogador.right < LARGURA:
                jogador.x += vel_jogador

            if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and jogador.top > 0:
                jogador.y -= vel_jogador

            if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and jogador.bottom < ALTURA:
                jogador.y += vel_jogador

            if cooldown_tiro > 0:
                cooldown_tiro -= 1

            if teclas[pygame.K_SPACE] and cooldown_tiro == 0:
                tiros_jogador.append(pygame.Rect(jogador.centerx - 10, jogador.top, 4, 14))
                tiros_jogador.append(pygame.Rect(jogador.centerx + 6, jogador.top, 4, 14))
                cooldown_tiro = 7
                som_tiro.play()

            # Colisão dos tiros com o boss
            for tiro in tiros_jogador[:]:
                tiro.y -= 14

                if tiro.bottom < 0:
                    tiros_jogador.remove(tiro)

                elif tiro.colliderect(boss):
                    tiros_jogador.remove(tiro)
                    vida_boss -= 1.5
                    som_hit_boss.play()
                    boss_flash_timer = 6

                    if vida_boss <= 0:
                        vida_boss = 0
                        explosao_boss = True
                        estado_jogo = "explodindo"
                        tempo_explosao = 60

                        for _ in range(40):
                            angulo = random.uniform(0, 2 * math.pi)
                            velocidade = random.uniform(2, 7)

                            vx = math.cos(angulo) * velocidade
                            vy = math.sin(angulo) * velocidade

                            particulas_boss.append([
                                boss.centerx,
                                boss.centery,
                                vx, vy,
                                random.randint(3, 7),
                                random.randint(20, 60)
                            ])

            # Mudança de fase do boss
            if vida_boss <= 75 and fase_boss == 1:
                fase_boss = 2
                vel_boss = 5.0
                aviso_timer = 120

            if aviso_timer > 0:
                aviso_timer -= 1

            boss.x += vel_boss

            if boss.right >= LARGURA - 20:
                boss.right = LARGURA - 20
                vel_boss = -abs(vel_boss)

            elif boss.left <= 20:
                boss.left = 20
                vel_boss = abs(vel_boss)

            cooldown_ataque_boss += 1

            # Ataques da fase 1
            if fase_boss == 1:
                if cooldown_ataque_boss >= 35:
                    cooldown_ataque_boss = 0
                    quantidade = 5 if modo_facil else 7

                    for i in range(quantidade):
                        angulo = (i - (quantidade - 1) / 2) * 0.22
                        vx = math.sin(angulo) * 4 * multiplicador_tiros
                        vy = math.cos(angulo) * 4 * multiplicador_tiros

                        tiros_boss.append([
                            pygame.Rect(boss.centerx - 6, boss.bottom, 12, 12),
                            vx, vy, 1
                        ])

            # Ataques da fase 2
            elif fase_boss == 2:
                if cooldown_ataque_boss >= 30:
                    cooldown_ataque_boss = 0

                    # Leque de tiros
                    quantidade = 5 if modo_facil else 7

                    for i in range(quantidade):
                        angulo = (i - (quantidade - 1) / 2) * 0.22
                        vx = math.sin(angulo) * 4.5 * multiplicador_tiros
                        vy = math.cos(angulo) * 4.5 * multiplicador_tiros

                        tiros_boss.append([
                            pygame.Rect(boss.centerx - 6, boss.bottom, 12, 12),
                            vx, vy, 1
                        ])

                    # Tiros radiais
                    num_tiros = 7 if modo_facil else 10

                    for i in range(num_tiros):
                        angulo = i * (2 * math.pi / num_tiros)
                        vx = math.cos(angulo) * 3.5
                        vy = math.sin(angulo) * 3.5

                        tiros_boss.append([
                            pygame.Rect(boss.centerx - 5, boss.centery - 5, 10, 10),
                            vx, vy, 2
                        ])

            # Movimento dos tiros do boss
            for item in tiros_boss[:]:
                t_rect, vx, vy, tipo = item

                t_rect.x += vx
                t_rect.y += vy

                if (t_rect.top > ALTURA or t_rect.bottom < 0
                        or t_rect.left < 0 or t_rect.right > LARGURA):
                    tiros_boss.remove(item)

                elif jogador.collidepoint(t_rect.center):
                    tiros_boss.remove(item)

                    if modo != "teste" and not invulneravel:
                        vidas_jogador -= 1
                        som_dano.play()
                        invulneravel = True
                        tempo_invulnerabilidade = DURACAO_INVULNERABILIDADE

                        if vidas_jogador <= 0:
                            estado_jogo = "game_over"
                            contador_mortes += 1
                            pygame.mixer.music.fadeout(1200)

            # Atualização do efeito de dano
            if boss_flash_timer > 0:
                boss_flash_timer -= 1

            # --- DESENHO DO JOGO ---
            atualizar_e_desenhar_wallpaper()

            if not invulneravel or (tempo_invulnerabilidade // 6) % 2 == 0:
                tela.blit(
                    nave_img,
                    nave_img.get_rect(center=jogador.center)
                )

            for tiro in tiros_jogador:
                pygame.draw.rect(tela, AMARELO_TIRO, tiro, border_radius=2)

            for item in tiros_boss:
                t_rect, _, _, tipo = item

                if tipo == 1:
                    pygame.draw.ellipse(tela, VERMELHO_TIRO, t_rect)
                else:
                    pygame.draw.circle(tela, AZUL_CLARO_TIRO, t_rect.center, 6)


            # Boss com efeito de dano e mudança de cor por fase
            if boss_flash_timer > 0:
                imagem_boss_atual = boss_img_branco
            elif fase_boss == 2:
                imagem_boss_atual = boss_img_fase2
            else:
                imagem_boss_atual = boss_img

            tela.blit(
                imagem_boss_atual,
                imagem_boss_atual.get_rect(center=boss.center)
            )

            # Barra de vida
            pygame.draw.rect(tela, VERMELHO_VIDA, (200, 15, 400, 15))
            largura_atual = int(400 * (vida_boss / vida_max_boss))
            pygame.draw.rect(tela, VERDE_VIDA, (200, 15, largura_atual, 15))

            display_vidas = "∞" if modo == "teste" else str(vidas_jogador)
            texto_vidas = fonte.render(f"Vidas: {display_vidas}", True, AZUL_NAVE)
            tela.blit(texto_vidas, (20, 15))

            texto_fase = fonte.render(f"FASE {fase_boss}", True, (255, 255, 100))
            tela.blit(texto_fase, (680, 15))

            if aviso_timer > 0:
                texto_aviso = fonte_aviso.render(
                    "SPELL CARD: INFERNO DE BALAS ATIVADO!",
                    True, (255, 100, 100)
                )
                tela.blit(texto_aviso, texto_aviso.get_rect(center=(LARGURA // 2, 120)))

        # --- DESENHO DA EXPLOSÃO ---
        elif estado_jogo == "explodindo":
            atualizar_e_desenhar_wallpaper()

            for particula in particulas_boss:
                x, y = int(particula[0]), int(particula[1])
                tamanho = particula[4]

                pygame.draw.circle(
                    tela,
                    (255, 180, 50),
                    (x, y),
                    tamanho
                )

        # --- TELAS DE RESULTADO ---
        if estado_jogo == "vitoria":
            atualizar_e_desenhar_wallpaper()
            desenhar_caixa_resultado(
                "VICTORY!",
                "Boss derrotado!",
                VERDE_VIDA
            )

        elif estado_jogo == "game_over":
            atualizar_e_desenhar_wallpaper()
            desenhar_caixa_resultado(
                "GAME OVER",
                "Voce foi derrotado!",
                VERMELHO_VIDA
            )

        # Atualização da tela em todos os estados
        pygame.display.flip()
        relogio.tick(60)


menu_principal()