import ast,base64,copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from generate_report import ReportError,validate,render,write_report,originality,image_uri,readiness
from import_analyzer import extract
from sample_cases import full_case,screenshot_case,analyzer_case,partial_case,claim

class ReportTests(unittest.TestCase):
    def rejects(self,d):
        with self.assertRaises(ReportError):validate(d)
    def test_text_complete(self):self.assertIsNone(validate(full_case())['question'])
    def test_benchmark_screenshot(self):self.assertIn('data:image/png',render(screenshot_case(),ROOT/'examples/media')[0])
    def test_product_screenshot(self):self.assertIn('data:image/png',render(screenshot_case(True),ROOT/'examples/media')[0])
    def test_analyzer_handoff(self):self.assertIsNone(validate(analyzer_case())['question'])
    def test_only_benchmark_one_question(self):self.assertIn('商品是什么',validate(partial_case())['question'])
    def test_only_product_one_question(self):self.assertIn('对标',validate(partial_case('benchmark'))['question'])
    def test_unknown_optional_fields(self):self.assertIn('未知／未获取到',render(full_case())[0])
    def test_missing_name_does_not_fake_complete(self):
        d=full_case();d['product']['name']=None;self.rejects(d)
    def test_pending_cannot_include_plans(self):
        d=partial_case();d['plans']=full_case()['plans'];self.rejects(d)
    def test_pending_report_is_explicit(self):self.assertIn('只需补充这一点',render(partial_case())[0])
    def test_fake_block_when_ready(self):
        d=full_case();d['status']='needs_input';self.rejects(d)
    def test_product_cannot_cite_benchmark(self):
        d=full_case();d['product']['price']['evidence_ids']=['E1'];self.rejects(d)
    def test_product_cannot_cite_analyzer(self):
        d=analyzer_case();d['product']['price']['evidence_ids']=['E1'];self.rejects(d)
    def test_fact_cannot_be_analysis(self):
        d=full_case();d['product']['name']['type']='ANALYSIS';self.rejects(d)
    def test_unseen_image(self):
        d=screenshot_case();d['sources'][0]['inspected']=False;self.rejects(d)
    def test_unclear_product_fact(self):
        d=full_case();d['evidence'][1]['clear']=False;self.rejects(d)
    def test_quote_not_in_material(self):
        d=full_case();d['evidence'][1]['quote']='凭空来的认证';self.rejects(d)
    def test_duplicate_source(self):
        d=full_case();d['sources'].append(copy.deepcopy(d['sources'][0]));self.rejects(d)
    def test_duplicate_evidence(self):
        d=full_case();d['evidence'].append(copy.deepcopy(d['evidence'][0]));self.rejects(d)
    def test_unknown_evidence(self):
        d=full_case();d['analysis']['core']['evidence_ids']=['absent'];self.rejects(d)
    def test_fake_fit_score(self):
        d=full_case();d['analysis']['fit']['level']=98;self.rejects(d)
    def test_five_titles_exact(self):
        d=full_case();d['titles'].pop();self.rejects(d)
    def test_three_plans_exact(self):
        d=full_case();d['plans'].pop();self.rejects(d)
    def test_title_mapping(self):
        d=full_case();d['plans'][1]['title_id']='T1';self.rejects(d)
    def test_cover_missing(self):
        d=full_case();d['plans'][0]['cover'].pop('boundary');self.rejects(d)
    def test_opening_is_actual(self):
        d=full_case();d['plans'][0]['opening']='标签写得不同但正文没改';self.rejects(d)
    def test_cta_is_actual(self):
        d=full_case();d['plans'][0]['cta']='没有出现在正文';self.rejects(d)
    def test_complete_body_required(self):
        d=full_case();d['plans'][0]['paragraphs']=['开头','结尾'];d['plans'][0].update(opening='开头',cta='结尾');self.rejects(d)
    def test_reject_original_title(self):
        d=full_case();d['titles'][0]['copy']['text']=d['sources'][0]['title'];self.rejects(d)
    def test_reject_near_title(self):
        d=full_case();d['sources'][0]['title']='高手在民间？才9.9元家里的老人味真没了';d['titles'][0]['copy']['text']='高手果然在民间，9.9元老人味终于没了';self.assertIn('benchmark title reuse',originality(d))
    def test_reject_sentence_copy(self):
        d=full_case();d['plans'][0]['paragraphs'][1]=d['sources'][0]['content'];self.assertIn('long benchmark expression reuse',originality(d))
    def test_reject_renamed_family_story(self):
        d=full_case();d['plans'][0]['paragraphs'][1]='我外婆搬来后，用了7天，真的有效。';self.rejects(d)
    def test_reject_unprovided_effect(self):
        d=full_case();d['plans'][0]['paragraphs'][1]='亲测，这个产品真的有效。';self.rejects(d)
    def test_wrong_fact_binding_does_not_whitelist_effect(self):
        d=full_case();d['plans'][0]['paragraphs'][1]='亲测有效，放心买。';d['fact_uses'].append({'text':'亲测有效','field':'price'});self.rejects(d)
    def test_wrong_number_binding(self):
        d=full_case();d['plans'][0]['paragraphs'][1]='只要99元就能买到。';d['fact_uses'].append({'text':'99元','field':'price'});self.rejects(d)
    def test_duplicate_body_rejected(self):
        d=full_case();d['plans'][1]['paragraphs']=d['plans'][0]['paragraphs'];self.assertIn('plan bodies too similar',originality(d))
    def test_fake_distinct_titles_same_strategy(self):
        d=full_case();a,b=d['plans'][:2]
        for key in ('structure','product_position','trust'):b[key]=a[key]
        self.assertIn('same structure/placement/trust',originality(d))
    def test_distinct_demo(self):self.assertEqual(originality(full_case()),[])
    def test_priority_unique(self):
        d=full_case();d['priority'][2]['plan_id']='A';self.rejects(d)
    def test_semantic_review_required(self):
        d=full_case();d['review']['story']='PASS';self.rejects(d)
    def test_two_backup_titles(self):
        d=full_case();used={p['title_id'] for p in d['plans']};self.assertEqual(len([t for t in d['titles'] if t['id'] not in used]),2)
    def test_script_html_escaping(self):
        d=full_case();d['sources'][1]['label']='<script>globalThis.pwned=true</script> & " 😊';r=render(d)[0];self.assertNotIn('<script>',r);self.assertIn('&lt;script&gt;',r);self.assertIn('😊',r)
    def test_attribute_injection(self):
        d=screenshot_case();d['sources'][0]['label']='" onerror="alert()';r=render(d,ROOT/'examples/media')[0];self.assertIn('&quot; onerror=&quot;',r);self.assertNotIn('alt="" onerror=',r)
    def test_template_marker_is_literal(self):
        d=full_case();d['sources'][0]['label']='@@CONTENT@@';self.assertIn('@@CONTENT@@',render(d)[0])
    def test_offline_html(self):
        r=render(full_case())[0];self.assertNotIn('<script',r);self.assertNotIn('src="http',r);self.assertNotIn('href="http',r);self.assertIn("default-src 'none'",r)
    def test_path_rejection(self):
        for v in ['../x.png','/tmp/x.png','C:/x.png','https://example.com/x.png','..\\x.png']:
            with self.subTest(v=v),self.assertRaises(ReportError):image_uri({'file':v},ROOT,[0])
    def test_missing_image_degrades(self):self.assertIsNone(image_uri({'file':'absent.png'},ROOT,[0])[0])
    def test_svg_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'a.png').write_text('<svg onload="evil()"/>');self.assertIsNone(image_uri({'file':'a.png'},td,[0])[0])
    def test_image_budget(self):self.assertIsNone(image_uri({'file':'product.png'},ROOT/'examples/media',[40*1024*1024])[0])
    def test_image_self_contained(self):
        uri,_=image_uri({'file':'product.png'},ROOT/'examples/media',[0]);self.assertEqual(base64.b64decode(uri.split(',')[1]),(ROOT/'examples/media/product.png').read_bytes())
    def test_outputs_created(self):
        with tempfile.TemporaryDirectory() as td:
            write_report(full_case(),Path(td)/'report.html');self.assertEqual({p.name for p in Path(td).iterdir()},{'report.html','chat-summary.md','original-notes.md'})
    def test_failed_validation_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            d=full_case();d['plans']=[]
            with self.assertRaises(ReportError):write_report(d,Path(td)/'bad.html')
            self.assertEqual(list(Path(td).iterdir()),[])
    def test_chat_is_short(self):
        r,s,n=render(full_case());self.assertLess(len(s),len(n));self.assertIn('方案',r)
    def test_import_preserves_judgment(self):
        x=extract({'schema_version':'1.0','claims':{'c':{'text':'可能提升信任','type':'ANALYSIS','evidence_ids':['e']}},'dna':{'trust':'c'},'evidence':[{'id':'e'}]});self.assertEqual(x['dna']['trust']['upstream_type'],'ANALYSIS')
    def test_import_missing_claim(self):self.assertIn('Missing claim',str(extract({'schema_version':'1.0','claims':{},'dna':{'trust':'missing'}})))
    def test_import_unknown_schema(self):
        with self.assertRaises(ValueError):extract({'schema_version':'2'})
    def test_no_runtime_network(self):
        tree=ast.parse((ROOT/'scripts/generate_report.py').read_text(encoding='utf-8'))
        imports={n.names[0].name if isinstance(n,ast.Import) else n.module for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))}
        self.assertFalse(imports&{'requests','urllib','http','socket','playwright','selenium'})

if __name__=='__main__':unittest.main()
