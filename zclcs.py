#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, locale, curses, shutil, ConfigParser
from curses import wrapper
from curses.textpad import Textbox

DIRS = []
if (len(sys.argv) == 1):
	config = ConfigParser.ConfigParser()
	config.read("./.conf")
	items = config.items("DIRS")
	for item in items:
		DIRS.append(item[1])
else:
	if sys.argv[1] != "?" and sys.argv[1] != "--help":
		DIRS.append(sys.argv[1])
	else:
		print("Programmed by Ryan Chiu.\n")
		print("****************************************************")
		print("{} will read '.conf' file by default, which contains all the paths that need to be shown.".format(sys.argv[0]))
		print("And this '.conf' file must list the paths under '[DIRS]' like this: '0:full path name', one path a line.")
		print("If with a parameter, then it should be a full path name, like '/mnt/harddisk01'.\n")
		print("When getting into it, type '?' for how to operate.")
		print("****************************************************")
		exit()

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

'''
all kinds of defines in the program
'''
offsets = [0, 0]
lines = []
fcsidx = -1
pnu = 0 #PATH NUMBER
vpaths = [] #VISITED PATHS LIST

'''
the main pgrogram here
'''
def main(stdscr):
	curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

	rfs_screen(stdscr)

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
					rfs_screen(stdscr)
					break
				elif m_ch == ord('n'):
					mva_bottom(stdscr, "please hit the number(#x) of the path to move into, or 'c' to cancel out.")
				elif m_ch == ord('c'):
					shw_status(stdscr, "file")
					break
		elif ch == ord('r'):
			if not fn:
				continue
			mva_bottom(stdscr, "rename it, y/n?(if yes, then edit the new name and fire it with ctrl+g when it's done.)")
			while True:
				r_ch = stdscr.getch()
				if r_ch == ord('y'):
					r_title = "new name:"
					yx = stdscr.getmaxyx()
					mva_bottom(stdscr, r_title)
					editwin = curses.newwin(1, yx[1] - len(r_title) - 1, yx[0] - 1, len(r_title) + 1)
					stdscr.refresh()
					box = Textbox(editwin)
					# Let the user edit until Ctrl-G is struck.
					box.edit()
					# Get resulting contents
					newname = box.gather().strip()
					if newname == line['fln']:
						mva_bottom(stdscr, "no change.")
					else:
						old_name = os.path.join(line['phn'], line['fln'])
						new_name = os.path.join(line['phn'], newname)
						os.rename(old_name, new_name)
						rfs_screen(stdscr)
					break
				elif r_ch == ord('n'):
					shw_status(stdscr, "file")
					break
		elif ch == curses.KEY_F5:
			stdscr.clear()
			scrolllines(stdscr, 0)
		elif ch == ord('?'):
			mva_bottom(stdscr, "'u'/'j' to select,'d' to remove,'m' to move,ENTER into a folder,UP/DW to scroll,F5 to refresh,'?' to help,'q' to quit.")
		elif ch in (curses.KEY_ENTER, 10):
			if not fn:
				continue
			if line['pnu'] != -1:
				vpath = os.path.join(line['phn'], line['fln'])
				psh_vpath(vpath, -1)
				rfs_screen(stdscr)
		elif ch == curses.KEY_BACKSPACE:
			pop_vpath()
			rfs_screen(stdscr)
		else:
                        continue

'''
all the functions & stuff needed in the main program
'''
def tnc_line(string, max_len):
	if (len(string) >= max_len):
		return string[0:(max_len - 3)] + "..."
	else:
		return string

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

def rld_files(dirs):
	global offsets, lines, pnu
	offsets = [0, 0]
	lines = []
	pnu = 0
	for path in dirs:
		files = os.listdir(path)
		exp_line(True, False, pnu, "#{0} in path [{1}]:".format(pnu, path), curses.color_pair(1), path, "")
		exp_line(True, False, -1, '{0: ^3} {1:7} {2:101}'.format("#", "size", "file name"), curses.A_UNDERLINE, "", "")
		i = 0
		for f in files:
			fn = os.path.join(path, f)
			f_dcr = curses.color_pair(3)
			pnum = -1
			if os.path.isdir(fn):
				f_dcr = curses.color_pair(2)
				pnum = pnu
			exp_line(False, False, pnum, '{0: ^3} {1:7} {2:101}'.format(i, str_hsize(os.path.getsize(fn)), tnc_line(f, 101)), f_dcr, path, f)
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
	del_line(get_fidx())
	mvfcs(-1)

def exp_line(skp, fcs, pnu, txt, dcr, phn, fln):
	lines.append({"skp" : skp, "fcs" : fcs, "pnu" : pnu, "txt" : txt, "dcr" : dcr, "phn" : phn, "fln" : fln})

def get_fidx():
	if vpaths != []:
		pf = vpaths[len(vpaths) - 1]
		return pf['fidx']
	else:
		return fcsidx

def set_fidx(fidx):
	global fcsidx, vpaths
	if vpaths != []:
		pf = pop_vpath()
		psh_vpath(pf['path'], fidx)
	else:
		fcsidx = fidx

def rfs_screen(scr):
	global vpaths
	if vpaths != []:
		dirs = []
		pf = vpaths[len(vpaths) - 1]
		dirs.append(pf["path"])
		rld_files(dirs)
	else:
		rld_files(DIRS)
	scr.clear()
	mvfcs(0)
	scrolllines(scr, 0)

def psh_vpath(path, fidx):
	global vpaths
	pf = {"path" : path, "fidx" : fidx}
	vpaths.append(pf)

def pop_vpath():
	global vpaths
	if vpaths != []:
		vpath = vpaths[len(vpaths) - 1]
		del vpaths[len(vpaths) - 1]
		return vpath
	else:
		return []

def shw_status(stdscr, mode):
	if mode == "file":
		if get_fidx() < 0 or get_fidx() >= len(lines):
			return
		line = get_fcsline()
		mva_bottom(stdscr, "\"{}\"".format(os.path.join(line['phn'], line['fln'])))
	elif mode == "":
		return

def mva_bottom(scr, txt):
	yx = scr.getmaxyx()
	l = ""
	for i in range(0, yx[1] - 1):
		l += " "
	scr.addstr(yx[0] - 1, 0, l)
	scr.addstr(yx[0] - 1, 0, tnc_line(txt, yx[1] - 1), curses.A_REVERSE)

def mvfcs(step):
        global lines
	fidx = get_fidx()
        fidx += step
        while fidx >= 0 and fidx < len(lines) and lines[fidx]['skp']:
                if step <= 0:
                        fidx -= 1
                elif step > 0:
                        fidx += 1
        if fidx < -1:
                fidx = -1
        elif fidx >= len(lines):
                fidx = len(lines)
	set_fidx(fidx)
        setfcsline(fidx)

def setfcsline(idx):
	global lines
        i = 0
        for line in lines:
                if i == idx:
                        line['fcs'] = True
                else:
                        line['fcs'] = False
                i += 1

def scrolllines(scr, step):
	global offsets, lines
        yx = scr.getmaxyx()
	l = ""
	for x in range(0, yx[1] - 1):
		l += " "
	offsets[0] -= step
        if offsets[0] < 0:
                offsets[0] = 0
        elif offsets[0] >= len(lines):
                offsets[0] = len(lines) - 1
        end = offsets[0] + yx[0] - 1
        if end >= len(lines):
                end = len(lines)
		offsets[0] = end - yx[0] + 1
		if offsets[0] < 0:
			offsets[0] = 0
        y = 0
        for i in range(offsets[0], end):
                t = ""
		t_dcr = lines[i]['dcr']
                if lines[i]['fcs']:
                        t = "[*]"
			t_dcr = curses.A_BOLD
		scr.addstr(y, 0, l)
		if yx[1] > (300 - 5):
                	scr.addstr(y, 0, "{0:3} {1:300}".format(t, lines[i]['txt']), t_dcr)
		else:
			w = yx[1] - 5
			scr.addstr(y, 0, "{0:3} {1}".format(t, tnc_line(lines[i]['txt'], w)), t_dcr)
                y += 1

wrapper(main)
