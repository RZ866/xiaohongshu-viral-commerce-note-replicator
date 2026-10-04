import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from generate_report import write_report
from sample_cases import full_case
d=full_case();d['sources'][0]['label']='<script>globalThis.pwned=true</script><img src=x onerror="evil()"> & 中文 😊'
write_report(d,ROOT/'.qa/hostile.html')
