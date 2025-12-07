class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, data):
        self.items.append(data)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)  # FIFO

    def peek(self):
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return list(self.items)

    def __str__(self):
        return str(self.items)
    
    # ===== Tambahkan method remove =====
    def remove(self, item):
        try:
            self.items.remove(item)
        except ValueError:
            pass