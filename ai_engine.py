import random

class IA_Sentinela:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.5):
        self.q_table = {}  # Estado: [Ação 0 (Nada), Ação 1 (Lockdown)]
        self.lr = learning_rate
        self.df = discount_factor
        self.epsilon = epsilon
        self.last_state = None
        self.last_action = None

    def get_state(self, perc_infectados, delta, lockdown):
        return (
            round(perc_infectados * 10),
            int(delta > 0),
            int(lockdown)
        )

    def decidir_acao(self, perc_infectados, delta, lockdown):
        state = self.get_state(perc_infectados, delta, lockdown)
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0]

        # Epsilon-greedy (Exploração vs Explotação)
        if random.random() < self.epsilon:
            action = random.choice([0, 1])
        else:
            action = self.q_table[state].index(max(self.q_table[state]))
        
        self.last_state = state
        self.last_action = action
        return action

    def treinar(self, novo_perc_infectados, delta, novos_mortos, em_lockdown):
        if self.last_state is None: return

        recompensa = 0

        new_state = self.get_state(novo_perc_infectados, delta, em_lockdown)
        if new_state not in self.q_table:
            self.q_table[new_state] = [0.0, 0.0]

        # FUNÇÃO DE RECOMPENSA CALIBRADA
        # Penalidade pesada por morte (-30)
        # Recompensa por não estar em lookdown
        recompensa += (- novos_mortos * 30 + (40 if not em_lockdown else 0) - (novo_perc_infectados * 20))
        
        self.ultima_recompensa = recompensa

        if em_lockdown:
            recompensa -= 30  # Custo do lockdown
        else:
            recompensa += 40  # "Bônus" por manter a economia aberta
        # Bônus por manter a infecção baixa e a economia funcionando
        if novo_perc_infectados == 0 and not em_lockdown:
            recompensa += 100 
        elif novo_perc_infectados == 0 and em_lockdown:
            recompensa -= 3000 # O custo continua existindo

        # Atualização da Q-Table (Equação de Bellman)
        old_value = self.q_table[self.last_state][self.last_action]
        next_max = max(self.q_table[new_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (recompensa + self.df * next_max)
        self.q_table[self.last_state][self.last_action] = new_value