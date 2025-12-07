class DoubleLinkedList:
    class _Node:
        def __init__(self, data):
            self.data = data
            self.next = None
            self.prev = None

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

        # --- FIX: inisialisasi repeat & shuffle supaya tidak error ---
        self.repeat_mode = 0   # 0 = none, 1 = all, 2 = one
        self.shuffle = False

    # ============================
    # INSERT
    # ============================
    def add_last(self, data):
        new_node = self._Node(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1

    def add_first(self, data):
        new_node = self._Node(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    # ============================
    # GET NODE BY INDEX
    # ============================
    def get_node(self, index):
        if index < 0 or index >= self.size:
            return None
        
        current = self.head
        for _ in range(index):
            current = current.next
        return current

    # ============================
    # DELETE BY VALUE
    # ============================
    def remove(self, data):

        # FIX: jika list kosong
        if self.size == 0:
            return False

        # FIX: jika hanya 1 node
        if self.size == 1:
            if self.head.data == data:
                self.clear()
                return True
            return False
        
        current = self.head
        while current:
            if current.data == data:

                # update pointer current
                if current == self.current:
                    self.current = current.next or current.prev

                # update head
                if current == self.head:
                    self.head = current.next
                    self.head.prev = None

                # update tail
                elif current == self.tail:
                    self.tail = current.prev
                    self.tail.next = None

                # update link tengah
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev

                self.size -= 1
                return True

            current = current.next
        return False

    # ============================
    # DELETE BY INDEX
    # ============================
    def delete_at(self, index):
        if index < 0 or index >= self.size:
            return False

        # FIX: jika hanya 1 node
        if self.size == 1:
            self.clear()
            return True

        # Hapus head
        if index == 0:
            to_delete = self.head

            if to_delete == self.current:
                self.current = to_delete.next

            self.head = to_delete.next
            self.head.prev = None
            self.size -= 1
            return True

        # Hapus tail
        if index == self.size - 1:
            to_delete = self.tail

            if to_delete == self.current:
                self.current = to_delete.prev

            self.tail = to_delete.prev
            self.tail.next = None
            self.size -= 1
            return True

        # Hapus di tengah
        to_delete = self.get_node(index)

        if to_delete == self.current:
            self.current = to_delete.next or to_delete.prev

        to_delete.prev.next = to_delete.next
        to_delete.next.prev = to_delete.prev

        self.size -= 1
        return True

    # ============================
    # SEARCH
    # ============================
    def search_by_title(self, title):
        current = self.head
        while current:
            if hasattr(current.data, "judul") and current.data.judul.lower() == title.lower():
                return current.data
            current = current.next
        return None

    # ============================
    # UTILS
    # ============================
    def show(self):
        print("\n=== PLAYLIST ===")
        current = self.head
        i = 1
        while current:
            print(f"{i}. {current.data}")
            i += 1
            current = current.next
        print("=================\n")

    def is_empty(self):
        return self.head is None

    # ============================
    # PLAYLIST POINTER
    # ============================
    def play_first(self):
        if not self.head:
            return None
        self.current = self.head
        return self.current.data

    def next_song(self):
        if not self.current:
            return None
        if not self.current.next:
            return None
        self.current = self.current.next
        return self.current.data

    def prev_song(self):
        if not self.current:
            return None
        if not self.current.prev:
            return None
        self.current = self.current.prev
        return self.current.data
    
    # =====================================================
    # FITUR TAMBAHAN (TIDAK MENGGANGGU KODE LAMA)
    # =====================================================
    def set_repeat_mode(self, mode):
        self.repeat_mode = mode

    def enable_shuffle(self, status=True):
        self.shuffle = status

    def get_current(self):
        return self.current.data if self.current else None

    def clear(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def to_list(self):
        lst = []
        cur = self.head
        while cur:
            lst.append(cur.data)
            cur = cur.next
        return lst

    def jump_to(self, index):
        node = self.get_node(index)
        if node:
            self.current = node
            return node.data
        return None

    def jump_to_song(self, song):
        cur = self.head
        while cur:
            if cur.data == song:
                self.current = cur
                return cur.data
            cur = cur.next
        return None

    # =====================================================
    # NEXT / PREV SMART MODE (FIXED)
    # =====================================================
    def next_song_smart(self):
        if self.size == 0 or not self.current:
            return None

        # repeat one
        if self.repeat_mode == 2:
            return self.current.data

        # shuffle mode
        if self.shuffle:
            import random
            lst = self.to_list()
            if not lst:
                return None
            chosen = random.choice(lst)
            return self.jump_to_song(chosen)

        # normal next
        if self.current.next:
            self.current = self.current.next
            return self.current.data

        # repeat all
        if self.repeat_mode == 1:
            return self.play_first()

        return None

    def prev_song_smart(self):
        if self.size == 0 or not self.current:
            return None

        # repeat one
        if self.repeat_mode == 2:
            return self.current.data

        # shuffle mode (backward random)
        if self.shuffle:
            import random
            lst = self.to_list()
            if not lst:
                return None
            chosen = random.choice(lst)
            return self.jump_to_song(chosen)

        # normal prev
        if self.current.prev:
            self.current = self.current.prev
            return self.current.data

        # repeat all (balik ke tail)
        if self.repeat_mode == 1:
            self.current = self.tail
            return self.current.data

        return None