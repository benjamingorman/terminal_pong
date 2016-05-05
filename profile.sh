python -m cProfile -o profile.bin main.py

echo -e "import pstats\np = pstats.Stats('profile.bin')\np.strip_dirs().sort_stats('time').print_stats()" | python > profile.txt
