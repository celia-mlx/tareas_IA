import csv
import random

import matplotlib
matplotlib.use("Agg")  # pas de fenêtre : on sauvegarde l'image dans un fichier
import matplotlib.pyplot as plt

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


def verify_env_by_hand(env):
    """Vérification à la main des trois cas demandés dans l'exercice."""
    print("--- VÉRIFICATION DE L'ENVIRONNEMENT ---")

    # 1) Un pas au nord depuis S : on arrive en (2, 0), r = -1, l'épisode continue
    result = env.step((3, 0), 'N')
    print(f"Nord depuis S      -> {result}")
    assert result == ((2, 0), -1, False)

    # 2) Un pas à l'est depuis S : on tombe, retour à S, r = -100, l'épisode continue
    result = env.step((3, 0), 'E')
    print(f"Est depuis S       -> {result}")
    assert result == ((3, 0), -100, False)

    # 3) Un pas au sud depuis (2, 11) : on entre en G, r = -1, l'épisode se termine
    result = env.step((2, 11), 'S')
    print(f"Sud depuis (2, 11) -> {result}")
    assert result == ((3, 11), -1, True)

    print("Les 3 cas sont corrects.\n")


def moving_average(values, window=10):
    """Moyenne mobile : pour chaque épisode, moyenne des `window` derniers (ou moins au début)."""
    averages = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        chunk = values[start:i + 1]
        averages.append(sum(chunk) / len(chunk))
    return averages


def save_rewards_csv(episode_rewards, smoothed, filename="recompensas_por_episodio.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["episodio", "recompensa", "media_movil_10"])
        for i, (rew, avg) in enumerate(zip(episode_rewards, smoothed), start=1):
            writer.writerow([i, rew, round(avg, 2)])
    print(f"Série complète sauvegardée dans : {filename}")


def save_rewards_plot(episode_rewards, smoothed, filename="curva_q_learning.png"):
    plt.figure(figsize=(9, 5))
    plt.plot(range(1, len(episode_rewards) + 1), episode_rewards,
             color="lightgray", linewidth=0.8, label="Récompense par épisode")
    plt.plot(range(1, len(smoothed) + 1), smoothed,
             color="tab:red", linewidth=1.8, label="Moyenne mobile (10 épisodes)")
    plt.ylim(-150, 0)  # coupe les très gros -100 cumulés pour garder la courbe lisible
    plt.xlabel("Épisodes")
    plt.ylabel("Somme des récompenses pendant l'épisode")
    plt.title("Q-learning sur Cliff Walking (ε = 0.1, α = 0.5)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Graphique sauvegardé dans : {filename}")


def run_experiment():
    SEED = 42
    EPISODES = 500
    ALPHA = 0.5
    GAMMA = 1.0
    EPSILON = 0.1
    MAX_STEPS = 200

    env = CliffWalkingEnv()
    verify_env_by_hand(env)

    agent = QLearningAgent(ACTIONS, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON, seed=SEED)

    episode_rewards = []
    truncated_episodes = 0  # épisodes coupés par le tope de 200 pas (sans atteindre G)

    # Phase d'entraînement
    for ep in range(EPISODES):
        state = env.reset()
        total_reward = 0
        steps = 0
        reached_goal = False

        while steps < MAX_STEPS:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(state, action)

            agent.update(state, action, reward, next_state, done)

            total_reward += reward
            state = next_state
            steps += 1

            if done:
                reached_goal = True
                break

        if not reached_goal:
            truncated_episodes += 1

        episode_rewards.append(total_reward)

    smoothed = moving_average(episode_rewards, window=10)

    print(f"Entraînement terminé (Seed: {SEED}, Épisodes: {EPISODES})")
    print(f"Récompense moyenne des 10 derniers épisodes: {sum(episode_rewards[-10:]) / 10.0}")
    print(f"Épisodes coupés par le tope de {MAX_STEPS} pas : {truncated_episodes} / {EPISODES}\n")

    # Série complète des 500 récompenses
    save_rewards_csv(episode_rewards, smoothed)
    save_rewards_plot(episode_rewards, smoothed)
    print()

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
    print(f"Retour greedy total : {eval_reward}")

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
