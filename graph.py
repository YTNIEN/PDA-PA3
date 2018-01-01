'''2017PDA PA3 - Fixed Outline Floorplanning.

Elements for graph manipulation.
'''

class Dag:
    '''Directed Acyclic Graph (DAG).
    '''
    def __init__(self, blocks):
        self.nodes = []
        self.name_to_nodes = {}
        self.source = Node(None)
        self.terminal = Node(None)
        self._create_nodes(blocks)
        # TODO: connect nodes

    def connect(self, from_idx, to_idx):
        '''Connect two nodes in both directions.
        '''
        from_node = self.nodes[from_idx]
        to_node = self.nodes[to_idx]
        from_node.add_out_node(to_node)
        to_node.add_in_node(from_node)

    def connect_to_st(self):
        '''Connect those without in_nodes to source, those without out_nodes to terminal.
        '''
        for node in self.nodes:
            if not node.in_nodes:
                self.source.add_out_node(node)
                node.add_in_node(self.source)
            elif not node.out_nodes:
                self.terminal.add_in_node(node)
                node.add_out_node(self.terminal)

    def init_count(self):
        '''Initialize counts of nodes to their number of in-nodes.
        '''
        for node in self.nodes:
            node.init_count()

    def _create_nodes(self, blocks):
        '''Create new node to graph.
        Each node is created for each block sent, and stands for it.
        '''
        for blk in blocks:
            node = Node(blk)
            self.nodes.append(node)
            self.name_to_nodes[blk.name] = node

    def _print(self):
        '''Print interconnection of nodes.
        '''
        for node in self.nodes:
            print('> {}'.format(node.block.name))
            for in_node in node.in_nodes:
                try:
                    print('{} ->'.format(in_node.block.name))
                except AttributeError:
                    print('Source ->')
            for out_node in node.out_nodes:
                try:
                    print('-> {}'.format(out_node.block.name))
                except AttributeError:
                    print('-> Terminal')
        print('> Source')
        for out_node in self.source.out_nodes:
            print('-> {}'.format(out_node.block.name))
        print('> Terminal')
        for in_node in self.source.in_nodes:
            print('{} ->'.format(in_node.block.name))

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
