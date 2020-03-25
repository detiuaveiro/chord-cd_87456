from utils import dht_hash, contains_predecessor, contains_successor


class FingerTable:
    def __init__(self, succ_addr):
        self.ft = [succ_addr]
        for i in range(1, 10):
            self.ft.append(None)
        self.update_index = 0

    def update_index(self, index, addr):
        self.ft[i] = addr
        i = (i + 1) % len(self.ft)

    def get_update_index(self):
        return self.update_index

    def closest_preceding_node(self, node_id):
        # ainda nao tem em conta os ids serem circulares
        print(self.ft)
        for entry in self.ft[::-1]:
            if entry and dht_hash(entry.__str__()) < node_id:
                print(entry)
                return entry