# Rscript scripts/validate_teaching.R [Python summary.csv] [R output directory]
# Run from the repository root; defaults: output/teaching/summary.csv, output/R-validation.
# Fixed teaching fixtures only; base R/stats, no car or SPSS validation.
# Levene(mean) is independently reconstructed as one-way ANOVA of absolute deviations.
# No data generation, raw-file edits, formal BE assessment, or general sparse-CI API.
# source() only defines run_validation(); WebR may call run_validation(c(...)) explicitly.
run_validation <- function(args = character()) {
  if (length(args) > 2L) stop("Expected at most two arguments")
  summary_path <- if (length(args) >= 1L) args[[1L]] else "output/teaching/summary.csv"
  out <- if (length(args) >= 2L) args[[2L]] else "output/R-validation"
  read_utf8 <- function(path) {
    x <- read.csv(path, fileEncoding = "UTF-8", stringsAsFactors = FALSE, check.names = FALSE)
    names(x) <- sub("^\ufeff", "", names(x))
    x
  }
  assay <- read_utf8("datasets/teaching/tablet_assay.csv")
  paired <- read_utf8("datasets/teaching/bioeq_cmax.csv")
  events <- read_utf8("datasets/teaching/adverse_events.csv")
  python <- read_utf8(summary_path)
  stopifnot(all(c("field", "value") %in% names(python)), !anyDuplicated(python$field),
    nrow(assay) == 40L, nrow(paired) == 24L, nrow(events) == 240L,
    all(c("tablet_id", "process", "assay_pct") %in% names(assay)),
    all(c("subject_id", "cmax_T", "cmax_R") %in% names(paired)),
    all(c("subject_id", "drug", "adverse_event") %in% names(events)),
    !anyNA(assay), !anyNA(paired), !anyNA(events),
    !anyDuplicated(assay$tablet_id), !anyDuplicated(paired$subject_id),
    !anyDuplicated(events$subject_id),
    all(assay$process %in% c("A_对照工艺", "B_新工艺")),
    all(events$drug %in% c("A药", "B药")), all(events$adverse_event %in% c(0, 1)))
  a <- assay$assay_pct[assay$process == "A_对照工艺"]
  b <- assay$assay_pct[assay$process == "B_新工艺"]
  stopifnot(length(a) == 20L, length(b) == 20L, all(is.finite(c(a, b))),
    diff(range(a)) > 0, diff(range(b)) > 0,
    all(is.finite(paired$cmax_T)), all(is.finite(paired$cmax_R)),
    all(paired$cmax_T > 0), all(paired$cmax_R > 0))
  rows <- list()
  put <- function(prefix, values) {
    for (j in seq_along(values)) rows[[length(rows) + 1L]] <<-
      data.frame(field = paste0(prefix, names(values)[j]), value = unname(values[j]))
  }
  sw <- function(prefix, x) {
    z <- shapiro.test(x)
    put(prefix, c(statistic = unname(z$statistic), pvalue = z$p.value))
  }
  test <- function(prefix, fit) put(prefix,
    c(statistic = unname(fit$statistic), df = unname(fit$parameter), pvalue = fit$p.value))
  matrix_fields <- function(prefix, x) {
    for (i in seq_len(nrow(x))) for (j in seq_len(ncol(x)))
      put("", setNames(x[i, j], paste0(prefix, "[", i - 1L, "][", j - 1L, "]")))
  }
  put("metadata.inputs.", c(tablet_assay.rows = nrow(assay),
    bioeq_cmax.rows = nrow(paired), adverse_events.rows = nrow(events)))
  put("tablet_assay.analysis_set.", c(input_rows = nrow(assay), included_rows = nrow(assay), excluded_rows = 0))
  for (g in c("A", "B")) {
    x <- if (g == "A") a else b
    prefix <- paste0("tablet_assay.groups.", g, ".")
    put(prefix, c(n = length(x), mean = mean(x), sd = sd(x)))
    sw(paste0(prefix, "shapiro."), x)
  }
  deviations <- c(abs(a - mean(a)), abs(b - mean(b)))
  group <- factor(rep(c("A", "B"), c(length(a), length(b))))
  lev <- anova(lm(deviations ~ group))
  put("tablet_assay.levene.", c(statistic = lev[["F value"]][1L], pvalue = lev[["Pr(>F)"]][1L]))
  for (method in c("pooled", "welch")) {
    fit <- t.test(b, a, var.equal = method == "pooled", conf.level = 0.95)
    prefix <- paste0("tablet_assay.tests.", method, ".")
    test(prefix, fit)
    put(prefix, c(mean_diff = mean(b) - mean(a), "ci95[0]" = fit$conf.int[1L], "ci95[1]" = fit$conf.int[2L]))
  }
  pooled_sd <- sqrt(((length(a) - 1) * var(a) + (length(b) - 1) * var(b)) / (length(a) + length(b) - 2))
  put("tablet_assay.", c(cohens_d = (mean(b) - mean(a)) / pooled_sd))
  # These columns already contain unique ID-aligned pairs, checked above.
  delta <- log(paired$cmax_T) - log(paired$cmax_R)
  stopifnot(diff(range(delta)) > 0)
  n <- length(delta); se <- sd(delta) / sqrt(n)
  fit <- t.test(log(paired$cmax_T), log(paired$cmax_R), paired = TRUE)
  put("paired_log_demo.analysis_set.", c(left_rows = n, right_rows = n, candidate_pairs = n, complete_pairs = n, excluded_pairs = 0))
  put("paired_log_demo.", c(mean_log_difference = mean(delta), sd_log_difference = sd(delta), se_log_difference = se,
    cohens_dz = mean(delta) / sd(delta), gmr_pct = 100 * exp(mean(delta))))
  sw("paired_log_demo.shapiro.", delta)
  test("paired_log_demo.paired_t.", fit)
  put("paired_log_demo.paired_t.", c("ci95_mean_log_difference[0]" = fit$conf.int[1L], "ci95_mean_log_difference[1]" = fit$conf.int[2L]))
  ci90 <- 100 * exp(mean(delta) + c(-1, 1) * qt(0.95, n - 1L) * se)
  put("paired_log_demo.", c("ci90_pct[0]" = ci90[1L], "ci90_pct[1]" = ci90[2L],
    "teaching_bounds_pct[0]" = 80, "teaching_bounds_pct[1]" = 125))
  tab <- table(factor(events$drug, levels = c("A药", "B药")), factor(events$adverse_event, levels = c(1, 0)))
  expected <- outer(rowSums(tab), colSums(tab)) / sum(tab)
  stopifnot(all(tab > 0), min(expected) >= 5)
  matrix_fields("adverse_events.table", tab)
  matrix_fields("adverse_events.expected", expected)
  put("adverse_events.", c(n = sum(tab), "row_n[0]" = sum(tab[1L, ]), "row_n[1]" = sum(tab[2L, ]), minimum_expected = min(expected)))
  pA <- tab[1L, 1L] / sum(tab[1L, ]); pB <- tab[2L, 1L] / sum(tab[2L, ])
  put("adverse_events.rates.", c("A药" = pA, "B药" = pB))
  test("adverse_events.tests.pearson.", chisq.test(tab, correct = FALSE))
  test("adverse_events.tests.yates.", chisq.test(tab, correct = TRUE))
  put("adverse_events.tests.fisher.", c(pvalue = fisher.test(tab, alternative = "two.sided")$p.value))
  sample_or <- tab[1L, 1L] * tab[2L, 2L] / (tab[1L, 2L] * tab[2L, 1L])
  or_ci <- exp(log(sample_or) + c(-1, 1) * 1.96 * sqrt(sum(1 / tab)))
  rd <- pA - pB
  rd_ci <- rd + c(-1, 1) * 1.96 * sqrt(pA * (1 - pA) / sum(tab[1L, ]) + pB * (1 - pB) / sum(tab[2L, ]))
  put("adverse_events.effects.odds_ratio_sample.", c(estimate = sample_or, "ci95[0]" = or_ci[1L], "ci95[1]" = or_ci[2L]))
  put("adverse_events.effects.risk_difference.", c(estimate = rd, "ci95[0]" = rd_ci[1L], "ci95[1]" = rd_ci[2L]))
  put("adverse_events.analysis_set.", c(input_rows = nrow(events), included_rows = nrow(events), excluded_rows = 0))
  # Literal aggregate teaching fixture, not reconstructed subject records.
  mc <- matrix(c(42, 18, 6, 54), 2, byrow = TRUE)
  mb <- mc[1L, 2L]; mcv <- mc[2L, 1L]; m <- mb + mcv
  matrix_fields("mcnemar_demo.table", mc)
  put("mcnemar_demo.", c(b = mb, c = mcv, discordant_pairs = m, n_pairs = sum(mc)))
  put("mcnemar_demo.marginal_rates.", c(A = sum(mc[1L, ]) / sum(mc), B = sum(mc[, 1L]) / sum(mc)))
  put("mcnemar_demo.tests.exact_binomial.", c(pvalue = binom.test(mb, m, p = 0.5, alternative = "two.sided")$p.value))
  test("mcnemar_demo.tests.chi_square_corrected.", mcnemar.test(mc, correct = TRUE))
  test("mcnemar_demo.tests.chi_square_uncorrected.", mcnemar.test(mc, correct = FALSE))
  result <- do.call(rbind, rows)
  stopifnot(!anyDuplicated(result$field), all(is.finite(result$value)))
  idx <- match(result$field, python$field)
  py_value <- suppressWarnings(as.numeric(python$value[idx]))
  # |R-Python| <= absolute tolerance + relative tolerance * |Python|.
  # Shapiro implementations use approximate P algorithms; its tolerance is explicit.
  is_sw <- grepl("\\.shapiro\\.", result$field)
  abs_tol <- ifelse(is_sw, 1e-8, 1e-9)
  rel_tol <- ifelse(is_sw, 1e-7, 1e-8)
  difference <- abs(result$value - py_value)
  tolerance <- abs_tol + rel_tol * abs(py_value)
  passed <- !is.na(idx) & is.finite(py_value) & is.finite(difference) & difference <= tolerance
  comparison <- data.frame(field = result$field, R_value = result$value, Python_value = py_value,
    absolute_difference = difference, absolute_tolerance = abs_tol, relative_tolerance = rel_tol,
    allowed_difference = tolerance, passed = passed)
  dir.create(out, recursive = TRUE, showWarnings = FALSE)
  write.csv(result, file.path(out, "r_results.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(comparison, file.path(out, "comparison.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  capture.output(cat("Scope: fixed teaching fixtures; base R/stats; no car/SPSS runtime claim.\n",
    "Levene(mean): one-way ANOVA of absolute group-mean deviations.\n",
    "Compared numeric fields only; metadata strings, diagnostics and formal BE are outside this check.\n",
    "Python summary: ", summary_path, "\n", sep = ""), sessionInfo(), file = file.path(out, "sessionInfo.txt"))
  if (!all(passed)) stop(sum(!passed), " numeric comparisons failed; inspect ", file.path(out, "comparison.csv"))
  message("Validated ", nrow(comparison), " numeric fields; saved outputs to ", out)
  invisible(list(n_checked = nrow(comparison), passed = TRUE, output_directory = out))
}
if (sys.nframe() == 0L) run_validation(commandArgs(trailingOnly = TRUE))
