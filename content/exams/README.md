# Checked June 2025 exam pilot

The five owner-supplied Edexcel question papers and matching mark schemes provide 47 original questions and 350 marks. `pilot-metadata.json` records their source identity, original question order, marks and syllabus mappings. `exam-catalogue.json` joins checked descriptors to the five printable payloads by stable ID. Original PDFs remain outside the public artifact.

Prompts use native HTML and LaTeX, with faithful source diagrams. The relevant original paper instructions accompany each standalone question, including rounding and mechanics gravity conventions. Solutions preserve the complete question-specific official mark schemes, alternative methods and guidance as ordered vector or high-resolution images. General marking-administration pages are omitted. Solution image text is not searchable mathematical text. Keep source diagrams and mathematical expressions intact at continuation boundaries.

Each paper retains its printed code, title, date, original question numbers and source hashes. The supplied mark-scheme hashes are authoritative; earlier linked-copy fingerprints remain separate provenance. Fully qualified `skillMappings` may span books, and do not allocate marks among skills.

Difficulty follows the requested paper order: 16 questions split 5/6/5, six split 2/2/2, ten split 3/4/3 and nine split 3/3/3. This is a guide rather than a measured difficulty rating. QP/MS totals agree for all 47 questions. Core Pure 1's general marking guidance mentions 100 marks; its paper and question totals establish 75.

The existing 2,475 booklet entries retain their IDs and original payloads. Classification in `content/practice-classification.json` places 290 source-labelled exam-style entries and 88 each Bronze/Silver/Gold in Exam bank, with Bronze/Silver/Gold mapped to Easy/Medium/Difficult. Other difficulty remains unknown. Exam bank therefore has 601 questions; Practice questions has 8,068. The combined pool has 8,669 questions.

Run `python3 -m unittest discover -s tests -p test_exam_metadata.py` for source identity, joins, assets, marks, difficulty and unchanged practice payload checks. Per-paper source/visual acceptance and six-mode integrated printing are recorded in `docs/evidence/v059-import-*.json`.
