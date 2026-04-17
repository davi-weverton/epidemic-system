from flask import Flask, render_template
from flask_socketio import SocketIO
import eventlet
import random
from simulation import Agente, calcular_infeccao
from ai_engine import IA_Sentinela

rodando = False
resetar_ia = True
treinando = False
perc_anterior = 0
BETA_ATUAL = 0.5
ALFA_ATUAL = 0.003
TETA_ATUAL = 0.99

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Configurações do Ambiente
LARGURA, ALTURA = 800, 600
POPULACAO_INICIAL = 100
agentes = [Agente(i, LARGURA, ALTURA) for i in range(POPULACAO_INICIAL)]

# Começa com 50 infectados conforme você pediu
for i in range(45):
    agentes[i].status = 1 

ia = IA_Sentinela()
mortes_no_ciclo = 0
contador_frames = 0
ultima_acao = 0 # Variável global para manter o estado da IA entre os frames

@app.route('/')
def index():
    return render_template('index.html')

def loop_simulacao():
    global mortes_no_ciclo, agentes, contador_frames, ultima_acao, perc_anterior, ALFA_ATUAL, BETA_ATUAL, TETA_ATUAL
    while rodando:
        if not agentes: 
            print("Simulação encerrada: todos os agentes morreram.")
            break

        num_infectados = sum(1 for a in agentes if a.status == 1)
        if num_infectados == 0:
            break

        contador_frames += 1
        num_infectados = sum(1 for a in agentes if a.status == 1)
        perc = num_infectados / len(agentes) if agentes else 0
        
        # A IA só decide e age a cada 10 rodadas
        delta = perc - perc_anterior
        perc_anterior = perc
        if contador_frames % 10 == 0:
            ultima_acao = ia.decidir_acao(perc, delta, ultima_acao == 1)
            ia.treinar(perc, delta, mortes_no_ciclo, ultima_acao == 1)
            mortes_no_ciclo = 0

            if ultima_acao == 1:
                candidatos = [a for a in agentes if not a.em_lockdown]
                if candidatos:
                    # 10% da população por vez
                    qtd = int(len(candidatos) * 0.10) 
                    for a in random.sample(candidatos, qtd):
                        a.em_lockdown = True
                        a.timer_lockdown = 50 

        # 4. Bio-Simulação
        calcular_infeccao(agentes, beta=BETA_ATUAL, raio=10)
        
        dados_envio = []
        for a in agentes[:]:
            a.mover(LARGURA, ALTURA, velocidade=2.0)
            
            estado = a.atualizar_saude(alfa=ALFA_ATUAL, teta=TETA_ATUAL)
            
            if estado == "morto":
                mortes_no_ciclo += 1
                agentes.remove(a)
            else:
                if a.em_lockdown:
                    a.timer_lockdown -= 1
                    if a.timer_lockdown <= 0:
                        a.em_lockdown = False
                dados_envio.append(a.to_dict())

        # 5. Comunicação com Frontend
        # Usamos ultima_acao para garantir que o valor exista sempre
        s = sum(1 for a in agentes if a.status == 0)
        i = sum(1 for a in agentes if a.status == 1)
        r = sum(1 for a in agentes if a.status == 2)
        l = sum(1 for a in agentes if a.em_lockdown)
        mortos_totais = POPULACAO_INICIAL - len(agentes)

        socketio.emit('update', {
            'agentes': dados_envio,
            'acao_ia': "LOCKDOWN ATIVO" if ultima_acao == 1 else "MONITORANDO",
            'reward': getattr(ia, 'ultima_recompensa', 0), # Pega a recompensa da IA
            'stats': {
                'total': len(agentes),
                's': s, 'i': i, 'r': r, 'm': mortos_totais, 'l': l
            }
        })
        
        socketio.sleep(0.1)

def reset_simulacao():
    global agentes, mortes_no_ciclo, contador_frames, ultima_acao, perc_anterior, ia

    agentes = [Agente(i, LARGURA, ALTURA) for i in range(POPULACAO_INICIAL)]

    for i in range(45):
        agentes[i].status = 1

    mortes_no_ciclo = 0
    contador_frames = 0
    ultima_acao = 0
    perc_anterior = 0

    global ia, resetar_ia

    if resetar_ia:
        ia = IA_Sentinela()

def rodar_episodio():
    global agentes, mortes_no_ciclo, contador_frames, ultima_acao, perc_anterior, ia

    # reset ambiente (NÃO reset IA)
    agentes = [Agente(i, LARGURA, ALTURA) for i in range(POPULACAO_INICIAL)]
    for i in range(45):
        agentes[i].status = 1

    mortes_no_ciclo = 0
    contador_frames = 0
    ultima_acao = 0
    perc_anterior = 0

    while True:
        if not agentes:
            break

        num_infectados = sum(1 for a in agentes if a.status == 1)
        if num_infectados == 0:
            ultima_acao = 0 # Força a IA a "desligar" o lockdown
            for a in agentes:
                a.em_lockdown = False

        perc = num_infectados / len(agentes)

        delta = perc - perc_anterior
        perc_anterior = perc

        if contador_frames % 10 == 0:
            ultima_acao = ia.decidir_acao(perc, delta, ultima_acao == 1)
            ia.treinar(perc, delta, mortes_no_ciclo, ultima_acao == 1)
            mortes_no_ciclo = 0

        calcular_infeccao(agentes, beta=0.08, raio=10)

        for a in agentes[:]:
            a.mover(LARGURA, ALTURA, 2.0)
            estado = a.atualizar_saude(0.004, 0.9999)

            if estado == "morto":
                mortes_no_ciclo += 1
                agentes.remove(a)

        contador_frames += 1

        if num_infectados == 0:
            break

def treinar_n_episodios(n):
    global treinando

    treinando = True

    for _ in range(n):
        rodar_episodio()

    treinando = False
    print(f"Treino finalizado: {n} episódios")
    print("ENVIANDO EVENTO")
    
@socketio.on('start')
def start_sim(data=None):
    global rodando, agentes, POPULACAO_INICIAL, BETA_ATUAL, ALFA_ATUAL, TETA_ATUAL
    
    if not rodando:
        if data:
            POPULACAO_INICIAL = data.get('populacao', 100)
            BETA_ATUAL = data.get('beta', 0.5)
            ALFA_ATUAL = data.get('alfa', 0.003)
            TETA_ATUAL = data.get('teta', 0.99) # Atualiza o Teta global
            
            # Recriar população
            agentes = [Agente(i, LARGURA, ALTURA) for i in range(POPULACAO_INICIAL)]
            num_init = data.get('infectados', 45)
            for i in range(min(num_init, len(agentes))):
                agentes[i].status = 1
        
        rodando = True
        socketio.start_background_task(loop_simulacao)

@socketio.on('stop')
def stop_sim():
    global rodando
    rodando = False

@socketio.on('toggle_ia')
def toggle_ia(data):
    global resetar_ia
    resetar_ia = data['resetar']

@socketio.on('treinar')
def treinar(data):
    n = int(data.get('episodios', 10))
    socketio.start_background_task(treinar_n_episodios, n)
    socketio.emit('treino_finalizado')

if __name__ == '__main__':
    socketio.run(app, debug=True)

debug = False