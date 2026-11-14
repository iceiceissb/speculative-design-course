from pathlib import Path
p=Path('tmp/assignment2/build-deck.mjs')
s=p.read_text(encoding='utf-8').replace("'deck-validation.json'", "'deck-validation-final.json'")
p.write_text(s,encoding='utf-8')
