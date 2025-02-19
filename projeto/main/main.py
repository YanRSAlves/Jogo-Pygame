import pygame as py
import random
import time

py.init()

# Configurações da tela
LARGURA, ALTURA = 600, 400
tela = py.display.set_mode((LARGURA, ALTURA))
py.display.set_caption("CORRE! DINO lvls")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
TRANSPARENTE = (0, 0, 0, 0)  # Totalmente transparente

# Fonte
fonte = py.font.Font(None, 36)

# Função para carregar e redimensionar imagens
def carregar_imagem(caminho, largura=LARGURA, altura=ALTURA):
    imagem = py.image.load(caminho)
    return py.transform.scale(imagem, (largura, altura))

# ======== CARREGAMENTO DE MÍDIAS ========
fundo_menu = carregar_imagem("fundos/corre-dino.png", 600, 400)
tela_game_over = carregar_imagem("fundos/game-over.png", 600, 400)
icone_facil = carregar_imagem("fundos/1estrela.jpg", 80, 80)
icone_medio = carregar_imagem("fundos/2estrela.jpg", 80, 80)
icone_dificil = carregar_imagem("fundos/3esstrela.jpg", 80, 80)

dino_correndo = py.image.load("Dinos/male/cole/base/move.png")  # Sprite de corrida
dino_pulando = py.image.load("Dinos/male/cole/base/jump.png")  # Sprite de pulo

# Sons
som_clique = py.mixer.Sound("Musicas/smw_1-up.wav")

# Posições dos botões
botao_facil = py.Rect(100, 200, 80, 80)
botao_medio = py.Rect(260, 200, 80, 80)
botao_dificil = py.Rect(420, 200, 80, 80)


# Obstáculos (Árvores)
arvores = []
obstaculos = []

# Função para carregar e cortar as árvores
def carregar_arvores():
    imagem = py.image.load("fundos/arvores/AnimatedAutum.png")
    for i in range(16):
        arvore = imagem.subsurface(i * 64, 0, 64, 64)  # Cortando a imagem das árvores
        arvores.append(arvore)

# Carregar as árvores
carregar_arvores()

# Função para criar um obstáculo evitando sequências diretas
def gerar_obstaculo():
    if not obstaculos or obstaculos[-1].x < LARGURA - 200:
        x = random.randint(LARGURA, LARGURA + 300)
        y = ALTURA - 84
        obstaculos.append(py.Rect(x, y, 64, 64))

# Função para desenhar obstáculos
def desenhar_obstaculos():
    for obs in obstaculos:
        arvore = random.choice(arvores)  # Escolher aleatoriamente uma árvore
        tela.blit(arvore, (obs.x, obs.y))

# Função para atualizar a posição dos obstáculos
def mover_obstaculos(dificuldade):
    velocidade = 4
    if dificuldade == "medio":
        velocidade = 6
    elif dificuldade == "dificil":
        velocidade = 9

    for obs in obstaculos:
        obs.x -= velocidade
    if obstaculos and obstaculos[0].x < -64:
        obstaculos.pop(0)
    gerar_obstaculo()

# Função para carregar o chão
def carregar_chao():
    chao_imagem = py.image.load("fundos/5.png")
    chao = py.transform.scale(chao_imagem, (LARGURA, 180))  # Redimensiona para largura total da tela
    return chao

# Carregar a imagem do chão
chao_imagem = carregar_chao()

# Função para desenhar o chão
def desenhar_chao():
    tela.blit(chao_imagem, (0, ALTURA - 180))  # Desenha o chão na parte inferior da tela

# Função para verificar clique nos botões
def verificar_click(posicao):
    if botao_facil.collidepoint(posicao):
        som_clique.play()
        return "facil"
    if botao_medio.collidepoint(posicao):
        som_clique.play()
        return "medio"
    if botao_dificil.collidepoint(posicao):
        som_clique.play()
        return "dificil"
    return None

# Função para exibir a tela de seleção
def escolher_dificuldade():
    while True:
        tela.blit(fundo_menu, (0, 0))
        tela.blit(icone_facil, botao_facil.topleft)
        tela.blit(icone_medio, botao_medio.topleft)
        tela.blit(icone_dificil, botao_dificil.topleft)
        py.display.update()

        for evento in py.event.get():
            if evento.type == py.QUIT:
                py.quit()
            if evento.type == py.MOUSEBUTTONDOWN:
                dificuldade = verificar_click(evento.pos)
                if dificuldade:
                    return dificuldade

# Classe do Dino
class Dino:
    def __init__(self):
        self.x, self.y = 50, ALTURA - 64
        self.vel_y = 0
        self.vel_x = 0  # Velocidade horizontal
        self.pulando = False
        self.gravidade = 0.5
        self.velocidade = 5  # Velocidade de movimentação
        self.sprite_index = 0
        self.sprites_corrida = [dino_correndo.subsurface((i * 24, 0, 24, 24)) for i in range(6)]
        self.sprites_pulo = [dino_pulando.subsurface((i * 24, 0, 24, 24)) for i in range(4)]
        self.imagem = self.sprites_corrida[0]

    def pular(self):
        if not self.pulando:
            self.pulando = True
            self.vel_y = -10

    def mover(self, tecla):
        if tecla == py.K_a or tecla == py.K_LEFT:  # Movimentar para a esquerda
            self.vel_x = -self.velocidade
        elif tecla == py.K_d or tecla == py.K_RIGHT:  # Movimentar para a direita
            self.vel_x = self.velocidade
        elif tecla == py.K_w or tecla == py.K_UP:  # Movimentar para cima
            if not self.pulando:
                self.pular()
        elif tecla == py.K_s or tecla == py.K_DOWN:  # Movimentar para baixo (Cair mais rápido ou agachar)
            self.y += 5

    def parar(self):
        self.vel_x = 0  # Quando a tecla for solta, o Dino para de se mover horizontalmente

    def atualizar(self):
        self.x += self.vel_x  # Atualizando a posição horizontal com base na velocidade
        if self.pulando:
            self.vel_y += self.gravidade
            self.y += self.vel_y
            if self.y >= ALTURA - 64:
                self.y = ALTURA - 64
                self.pulando = False
            self.sprite_index = (self.sprite_index + 1) % 4
            self.imagem = self.sprites_pulo[self.sprite_index]
        else:
            # Diminuindo a velocidade da animação
            self.sprite_index = (self.sprite_index + 1) % 6
            self.imagem = self.sprites_corrida[self.sprite_index]

    def desenhar(self):
        tela.blit(self.imagem, (self.x, self.y))

    def colisao(self):
        dino_rect = py.Rect(self.x, self.y, 24, 24)
        for obs in obstaculos:
            if dino_rect.colliderect(obs):
                return True
        return False

# Função para exibir a tela de "Game Over"
def exibir_game_over():
    tela.blit(tela_game_over, (0, 0))
    texto = "(M) Menu (F) Fechar o Jogo"
    texto_renderizado = ""
    for char in texto:
        texto_renderizado += char
        tela.blit(fonte.render(texto_renderizado, True, PRETO), (LARGURA // 2 - 150, ALTURA // 8))
        py.display.update()
        py.time.delay(50)

    while True:
        for evento in py.event.get():
            if evento.type == py.QUIT:
                py.quit()
                return None
            if evento.type == py.KEYDOWN:
                if evento.key == py.K_m:
                    return 'menu'
                elif evento.key == py.K_f:
                    return 'fechar'

# Função para rodar o jogo
def jogo():
    while True:
        dificuldade = escolher_dificuldade()
        if not dificuldade:
            return

        if dificuldade == "facil":
            fundo_atual = carregar_imagem("fundos/bosque/1280x720/2.jpg")
        elif dificuldade == "medio":
            fundo_atual = carregar_imagem("fundos/fundo-glacial.png")
        else:
            fundo_atual = carregar_imagem("fundos/bosque/1280x720/1.jpg")

        dino = Dino()
        clock = py.time.Clock()
        obstaculos.clear()
        gerar_obstaculo()
        tempo_inicio = time.time()

        while True:
            tela.blit(fundo_atual, (0, 0))
            desenhar_chao()  # Desenha o chão sem variações
            dino.atualizar()
            dino.desenhar()
            mover_obstaculos(dificuldade)
            desenhar_obstaculos()

            tempo_jogo = int(time.time() - tempo_inicio)
            texto_tempo = fonte.render(f"Tempo: {tempo_jogo}s | Nível: {dificuldade}", True, PRETO)
            tela.blit(texto_tempo, (10, 10))

            if dino.colisao():
                opcao = exibir_game_over()
                if opcao == 'menu':
                    break  # Reinicia o jogo
                elif opcao == 'fechar':
                    return  # Retorna ao menu principal

            for evento in py.event.get():
                if evento.type == py.QUIT:
                    py.quit()
                    return
                if evento.type == py.KEYDOWN:
                    if evento.key == py.K_SPACE:
                        dino.pular()
                    else:
                        dino.mover(evento.key)
                if evento.type == py.KEYUP:
                    if evento.key in [py.K_a, py.K_d, py.K_w, py.K_s]:
                        dino.parar()

            py.display.update()
            clock.tick(60)

# Inicia o jogo
if __name__ == "__main__":
    jogo()