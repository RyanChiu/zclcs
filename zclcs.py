#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale, curses, shutil, ConfigParser
from curses import wrapper

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

config = ConfigParser.ConfigParser()
config.read("./zclcs.conf")
items = config.items("DIRS")
DIRS = []
for item in items:
	DIRS.append(item[1])

'''
all kinds of defines in the program
'''
lines = []
offsets = [0, 0]
fcsidx = -1
pnu = 0

'''
the main pgrogram here
'''
def main(stdscr):
	curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

	# clear screen
	stdscr.clear()

	# do the show off stuff below
	apd_files(DIRS)

	scrolllines(stdscr, 0)

	while True:
                ch = stdscr.getch()
		line = get_fcsline()
		fn = ""
		if line != {}:
			fn = os.path.join(line['phn'], line['fln'])
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
		elif ch == ord('d'):
			if not fn:
				continue
			mva_bottom(stdscr, "delete it, y/n?")
			while True:
				d_ch = stdscr.getch()
				if d_ch == ord('y'):
					if os.path.isdir(fn):
						shutil.rmtree(fn)
					else:
						os.remove(fn)
					del_fcsline()
					stdscr.clear()
					scrolllines(stdscr, 0)
					shw_status(stdscr, "file")
					break
				elif d_ch == ord('n'):
					shw_status(stdscr, "file")
					break
				else:
					mva_bottom(stdscr, "please enter y to make sure, or n to cancel it.")
		elif ch == ord('m'):
			if not fn:
				continue
			mva_bottom(stdscr, "please hit the number(#x) of the path to move into, or 'c' to cancel out.")
			while True:
				m_ch = stdscr.getch()
				if m_ch >= ord('0') and m_ch <= ord('9'):
					plines = get_pthlines()
					sidx = int(m_ch) - 48
					if sidx < len(plines):
						mva_bottom(stdscr, "move into \"{}\", y/n?".format(plines[sidx]["phn"]))
				elif m_ch == ord('y'):
					shutil.move(fn, plines[sidx]["phn"])
					global lines, pnu
					lines = []
					pnu = 0
					apd_files(DIRS)
					stdscr.clear()
					scrolllines(stdscr, 0)
					break
				elif m_ch == ord('n'):
					mva_bottom(stdscr, "please hit the number(#x) of the path to move into, or 'c' to cancel out.")
				elif m_ch == ord('c'):
					shw_status(stdscr, "file")
					break
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
	global pnu
	for path in dirs:
		files = os.listdir(path)
		exp_line(True, False, pnu, "#{0} in path [{1}]:".format(pnu, path), curses.color_pair(2), path, "")
		exp_line(True, False, -1, '{0: ^3} {1:85} {2:7}'.format("#", "file name", "size"), curses.A_UNDERLINE, "", "")
		i = 0
		for fn in files:
			exp_line(False, False, pnu, '{0: ^3} {1:85} {2:7}'.format(i, tnc_filename(fn, 80), str_hsize(os.path.getsize(os.path.join(path, fn)))), 0, path, fn)
			i += 1
		pnu += 1

def get_fcsline():
	for line in lines:
		if line['fcs'] and not line['skp']:
			return line
	return {}

def get_pthlines():
	plines = []
	for line in lines:
		if line['pnu'] != -1 and line['phn'] != "" and line['fln'] == "":
			plines.append(line)
	return plines

def del_line(idx):
	if idx < 0 and idx >= (len(lines) - 1):
		return
	del lines[idx]

def del_fcsline():
	del_line(fcsidx)
	mvfcs(1)

def exp_line(skp, fcs, pnu, txt, dcr, phn, fln):
	lines.append({"skp" : skp, "fcs" : fcs, "pnu" : pnu, "txt" : txt, "dcr" : dcr, "phn" : phn, "fln" : fln})

def shw_status(stdscr, mode):
	if mode == "file":
		if fcsidx < 0 or fcsidx >= len(lines):
			return
		line = get_fcsline()
		mva_bottom(stdscr, "\"{}\"".format(os.path.join(line['phn'], line['fln'])))
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
                t = ""
		t_dcr = lines[i]['dcr']
                if lines[i]['fcs']:
                        t = "[*]"
			t_dcr = curses.A_BOLD
		if yx[1] > (300 - 5):
                	scr.addstr(y, 0, "{0:3} {1:300}".format(t, lines[i]['txt']), t_dcr)
		else:
			w = yx[1] - 5
			scr.addstr(y, 0, "{0:3} {1}".format(t, tnc_filename(lines[i]['txt'], w)), t_dcr)
                y += 1

wrapper(main)
