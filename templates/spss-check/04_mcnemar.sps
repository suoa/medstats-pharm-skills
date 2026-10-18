* Encoding: UTF-8.
* Fixed synthetic aggregated teaching table only; generated rows below.
* Candidate syntax, not executed in SPSS.
* Start in a NEW SPSS session using Unicode mode, with no unsaved user data.
* Run Section 1 first; inspect its output before selecting Section 2.
* DATA LIST replaces an unnamed active dataset; do not run over user data.
* Generated paths must be valid; the generator prepares the output directory.
* Use a fresh extracted pack for each run; OUTPUT SAVE overwrites existing SPV.

* Section 1 - Import the complete square table: testA, testB, frequency.
CD '@REPO_ROOT@'.
OUTPUT NEW.
SET DECIMAL DOT.
SHOW VERSION.
SHOW DECIMAL.

* The generator inserts all four rows; test codes: 1 positive, 2 negative.
DATA LIST FREE /testA (F8.0) testB (F8.0) frequency (F12.0).
BEGIN DATA
@MCNEMAR_ROWS@
END DATA.
WEIGHT OFF.
FILTER OFF.
SPLIT FILE OFF.
VALUE LABELS testA testB 1 '阳性' 2 '阴性'.
LIST VARIABLES=testA testB frequency.
FREQUENCIES VARIABLES=testA testB frequency.

* STOP HERE: exactly one row per category combination; all counts nonnegative.
* Compare the imported four rows and total count to the generated task sheet.
* If any gate fails, stop; do not select Section 2 or invent missing counts.

* Section 2 - Weighted paired table and the explicitly named comparison.
WEIGHT BY frequency.
TITLE 'Paired table: SPSS McNemar output for comparison'.
CROSSTABS
 /TABLES=testA BY testB
 /STATISTICS=MCNEMAR
 /CELLS=COUNT.

* Inspect the actual column label; software defaults need not match the course.
* The primary calculation uses only the two discordant weighted rows below.
TITLE 'Primary: two-sided exact binomial on discordant pairs'.
TEMPORARY.
SELECT IF (testA<>testB).
NPAR TESTS
 /BINOMIAL(.5)=testA(1,2).
WEIGHT OFF.

* Verify weighted discordant N and both category counts against the task sheet.
* Read the exact two-sided probability; do not substitute asymptotic or mid-P.
* This fixed task has a small discordant total; no Exact Tests add-on requested.
* Do not interpret absence of discordance as proof of equivalence.
OUTPUT SAVE OUTFILE='@OUTPUT_DIR@/04_mcnemar.spv'.
OUTPUT EXPORT
 /CONTENTS EXPORT=ALL
 /PDF DOCUMENTFILE='@OUTPUT_DIR@/04_mcnemar.pdf'.
