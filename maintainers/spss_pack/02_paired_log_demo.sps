* Encoding: UTF-8.
* Fixed synthetic teaching CSV only; candidate syntax, not executed in SPSS.
* Start in a NEW SPSS session using Unicode mode, with no unsaved user data.
* Run Section 1 first; inspect its output before selecting Section 2.
* GET DATA replaces an unnamed active dataset; do not run over user data.
* This is a paired log-scale bounds demonstration, not formal crossover BE.
* Generated paths must be valid; the generator prepares the output directory.
* Use a fresh extracted pack for each run; OUTPUT SAVE overwrites existing SPV.

* Section 1 - Import and manual whole-pair gates.
CD '@REPO_ROOT@'.
OUTPUT NEW.
SET DECIMAL DOT.
SHOW VERSION.
SHOW DECIMAL.

GET DATA
 /TYPE=TXT
 /FILE='datasets/teaching/bioeq_cmax.csv'
 /ENCODING='UTF8'
 /ARRANGEMENT=DELIMITED
 /FIRSTCASE=2
 /DELCASE=LINE
 /DELIMITERS=','
 /QUALIFIER='"'
 /VARIABLES=subject_id A16 cmax_R F16.5 cmax_T F16.5.
WEIGHT OFF.
FILTER OFF.
SPLIT FILE OFF.

COMPUTE check_missing_id=(subject_id='').
COMPUTE check_missing_pair=(NMISS(cmax_T,cmax_R)>0).
COMPUTE check_nonpositive=0.
IF (cmax_T<=0 OR cmax_R<=0) check_nonpositive=1.
AGGREGATE
 /OUTFILE=* MODE=ADDVARIABLES
 /BREAK=subject_id
 /id_rows=N.
FREQUENCIES VARIABLES=id_rows check_missing_id
 check_missing_pair check_nonpositive.
LIST VARIABLES=subject_id cmax_R cmax_T /CASES=FROM 1 TO 5.

* STOP HERE: all flags must be zero; every id_rows must equal one.
* Check complete-pair N and same-row subject alignment against the CSV.
* If any gate fails, stop; do not select Section 2 or delete one arm only.

* Section 2 - Transform only positive complete pairs; direction ln(T)-ln(R).
IF (cmax_T>0 AND cmax_R>0) ln_t=LN(cmax_T).
IF (cmax_T>0 AND cmax_R>0) ln_r=LN(cmax_R).
COMPUTE d_log=ln_t-ln_r.
VARIABLE LABELS d_log 'Paired log difference ln(T)-ln(R)'.
EXAMINE VARIABLES=d_log
 /PLOT=BOXPLOT NPPLOT
 /STATISTICS=DESCRIPTIVES
 /MISSING=LISTWISE.

* Inspect the DIFFERENCE Q-Q plot and outliers; a large SW P is not proof.
TITLE 'Paired log difference: CI90 bounds demo'.
T-TEST PAIRS=ln_t WITH ln_r (PAIRED)
 /MISSING=ANALYSIS
 /CRITERIA=CI(.90).

TITLE 'Paired log difference: CI95 difference test'.
T-TEST PAIRS=ln_t WITH ln_r (PAIRED)
 /MISSING=ANALYSIS
 /CRITERIA=CI(.95).

* Derive GMR and its CI90 from the current d_log values, not reference ends.
AGGREGATE
 /OUTFILE=* MODE=ADDVARIABLES
 /pair_n=N(d_log)
 /d_mean=MEAN(d_log)
 /d_sd=SD(d_log).
COMPUTE d_se=$SYSMIS.
COMPUTE tcrit90=$SYSMIS.
COMPUTE gmr_pct=$SYSMIS.
COMPUTE gmr90_lo_pct=$SYSMIS.
COMPUTE gmr90_hi_pct=$SYSMIS.
DO IF (pair_n>1 AND d_sd>0).
 COMPUTE d_se=d_sd/SQRT(pair_n).
 COMPUTE tcrit90=IDF.T(.95,pair_n-1).
 COMPUTE gmr_pct=100*EXP(d_mean).
 COMPUTE gmr90_lo_pct=100*EXP(d_mean-tcrit90*d_se).
 COMPUTE gmr90_hi_pct=100*EXP(d_mean+tcrit90*d_se).
END IF.
FORMATS pair_n (F8.0) d_mean d_sd d_se (F16.10)
 gmr_pct gmr90_lo_pct gmr90_hi_pct (F16.8).
TITLE 'GMR percent and CI90 from current log differences'.
LIST VARIABLES=pair_n d_mean d_sd d_se
 gmr_pct gmr90_lo_pct gmr90_hi_pct
 /CASES=FROM 1 TO 1.

* Missing derived results or zero/negligible difference SD require a stop.
* CI90 within teaching bounds is not a formal bioequivalence conclusion.
* Sequence, period, carryover assessment and other PK endpoints are absent.
OUTPUT SAVE OUTFILE='@OUTPUT_DIR@/02_paired_log_demo.spv'.
OUTPUT EXPORT
 /CONTENTS EXPORT=ALL
 /PDF DOCUMENTFILE='@OUTPUT_DIR@/02_paired_log_demo.pdf'.
