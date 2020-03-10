# coding: utf-8

import socket
import threading
import logging
import pickle
from utils import dht_hash, contains_predecessor, contains_successor


class DHT_Node(threading.Thread):
    """ DHT Node Agent. """
    def __init__(self, address, dht_address=None, timeout=3):
        """ Constructor

        Parameters:
            address: self's address
            dht_address: address of a node in the DHT
            timeout: impacts how often stabilize algorithm is carried out
        """
        threading.Thread.__init__(self)
        self.id = dht_hash(address.__str__())
        self.addr = address #My address
        self.dht_address = dht_address  #Address of the initial Node
        if dht_address is None:
            self.inside_dht = True
            #I'm my own successor
            self.successor_id = self.id
            self.successor_addr = address
            self.predecessor_id = None
            self.predecessor_addr = None
        else:
            self.inside_dht = False
            self.successor_id = None
            self.successor_addr = None
            self.predecessor_id = None
            self.predecessor_addr = None
        self.keystore = {}  # Where all data is stored
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.id))

    def send(self, address, msg):
        """ Send msg to address. """
        payload = pickle.dumps(msg)
        self.socket.sendto(payload, address)

    def recv(self):
        """ Retrieve msg payload and from address."""
        try:
            payload, addr = self.socket.recvfrom(1024)
        except socket.timeout:
            return None, None

        if len(payload) == 0:
            return None, addr
        return payload, addr

    def node_join(self, args):
        """ Process JOIN_REQ message.

        Parameters:
            args (dict): addr and id of the node trying to join
        """

        self.logger.debug('Node join: %s', args)
        addr = args['addr']
        identification = args['id']
        if self.id == self.successor_id: #I'm the only node in the DHT
            self.successor_id = identification
            self.successor_addr = addr
            args = {'successor_id': self.id, 'successor_addr': self.addr}
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        elif contains_successor(self.id, self.successor_id, identification):
            args = {'successor_id': self.successor_id, 'successor_addr': self.successor_addr}
            self.successor_id = identification
            self.successor_addr = addr
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        else:
            self.logger.debug('Find Successor(%d)', args['id'])
            self.send(self.successor_addr, {'method': 'JOIN_REQ', 'args':args})
        self.logger.info(self)

    def notify(self, args):
        """ Process NOTIFY message.
            Updates predecessor pointers.

        Parameters:
            args (dict): id and addr of the predecessor node
        """

        self.logger.debug('Notify: %s', args)
        if self.predecessor_id is None or contains_predecessor(self.id, self.predecessor_id, args['predecessor_id']):
            self.predecessor_id = args['predecessor_id']
            self.predecessor_addr = args['predecessor_addr']
        self.logger.info(self)

    def stabilize(self, from_id, addr):
        """ Process STABILIZE protocol.
            Updates all successor pointers.

        Parameters:
            from_id: id of the predecessor of node with address addr
            addr: address of the node sending stabilize message
        """

        self.logger.debug('Stabilize: %s %s', from_id, addr)
        if from_id is not None and contains_successor(self.id, self.successor_id, from_id):
            # Update our successor
            self.successor_id = from_id
            self.successor_addr = addr

        # notify successor of our existence, so it can update its predecessor record
        args = {'predecessor_id': self.id, 'predecessor_addr': self.addr}
        self.send(self.successor_addr, {'method': 'NOTIFY', 'args':args})

    def put(self, key, value, address):
        """ Store value in DHT.

            Parameters:
            key: key of the data
            value: data to be stored
            address: address where to send ack/nack
        """
        key_hash = dht_hash(key)
        self.logger.debug('Put: %s %s', key, key_hash)
        if contains_successor(self.id, self.successor_id, key_hash):
            self.keystore[key] = value
            self.send(address, {'method': 'ACK'})
        else:
            # send to DHT
            # Fill here
            self.send(address, {'method': 'NACK'})

    def get(self, key, address):
        """ Retrieve value from DHT.

            Parameters:
            key: key of the data
            address: address where to send ack/nack
        """
        key_hash = dht_hash(key)
        self.logger.debug('Get: %s %s', key, key_hash)
        if contains_successor(self.id, self.successor_id, key_hash):
            value = self.keystore[key]
            self.send(address, {'method': 'ACK', 'args': value})
        else:
            # send to DHT
            # Fill here
            self.send(address, {'method': 'NACK'})

    def run(self):
        self.socket.bind(self.addr)

        # Loop untiln joining the DHT
        while not self.inside_dht:
            join_msg = {'method': 'JOIN_REQ', 'args': {'addr':self.addr, 'id':self.id}}
            self.send(self.dht_address, join_msg)
            payload, addr = self.recv()
            if payload is not None:
                output = pickle.loads(payload)
                self.logger.debug('O: %s', output)
                if output['method'] == 'JOIN_REP':
                    args = output['args']
                    self.successor_id = args['successor_id']
                    self.successor_addr = args['successor_addr']
                    self.inside_dht = True
                    self.logger.info(self)

        done = False
        while not done:
            payload, addr = self.recv()
            if payload is not None:
                output = pickle.loads(payload)
                self.logger.info('O: %s', output)
                if output['method'] == 'JOIN_REQ':
                    self.node_join(output['args'])
                elif output['method'] == 'NOTIFY':
                    self.notify(output['args'])
                elif output['method'] == 'PUT':
                    self.put(output['args']['key'], output['args']['value'], addr)
                elif output['method'] == 'GET':
                    self.get(output['args']['key'], addr)
                elif output['method'] == 'PREDECESSOR':
                    # Reply with predecessor id
                    self.send(addr, {'method': 'STABILIZE', 'args': self.predecessor_id})
                elif output['method'] == 'STABILIZE':
                    # Initiate stabilize protocol
                    self.stabilize(output['args'], addr)
            else: #timeout occurred, lets run the stabilize algorithm
                # Ask successor for predecessor, to start the stabilize process
                self.send(self.successor_addr, {'method': 'PREDECESSOR'})

    def __str__(self):
        return 'Node ID: {}; DHT: {}; Successor: {}; Predecessor: {}'\
            .format(self.id, self.inside_dht, self.successor_id, self.predecessor_id)

    def __repr__(self):
        return self.__str__()
