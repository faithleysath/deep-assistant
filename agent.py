import os
base_path = os.path.dirname(os.path.realpath(__file__))

class Agent:
    def __init__(self, name):
        self.name = name
        self.prompt_file = os.path.join(base_path, 'agents', name, 'prompt.txt')