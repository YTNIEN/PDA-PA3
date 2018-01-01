'''2017PDA PA3 - Fixed Outline Floorplanning.

Elements for graph manipulation.
'''

from collections import deque

class Dag:
    '''Directed Acyclic Graph (DAG).
    '''
    def __init__(self, blocks):
        self.nodes = []
        self.name_to_nodes = {}
        self.source = Node(None)
        self.target = Node(None) # target not terminal
        self._create_nodes(blocks)

    def connect(self, from_idx, to_idx):
        '''Connect two nodes in both directions.
        '''
        from_node = self.nodes[from_idx]
        to_node = self.nodes[to_idx]
        from_node.add_out_node(to_node)
        to_node.add_in_node(from_node)

    def connect_to_st(self):
        '''Connect those without in_nodes to source, those without out_nodes to target.
        '''
        for node in self.nodes:
            if not node.in_nodes:
                self.source.add_out_node(node)
                node.add_in_node(self.source)
            if not node.out_nodes:
                self.target.add_in_node(node)
                node.add_out_node(self.target)

    def init_count(self):
        '''Initialize counts of nodes to their number of in-nodes.
        '''
        for node in self.nodes:
            node.init_count()
        self.target.init_count()
        self.source.init_count()

    def get_target_weight(self):
        '''Return calculated final weight (width or height of floorplan).
        '''
        raise NotImplementedError

    def _propagate_weights(self):
        '''Propagate node weights from source to target.
        '''
        # TODO: no leaving most common login to derived class
        raise NotImplementedError

    def _create_nodes(self, blocks):
        '''Create new node to graph.
        Each node is created for each block sent, and stands for it.
        '''
        for blk in blocks:
            node = Node(blk)
            self.nodes.append(node)
            self.name_to_nodes[blk.name] = node

    def _set_coord(self):
        raise NotImplementedError

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
                    print('-> Target')
        print('> Source')
        for out_node in self.source.out_nodes:
            print('-> {}'.format(out_node.block.name))
        print('> Target')
        for in_node in self.target.in_nodes:
            print('{} ->'.format(in_node.block.name))

    def _print_weight(self):
        '''Print weight of node, which is right-x of corresponding block in floorplan.
        '''
        for node in self.nodes:
            print('{} x: {}'.format(node.block.name, node.weight))

class Hcg(Dag):
    '''Horizontal constraint graph.
    '''
    def __init__(self, blocks):
        Dag.__init__(self, blocks)

    def _propagate_weights(self):
        '''Create new node to graph.
        Each node is created for each block sent, and stands for it.
        '''
        self.init_count()
        visited = set()
        queue = deque([self.source])
        while queue:
            cur = queue.popleft()
            visited.add(cur)
            for out in cur.out_nodes:
                out.dec_count()
                if cur.weight > out.weight:
                    out.weight = cur.weight
                if out.count == 0:
                    # set weight
                    try:
                        out.weight += out.block.get_width()
                    except AttributeError:
                        # encounter target
                        pass
                    queue.append(out)

    def get_target_weight(self):
        '''Return calculated final weight (width of floorplan).
        '''
        self._propagate_weights()
        self._set_coord()
        return self.target.weight

    def _set_coord(self):
        '''Set left-x and right-x of block.
        '''
        for node in self.nodes:
            node.block.left_x = node.weight - node.block.get_width()
            node.block.right_x = node.weight
            # print('{}: {} to {}'.format(node.block.name, node.block.left_x, node.block.right_x))

class Vcg(Dag):
    '''Horizontal constraint graph.
    '''
    def __init__(self, blocks):
        Dag.__init__(self, blocks)

    def _propagate_weights(self):
        '''Create new node to graph.
        Each node is created for each block sent, and stands for it.
        '''
        self.init_count()
        visited = set()
        queue = deque([self.source])
        while queue:
            cur = queue.popleft()
            visited.add(cur)
            for out in cur.out_nodes:
                out.dec_count()
                if cur.weight > out.weight:
                    out.weight = cur.weight
                if out.count == 0:
                    # set weight
                    try:
                        out.weight += out.block.get_height()
                    except AttributeError:
                        # enounter target
                        pass
                    queue.append(out)

    def get_target_weight(self):
        '''Return calculated final weight (height of floorplan).
        '''
        self._propagate_weights()
        self._set_coord()
        return self.target.weight

    def _set_coord(self):
        '''Set bottom-y and top-y of block.
        '''
        for node in self.nodes:
            node.block.bottom_y = node.weight - node.block.get_height()
            node.block.top_y = node.weight
            # print('{}: {} to {}'.format(node.block.name, node.block.bottom_y, node.block.top_y))

class Node:
    '''Node.
    '''
    def __init__(self, block):
        self.block = block
        self.in_nodes = [] # nodes, which serve as input nodes to this node
        self.out_nodes = [] # output nodes
        self.count = 0
        self.level = 0
        self.weight = 0

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
