"""Offline inventories must close image dependencies and reject incomplete practice."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('offline_manifest',Path(__file__).resolve().parents[1]/'scripts/offline_manifest.py')
offline=importlib.util.module_from_spec(spec);spec.loader.exec_module(offline)

class OfflineInventory(unittest.TestCase):
    def fixture(self,root,missing=False):
        files={'index.html':'<title>Luisa</title>','release.json':'{"version":"0.26"}',
               'teaching-catalogue.js':'window.LUISA_TEACHING={};',
               'content/test.json':json.dumps([{'question':'<img src="assets/diagram.svg">','steps':['Answer']}]),
               'assets/diagram.svg':'<svg xmlns="http://www.w3.org/2000/svg"><image href="detail.svg"/></svg>'}
        if not missing:files['assets/detail.svg']='<svg xmlns="http://www.w3.org/2000/svg"/>'
        files['textbook-catalogue.json']=json.dumps({'skills':{'test':{'course':'test','book':'test'}},'books':[{'id':'test','title':'Test','course':'test','chapters':[{'id':'1','title':'One','resources':[]}]}],'questions':[{'skill':'test','targets':[{'book':'test','chapter':'1'}]}]})
        entries={}
        for name,data in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
            entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data.encode())}
        return entries

    def test_nested_svg_is_required_and_hashed_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root);result=offline.generate(root,entries,'0.26')
            self.assertIn('assets/detail.svg',result['packs'][0]['files'])
            self.assertEqual(result['files']['assets/detail.svg'],entries['assets/detail.svg'])
            self.assertIn('Teaching slides',result['packs'][0]['unavailable'])
            self.assertIn('offline-catalogue.json',entries)

    def test_missing_nested_dependency_fails_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root,missing=True)
            with self.assertRaisesRegex(ValueError,'Unresolved nested offline dependency'):
                offline.generate(root,entries,'0.26')

    def test_print_and_practice_PDFs_required_LIB_028(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root)
            def put(name,data):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
                entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data)}
            put('data.js','window.FMQ_LIBRARY='+json.dumps({'courses':[{'id':'maths-a-level','books':[{'id':'test','title':'Test','topics':[{'printoutPath':'topic.pdf','skills':[{'id':'test','printoutPath':'skill.pdf','questions':[1]}]}]}]}]})+';')
            for name in ['topic.pdf','skill.pdf','practice.pdf']:put(name,'%PDF-fixture')
            cat=json.loads((root/'textbook-catalogue.json').read_text());cat['books'][0]['chapters'][0]['resources']=[{'type':'practice','access':'available','url':'practice.pdf'}]
            put('textbook-catalogue.json',json.dumps(cat))
            result=offline.generate(root,entries,'0.28')
            self.assertTrue({'topic.pdf','skill.pdf','practice.pdf'}<=set(result['packs'][0]['files']))
            del entries['skill.pdf']
            with self.assertRaisesRegex(ValueError,'Offline print PDF missing'):offline.generate(root,entries,'0.28')

    def test_inventory_revision_changes_with_actual_bytes_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root);first=offline.generate(root,entries,'0.26')
            content='<svg><!-- revised --></svg>';p=root/'assets/detail.svg';p.write_text(content)
            entries['assets/detail.svg']={'sha256':hashlib.sha256(content.encode()).hexdigest(),'bytes':len(content)}
            second=offline.generate(root,entries,'0.26')
            self.assertNotEqual(first['revision'],second['revision'])

    def test_practice_booklet_working_and_images_belong_to_chapter_pack(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root)
            additions={
                'practice-catalogue.json':json.dumps({'questions':[{'bookId':'test','chapterNumber':1,'dataPath':'content/practice/test/chapter-01.json'}]}),
                'content/practice/test/chapter-01.json':json.dumps({'questions':[{'question':'Prompt', 'steps':['<img src="resources/practice-solutions/answer.svg">'], 'hints':['Hint']}]}),
                'resources/practice-solutions/answer.svg':'<svg xmlns="http://www.w3.org/2000/svg"><image href="detail.svg"/></svg>',
                'resources/practice-solutions/detail.svg':'<svg xmlns="http://www.w3.org/2000/svg"/>'}
            for name,data in additions.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
                entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data.encode())}
            result=offline.generate(root,entries,'0.58');pack=result['packs'][0]
            self.assertEqual(pack['practiceEntries'],2)
            self.assertIn('practice-catalogue.json',result['shared'])
            self.assertTrue(set(additions)-{'practice-catalogue.json'} <= set(pack['files']))
            del entries['resources/practice-solutions/detail.svg']
            with self.assertRaisesRegex(ValueError,'Unresolved nested offline dependency'):
                offline.generate(root,entries,'0.58')

    def test_mapped_exam_payload_and_worked_diagrams_are_complete(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root)
            additions={
                'exam-catalogue.json':json.dumps({'questions':[
                    {'id':'exam/test/q1','dataPath':'content/exams/test.json','skillMappings':[
                        {'courseId':'test','bookId':'test','skillId':'test'},
                        {'courseId':'test','bookId':'test','skillId':'test'}]}]}),
                'content/exams/test.json':json.dumps({'questions':[{'question':'Prompt',
                    'steps':['<img src="assets/exam.svg">']}]}),
                'assets/exam.svg':'<svg><image href="exam-detail.svg"/></svg>',
                'assets/exam-detail.svg':'<svg/>',
            }
            for name,data in additions.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
                entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data.encode())}
            result=offline.generate(root,entries,'0.59');pack=result['packs'][0]
            self.assertIn('exam-catalogue.json',result['shared'])
            self.assertTrue({'content/exams/test.json','assets/exam.svg','assets/exam-detail.svg'} <= set(pack['files']))
            self.assertEqual(pack['practiceEntries'],2)
            # The library skill may belong to a different book from its Edexcel
            # chapter target (Core1 hyperbolic skill -> Core2 chapter6).
            cat = json.loads((root/'textbook-catalogue.json').read_text())
            cat['skills']['test']['book'] = 'source-book'
            (root/'textbook-catalogue.json').write_text(json.dumps(cat))
            exam = json.loads((root/'exam-catalogue.json').read_text())
            for m in exam['questions'][0]['skillMappings']:m['bookId']='source-book'
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            self.assertIn('content/exams/test.json', offline.generate(root,entries,'0.59')['packs'][0]['files'])
            # Identical skill text in a different course must not cross-match.
            for m in exam['questions'][0]['skillMappings']:m['courseId']='different-course'
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            with self.assertRaisesRegex(ValueError,'Offline exam mapping has no chapter pack'):
                offline.generate(root,entries,'0.59')
            cat['skills']['test']['book']='test'
            (root/'textbook-catalogue.json').write_text(json.dumps(cat))
            for m in exam['questions'][0]['skillMappings']:m.update(courseId='test',bookId='test')
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            # A practice-only skill also resolves to its chapter; payload/answer
            # dependencies are not already referenced by the ordinary fixture.
            practice={'questions':[{'bookId':'test','chapterNumber':1,
                'skillIds':['practice-only'], 'dataPath':'content/practice/test.json'}]}
            (root/'practice-catalogue.json').write_text(json.dumps(practice))
            p=root/'content/practice/test.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{"questions":[]}')
            entries['content/practice/test.json']={}
            exam=json.loads((root/'exam-catalogue.json').read_text())
            for m in exam['questions'][0]['skillMappings']:m['skillId']='practice-only'
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            result=offline.generate(root,entries,'0.59')
            self.assertIn('assets/exam-detail.svg', result['packs'][0]['files'])
            # Unresolvable mappings must fail closed, not silently lose content.
            for m in exam['questions'][0]['skillMappings']:m['skillId']='unmapped'
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            with self.assertRaisesRegex(ValueError,'Offline exam mapping has no chapter pack'):
                offline.generate(root,entries,'0.59')
            for m in exam['questions'][0]['skillMappings']:m['skillId']='test'
            (root/'exam-catalogue.json').write_text(json.dumps(exam))
            del entries['content/exams/test.json']
            with self.assertRaisesRegex(ValueError,'Offline exam questions missing'):
                offline.generate(root,entries,'0.59')

if __name__=='__main__':unittest.main()
