from flask import Flask, render_template
from flask_socketio import SocketIO
import eventlet
import random
from simulation import Agente, calcular_infeccao
from ai_engine import IA_Sentinela

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

largura, altura = 800, 600
agentes = [Agente(i, largura, altura) for i in range(200)]
agentes[0].status = 1 # Primeiro infectado
ia = IA_Sentinela()

@app.route('/')
def index():
    return render_template('index.html')

def loop_simulacao():
    while True:
        num_infectados = sum(1 for a in agentes if a.status == 1)
        acao = ia.decidir_acao(num_infectados / len(agentes))
        
        if acao == "LOCKDOWN":
            for a in random.sample(agentes, int(len(agentes)*0.3)):
                if not a.em_lockdown:
                    a.em_lockdown = True
                    a.timer_lockdown = 20 # 20 rodadas

        calcular_infeccao(agentes, beta=0.1, raio=10)
        
        dados = []
        for a in agentes[:]:
            a.mover(largura, altura, velocidade=4)
            if a.atualizar_saude(alfa=0.005, teta=0.98) == "morto":
                agentes.remove(a)
            else:
                dados.append(a.to_dict())
                if a.em_lockdown:
                    a.timer_lockdown -= 1
                    if a.timer_lockdown <= 0: a.em_lockdown = False

        socketio.emit('update', {'agentes': dados, 'acao_ia': acao})
        socketio.sleep(0.05)

@socketio.on('connect')
def start():
    socketio.start_background_task(loop_simulacao)

if __name__ == '__main__':
    socketio.run(app, debug=True)