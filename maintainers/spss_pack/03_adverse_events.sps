* Encoding: UTF-8.
* Fixed nonsparse synthetic teaching CSV only; not a general sparse-table tool.
* Candidate syntax, not executed in SPSS.
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
 /FILE='datasets/teaching/adverse_events.csv'
 /ENCODING='UTF8'
 /ARRANGEMENT=DELIMITED
 /FIRSTCASE=2
 /DELCASE=LINE
 /DELIMITERS=','
 /QUALIFIER='"'
 /VARIABLES=subject_id A16 drug A40 adverse_event F8.0.
WEIGHT OFF.
FILTER OFF.
SPLIT FILE OFF.

COMPUTE drug_code=$SYSMIS.
IF (drug='A药') drug_code=1.
IF (drug='B药') drug_code=2.
VALUE LABELS drug_code 1 'A药' 2 'B药'.
COMPUTE event_display=$SYSMIS.
IF (adverse_event=1) event_display=1.
IF (adverse_event=0) event_display=2.
VALUE LABELS event_display 1 '发生' 2 '未发生'.
COMPUTE check_missing_id=(subject_id='').
COMPUTE check_bad_drug=MISSING(drug_code).
COMPUTE check_bad_event=MISSING(event_display).
AGGREGATE
 /OUTFILE=* MODE=ADDVARIABLES
 /BREAK=subject_id
 /id_rows=N.
FREQUENCIES VARIABLES=drug drug_code adverse_event event_display
 id_rows check_missing_id check_bad_drug check_bad_event.

* STOP HERE: all flags must be zero; every id_rows must equal one.
* Check both group counts and total N against the generated acceptance sheet.
* If any gate fails, stop; do not select Section 2 or silently recode values.

* Section 2 - Independent table, A/B rows and event/non-event columns.
TITLE 'Independent adverse events: A versus B, event first'.
CROSSTABS
 /TABLES=drug_code BY event_display
 /STATISTICS=CHISQ RISK
 /CELLS=COUNT EXPECTED ROW.

* CHISQ requests Pearson and the built-in two-by-two Yates/Fisher output.
* No METHOD=EXACT add-on is requested; inspect the actual Fisher row/columns.
* Select the prespecified course method, not the smallest of several P values.
* Verify the Risk Estimate compares A to B and event to non-event.
* Its OR point estimate must match the explicit sample OR derived below.
* Native SPSS CI endpoints can differ in last digits through critical constants.

* Derive A-minus-B risk difference and Wald CI95 from actual individual flags.
COMPUTE is_a=(drug_code=1).
COMPUTE is_b=(drug_code=2).
COMPUTE event_a=(drug_code=1 AND adverse_event=1).
COMPUTE event_b=(drug_code=2 AND adverse_event=1).
AGGREGATE
 /OUTFILE=* MODE=ADDVARIABLES
 /n_a=SUM(is_a)
 /n_b=SUM(is_b)
 /events_a=SUM(event_a)
 /events_b=SUM(event_b).
COMPUTE risk_a=$SYSMIS.
COMPUTE risk_b=$SYSMIS.
COMPUTE rd_a_minus_b=$SYSMIS.
COMPUTE rd_se=$SYSMIS.
COMPUTE rd95_lo=$SYSMIS.
COMPUTE rd95_hi=$SYSMIS.
COMPUTE sample_or=$SYSMIS.
COMPUTE or_log_se=$SYSMIS.
COMPUTE or95_lo=$SYSMIS.
COMPUTE or95_hi=$SYSMIS.
COMPUTE zcrit=1.96.
DO IF (n_a>0 AND n_b>0).
 COMPUTE risk_a=events_a/n_a.
 COMPUTE risk_b=events_b/n_b.
 COMPUTE rd_a_minus_b=risk_a-risk_b.
 COMPUTE rd_se=SQRT(risk_a*(1-risk_a)/n_a+risk_b*(1-risk_b)/n_b).
 COMPUTE rd95_lo=rd_a_minus_b-zcrit*rd_se.
 COMPUTE rd95_hi=rd_a_minus_b+zcrit*rd_se.
END IF.
DO IF (events_a>0 AND events_b>0 AND n_a>events_a AND n_b>events_b).
 COMPUTE sample_or=events_a*(n_b-events_b)/((n_a-events_a)*events_b).
 COMPUTE or_log_se=SQRT(1/events_a+1/(n_a-events_a)
  +1/events_b+1/(n_b-events_b)).
 COMPUTE or95_lo=EXP(LN(sample_or)-zcrit*or_log_se).
 COMPUTE or95_hi=EXP(LN(sample_or)+zcrit*or_log_se).
END IF.
FORMATS n_a n_b events_a events_b (F8.0)
 risk_a risk_b rd_a_minus_b rd_se rd95_lo rd95_hi
 sample_or or_log_se or95_lo or95_hi (F16.10).
TITLE 'A versus B: RD Wald and sample OR log-Wald CI95'.
LIST VARIABLES=n_a events_a n_b events_b risk_a risk_b
 zcrit rd_a_minus_b rd_se rd95_lo rd95_hi
 sample_or or_log_se or95_lo or95_hi
 /CASES=FROM 1 TO 1.

* The Wald interval here is for the fixed nonsparse teaching data only.
* Do not reuse it for rare events, zero cells or boundary risks without review.
OUTPUT SAVE OUTFILE='@OUTPUT_DIR@/03_adverse_events.spv'.
OUTPUT EXPORT
 /CONTENTS EXPORT=ALL
 /PDF DOCUMENTFILE='@OUTPUT_DIR@/03_adverse_events.pdf'.
