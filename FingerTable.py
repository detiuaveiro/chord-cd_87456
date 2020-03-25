from utils import dht_hash, contains_predecessor, contains_successor


class FingerTable:

    def __init__(self, succ_addr):
        self.ft = [succ_addr]
        for i in range(1, 10):
            self.ft.append(None)

    def update_succ(self, succ_addr):
        print("Olá\n\n\n\n")
        self.ft[0] = succ_addr


    def closest_preceding_node(self, node_id):
        print(self.ft)
        for entry in self.ft[::-1]:
            if entry and dht_hash(entry.__str__()) < node_id:
                print(entry)
                return entry