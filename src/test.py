#!/usr/bin/env python3
import sys
import os
import click
import argparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Required positional argument
parser.add_argument('pos_arg', type=int,
                    help='A required integer positional argument')

# Optional positional argument
parser.add_argument('opt_pos_arg', type=int, nargs='?',
                    help='An optional integer positional argument')

# Optional argument
parser.add_argument('--opt_arg', type=int,
                    help='An optional integer argument')

# Switch
parser.add_argument('--switch', action='store_true',
                    help='A boolean switch')

print(sys.argv)
args = parser.parse_args()

print("Argument values:")
print(args.pos_arg)
print(args.opt_pos_arg)
print(args.opt_arg)
print(args.switch)
print()

cmd = sys.argv[0]
argument = ['1', '2', '--opt_arg', '4', '--switch']
sys.argv = [cmd] + argument

args = parser.parse_args()

print("Argument values:")
print(args.pos_arg)
print(args.opt_pos_arg)
print(args.opt_arg)
print(args.switch)
