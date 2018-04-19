from pymote import NetworkGenerator
from pymote.npickle import write_pickle
from pymote.algorithms.maximumfind import MaxFind
from pymote.algorithms.saturation import Saturation
from pymote.simulation import Simulation
from networkx import minimum_spanning_tree

net_gen = NetworkGenerator(30)
net = net_gen.generate_random_network()
#net.show()
graph_tree = minimum_spanning_tree(net)
net.adj = graph_tree.adj
#net.show()

net.algorithms = (MaxFind, )

# = net.nodes()[0]# uzimamo prvi cvor u listi cvorova mreze
#some_node.memory['I'] = 'Activate'

# some_node_2 = net.nodes()[2]# uzimamo prvi cvor u listi cvorova mreze
# some_node_2.memory['I'] = 'Activate'


write_pickle(net,'mreza.tar.gz')

sim = Simulation(net)
sim.run()
#write_pickle(net,'mreza.tar.gz')
