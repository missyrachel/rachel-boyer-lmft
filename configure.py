"""Set the verified GitHub repository before connecting Netlify."""
import json,re,sys
from pathlib import Path
if len(sys.argv)!=2 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+',sys.argv[1]):
 raise SystemExit('Usage: python3 configure.py VERIFIED_OWNER/VERIFIED_REPOSITORY')
(Path(__file__).parent/'cms/repository.json').write_text(json.dumps({'repository':sys.argv[1]},indent=2)+'\n')
print('Repository configured. Next connect this repository and OAuth in your existing Netlify project.')
