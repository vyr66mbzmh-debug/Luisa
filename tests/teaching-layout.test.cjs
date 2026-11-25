const test = require('node:test');
const assert = require('node:assert/strict');
const { prepare } = require('../lesson-controls.js');

function slide(shapes) {
  return { shapes, headerShapes: [], contentHeight: 200 };
}

function cover(id, x, y, h) {
  return { id, box: { x, y, w: 70, h }, cover: true, coverLabel: id };
}

test('paired controls and their answers move together without changing the input deck', () => {
  const source = slide([
    cover('left', 0, 15, 20), cover('right', 80, 20, 28),
    { id: 'working', box: { x: 4, y: 17, w: 62, h: 16 }, answerFor: 'left' },
  ]);
  const result = prepare(source, { height: 200 });
  assert.deepEqual(result.shapes.slice(0, 2).map(s => [s.box.y, s.box.h]), [[20, 28], [20, 28]]);
  assert.equal(result.shapes[2].box.y, 22);
  assert.equal(source.shapes[0].box.h, 20);
  assert.equal(source.shapes[2].box.y, 17);
});

test('a nearby question prevents a paired control from covering it', () => {
  const source = slide([
    cover('left', 0, 10, 20), cover('right', 80, 10, 42),
    { id: 'question', box: { x: 0, y: 33, w: 70, h: 20 } },
  ]);
  assert.equal(prepare(source, { height: 200 }).shapes[0].box.h, 20);
});

test('data-table borders preserve long division and unruled matrices', () => {
  const table = String.raw`\begin{array}{c|cc}x&1&2\\y&3&4\end{array}`;
  const division = String.raw`\begin{array}{r|ll}&x&1\\x&2&3\end{array}`;
  const matrix = String.raw`\begin{array}{cc}1&2\\3&4\end{array}`;
  const shapes = [table, division, matrix].map((tex, i) => ({
    id: String(i), box: { x: 0, y: 0, w: 70, h: 60 }, transcription: { tex },
  }));
  const result = prepare(slide(shapes), { height: 200 }).shapes.map(s => s.transcription.tex);
  assert.match(result[0], /\{\|c\|c\|c\|\}/);
  assert.equal(result[1], division);
  assert.equal(result[2], matrix);
});

test('a source question image presents one structured transcript including its figure description', () => {
  const renderer = require('../lesson-renderer.js');
  const markup = renderer.shape({
    id: 'question', kind: 'pic', box: { x: 0, y: 0, w: 300, h: 180 },
    asset: 'diagram.webp', alt: 'Question',
    accessibleTex: String.raw`Calculate \(\frac{2}{3}\) of the labelled length.`,
    diagramDescription: 'The marked length is 24 cm.',
  }, {});
  assert.match(markup, /class="lesson-question-transcript"/);
  assert.match(markup, /data-math="\\frac\{2\}\{3\}"/);
  assert.match(markup, /marked length is 24 cm/);
  assert.match(markup, /<img [^>]*alt=""/);
});

test('question marks require working for the same part; exam paper codes are not mark allocations', () => {
  const shape = (id, tex) => ({id, box:{x:0,y:0,w:180,h:80}, transcription:{tex}});
  const question = shape('prompt', String.raw`Edexcel M2 June 2005\par (a) Find the speed. (3)\par (b) Find the time. [2 marks]`);
  const answer = shape('work-0', String.raw`(a) Use equation (3) to find the speed. [M1] [A1] [A1]`);
  const bare = prepare(slide([question]), {height:200}).shapes[0].transcription.tex;
  assert.doesNotMatch(bare, /marks|\(3\)/);
  const checked = prepare(slide([question, answer]), {height:200}).shapes;
  assert.match(checked[0].transcription.tex, /speed\. \[3 marks\]/);
  assert.doesNotMatch(checked[0].transcription.tex, /2 marks/);
  assert.match(checked[1].transcription.tex, /equation \(3\)/);
});

test('separate mark labels, mixed maths runs and trailing punctuation follow the same rule', () => {
  const p = parts => ({fontSize:20,parts});
  const text = text => ({type:'text',text});
  const math = tex => ({type:'math',tex});
  const shape = {id:'question',box:{x:0,y:0,w:160,h:100},text:{paragraphs:[
    p([text('(a) Find '), math('p'), text('. '), text('(3)')]),
    p([text('(b) Exactly two programmes (2).')]),
    p([text('(5)')]), p([text('Use equation (3).')])
  ]}};
  const rows = prepare(slide([shape]),{height:200}).shapes[0].text.paragraphs;
  const line = i => rows[i].parts.map(r => r.text ?? r.tex).join('');
  assert.equal(line(0).trim(), '(a) Find p.');
  assert.equal(line(1), '(b) Exactly two programmes.');
  assert.equal(line(2), '');
  assert.equal(line(3), 'Use equation (3).');
});
