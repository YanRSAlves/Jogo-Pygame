import pygame as py
import random
import time
import os
import json

py.init()

# Configurar o diretório base para os recursos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações da tela
LARGURA, ALTURA = 600, 400
tela = py.display.set_mode((LARGURA, ALTURA))
py.display.set_caption("CORRE! DINO lvls")
clock = py.time.Clock()

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# Fonte
fonte = py.font.Font(None, 36)

# Função para carregar e redimensionar imagens
def carregar_imagem(caminho, largura=LARGURA, altura=ALTURA):
    caminho_completo = os.path.join(BASE_DIR, caminho)
    try:
        imagem = py.image.load(caminho_completo).convert_alpha()
        return py.transform.scale(imagem, (largura, altura))
    except Exception as e:
        print(f"Erro ao carregar a imagem {caminho_completo}: {e}")
        return None

# ======== CARREGAMENTO DE MÍDIAS ========
fundo_menu = carregar_imagem("fundos/corre-dino.png", 600, 400)
tela_game_over = carregar_imagem("fundos/game-over.png", 600, 400)
icone_facil = carregar_imagem("fundos/1estrela.jpg", 80, 80)
icone_medio = carregar_imagem("fundos/2estrela.jpg", 80, 80)
icone_dificil = carregar_imagem("fundos/3estrela.jpg", 80, 80)

# Carregamento dos sprites do dinossauro
try:
    dino_correndo = py.image.load(os.path.join(BASE_DIR, "Dinos/move.png")).convert_alpha()
    dino_pulando = py.image.load(os.path.join(BASE_DIR, "Dinos/jump.png")).convert_alpha()
except Exception as e:
    print(f"Erro ao carregar sprites do dinossauro: {e}")
    py.quit()
    exit(1)

# Sons
try:
    som_clique = py.mixer.Sound(os.path.join(BASE_DIR, "Musicas/smw_1-up.wav"))
    som_pulo = py.mixer.Sound(os.path.join(BASE_DIR, "Musicas/jump.wav"))
    som_power_up = py.mixer.Sound(os.path.join(BASE_DIR, "Musicas/powerup.wav"))
    som_morte = py.mixer.Sound(os.path.join(BASE_DIR, "Musicas/death.wav"))
except Exception as e:
    print(f"Erro ao carregar sons: {e}")
    # Criar sons vazios para evitar erros
    som_clique = py.mixer.Sound(py.mixer.Sound.get_length())
    som_pulo = py.mixer.Sound(py.mixer.Sound.get_length())
    som_power_up = py.mixer.Sound(py.mixer.Sound.get_length())
    som_morte = py.mixer.Sound(py.mixer.Sound.get_length())

# Posições dos botões
botao_facil = py.Rect(100, 250, 80, 80)
botao_medio = py.Rect(260, 250, 80, 80)
botao_dificil = py.Rect(420, 250, 80, 80)

# Lista global de obstáculos
obstaculos = []

# Sistema de Power-ups
class PowerUp:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x = x
        self.y = y
        self.ativo = True
        self.duracao = 5
        self.tempo_ativo = 0
        self.cor = AZUL if tipo == 'velocidade' else VERDE if tipo == 'invencibilidade' else VERMELHO

class SistemaPowerUp:
    def __init__(self):
        self.power_ups = []
        self.tempo_desde_ultimo = 0
        self.intervalo_spawn = 10
    
    def gerar_power_up(self):
        tipos = ['velocidade', 'invencibilidade', 'pulo_duplo']
        tipo = random.choice(tipos)
        x = LARGURA + 50
        y = random.randint(ALTURA - 180, ALTURA - 100)
        self.power_ups.append(PowerUp(tipo, x, y))
    
    def atualizar(self, dino, dt):
        for power_up in self.power_ups[:]:
            power_up.x -= 300 * dt
            if power_up.x < -50:
                self.power_ups.remove(power_up)
                continue
            if self.verificar_colisao(power_up, dino):
                self.aplicar_efeito(power_up, dino)
                som_power_up.play()
                self.power_ups.remove(power_up)
        
        self.tempo_desde_ultimo += dt
        if self.tempo_desde_ultimo >= self.intervalo_spawn:
            self.gerar_power_up()
            self.tempo_desde_ultimo = 0
    
    def verificar_colisao(self, power_up, dino):
        dino_rect = py.Rect(dino.x, dino.y, 24, 24)
        power_up_rect = py.Rect(power_up.x, power_up.y, 20, 20)
        return dino_rect.colliderect(power_up_rect)
    
    def aplicar_efeito(self, power_up, dino):
        dino.aplicar_efeito(power_up.tipo, power_up.duracao)
    
    def desenhar(self, tela):
        for power_up in self.power_ups:
            py.draw.circle(tela, power_up.cor, (int(power_up.x), int(power_up.y)), 10)

# Sistema de Recordes
class SistemaRecordes:
    def __init__(self):
        self.arquivo_recordes = os.path.join(BASE_DIR, "recordes.json")
        self.recordes = self.carregar_recordes()
    
    def carregar_recordes(self):
        try:
            with open(self.arquivo_recordes, 'r') as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            return {"facil": 0, "medio": 0, "dificil": 0}
    
    def salvar_recordes(self):
        with open(self.arquivo_recordes, 'w') as arquivo:
            json.dump(self.recordes, arquivo)
    
    def verificar_recorde(self, pontos, dificuldade):
        if pontos > self.recordes[dificuldade]:
            self.recordes[dificuldade] = pontos
            self.salvar_recordes()
            return True
        return False
    
    def mostrar_recordes(self, tela):
        y = 50
        for dificuldade, pontos in self.recordes.items():
            texto = f"Recorde {dificuldade}: {pontos}"
            superficie = fonte.render(texto, True, BRANCO)
            tela.blit(superficie, (LARGURA - 220, y))
            y += 30

# Classe do Dino melhorada
class Dino:
    def __init__(self):
        self.x = 50
        self.y = ALTURA - 64
        self.vel_x = 0
        self.vel_y = 0
        self.pulando = False
        self.gravidade = 1800
        self.jump_velocity = -600
        self.mov_vel = 300
        self.sprite_index = 0
        self.sprites_corrida = [dino_correndo.subsurface((i * 24, 0, 24, 24)).convert_alpha() for i in range(6)]
        self.sprites_pulo = [dino_pulando.subsurface((i * 24, 0, 24, 24)).convert_alpha() for i in range(4)]
        self.imagem = self.sprites_corrida[0]
        self.anim_timer = 0
        self.pontos = 0
        self.ultimo_obstaculo = None
        
        # Novos atributos
        self.invencivel = False
        self.tempo_invencivel = 0
        self.pulos_disponiveis = 1
        self.velocidade_original = self.mov_vel
        self.efeitos_ativos = {}

    def pular(self):
        if self.pulos_disponiveis > 0:
            self.pulando = True
            self.vel_y = self.jump_velocity
            self.pulos_disponiveis -= 1
            som_pulo.play()

    def mover(self, tecla):
        if tecla in [py.K_a, py.K_LEFT]:
            self.vel_x = -self.mov_vel
        elif tecla in [py.K_d, py.K_RIGHT]:
            self.vel_x = self.mov_vel
        elif tecla in [py.K_w, py.K_UP, py.K_SPACE]:
            self.pular()
        elif tecla in [py.K_s, py.K_DOWN]:
            if self.pulando:
                self.vel_y += self.gravidade * 0.05

    def parar(self):
        self.vel_x = 0

    def atualizar(self, dt):
        self.x += self.vel_x * dt

        if self.pulando:
            self.vel_y += self.gravidade * dt
            self.y += self.vel_y * dt
            if self.y >= ALTURA - 64:
                self.y = ALTURA - 64
                self.pulando = False
                self.vel_y = 0
                self.pulos_disponiveis = 1

        # Atualiza a animação
        self.anim_timer += dt
        if self.pulando:
            if self.anim_timer >= 0.1:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites_pulo)
                self.imagem = self.sprites_pulo[self.sprite_index]
                self.anim_timer = 0
        else:
            if self.anim_timer >= 0.1:
                self.sprite_index = (self.sprite_index + 1) % len(self.sprites_corrida)
                self.imagem = self.sprites_corrida[self.sprite_index]
                self.anim_timer = 0

        # Atualiza efeitos dos power-ups
        for efeito, tempo in list(self.efeitos_ativos.items()):
            self.efeitos_ativos[efeito] -= dt
            if self.efeitos_ativos[efeito] <= 0:
                self.remover_efeito(efeito)

        # Atualiza pontuação
        for obs in obstaculos:
            if obs.x + 64 < self.x and (self.ultimo_obstaculo is None or obs != self.ultimo_obstaculo):
                self.pontos += 1
                self.ultimo_obstaculo = obs

    def aplicar_efeito(self, tipo, duracao):
        self.efeitos_ativos[tipo] = duracao
        
    def remover_efeito(self, tipo):
        if tipo == 'velocidade':
            self.mov_vel = self.velocidade_original
        elif tipo == 'invencibilidade':
            self.invencivel = False
        elif tipo == 'pulo_duplo':
            self.pulos_disponiveis = 1
        self.efeitos_ativos.pop(tipo, None)

    def desenhar(self):
        if self.invencivel:
            if int(py.time.get_ticks() / 100) % 2 == 0:
                tela.blit(self.imagem, (self.x, self.y))
        else:
            tela.blit(self.imagem, (self.x, self.y))

    def colisao(self):
        if self.invencivel:
            return False
        dino_rect = py.Rect(self.x, self.y, 24, 24)
        for obs in obstaculos:
            if dino_rect.colliderect(obs):
                return True
        return False

# Obstáculos e funções de jogo existentes
arvores = []

def carregar_arvores():
    caminho_arvores = os.path.join(BASE_DIR, "fundos/arvores/arvore.png")
    imagem = py.image.load(caminho_arvores).convert_alpha()
    for i in range(16):
        arvore = imagem.subsurface(i * 64, 0, 64, 64)
        arvores.append(arvore)

carregar_arvores()

def gerar_obstaculo():
    if not obstaculos or obstaculos[-1].x < LARGURA - 200:
        x = random.randint(LARGURA, LARGURA + 300)
        y = ALTURA - 84
        obstaculos.append(py.Rect(x, y, 64, 64))

def desenhar_obstaculos():
    for obs in obstaculos:
        arvore = random.choice(arvores)
        tela.blit(arvore, (obs.x, obs.y))

def mover_obstaculos(dificuldade, dt):
    velocidades = {
        "facil": 240,
        "medio": 360,
        "dificil": 540
    }
    velocidade = velocidades[dificuldade]
    for obs in obstaculos:
        obs.x -= velocidade * dt
    if obstaculos and obstaculos[0].x < -64:
        obstaculos.pop(0)
    gerar_obstaculo()

def carregar_chao():
    caminho_chao = os.path.join(BASE_DIR, "fundos/caminho_chao.png")
    chao_imagem = py.image.load(caminho_chao).convert_alpha()
    return py.transform.scale(chao_imagem, (LARGURA, 180))

chao_imagem = carregar_chao()

def desenhar_chao():
    tela.blit(chao_imagem, (0, ALTURA - 180))

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
                exit()
            if evento.type == py.MOUSEBUTTONDOWN:
                dificuldade = verificar_click(evento.pos)
                if dificuldade:
                    return dificuldade

def mostrar_novo_recorde(pontos, dificuldade):
    superficie = fonte.render(f"NOVO RECORDE: {pontos}!", True, BRANCO)
    tela.blit(superficie, (LARGURA // 2 - 200, ALTURA // 4))
    py.display.update()
    py.time.delay(2000)

def exibir_game_over(pontos):
    som_morte.play()
    tela.blit(tela_game_over, (0, 0))
    
    # Mostra a pontuação final
    texto_pontos = fonte.render(f"Pontuação Final: {pontos}", True, AZUL)
    tela.blit(texto_pontos, (LARGURA // 2 - 100, ALTURA // 4 - 80))
    
    mensagem = " (M) Menu (R) Recomeçar (F) Fechar o Jogo"
    for i in range(1, len(mensagem) + 1):
        texto_renderizado = fonte.render(mensagem[:i], True, VERMELHO)
        tela.blit(texto_renderizado, (LARGURA // 2 - 250, ALTURA // 8))
        py.display.update()
        py.time.delay(50)
    
    while True:
        for evento in py.event.get():
            if evento.type == py.QUIT:
                py.quit()
                exit()
            if evento.type == py.KEYDOWN:
                if evento.key == py.K_m:
                    return 'menu'
                elif evento.key == py.K_f:
                    return 'fechar'
                elif evento.key == py.K_r:
                    return 'recomecar'

def mostrar_status(dino, dificuldade):
    # Mostra pontuação atual
    texto_pontos = fonte.render(f"Pontos: {dino.pontos}", True, PRETO)
    tela.blit(texto_pontos, (10, 10))
    
    # Mostra nível de dificuldade
    texto_dificuldade = fonte.render(f"Nível: {dificuldade}", True, PRETO)
    tela.blit(texto_dificuldade, (10, 40))
    
    # Mostra power-ups ativos
    y = 70
    for efeito, tempo in dino.efeitos_ativos.items():
        texto_efeito = fonte.render(f"{efeito}: {tempo:.1f}s", True, AZUL)
        tela.blit(texto_efeito, (10, y))
        y += 30

def jogo():
    sistema_recordes = SistemaRecordes()
    
    while True:
        dificuldade = escolher_dificuldade()
        if not dificuldade:
            return

        # Carrega fundo de acordo com a dificuldade
        if dificuldade == "facil":
            fundo_atual = carregar_imagem("fundos/bosque/fundo-florestal.jpg")
        elif dificuldade == "medio":
            fundo_atual = carregar_imagem("fundos/bosque/fundo-glacial.png")
        else:
            fundo_atual = carregar_imagem("fundos/bosque/fundo-noturno.jpg")

        dino = Dino()
        sistema_power_ups = SistemaPowerUp()
        obstaculos.clear()
        
        # Cria o primeiro obstáculo
        primeiro_obstaculo = py.Rect(LARGURA + 200, ALTURA - 84, 64, 64)
        obstaculos.append(primeiro_obstaculo)

        pausado = False
        rodando = True
        
        while rodando:
            dt = clock.tick(60) / 1000.0
            
            for evento in py.event.get():
                if evento.type == py.QUIT:
                    py.quit()
                    exit()
                if evento.type == py.KEYDOWN:
                    if evento.key == py.K_p:
                        pausado = not pausado
                    elif evento.key == py.K_ESCAPE:
                        rodando = False
                    else:
                        dino.mover(evento.key)
                if evento.type == py.KEYUP:
                    if evento.key in [py.K_a, py.K_d, py.K_LEFT, py.K_RIGHT]:
                        dino.parar()

            if pausado:
                texto_pausa = fonte.render("PAUSADO", True, VERMELHO)
                tela.blit(texto_pausa, (LARGURA // 2 - 50, ALTURA // 2))
                py.display.update()
                continue

            # Atualiza o jogo
            tela.blit(fundo_atual, (0, 0))
            desenhar_chao()
            
            dino.atualizar(dt)
            mover_obstaculos(dificuldade, dt)
            sistema_power_ups.atualizar(dino, dt)
            
            # Desenha elementos
            desenhar_obstaculos()
            sistema_power_ups.desenhar(tela)
            dino.desenhar()
            mostrar_status(dino, dificuldade)
            sistema_recordes.mostrar_recordes(tela)

            if dino.colisao():
                # Verifica novo recorde
                if sistema_recordes.verificar_recorde(dino.pontos, dificuldade):
                    mostrar_novo_recorde(dino.pontos, dificuldade)
                
                opcao = exibir_game_over(dino.pontos)
                if opcao == 'menu':
                    break
                elif opcao == 'fechar':
                    return
                elif opcao == 'recomecar':
                    dino = Dino()
                    sistema_power_ups = SistemaPowerUp()
                    obstaculos.clear()
                    gerar_obstaculo()
                    continue

            py.display.update()

if __name__ == "__main__":
    jogo()