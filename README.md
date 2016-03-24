<b>Programmed by Ryan Chiu.</b>

1st. of all, this is a little tool to manage files from different directories, try to put the views together.<br/>
2nd., it could let you remove/rename/move a file in the view you pre-defined (and now could follow one path parameter).<br/>
3rd., it has no multi-thread stuff there, so, some time you need to wait for a long term action, such as copy/move/delete a big file etc..<br/>
4th., please, use it for "not that many files" situation there.

################################################################################
./zclcs.py will read '.conf' file by default, which contains all the paths that need to be shown.
And this '.conf' file must list the paths under '[DIRS]' like this: '0:full path name', one path a line.
If with a parameter, then it should be a full path name, like '/mnt/harddisk01'.
With "?" or "--help" to get the above info.

When getting into it, type "?" for how to operate.
################################################################################

The TUI should be like this:<br/>

		#0 in path [/var]:
		#  size    file name
		0  4.0K    backups
		1  4.0K    spool
		2  4.0K    cache
		3  4.0K    lib
		4  4.0K    opt
		5  4.0K    local
		6  40.0    lock
		7  4.0K    mail
		8  900.0   run
		9  4.0K    tmp
		10  4.0K    log
		11  100.0M  swap
		
		'u'/'j' to select,'d' to remove,'m' to move,ENTER into a folder,F5 to refresh,'?' to help,'q' to quit.
