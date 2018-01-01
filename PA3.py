#! /uhome/chome/2017PDA/2017PDA01/anaconda3/bin/python3
# -*- encoding: utf-8 -*-
'''2017PDA PA3 - Fixed Outline Floorplanning.

Given a set of rectangular macros, or blocks, and a set of nets,
a floorplaner places and packs all the macros into a bounding box without overlapping,
optimizing total area overhead and net wirelength.
'''

import sys
import time
import argparse
# import tkinter as tk

from collections import namedtuple

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
        self.up_y = -1

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
            print(err, file=sys.stderr)

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
            print(err, file=sys.stderr)

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
    flpr = Floorplan(argv.alpha)
    # parse block
    flpr.parse_block_file(args.block_file)
    # parse net
    flpr.parse_net_file(args.net_file)
    # sequence pair
    # - longest path by modified BFS

if __name__ == '__main__':
    main(sys.argv[1:])
