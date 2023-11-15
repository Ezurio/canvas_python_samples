@echo off

mcumgr -c %1 fs upload boot.py /lfs1/boot.py
mcumgr -c %1 fs upload main.py /lfs1/main.py