# FileIndexer

This Python script will index a directory and store the md5 checksums in a **sqlite** database.

# Features
The following features or command line parameters are planned:
## Indexing
Index all files in an directory

Command line:
	python fileIndexer.py index <directoryname>

All files in this directory get scanned and a sqlite database will be created in this directory 
containing all md5 checksums of all files.

## Query for new files

With this command you can check if in another directory there are files that are **not** in the
target directory.

Command line:
	python fileIndexer.py isNew <indexedDirectory> <otherDirectory>

## Query for contained files

You can check if another directory contains files that are allready in the target directory.

Command line:
	python fileIndexer.py isOld <indexedDirectory> <otherDirectory>

## Query for duplicate files

Command line:
	python fileIndexer.py getDups <indexedDirectory>

# Status

Indexing without command line argument works.

