from pathlib import Path
p=Path('tmp/assignment2/build-deck.mjs')
s=p.read_text(encoding='utf-8').replace("'--validate-heading-fit'],requiredNativeTableOwnerSlides", "'--validate-heading-fit',...[3,6,9,13].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides")
p.write_text(s,encoding='utf-8')
