#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale, curses
from curses import wrapper

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

lines = []
offsets = [0, 0]
fcsidx = -1

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
	stdscr.clear()

	# do the show off stuff below
	apd_files(CLC_DIRS)
	apd_files(STMP_DIRS)

	scrolllines(stdscr, 0)

	while True:
                ch = stdscr.getch()
                if ch == ord('q'):
                        break
                elif ch == curses.KEY_UP:
                        scrolllines(stdscr, 1)
                elif ch == curses.KEY_DOWN:
                        scrolllines(stdscr, -1)
                elif ch == ord('u'):
                        mvfcs(-1)
                        scrolllines(stdscr, 0)
			shw_status(stdscr, "file")
                elif ch == ord('j'):
                        mvfcs(1)
                        scrolllines(stdscr, 0)
			shw_status(stdscr, "file")
		elif ch in (curses.KEY_ENTER, 10):
			continue
		else:
                        continue

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

def apd_files(dirs):
	for path in dirs:
		files = os.listdir(path)
		exp_line(True, False, "in path [" + path + "]:", curses.A_BOLD, "", "")
		exp_line(True, False, '{0: ^3} {1:85} {2:7}'.format("#", "file name", "size"), curses.A_UNDERLINE, "", "")
		i = 0
		for fn in files:
			exp_line(False, False, '{0: ^3} {1:85} {2:7}'.format(i, tnc_filename(fn, 80), str_hsize(os.path.getsize(path + fn))), 0, path, fn)
			i += 1

def get_fcsline():
	for line in lines:
		if line['fcs'] and not line['skp']:
			return line

def exp_line(skp, fcs, txt, dcr, phn, fln):
	lines.append({"skp" : skp, "fcs" : fcs, "txt" : txt, "dcr" : dcr, "phn" : phn, "fln" : fln})

def shw_status(stdscr, mode):
	if mode == "file":
		if fcsidx < 0 or fcsidx >= (len(lines) - 1):
			return
		line = get_fcsline()
		mva_bottom(stdscr, "\"{}\"".format(line['phn'] + line['fln']))
	elif mode == "":
		return

def mva_bottom(stdscr, txt):
	yx = stdscr.getmaxyx()
	l = ""
	for i in range(0, yx[1] - 1):
		l += " "
	stdscr.addstr(yx[0] - 1, 0, l)
	stdscr.addstr(yx[0] - 1, 0, txt)
	

def mvfcs(step):
        global fcsidx
        fcsidx += step
        while fcsidx >= 0 and fcsidx < len(lines) and lines[fcsidx]['skp']:
                if step < 0:
                        fcsidx -= 1
                elif step > 0:
                        fcsidx += 1
        if fcsidx < -1:
                fcsidx = -1
        elif fcsidx >= len(lines):
                fcsidx = len(lines)
        setfcsline(fcsidx)

def setfcsline(idx):
        i = 0
        for line in lines:
                if i == idx:
                        line['fcs'] = True
                else:
                        line['fcs'] = False
                i += 1

def scrolllines(scr, step):
        yx = scr.getmaxyx()
        offsets[0] -= step
        if offsets[0] < 0:
                offsets[0] += step
        elif offsets[0] > len(lines):
                offsets[0] = len(lines) - 1
        elif (len(lines) - offsets[0]) < yx[0]:
                offsets[0] += step
        h = offsets[0] + yx[0]
        if h > len(lines):
                h = len(lines) - offsets[0]
        y = 0
        for i in range(offsets[0], h):
                t = "";
                if lines[i]['fcs']:
                        t = "[*]"
		if yx[1] > (300 - 5):
                	scr.addstr(y, 0, "{0: ^5} {1:300}".format(t, lines[i]['txt']), lines[i]['dcr'])
		else:
			w = yx[1] - 5
			scr.addstr(y, 0, "{0: ^5} {1}".format(t, tnc_filename(lines[i]['txt'], w)), lines[i]['dcr'])
                y += 1

wrapper(main)
