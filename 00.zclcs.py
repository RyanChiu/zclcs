#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale, curses
from curses import wrapper

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

lines = []
offsets = [0, 0]

'''
all kinds of defines in the program
'''
CLC_DIRS = {
	'/media/40G/mldonkey-downloads/lib/incoming/files/',
	'/media/40G/rtorrent-downloads/files/'
}

STMP_DIRS = {
	'/media/40G/.stmp/',
	'/media/40G/TDDOWNLOAD/.stmp/'
}

'''
the main pgrogram here
'''
def main(stdscr):
	# clear screen
	stdscr.clear();
	stdscr.scrollok(True)
	stdscr.setscrreg(0, 30)

	# do the show off stuff below
	margin_left = 3;
	y = scr_files(stdscr, CLC_DIRS, 0, margin_left)
	y += 2 
	y = scr_files(stdscr, STMP_DIRS, y, margin_left)

	while True:
		c = stdscr.getch()
		if c in [curses.KEY_UP, curses.KEY_DOWN]:
			stdscr.addstr(0, 0, "oh, com'on!")
		elif c in [ord("q"), curses.KEY_HOME]:
			break
		
'''
all the functions & stuff needed in the main program
'''
def tnc_filename(filename, max):
	if (len(filename) >= max):
		return filename[0:(max-3)] + "..."
	else:
		return filename

def str_hsize(size):
	import bisect
	d = [(1024-1,'K'), (1024**2-1,'M'), (1024**3-1,'G'), (1024**4-1,'T')]
	s = [x[0] for x in d]
	index = bisect.bisect_left(s, size) - 1
	if index == -1:
		return str(round(size, 2))
	else:
		b, u = d[index]
	return str(round(size / (b+1), 2)) + u

def scr_files(scr, dirs, y, x):
	for path in dirs:
		files = os.listdir(path)
		scr.addstr(y, x, "in path [" + path + "]:", curses.A_BOLD)
		y += 1
		scr.addstr(y, x, '{0:3} {1:85} {2:7}'.format("#", "file name", "size"), curses.A_UNDERLINE)
		i = 0
		for file in files:
			y += 1
			scr.addstr(y, x, '{0:3} {1:85} {2:7}'.format(i, tnc_filename(file, 80), str_hsize(os.path.getsize(path + file))))
			i += 1
	return y

def prt_files(dirs):
	for path in dirs:
		files = os.listdir(path)
		print("in path [" + path + "]:")
		print('%3s %-80s %7s' % ("#", "file name", "size"))
		i = 0
		for file in files:
			print('%3s %-80s %7s' % (i, tnc_filename(file, 80), str_hsize(os.path.getsize(path + file))))
			i += 1

wrapper(main)
