import random

# Definition des actions et de l'ordre de priorité pour les égalités (N, E, S, W)
ACTIONS = ['N', 'E', 'S', 'W']
ACTION_DELTAS = {
    'N': (-1, 0),
    'E': (0, 1),
    'S': (1, 0),
    'W': (0, -1)
}

class CliffWalkingEnv:
    def __init__(self):
        self.rows = 4
        self.cols = 12
        self.start = (3, 0)
        self.goal = (3, 11)

    def reset(self):
        return self.start

    def step(self, state, action):
        r, c = state
        dr, dc = ACTION_DELTAS[action]
        nr, nc = r + dr, c + dc

        # Gérer les limites de la grille (rester sur place si on tape un mur)
        nr = max(0, min(self.rows - 1, nr))
        nc = max(0, min(self.cols - 1, nc))

        # vérifier si on tombe dans la falaise : ligne 3, colonnes 1 à 10
        if nr == 3 and 1 <= nc <= 10:
            # Coûte -100 et ramène à S, l'épisode continue (done = False)
            return self.start, -100, False

        # Vérifier si on atteint la meta (G)
        if (nr, nc) == self.goal:
            # Coûte -1 et l'épisode se termine (done = True)
            return (nr, nc), -1, True

        # Transition ordinaire
        return (nr, nc), -1, False


class QLearningAgent:
    def __init__(self, actions, alpha=0.5, gamma=1.0, epsilon=0.1, seed=42):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Fixer la graine aléatoire pour la reproductibilité
        random.seed(seed)
        
        # Table Q : dictionnaire (état, action) -> valeur Q, initialisée à 0
        self.q_table = {}

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def set_q(self, state, action, value):
        self.q_table[(state, action)] = value

    def choose_action(self, state, epsilon=None):
        if epsilon is None:
            epsilon = self.epsilon

        # Comportement epsilon-greedy
        if random.random() < epsilon:
            return random.choice(self.actions)
        else:
            # Exploitation : choisir l'action qui maximise Q(s, a)
            best_val = float('-inf')
            best_actions = []
            
            for a in self.actions:
                val = self.get_q(state, a)
                if val > best_val:
                    best_val = val
                    best_actions = [a]
                elif val == best_val:
                    best_actions.append(a)
            
            # En cas d'égalité, respecter l'ordre fixe (N, E, S, W)
            for a in self.actions:
                if a in best_actions:
                    return a
            return self.actions[0]

    def update(self, state, action, reward, next_state, next_state_terminal):
        current_q = self.get_q(state, action)
        
        if next_state_terminal:
            max_next_q = 0.0
        else:
            max_next_q = max(self.get_q(next_state, a) for a in self.actions)
        
        # Formule Q-learning : Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a'(Q(s',a')) - Q(s,a)]
        target = reward + self.gamma * max_next_q
        new_q = current_q + self.alpha * (target - current_q)
        self.set_q(state, action, new_q)


def run_experiment():
    SEED = 42
    EPISODES = 500
    ALPHA = 0.5
    GAMMA = 1.0
    EPSILON = 0.1

    env = CliffWalkingEnv()
    agent = QLearningAgent(ACTIONS, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON, seed=SEED)

    episode_rewards = []

    # Phase d'entraînement
    for ep in range(EPISODES):
        state = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 200

        while steps < max_steps:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(state, action)
            
            agent.update(state, action, reward, next_state, done)
            
            total_reward += reward
            state = next_state
            steps += 1
            
            if done:
                break
                
        episode_rewards.append(total_reward)

    print(f"Entraînement terminé (Seed: {SEED}, Épisodes: {EPISODES})")
    print(f"Récompense moyenne des 10 derniers épisodes: {sum(episode_rewards[-10:]) / 10.0}\n")

    # Évaluation Greedy (epsilon = 0)
    print("--- ÉVALUATION GREEDY (Politique Optimale) ---")
    state = env.reset()
    path = [state]
    eval_reward = 0
    steps = 0
    
    while steps < 100:
        action = agent.choose_action(state, epsilon=0.0)
        next_state, reward, done = env.step(state, action)
        eval_reward += reward
        path.append(next_state)
        state = next_state
        steps += 1
        if done:
            break

    print(f"Chemin trouvé (états) : {path}")
    print(f"Nombre de pas : {steps}")
    print(f"Retorn greedy total : {eval_reward}")

    # Affichage d'une grille avec la politique greedy
    print("\nPolitique Greedy apprise (Flèches) :")
    arrows = {'N': '↑', 'E': '→', 'S': '↓', 'W': '←'}
    for r in range(env.rows):
        row_str = ""
        for c in range(env.cols):
            pos = (r, c)
            if pos == env.goal:
                row_str += " G "
            elif r == 3 and 1 <= c <= 10:
                row_str += " C "
            else:
                best_action = agent.choose_action(pos, epsilon=0.0)
                row_str += f" {arrows[best_action]} "
        print(row_str)

if __name__ == "__main__":
    run_experiment()