rem @echo off
cd "C:\Users\Bot\Grupo Faro Verde\Proyectos y EO - Bot_excel"
:inicio
echo Date: %time% >>log.txt
python main.py 2>&1 >>log.txt
goto inicio