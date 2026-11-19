# Past-exam metadata pilot

`pilot-metadata.json` contains identifiers and syllabus metadata for five June 2025 Edexcel papers: 47 original questions and 350 marks. It contains no question text, question crops, mark-scheme text, hints or solutions. It must not be joined into the printable question catalogue while `printable` is false or `contentStatus` is `awaiting-owner-source-attachment`.

Each paper retains its printed paper code, title, date, question order, original question numbers, question-paper and mark-scheme URLs, and source SHA-256 hashes. `sourceQuestionPages` uses one-based inclusive PDF page numbers and includes the answer space belonging to that question. `skillMappings` contains fully qualified course/book/topic/skill references to `data.js`; mixed questions can cross books. Mapping is at whole-question level and does not allocate marks among skills.

Difficulty follows the requested original-paper order: 16 questions split 5/6/5, six split 2/2/2, ten split 3/4/3 and nine split 3/3/3 into easy/medium/difficult. This is a selection convention, not a measured difficulty rating. QP and MS per-question totals were compared independently and agree for all 47 questions. Core Pure 1's generic mark-scheme guidance mentions 100 marks; the paper and all question totals establish 75.

The existing practice-booklet classification is separate at `content/practice-classification.json`. Join it by the unchanged `id`; use `bank` for practice/exam selection. The 290 selected exam-bank questions have `examType: "exam-style"` and unknown (`null`) difficulty. The 88 Bronze, 88 Silver and 88 Gold questions are exam questions with easy, medium and difficult labels. The remaining 1,921 questions retain practice membership and unknown difficulty. Do not infer difficulty from position for these booklet questions.

Run `python3 -m unittest discover -s tests -p test_exam_metadata.py` to verify full stable-ID coverage, unchanged chapter hashes, category rules, pilot exclusion, marks, question numbering, difficulty bands and syllabus joins. Shared catalogue integration and release acceptance belong to the lead task.
