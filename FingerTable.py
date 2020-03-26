from utils import contains_successor


class FingerTable:
    def __init__(self, scss_id=None, scss_addr=None):
        self.index_entry = 0
        self.finger_Table = []
        self.entries = 10
        for n in range(self.entries):
            self.finger_Table.append({'id': scss_id, 'addr': scss_addr})

    def closest_preceding_node(self, node_id, test_id):
        for e in reversed(self.finger_Table):
            ft_id = e.get('id')
            if contains_successor(node_id, ft_id, test_id):
                return e
        return None

    def entry_ft(self):
        previous = self.index_entry + 2
        self.index_entry = (self.index_entry + 1) % 8
        return previous

    def update_ft(self, index, node_id, node_addr):
        self.finger_Table[index] = {'id': node_id, 'addr': node_addr}

    def get_succ_addr(self):
        return self.finger_Table[0].get('addr')

    def get_succ_id(self):
        return self.finger_Table[0].get('id')

    def __str__(self):
        s = '\n'
        for e in self.finger_Table:
            s += 'id: ' + str(e.get('id')) + ' with addr: ' + str(e.get('addr')) + '\n'

        return s

    def __repr(self):
        return self.__str__()
