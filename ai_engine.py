class IA_Sentinela:
    def __init__(self):
        self.q_table = {} # Simples para o exemplo

    def decidir_acao(self, perc_infectados):
        # Se mais de 15% infectados, ativa lockdown
        if perc_infectados > 0.15:
            return "LOCKDOWN"
        return "NADA"

    def calcular_recompensa(self, novos_mortos, em_lockdown):
        return -(novos_mortos * 10) - (em_lockdown * 0.5)