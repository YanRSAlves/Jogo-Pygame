import pygame as py

py.init()

# Configurações da tela
LARGURA, ALTURA = 600, 400
tela = py.display.set_mode((LARGURA, ALTURA))
py.display.set_caption("CORRE! DINO lvls")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# Fonte
fonte = py.font.Font(None, 36)


# Função para carregar e redimensionar imagens
def carregar_imagem(caminho, largura=LARGURA, altura=ALTURA):
    imagem = py.image.load(caminho)
    return py.transform.scale(imagem, (largura, altura))


# ======== CARREGAMENTO DE MÍDIAS ========
fundo_menu = carregar_imagem("fundos/corredino.png")
icone_facil = py.image.load("icons/1.png")
icone_medio = py.image.load("icons/2.png")
icone_dificil = py.image.load("icons/3.png")

# Sons
som_clique = py.mixer.Sound("Musicas/smw_1-up.wav")

# Posições dos botões
botao_facil = py.Rect(100, 200, 80, 80)
botao_medio = py.Rect(260, 200, 80, 80)
botao_dificil = py.Rect(420, 200, 80, 80)


# Função para desenhar os botões e verificar se há clique
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


# Classe para o Dinossauro (Sprite)
class Dino(py.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Carregar as imagens de animação (dividindo as imagens originais em partes)
        self.animacao_correndo = [
            self.cortar_imagem("Dinos/male/kuro/base/move.png", 0),  # Primeiro frame da animação
            self.cortar_imagem("Dinos/male/kuro/base/move.png", 1),  # Segundo frame da animação
            self.cortar_imagem("Dinos/male/kuro/base/move.png", 2)  # Terceiro frame da animação
        ]

        self.imagem_pulando = py.image.load("Dinos/male/kuro/base/jump.png")
        self.imagem_caindo = py.image.load("Dinos/male/kuro/base/dash.png")

        # Redimensionando para o tamanho do sprite
        self.animacao_correndo = [py.transform.scale(frame, (50, 50)) for frame in self.animacao_correndo]
        self.imagem_pulando = py.transform.scale(self.imagem_pulando, (50, 50))
        self.imagem_caindo = py.transform.scale(self.imagem_caindo, (50, 50))

        self.imagem = self.animacao_correndo[0]  # Inicializa com o primeiro frame da animação de corrida

        # Definindo a posição inicial do dinossauro
        self.rect = self.imagem.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Variáveis de controle do pulo
        self.velocidade_y = 0
        self.velocidade_x = 0  # Inicialmente, sem movimento horizontal
        self.no_chao = True
        self.gravidade = 0.5  # Acelerando a queda
        self.frame_atual = 0  # Controle de animação de movimento
        self.animacao_tempo = 0  # Timer para animar a corrida

    def cortar_imagem(self, caminho, indice):
        """
        Função para cortar a imagem 'move.png' em três frames (cada um com 48x24).
        """
        imagem = py.image.load(caminho)
        # Cortar a imagem em 3 partes
        return imagem.subsurface(py.Rect(indice * 48, 0, 48, 24))

    def update(self):
        # Aplica a gravidade
        if not self.no_chao:
            self.velocidade_y += self.gravidade  # A gravidade aumenta a velocidade de queda

        # Atualiza a animação do dinossauro
        if self.no_chao:
            # Animação de correr
            self.animacao_tempo += 1
            if self.animacao_tempo % 10 == 0:  # Muda a imagem a cada 10 quadros
                self.frame_atual = (self.frame_atual + 1) % len(self.animacao_correndo)
            self.imagem = self.animacao_correndo[self.frame_atual]
        else:
            self.imagem = self.imagem_pulando  # Imagem enquanto pula

        # Atualiza a posição do dinossauro
        self.rect.y += self.velocidade_y
        self.rect.x += self.velocidade_x  # Movimentação horizontal

        # Limitar a posição horizontal (não pode sair da tela)
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > LARGURA - self.rect.width:
            self.rect.x = LARGURA - self.rect.width

        # Limitar a posição vertical (não pode sair da tela)
        if self.rect.y < 0:  # Não pode sair pela parte superior
            self.rect.y = 0
        if self.rect.y >= ALTURA - 50:  # Chão
            self.rect.y = ALTURA - 50
            self.no_chao = True
            self.velocidade_y = 0

    def pular(self):
        if self.no_chao:
            self.velocidade_y = -15  # Ajuste para a altura do pulo
            self.no_chao = False

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)


# Função para exibir a tela de seleção com botões clicáveis
def escolher_dificuldade():
    rodando = True
    while rodando:
        tela.blit(fundo_menu, (0, 0))  # Aplica o fundo do menu

        # Desenha os botões
        tela.blit(icone_facil, botao_facil.topleft)
        tela.blit(icone_medio, botao_medio.topleft)
        tela.blit(icone_dificil, botao_dificil.topleft)

        py.display.update()

        for evento in py.event.get():
            if evento.type == py.QUIT:
                py.quit()
                return None
            if evento.type == py.MOUSEBUTTONDOWN:
                dificuldade = verificar_click(evento.pos)
                if dificuldade:
                    return dificuldade


# Função principal do jogo
def main():
    dificuldade = escolher_dificuldade()
    if not dificuldade:
        return  # Se o jogador fechou a tela, o jogo é encerrado

    clock = py.time.Clock()
    rodando = True

    # Definir o fundo com base na dificuldade
    if dificuldade == "facil":
        fundo_atual = carregar_imagem("fundos/bosque/1280x720/2.jpg")
    elif dificuldade == "medio":
        fundo_atual = carregar_imagem("fundos/fundo-glacial.png")
    else:
        fundo_atual = carregar_imagem("fundos/bosque/1280x720/1.jpg")

    # Criar o sprite do dinossauro
    dino = Dino(100, ALTURA - 50)  # Posição inicial do dinossauro

    while rodando:
        tela.blit(fundo_atual, (0, 0))  # Aplica o fundo atual conforme a dificuldade

        # Atualiza o sprite do dinossauro
        dino.update()
        dino.desenhar(tela)

        texto = fonte.render(f"Nível: {dificuldade.upper()}", True, PRETO)
        texto_rect = texto.get_rect(center=(LARGURA // 2, ALTURA // 4))  # Centraliza o texto
        tela.blit(texto, texto_rect)

        for evento in py.event.get():
            if evento.type == py.QUIT:
                rodando = False
            if evento.type == py.KEYDOWN:
                if evento.key == py.K_SPACE or evento.key == py.K_w:  # Tecla de pulo
                    dino.pular()
                if evento.key == py.K_LEFT or evento.key == py.K_a:  # Tecla de movimento para a esquerda
                    dino.velocidade_x = -5
                if evento.key == py.K_RIGHT or evento.key == py.K_d:  # Tecla de movimento para a direita
                    dino.velocidade_x = 5
            if evento.type == py.KEYUP:
                if evento.key == py.K_LEFT or evento.key == py.K_RIGHT or evento.key == py.K_a or evento.key == py.K_d:  # Para o movimento quando a tecla for solta
                    dino.velocidade_x = 0

        py.display.update()
        clock.tick(60)

    py.quit()


# Inicia o jogo
if __name__ == "__main__":
    main()