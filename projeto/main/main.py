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

    while rodando:
        tela.blit(fundo_atual, (0, 0))  # Aplica o fundo atual conforme a dificuldade

        texto = fonte.render(f"Nível: {dificuldade.upper()}", True, PRETO)
        tela.blit(texto, (0,0))

        for evento in py.event.get():
            if evento.type == py.QUIT:
                rodando = False

        py.display.update()
        clock.tick(60)

    py.quit()

# Inicia o jogo
if __name__ == "__main__":
    main()