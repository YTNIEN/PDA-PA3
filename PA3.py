#! /uhome/chome/2017PDA/2017PDA01/anaconda3/bin/python3
# -*- encoding: utf-8 -*-
'''2017PDA PA3 - Fixed Outline Floorplanning.

Given a set of rectangular macros, or blocks, and a set of nets,
a floorplaner places and packs all the macros into a bounding box without overlapping,
optimizing total area overhead and net wirelength.
'''
# pylint: disable=R0902, R0903

import argparse
import copy
import math
import sys
import time
from collections import namedtuple
from itertools import combinations
from random import randint, random, sample

import graph

START_TIME = time.time()
Terminal = namedtuple('Terminal', ['name', 'x', 'y'])

class Block:
    '''Hard circuit block, say macro, to place in floorplan.
    '''
    def __init__(self, name, width, height):
        '''Set name, width, height of a block.
        '''
        self.name = name
        self._width = width
        self._height = height
        self.is_rotated = False
        self.left_x = -1
        self.bottom_y = -1
        self.right_x = -1
        self.top_y = -1

    def get_width(self):
        '''Get width.
        '''
        return self._width

    def get_height(self):
        '''Get height.
        '''
        return self._height

    def rotate(self):
        '''Rotate this block.
        '''
        self.is_rotated = True if not self.is_rotated else False
        self._width, self._height = self._height, self._width

    def __repr__(self):
        return "Block(name='{0.name}', width={0._width}, height={0._height})".format(self)

class Net:
    '''Interconnect between blocks and terminals.
    '''
    def __init__(self, terminals):
        '''Initialize a net connecting terminals, which include certain blocks and terminal
        '''
        self.terminals = terminals

    def calc_length(self):
        '''Calculate the half-perimeter wire length of this net.
        Wire length is part of cost for a floorplan.
        '''
        #TODO: implement length estimation
        pass

class Floorplan:
    '''Floorplan consisting of copious blocks. Overlap among blocks is not allowed.
    The left-bottom corner is considered origin (0, 0), and no space is needed between two blocks.
    '''
    def __init__(self, alpha):
        '''
        '''
        self.alpha = alpha
        self.w_limit = -1
        self.h_limit = -1
        self.blocks = []
        self.name_to_block = {}
        self.terminals = []
        self.name_to_terminal = {}
        self.nets = []
        self.seq_pair = None

    def place_block(self):
        '''Do floorplanning via simulated-annealing.
        '''
        # initial solution
        self.seq_pair = (list(range(len(self.blocks))), list(range(len(self.blocks))))
        # self.seq_pair = ([0,6,3,4,1,5,2,7], [7,3,6,1,4,2,5,0])
        print(self.seq_pair)

        # TODO: tune annealing parameter
        best_sol = copy.deepcopy(self.seq_pair) # Best
        temp = 1000.0 # T
        move_cnt = 0 # MT
        uphill = 0 # uphill
        uphill_lim = 200 * len(self.blocks) # N
        reject_cnt = 0 # reject
        cool_ratio = 0.95

        width, height = self._calc_area_cost()
        wire_len = self._calc_wire_cost()
        cost = self._calc_cost(width*height, wire_len)
        best_cost = cost
        print('Init cost: {:,}'.format(cost))
        input()

        # while reject ratio in previous round was not so high and time is not up
        while True:
            move_cnt = 0
            uphill = 0
            reject_cnt = 0
            while True:
                move = randint(0, 0)
                # print('cur move: {}'.format(move))
                if move == 0:
                    # swap posive sequence only
                    idxes = sample(range(len(self.blocks)), 2)
                    # print(idxes)
                    old_seq_pair = copy.deepcopy(self.seq_pair)
                    (self.seq_pair[0][idxes[0]], self.seq_pair[0][idxes[1]]) = (self.seq_pair[0][idxes[1]], self.seq_pair[0][idxes[0]])
                elif move == 1:
                    pass
                else:
                    # FIXME: block rotation needs the configuration of rotation of each block
                    pass
                new_width, new_height = self._calc_area_cost()
                new_wire_len = self._calc_wire_cost()

                new_cost = self._calc_cost(new_width * new_height, new_wire_len)
                delta_cost = new_cost - cost
                move_cnt += 1

                if delta_cost < 0.0 or random() < math.exp(-1*delta_cost/temp):
                    # print('Delta cost: {}'.format(delta_cost), flush=True)
                    cost = new_cost
                    if delta_cost > 0:
                        uphill += 1
                    if new_cost < best_cost:
                        best_sol = copy.deepcopy(self.seq_pair)
                        best_cost = new_cost
                else:
                    # restore sequence pair
                    self.seq_pair = old_seq_pair
                    reject_cnt += 1

                if uphill > uphill_lim or move_cnt > 2*uphill_lim:
                    break
            temp = cool_ratio * temp
            # FIXME: add termination condition in terms of T
            if (reject_cnt/move_cnt) > 0.95 or (time.time() - START_TIME) >= 50.0:
                if reject_cnt/move_cnt > 0.95:
                    print('SA ends due to tons of rejection', flush=True)
                else:
                    print('SA ends at time-up', flush=True)
                break
        print('Best cost: {:,}'.format(best_cost))

    def parse_block_file(self, block_file):
        '''Parse input block file.
        '''
        try:
            with open(block_file, 'rt') as f:
                self.w_limit, self.h_limit = f.readline().split()[1:]
                nblock = int(f.readline().split()[1])
                nterminal = int(f.readline().split()[1])
                for line in f:
                    if not line.strip():
                        continue
                    strs = line.split()
                    if strs[1] == 'terminal':
                        terminal = Terminal(name=strs[0], x=int(strs[2]), y=int(strs[3]))
                        self.terminals.append(terminal)
                        self.name_to_block[terminal.name] = terminal
                    else:
                        block = Block(name=strs[0], width=int(strs[1]), height=int(strs[2]))
                        self.blocks.append(block)
                        self.name_to_block[block.name] = block
                assert len(self.blocks) == nblock, 'Wrong block number'
                assert len(self.terminals) == nterminal, 'Wrong terminal number'
        except OSError as err:
            sys.exit(err)

    def parse_net_file(self, net_file):
        '''Parse input net files.
        '''
        try:
            with open(net_file, 'rt') as f:
                # read first line for NumNets
                nnet = int(f.readline().split()[1]) # net count
                for line in f:
                    # skip blank line, say line with '\n' only
                    if not line.strip():
                        continue
                    line = line.split()
                    if line[0] == 'NetDegree:':
                        terminal_cnt = int(line[1])
                        terminals = []
                        for _ in range(terminal_cnt):
                            term_name = f.readline().strip()
                            if term_name in self.name_to_block:
                                terminals.append(self.name_to_block[term_name])
                            elif term_name in self.name_to_terminal:
                                terminals.append(self.name_to_terminal[term_name])
                            else:
                                print('Error: found terminal/block not specified in block file',
                                      file=sys.stderr)
                                sys.exit()
                        net = Net(terminals)
                        self.nets.append(net)
                    else:
                        print('Error: in parsing net file', file=sys.stderr)
                        sys.exit()
                assert nnet == len(self.nets), 'Net number not equivalent'

        except OSError as err:
            sys.exit(err)

    def _calc_cost(self, area, wire_len):
        '''Calculate final cost considering both area and wire length.
        '''
        return self.alpha * area + (1 - self.alpha) * wire_len

    def _calc_wire_cost(self):
        '''Calculate cost in terms of area and wire length.
        '''
        # wire length: HPWL of each net
        # TODO: add wire cost implementation
        return 0

    def _calc_area_cost(self):
        '''Construct constraint graph, HCG and VCG based on sequence pair and return width and
        height of floorplan.
        '''
        hcg = graph.Hcg(self.blocks) # horizontal constraint graph
        vcg = graph.Vcg(self.blocks) # vertical constraint graph
        for pair in combinations(self.seq_pair[0], 2):
            # print(pair)
            if self.seq_pair[1].index(pair[0]) < self.seq_pair[1].index(pair[1]):
                # horizontal constraint
                # print('Block "{}" is to the left of block "{}"'.format(self.blocks[pair[0]].name,
                #                                                        self.blocks[pair[1]].name))
                # print('HCG: {} -> {}'.format(*pair))
                hcg.connect(pair[0], pair[1])
            elif self.seq_pair[1].index(pair[0]) > self.seq_pair[1].index(pair[1]):
                # vertical constraint
                # print('Block "{}" is below block "{}"'.format(self.blocks[pair[1]].name,
                #                                                        self.blocks[pair[0]].name))
                # print('VCG: {} -> {}'.format(*pair))
                vcg.connect(pair[1], pair[0])
            else:
                assert self.seq_pair[1].index(pair[0]) != self.seq_pair[1].index(pair[1]), (
                'duplicate block index {} in sequence pair'.format(self.seq_pair[1].index(pair[0])))

        hcg.connect_to_st()
        vcg.connect_to_st()
        # modified BFS to find longest path
        # the accumulated weight at target in VCG and HCG is the size of floorplan
        weight = hcg.get_target_weight()
        height = vcg.get_target_weight()
        return weight, height

def parse_cmd_line(argv):
    '''Parse the argumets in command line.
    '''
    parser = argparse.ArgumentParser(description='PDA PA3 - Fixed Outline Floorplanning')
    parser.add_argument('alpha', metavar='<alpha α>', type=float,
                        help=('User defined ratio to balance chip area and wire length'))
    parser.add_argument('block_file', metavar='<input_block>', help='Input.block name')
    parser.add_argument('net_file', metavar='<input_net>', help='Input.net name')
    parser.add_argument('output_file', metavar='<output>', help='output name')
    args = parser.parse_args(argv)
    return args

def main(argv):
    '''Main function.
    '''
    print('PDA PA3 - Fixed Outline Floorplanning')
    args = parse_cmd_line(argv)
    flpr = Floorplan(args.alpha)
    flpr.parse_block_file(args.block_file)
    flpr.parse_net_file(args.net_file)
    flpr.place_block()
    # - sequence pair
    # - HPWL
    # - longest path by modified BFS

if __name__ == '__main__':
    main(sys.argv[1:])
