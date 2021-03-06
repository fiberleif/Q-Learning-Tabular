import argparse
import random
import time
from environment import QLEnvironment


def parse_arguments():
    print("[Info]: Start to parse arguments from commandline.")
    parser = argparse.ArgumentParser()
    # add arguments
    parser.add_argument('--maze_input', type=str, default='../env/maze_2.txt',
                        help=' path to the environment input.txt described previously')
    parser.add_argument('--value_file', type=str, default='./ql_value_file.txt',
                        help='path to output the value function')
    parser.add_argument('--q_value_file', type=str, default='./ql_q_value_file.txt',
                        help='path to output the q_value function')
    parser.add_argument('--policy_file', type=str, default='./ql_policy_file.txt',
                        help ='path to output the optimal policy')
    parser.add_argument('--num_episode', type=int, default=2000,
                        help='the number of train episodes')
    parser.add_argument('--max_episode_length', type=int, default=10000,
                        help='the maximum of the length of an episode')
    parser.add_argument('--learning_rate', type=float, default=0.1,
                        help='the learning rate of the q learning algorithm')
    parser.add_argument('--discount_factor', type=float, default=0.9,
                        help='the discount factor')
    parser.add_argument('--epsilon', type=float, default=0.8,
                        help='the value for the epsilon-greedy strategy')
    # parse arguments
    args = parser.parse_args()
    print("[Info]: Finish parsing arguments from commandline.")
    return args


def train(maze_env, value_file, q_value_file, policy_file, num_episode, max_episode_length, learning_rate,
          discount_factor, epsilon, **kwargs):

    # create value function and q value function
    print("[Info]: Start to create q value function component.")
    q_value_function = {}
    for state in maze_env.state_space:
        hashing_state = hash_state(state)
        for action in maze_env.action_space:
            hashing_state_action = hash_state_action(state, action)
            q_value_function[hashing_state_action] = 0
    print("[Info]: Finishing creating q value function component.")

    # train agent
    start = time.time()
    episodes_length = []
    print("[Info]: Start to train q value function.")
    for _ in range(num_episode):
        current_length = 0
        is_terminal = 0
        state = maze_env.reset()
        while not is_terminal and (current_length < max_episode_length):
            action, _ = get_max_action(state, q_value_function, maze_env)
            if random.random() <= epsilon:
                action = random.randint(0, len(maze_env.action_space) - 1)
            next_state, reward, is_terminal = maze_env.step(action)
            current_length += 1
            next_action, next_q_value = get_max_action(next_state, q_value_function, maze_env)
            max_q_value_target = reward + discount_factor*next_q_value
            q_value_function[hash_state_action(state, action)] = (1 - learning_rate) * \
                            q_value_function[hash_state_action(state, action)] + learning_rate*max_q_value_target
            state = next_state
        episodes_length.append(current_length)
    print("[Info]: Finish training q value function.")
    end = time.time()
    print("[Statistics]: Avg_length {0} and Time {1}s".format(sum(episodes_length) / len(episodes_length), end - start))

    # output
    print("[Info]: Start to output value function, q value function and policy to file.")
    file = open(q_value_file, "w")
    for key, value in q_value_function.items():
        state, action = reverse_hashing_state_action(key)
        file.write("{0} {1} {2} {3}\n".format(state[0], state[1], action, value))
    file.close()

    file = open(policy_file, "w")
    for state in maze_env.state_space:
        max_action, _ = get_max_action(state, q_value_function, maze_env)
        file.write("{0} {1} {2}\n".format(state[0], state[1], max_action))
    file.close()

    file = open(value_file, "w")
    for state in maze_env.state_space:
        max_action, _ = get_max_action(state, q_value_function, maze_env)
        file.write("{0} {1} {2}\n".format(state[0], state[1], q_value_function[hash_state_action(state, max_action)]))
    file.close()
    print("[Info]: Finish outputting value function, q value function and policy to file.")


# hash state
def hash_state(state):
    return str(state[0]) + "-" + str(state[1])


# reverse hashing state to state
def reverse_hashing_state(hashing_state):
    return [int(e) for e in hashing_state.split("-")]


# hash state, action
def hash_state_action(state, action):
    return str(state[0]) + "-" + str(state[1]) + "|" + str(action)


# reverse hashing state-action to state, action
def reverse_hashing_state_action(hashing_state_action):
    state , action = hashing_state_action.split("|")
    state = reverse_hashing_state(state)
    action = int(action)
    return state, action


# get action with max q value function
def get_max_action(state, q_value_function, maze_env):
    max_action = None
    max_q_value = -float('inf')
    for action in maze_env.action_space:
        current_q_value = q_value_function[hash_state_action(state, action)]
        if current_q_value > max_q_value:
            max_q_value = current_q_value
            max_action = action
    return max_action, max_q_value


def main():
    # parse arguments
    args = parse_arguments()
    # create env
    maze_env = QLEnvironment(args.maze_input)
    # train agent
    train(maze_env, **vars(args))


if __name__ == '__main__':
    main()
