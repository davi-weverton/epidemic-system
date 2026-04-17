import random
import math

class Agente:
    def __init__(self, id, x_lim, y_lim):
        self.id = id
        self.x = random.uniform(0, x_lim)
        self.y = random.uniform(0, y_lim)
        self.status = 0 # 0: Saudável, 1: Infectado, 2: Imune
        self.tempo_infectado = 0
        self.em_lockdown = False
        self.timer_lockdown = 0
        self.adesao = random.uniform(0.3, 1.0)

    def mover(self, x_lim, y_lim, velocidade):
        if self.em_lockdown:
            if random.random() > self.adesao:
                # Rebelde: se move devagar
                self.x += random.uniform(-velocidade * 0.5, velocidade * 0.5)
                self.y += random.uniform(-velocidade * 0.5, velocidade * 0.5)
            # else: obedeceu, não faz nada
        else:
            # Movimento normal — só uma vez
            self.x += random.uniform(-velocidade, velocidade)
            self.y += random.uniform(-velocidade, velocidade)

        self.x = max(0, min(x_lim, self.x))
        self.y = max(0, min(y_lim, self.y))

    def atualizar_saude(self, alfa, teta):
        if self.status == 1:
            self.tempo_infectado += 1
            # Chance de morte aumenta conforme o tempo passa doente
            chance_morte_atual = alfa * (1 + (self.tempo_infectado * 0.01))
            
            r = random.random()
            if r < chance_morte_atual:
                return "morto"
            elif r > teta:
                self.status = 2 # Recuperado/Imune
                return "recuperado"
        return "vivo"

    def to_dict(self):
        return {
        "id": self.id,    
        "x": self.x, 
        "y": self.y, 
        "s": self.status, 
        "l": self.em_lockdown
    }
def calcular_infeccao(agentes, beta, raio):
    infectados = [a for a in agentes if a.status == 1 and not a.em_lockdown]
    saudaveis = [a for a in agentes if a.status == 0 and not a.em_lockdown]
    
    for s in saudaveis:
        for i in infectados:
            dist = math.sqrt((s.x - i.x)**2 + (s.y - i.y)**2)
            
            if dist < 3 * raio:  # limite importante
                p = beta * math.exp(-dist / raio)
                
                if random.random() < p:
                    s.status = 1
                    break
