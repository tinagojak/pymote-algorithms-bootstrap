'''
INICIJALNO, JEDNOM:
1) Traversal -  DF*:
	- initiator šalje upit "koja je max temp" - token sadrzi upit
	- svaki cvor koji primi zapise vlastitu temperaturu u tmax i pita dalje svoje susjede
	- kada dodje do zadnjeg cvora (koji vise nema susjeda za proslijediti poruku), on vraca svoju tmax senderu
	- ako je primljena tmax veca od moje, zapisi primljenu kao tmax
	- tmax se vracaju do initiatora
2) Flood:
	- initiator šalje tmax svim cvorovima

LOOP:
3) Ako neki cvor ocita t vecu od tmax, salje flood 
'''


from pymote.algorithms.broadcast import Flood
from pymote.message import Message


net_gen = NetworkGenerator(100) 
net = net_gen.generate_random_network()
#net.nodes.memory = myTemp, maxTemp

#based on DF*
#u token dodati zahtjev za temp
#u return message dodati tmax
#kada primi return message, usporediti primljeni tmax s vlastitim, promijeniti po potrebi


class Traversal(NodeAlgorithm):
    required_params = ('myTemp', 'maxTemp')
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = \
                node.compositeSensor.read()['Neighbors']
            #node.memory[self.myTemp] = node.TEMPSENSOR.read('__')
            #node.memory[self.maxTemp] = node.myTemp
            node.status = 'IDLE'
        ini_node = self.network.nodes()[0]
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,
                                              destination=ini_node))

    def initiator(self, node, message):
        if message.header == NodeAlgorithm.INI:
            node.memory['initiator'] = True
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            node.memory['next'] = node.memory['unvisited'].pop()
            if (node.memory['unvisited']):
                node.send(Message(header='T',
                                  destination=node.memory['next']))
                node.send(Message(header='Visited',
                                  destination=node.memory['unvisited']))
                node.status = 'VISITED'
            else:
                node.status = 'DONE'

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            self.first_visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'] = list(node.memory[self.neighborsKey])
            node.memory['unvisited'].remove(message.source)
            node.status = 'AVAILABLE'

    def available(self, node, message):
        if message.header == 'T':
            self.first_visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'].remove(message.source)

    def visited(self, node, message):
        if message.header == 'T':
            node.memory['unvisited'].remove(message.source)
            # late visited, should not happen in unitary communication delay
            if node.memory['next'] == message.source:
                self.visit(node, message)

        if message.header == 'Visited':
            node.memory['unvisited'].remove(message.source)
            if node.memory['next'] == message.source:
                self.visit(node, message)

        if message.header == 'Return':
            self.visit(node, message)

    def done(self, node, message):
        pass

    def first_visit(self, node, message):
        # TODO: initiator is redundant - it can be deduced from entry==None
        node.memory['initiator'] = False  
        node.memory['entry'] = message.source
        try:
            node.memory['unvisited'].remove(message.source)
        except ValueError:
            pass
        if (node.memory['unvisited']):
            node.memory['next'] = node.memory['unvisited'].pop()
            node.send(Message(header='T',
                              destination=node.memory['next']))
            node.send(Message(header='Visited',
                              destination=set(node.memory[self.neighborsKey]) -
                              set([node.memory['entry'],
                                   node.memory['next']])))
            node.status = 'VISITED'
        else:
            node.send(Message(header='Return',
                              destination=node.memory['entry']))
            node.send(Message(header='Visited',
                              destination=set(node.memory[self.neighborsKey]) -
                              set([node.memory['entry']])))
            node.status = 'DONE'

    def visit(self, node, message):
        if (node.memory['unvisited']):
            node.memory['next'] = node.memory['unvisited'].pop()
            node.send(Message(header='T',
                              destination=node.memory['next']))
        else:
            if not node.memory['initiator']:
                node.send(Message(header='Return',
                                  destination=node.memory['entry']))
            node.status = 'DONE'

    STATUS = {
        'INITIATOR': initiator,
        'IDLE': idle,
        'AVAILABLE': available,
        'VISITED': visited,
        'DONE': done,
    }

