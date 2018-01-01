'''2017PDA PA3 - Fixed Outline Floorplanning.

Graph manimulation elements.
'''

class Graph:
    '''Graph.
    '''
    def __init__(self):
        self.nodes = []
        # TODO: connect nodes
    def add_node(self, block):
        '''Add new node to graph.
        Block is waht this this node represents.
        '''
        new_node = Node(block)
        self.nodes.append(new_node)

    def init_count(self):
        '''Initialize counts of nodes to their number of in-nodes.
        '''
        for node in self.nodes:
            node.init_count()

class Node:
    '''Node.
    '''
    def __init__(self, block):
        self.block = block
        self.in_nodes = [] # nodes, which serve as input nodes to this node
        self.out_nodes = [] # output nodes
        self.count = 0
        self.level = 0

    def add_in_node(self, in_node):
        '''Add ancestor node.
        '''
        self.in_nodes.append(in_node)

    def add_out_node(self, out_node):
        '''Add descendant node.
        '''
        self.out_nodes.append(out_node)

    def inc_count(self):
        '''Increase count.
        '''
        self.count += 1

    def dec_count(self):
        '''Decrease count.
        '''
        self.count -= 1
  
    def init_count(self):
        '''Initialize count to number of input nodes.
        '''
        self.count = len(self.in_nodes)
