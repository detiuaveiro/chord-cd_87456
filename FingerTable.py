from utils import dht_hash, contains_predecessor, contains_successor


class FingerTable:
    ft = []

    def __init__(self, succ_addr):
        self.init_ft(succ_addr)

    def init_ft(self, succ_addr):
        ft.append(succ_addr)
        for i in range(1, 10):
            ft.append(None)

    def closest_preceding_node(self, node_id):
        for entry in ft[::-1]:
            if entry and dht_hash(entry) < node_id:
                return entry
