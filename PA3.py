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
Terminal = namedtuple('Terminal', ['x', 'y'])

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
        return self._width if not self.is_rotated else self._height

    def get_height(self):
        '''Get height.
        '''
        return self._height if not self.is_rotated else self._width

    def rotate(self):
        '''Rotate this block.
        '''
        self.is_rotated = True if not self.is_rotated else False

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
    def __init__(self):
        '''
        '''
        pass

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
    print(type(args.alpha))
    return args

def main(argv):
    '''Main function.
    '''
    print('PDA PA3 - Fixed Outline Floorplanning')
    parse_cmd_line(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
