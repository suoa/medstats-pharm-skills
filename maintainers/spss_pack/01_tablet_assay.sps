* Encoding: UTF-8.
* Fixed synthetic teaching CSV only; candidate syntax, not executed in SPSS.
* Start in a NEW SPSS session using Unicode mode, with no unsaved user data.
* Run Section 1 first; inspect its output before selecting Section 2.
* GET DATA replaces an unnamed active dataset; do not run over user data.
* Generated paths must be valid; the generator prepares the output directory.
* Use a fresh extracted pack for each run; OUTPUT SAVE overwrites existing SPV.

* Section 1 - Import and manual input gates.
CD '@REPO_ROOT@'.
OUTPUT NEW.
SET DECIMAL DOT.
SHOW VERSION.
SHOW DECIMAL.

GET DATA
 /TYPE=TXT
 /FILE='datasets/teaching/tablet_assay.csv'
 /ENCODING='UTF8'
 /ARRANGEMENT=DELIMITED
 /FIRSTCASE=2
 /DELCASE=LINE
 /DELIMITERS=','
 /QUALIFIER='"'
 /VARIABLES=tablet_id A16 process A80 assay_pct F12.5.
WEIGHT OFF.
FILTER OFF.
SPLIT FILE OFF.

COMPUTE process_code=$SYSMIS.
IF (process='A_对照工艺') process_code=1.
IF (process='B_新工艺') process_code=2.
VALUE LABELS process_code 1 'A_对照工艺' 2 'B_新工艺'.
COMPUTE check_missing_id=(tablet_id='').
COMPUTE check_bad_process=MISSING(process_code).
COMPUTE check_missing_assay=MISSING(assay_pct).
AGGREGATE
 /OUTFILE=* MODE=ADDVARIABLES
 /BREAK=tablet_id
 /id_rows=N.
FREQUENCIES VARIABLES=process process_code id_rows
 check_missing_id check_bad_process check_missing_assay.
CROSSTABS
 /TABLES=process BY process_code
 /CELLS=COUNT.

* STOP HERE: every check flag must be zero; every id_rows must equal one.
* Check both group counts and total N against the generated acceptance sheet.
* If any gate fails, stop; do not select Section 2 or silently remove cases.

* Section 2 - Diagnostics and named analyses, only after Section 1 passes.
TITLE 'Tablet assay: independent groups B minus A'.
EXAMINE VARIABLES=assay_pct BY process_code
 /PLOT=BOXPLOT NPPLOT
 /STATISTICS=DESCRIPTIVES
 /MISSING=LISTWISE
 /NOTOTAL.

* Cross-version backup for Levene; read Based on Mean for the course rule.
* Its ANOVA table is not an additional primary test for this task.
ONEWAY assay_pct BY process_code
 /STATISTICS HOMOGENEITY
 /MISSING ANALYSIS.

* Group 1 is B, group 2 is A; verify the mean difference is B minus A.
* Use the preselected course or Welch row; never select the smaller P value.
T-TEST GROUPS=process_code(2 1)
 /VARIABLES=assay_pct
 /MISSING=ANALYSIS
 /CRITERIA=CI(.95).

OUTPUT SAVE OUTFILE='@OUTPUT_DIR@/01_tablet_assay.spv'.
OUTPUT EXPORT
 /CONTENTS EXPORT=ALL
 /PDF DOCUMENTFILE='@OUTPUT_DIR@/01_tablet_assay.pdf'.
