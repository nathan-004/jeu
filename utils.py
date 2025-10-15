from collections import deque

class Stack(deque):
    def empty(self):
        return len(self) == 0
    
    def empiler(self, el):
        super().append(el)
    
    def depiler(self):
        return super().popleft()