import os  
import hashlib
import sqlite3 as sqlite
import sys
import time

def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()

class FileInfo:
	def __init__(self, fileName = None, md5 = None, timeStamp = None):
		self.FileName = fileName
		self.Md5 = md5
		self.TimeStamp = timeStamp

def OpenDb(startDir):
		con = sqlite.connect(os.path.join(startDir, 'filehash.db'))
		sqlTblExists = 'SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'hashes\';'
		cur = con.cursor()    
		cur.execute(sqlTblExists)
		count = cur.fetchone()[0]
		if count == 0:
			print('Creating table')
			sqlCreateTbl = 'Create table hashes(filename TEXT, md5 TEXT, time TEXT);'
			cur.execute(sqlCreateTbl)
			sqlCreateIndex = 'CREATE UNIQUE INDEX "main"."idxfilename" ON "hashes" ("filename" ASC)'
			cur.execute(sqlCreateIndex)
			print ('done')
		
		cur.close()
		return con
	
def IsCurrent(con, fn, modTime):
	cur = con.cursor()
	sqlQueryGetCount = 'select count(*) from hashes where filename = ? and time = ?;'
	cur.execute(sqlQueryGetCount, [fn, modTime])
	isCurrent = cur.fetchone()[0] > 0
	cur.close()
	return isCurrent

def Save(con, info):
	cur = con.cursor()
	sqlDelete = 'delete from hashes where filename = ?;'
	cur.execute(sqlDelete, [info.FileName])		
	sqlSave = 'Insert into hashes(filename, md5, time) values(?,?,?);'
	cur.execute(sqlSave, [info.FileName, info.Md5, info.TimeStamp])
	cur.close()

def Get(con):
	cur = con.cursor()
	sqlQuery = 'select filename, md5, time from hashes;'
	cur.execute(sqlQuery)
	rows = cur.fetchall()
	infos = []
	for r in rows:
		info = FileInfo(r[0], r[1], '')
		infos.append(info)
	cur.close()	
	return infos

def GetMd5Count(con, md5):
	cur = con.cursor()
	sqlQuery = 'select count(*) from hashes where md5 = ?;'
	cur.execute(sqlQuery, [md5])
	cnt = cur.fetchone()[0]
	cur.close()	
	return cnt

def Delete(con, fn):
	cur = con.cursor()
	sqlDelete = 'delete from hashes where filename = ?;'
	cur.execute(sqlDelete, [fn])
	cur.close()

def IndexDirectory(startFolder):
	if not os.path.isdir(startFolder):
		print("'%s' is not a directory"%  startFolder)		
		return False

	print ("indexing '%s'" % startFolder)

	try:
		files = {}
		db = OpenDb(startFolder)
		counter = 0
		for root, dirs, filenames in os.walk(startFolder):
			for f in filenames:
				if f.lower() == 'filehash.db':
					continue
				fn = os.path.join(root, f)

		#		modTime = os.path.getmtime(fn)
				modTimeRaw = time.localtime(os.stat(fn).st_mtime)
				modTime = time.strftime('%Y-%m-%d %H:%M:%S', modTimeRaw)
				if IsCurrent(db, fn, modTime):
					#print ('skipped ', fn)
					continue
		
				#sys.stdout.write(fn)
				try:
					h = open(fn, 'r')
					md5 = md5_for_file(h, 10 * 2**10)
				finally:				
					h.close()

				info = FileInfo(fn, md5, modTime)
				#print(fn, md5, modTime)
				Save(db, info)
				#print(' done')
				counter = counter + 1
				if counter > 10:
					sys.stderr.write('.')
					db.commit()
					counter = 0
	
		# delete nonexistent files from db
		cur = db.cursor()
		sqlSelectFilenames = 'select filename from hashes;'
		sqlDelete = 'delete from hashes where filename = ?;'
		cur.execute(sqlSelectFilenames)
		rows = cur.fetchall()
		for r in rows:
			filename = r[0]
			if not os.path.isfile(filename):
				cur.execute(sqlDelete, [filename])
				print ("removed '%s' from db" % filename)
		cur.close()
	finally:
		db.close()
	return True

def GetNumberOfSameMd5(dir1, dir2):
	# check if both are dirs
	for d in [dir1, dir2]:
		if not os.path.isdir(dir1):
			print ("'%s' is not a dir" % d)
			return

	# check if both are indexed
	if not IndexDirectory(dir1) or not IndexDirectory(dir2):
		return
	
	try:
		db2 = OpenDb(dir2)
		files2 = Get(db2)
	finally:
		db2.close()

	try:
		db1 = OpenDb(dir1)
		for f2 in files2:
			md5Cnt = GetMd5Count(db1, f2.Md5)
			f2.Md5Count = md5Cnt
	finally:
		db1.close()

	return files2

def AreNew(dir1, dir2):
	files = GetNumberOfSameMd5(dir1, dir2)
	oldfiles = [f for f in files if f.Md5Count == 0]
	for f in oldfiles:
		print(f.FileName)

def AreOld(dir1, dir2):
	files = GetNumberOfSameMd5(dir1, dir2)
	oldfiles = [f for f in files if f.Md5Count > 0]
	for f in oldfiles:
		print(f.FileName)

def GetDupes(dir):
	exit('not implemented yet')
	db = OpenDb(dir1)
	db.close()

def toUnicode(s):
	return s.decode('utf-8')
	
cmd = sys.argv[1].lower()
if cmd == 'index':
	IndexDirectory(toUnicode(sys.argv[2]))
elif cmd == 'arenew':
	AreNew(toUnicode(sys.argv[2]), toUnicode(sys.argv[3]))
elif cmd == 'areold':
	AreOld(toUnicode(sys.argv[2]), toUnicode(sys.argv[3]))
elif cmd == 'getdupes':
	GetDupes(toUnicode(sys.argv[2]))
