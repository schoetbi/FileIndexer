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

def OpenDb():
		con = sqlite.connect('filehash.db')
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

def Delete(con, fn):
	cur = con.cursor()
	sqlDelete = 'delete from hashes where filename = ?;'
	cur.execute(sqlDelete, [fn])
	cur.close()

print('start')

files = {}
db = OpenDb()
counter = 0
for root, dirs, filenames in os.walk(ur'.'):
	for f in filenames:
		fn = os.path.join(root, f)

#		modTime = os.path.getmtime(fn)
		modTimeRaw = time.localtime(os.stat(fn).st_mtime)
		modTime = time.strftime('%Y-%m-%d %H:%M:%S', modTimeRaw)
		if IsCurrent(db, fn, modTime):
			print ('skipped ', fn)
			continue
		
		sys.stdout.write(fn)
		h = open(fn, 'r')
		md5 = md5_for_file(h, 10 * 2**10)
		h.close()

		info = FileInfo(fn, md5, modTime)
		#print(fn, md5, modTime)
		Save(db, info)
		print(' done')
		counter = counter + 1
		if counter > 10:
			print('/')			
			db.commit()
			counter = 0

