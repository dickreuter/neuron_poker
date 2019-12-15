"""memory management"""
import random


class ReplayMemory:

    def __init__(self):
        self.memory = []

    def push(self, event):
        self.memory.append(event)

    def sample(self, batch_size):
        samples = zip(random.sample(self.memory, batch_size))
        return samples
