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
from random import randint, random, sample, shuffle

import graph

START_TIME = time.time()
ABRT_TIME = START_TIME + 295.0
SHUFFLE_LIMIT = 50000
SHUFFLE_ABRT_TIME = START_TIME + 150.0
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
        '''Calculate the half-perimeter wire length (HPWL) of this net.
        Wire length is part of cost for a floorplan.
        '''
        xx = []
        yy = []
        for terminal in self.terminals:
            if isinstance(terminal, Block):
                center_x = (terminal.left_x + terminal.right_x) // 2
                center_y = (terminal.top_y + terminal.bottom_y) // 2
                xx.append(center_x)
                yy.append(center_y)
            elif isinstance(terminal, Terminal):
                xx.append(terminal.x)
                yy.append(terminal.y)
        return (max(xx) - min(xx)) + (max(yy) - min(yy))

class Floorplan:
    '''Floorplan consisting of copious blocks. Overlap among blocks is not allowed.
    The left-bottom corner is considered origin (0, 0), and no space is needed between two blocks.
    '''
    def __init__(self, alpha):
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
        self._initialize_seq_pair()
        # self.seq_pair = ([0,6,3,4,1,5,2,7], [7,3,6,1,4,2,5,0])
        # print(self.seq_pair)

        best_sol = copy.deepcopy(self.seq_pair) # Best
        temp = 200.0 # T
        uphill_lim = 50 * len(self.blocks) # N
        cool_ratio = 0.98

        move_cnt = 0 # MT
        uphill = 0 # uphill
        reject_cnt = 0 # reject

        width, height = self._calc_area()
        wire_len = self._calc_wire_len()
        cost = self._calc_cost(self._calc_area_cost(), wire_len)
        best_cost = cost
        print('Init cost: {:,}'.format(cost))

        # while reject ratio in previous round was not so high and time is not up
        while True:
            move_cnt = 0
            uphill = 0
            reject_cnt = 0
            while True:
                move = randint(0, 1)
                # print('cur move: {}'.format(move))
                if move == 0:
                    # Move1: swap 2 blocks in posive sequence only
                    idxes = sample(range(len(self.blocks)), 2) # index of block in list to swap
                    old_seq_pair = copy.deepcopy(self.seq_pair)
                    (self.seq_pair[0][idxes[0]], self.seq_pair[0][idxes[1]]) = (
                        self.seq_pair[0][idxes[1]], self.seq_pair[0][idxes[0]])
                elif move == 1:
                    # Move2: swap 2 blocks in both positive and negative sequences
                    old_seq_pair = copy.deepcopy(self.seq_pair)
                    blk_idxes = sample(range(len(self.blocks)), 2)
                    idx0_in_p_seq = self.seq_pair[0].index(blk_idxes[0])
                    idx1_in_p_seq = self.seq_pair[0].index(blk_idxes[1])
                    (self.seq_pair[0][idx0_in_p_seq], self.seq_pair[0][idx1_in_p_seq]) = (
                        self.seq_pair[0][idx1_in_p_seq], self.seq_pair[0][idx0_in_p_seq])
                    idx0_in_n_seq = self.seq_pair[1].index(blk_idxes[0])
                    idx1_in_n_seq = self.seq_pair[1].index(blk_idxes[1])
                    (self.seq_pair[1][idx0_in_n_seq], self.seq_pair[1][idx1_in_n_seq]) = (
                        self.seq_pair[1][idx1_in_n_seq], self.seq_pair[1][idx0_in_n_seq])
                else:
                    # Move3: rotate arbitrary block
                    # TODO: block rotation needs the configuration of rotation of each block
                    old_seq_pair = copy.deepcopy(self.seq_pair)

                new_width, new_height = self._calc_area()
                new_wire_len = self._calc_wire_len()

                new_cost = self._calc_cost(self._calc_area_cost(), new_wire_len)
                delta_cost = new_cost - cost
                move_cnt += 1

                if (delta_cost < 0.0 or random() < math.exp(-1*delta_cost/temp) or
                        self._is_valid(new_width, new_height)):
                    # print('Delta cost: {}'.format(delta_cost), flush=True)
                    cost = new_cost
                    if delta_cost > 0:
                        uphill += 1
                    if new_cost < best_cost or self._is_valid(new_width, new_height):
                        best_sol = copy.deepcopy(self.seq_pair)
                        best_cost = new_cost
                else:
                    # restore sequence pair
                    self.seq_pair = old_seq_pair
                    reject_cnt += 1
                if (uphill > uphill_lim) or (move_cnt > 2*uphill_lim) or (time.time() >= ABRT_TIME):
                    break
            temp = cool_ratio * temp
            if (reject_cnt/move_cnt) > 0.99 or (time.time() >= ABRT_TIME):
                if time.time() >= ABRT_TIME:
                    print('SA ends at time-up', flush=True)
                else:
                    print('SA ends due to heavy rejection', flush=True)
                break

        self.seq_pair = best_sol
        width, height = self._calc_area()
        print('Best cost: {:,}'.format(best_cost))
        print('Area: {}x{}={:,}'.format(width, height, width*height))
        print('Target: {}x{}={:,}'.format(self.w_limit, self.h_limit, self.w_limit*self.h_limit))

    def parse_block_file(self, block_file):
        '''Parse input block file.
        '''
        try:
            with open(block_file, 'rt') as f:
                self.w_limit, self.h_limit = [int(str_) for str_ in f.readline().split()[1:]]
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

    def calc_cost(self):
        '''Calculate cost considering both area and hpwl.
        '''
        width, height = self._calc_area()
        hpwl = self._calc_wire_len()
        return self._calc_cost(width*height, hpwl)

    def print_rpt(self, file_name='output.rpt'):
        '''Print floorplan result to file.
        '''
        width, height = self._calc_area()
        hpwl = self._calc_wire_len()
        cost = self._calc_cost(width*height, hpwl)
        with open(file_name, 'wt') as ofile:
            print(cost, file=ofile)
            print(hpwl, file=ofile)
            print(width*height, file=ofile)
            print('{} {}'.format(width, height), file=ofile)
            print('{:.0f}'.format(time.time()-START_TIME), file=ofile)
            for block in self.blocks:
                print('{0.name} {0.left_x} {0.bottom_y} {0.right_x} {0.top_y}'.format(block),
                      file=ofile)

    def _calc_cost(self, area, wire_len):
        '''Calculate final cost considering both area and wire length.
        '''
        return self.alpha * area + (1 - self.alpha) * wire_len

    def _calc_wire_len(self):
        '''Calculate cost in terms of area and wire length.
        '''
        hpwl = 0
        for net in self.nets:
            hpwl += net.calc_length()
        return hpwl

    def _calc_area(self):
        '''Construct constraint graph, HCG and VCG based on sequence pair to find out the size of
        floorplan.
        Return (width, height).
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
                    'duplicate block index {} in sequence pair'.format(
                        self.seq_pair[1].index(pair[0])))
        hcg.connect_to_st()
        vcg.connect_to_st()
        weight = hcg.get_target_weight()
        height = vcg.get_target_weight()
        return weight, height

    def _is_valid(self, width, height):
        '''Return True is current floorplan can fit into bounding box.
        '''
        return width <= self.w_limit and height < self.h_limit

    def _calc_area_cost(self):
        '''Calculate area cost and take whether current floorplan from self.seq_pair can fit into
        bounding box into consideration.
        '''
        width, height = self._calc_area()
        # if current area is already smaller both in width and height
        if width < self.w_limit and height < self.h_limit:
            return 0
        width = self.h_limit if width < self.w_limit else width
        height = self.w_limit if height < self.h_limit else height
        return width*height

    def _initialize_seq_pair(self):
        '''Initialize sequence pair (self.seq_pair) by shuffling it.
        '''
        self.seq_pair = (list(range(len(self.blocks))), list(range(len(self.blocks))))
        best_sol = copy.deepcopy(self.seq_pair)

        width, height = self._calc_area()
        best_area = width * height
        bbox_area = self.w_limit * self.h_limit
        for _ in range(SHUFFLE_LIMIT):
            shuffle(self.seq_pair[0])
            shuffle(self.seq_pair[1])
            new_width, new_height = self._calc_area()
            new_area = new_width * new_height
            if new_area < 3.5 * bbox_area and new_area < best_area:
                best_area = new_area
                best_sol = copy.deepcopy(self.seq_pair)
                print('Shuffle: {}x{}={:,}'.format(new_width, new_height, new_width*new_height))
            else:
                self.seq_pair = copy.deepcopy(best_sol)
            if time.time() >= SHUFFLE_ABRT_TIME:
                print('Shuffle terminated due to limit on time')
                break

def parse_cmd_line(argv):
    '''Parse the argumets in command line.
    '''
    parser = argparse.ArgumentParser(description='PDA PA3 - Fixed Outline Floorplanning')
    parser.add_argument('alpha', metavar='<alpha>', type=float,
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
    flpr.print_rpt(args.output_file)

if __name__ == '__main__':
    main(sys.argv[1:])
    print('Elapsed time: {:.3f} secs'.format(time.time()-START_TIME))
