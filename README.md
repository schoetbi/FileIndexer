# FileIndexer

This Python script will index a directory and store the md5 checksums in a **sqlite** database.

# Features
The following features or command line parameters are planned:
## Indexing
Index all files in an directory

Command line:
	python fileIndexer.py index dir

All files in this directory get scanned and a sqlite database will be created in this directory 
containing all md5 checksums of all files.

## Query for new files

With this command you can check if in dir2 are files that are **not** in dir1.

Command line:
	python fileIndexer.py areNew dir1 dir2

## Query for contained files

You can check if dir2 contains files that are allready in dir1.

Command line:
	python fileIndexer.py areOld dir1 dir2

## Query for duplicate files

Command line:
	python fileIndexer.py getDups dir

# Status

Indexing without command line argument works.

