import random

class IA_Sentinela:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.5, epsilon_min=0.05, epsilon_decay=0.97):
        self.q_table = {}  # Estado: [Ação 0 (Nada), Ação 1 (Lockdown)]
        self.lr = learning_rate
        self.df = discount_factor
        self.epsilon = epsilon
        self.last_state = None
        self.last_action = None
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memoria = []  # buffer de experiências
        self.batch_size = 32

    def get_state(self, perc_infectados, delta, lockdown):
        return (
            round(perc_infectados * 20),
            int(delta > 0.01),
            int(delta < - 0.01),
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
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return action

    def treinar(self, novo_perc_infectados, delta, novos_mortos, em_lockdown):
        if self.last_state is None:
            return

        new_state = self.get_state(novo_perc_infectados, delta, em_lockdown)
        if new_state not in self.q_table:
            self.q_table[new_state] = [0.0, 0.0]

        recompensa = 0.0
        recompensa -= novos_mortos * 50
        recompensa -= novo_perc_infectados * 20
        if em_lockdown:
            recompensa -= 10
        if novo_perc_infectados == 0:
            recompensa += 100

        self.ultima_recompensa = recompensa

        # Guarda ANTES de atualizar
        self.memoria.append((
            self.last_state,
            self.last_action,
            recompensa,
            new_state
        ))
        if len(self.memoria) > 2000:
            self.memoria.pop(0)

        # Treina APENAS no batch — não faz update duplo
        if len(self.memoria) >= self.batch_size:
            batch = random.sample(self.memoria, self.batch_size)
            for s, a, r, s_next in batch:
                if s not in self.q_table:
                    self.q_table[s] = [0.0, 0.0]
                if s_next not in self.q_table:
                    self.q_table[s_next] = [0.0, 0.0]
                old = self.q_table[s][a]
                next_max = max(self.q_table[s_next])
                self.q_table[s][a] = (1 - self.lr) * old + self.lr * (r + self.df * next_max)
        else:
            # Antes do batch ter dados suficientes, atualiza normalmente
            old_value = self.q_table[self.last_state][self.last_action]
            next_max = max(self.q_table[new_state])
            new_value = (1 - self.lr) * old_value + self.lr * (recompensa + self.df * next_max)
            self.q_table[self.last_state][self.last_action] = new_value