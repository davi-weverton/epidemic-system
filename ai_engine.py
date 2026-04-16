import random

class IA_Sentinela:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = {}  # Estado: [Ação 0 (Nada), Ação 1 (Lockdown)]
        self.lr = learning_rate
        self.df = discount_factor
        self.epsilon = epsilon
        self.last_state = None
        self.last_action = None

    def get_state(self, perc_infectados):
        # Discretiza o estado em faixas de 10% para a IA aprender padrões
        return round(perc_infectados * 10)

    def decidir_acao(self, perc_infectados):
        state = self.get_state(perc_infectados)
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

    def treinar(self, novo_perc_infectados, novos_mortos, em_lockdown):
        if self.last_state is None: return

        new_state = self.get_state(novo_perc_infectados)
        if new_state not in self.q_table:
            self.q_table[new_state] = [0.0, 0.0]

        # FUNÇÃO DE RECOMPENSA CALIBRADA
        # Penalidade pesada por morte (-100)
        # Penalidade moderada por Lockdown (-30) para evitar uso excessivo
        recompensa = -(novos_mortos * 100) - (30 if em_lockdown else 0)
        
        self.ultima_recompensa = recompensa

        # Bônus por manter a infecção baixa
        if novo_perc_infectados < 0.05:
            recompensa += 20

        # Atualização da Q-Table (Equação de Bellman)
        old_value = self.q_table[self.last_state][self.last_action]
        next_max = max(self.q_table[new_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (recompensa + self.df * next_max)
        self.q_table[self.last_state][self.last_action] = new_value