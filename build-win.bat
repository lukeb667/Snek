pyinstaller --name "Snek"  --windowed main.py
xcopy "config.ini" "dist/Snek"
rmdir build /s /q