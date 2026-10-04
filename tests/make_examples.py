import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from generate_report import write_report
from sample_cases import full_case,analyzer_case,screenshot_case,partial_case
CASES={'text':full_case,'screenshot':screenshot_case,'product-image':lambda:screenshot_case(True),'analyzer':analyzer_case,'missing-product':partial_case,'missing-benchmark':lambda:partial_case('benchmark')}
if __name__=='__main__':
    for name,build in CASES.items():
        d=build();folder=ROOT/'examples'/name;folder.mkdir(parents=True,exist_ok=True)
        (folder/'input.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
        write_report(d,folder/'xiaohongshu-replication-report.html',ROOT/'examples/media');print('Generated',name)
