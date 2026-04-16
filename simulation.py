import random
import math

class Agente:
    def __init__(self, id, x_lim, y_lim):
        self.id = id
        self.x = random.uniform(0, x_lim)
        self.y = random.uniform(0, y_lim)
        self.status = 0  # 0: Saudável, 1: Infectado, 2: Imune
        self.tempo_infectado = 0
        self.em_lockdown = False
        self.timer_lockdown = 0
        self.foco = (x_lim / 2, y_lim / 2)

    def mover(self, x_lim, y_lim, velocidade):
        if self.em_lockdown: return
        
        # 70% atração pelo foco, 30% aleatório
        if random.random() < 0.7:
            angle = math.atan2(self.foco[1] - self.y, self.foco[0] - self.x)
            self.x += math.cos(angle) * velocidade
            self.y += math.sin(angle) * velocidade
        else:
            self.x += random.uniform(-velocidade, velocidade)
            self.y += random.uniform(-velocidade, velocidade)

        self.x = max(0, min(x_lim, self.x))
        self.y = max(0, min(y_lim, self.y))

    def atualizar_saude(self, alfa, teta):
        if self.status == 1:
            self.tempo_infectado += 1
            r = random.random()
            if r < alfa: return "morto"
            if r > teta: self.status = 2
        return "vivo"

    def to_dict(self):
        return {"id": self.id, "x": self.x, "y": self.y, "s": self.status, "l": self.em_lockdown}

def calcular_infeccao(agentes, beta, raio):
    infectados = [a for a in agentes if a.status == 1 and not a.em_lockdown]
    saudaveis = [a for a in agentes if a.status == 0 and not a.em_lockdown]
    for s in saudaveis:
        for i in infectados:
            dist = math.sqrt((s.x - i.x)**2 + (s.y - i.y)**2)
            if dist < raio and random.random() < beta:
                s.status = 1
                break