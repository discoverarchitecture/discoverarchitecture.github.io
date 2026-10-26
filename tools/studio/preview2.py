# Renders the three board layouts on their own (web/boards.html), for screenshots and the canvas.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board2
SP = board2.SP
css = open(SP + 'draw2.css').read() + open(SP + 'board2.css').read()
fonts = 'family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@400;500;600'
boards = ''.join(f'<section id="{k}"><h2>{n}</h2>{board2.board(k, filled=True)}</section>' for k, n in board2.LAYOUTS)
open(SP + 'web/boards.html', 'w').write(f'''<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>{css} body{{margin:0;background:#CFCFCA;padding:40px;display:flex;flex-direction:column;gap:60px;font-family:Inter,sans-serif}} section{{width:1200px}} h2{{margin:0 0 12px;font:600 18px Inter}}</style></head>
<body>{boards}</body></html>''')
print('ok')
