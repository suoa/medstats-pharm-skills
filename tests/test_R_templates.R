# Rscript tests/test_R_templates.R
# Run from repository root. Uses actual fenced R blocks, not copied algorithms.
# Fixed teaching fixtures and explicit counterexamples; passing does not prove general robustness.
# Snippets and fixtures use temporary directories; evidence is copied to output/R-template-validation.
# Only reports/session information and case output/ directories persist; no CSV input copies persist.
# source() defines run_R_template_tests(); WebR may call it explicitly.
run_R_template_tests <- function(repo_root = getwd(), output_dir = NULL) {
  repo_root <- normalizePath(repo_root, mustWork = TRUE)
  if (is.null(output_dir)) output_dir <- file.path(repo_root, "output/R-template-validation")
  r_blocks <- function(relative_path) {
    lines <- readLines(file.path(repo_root, relative_path), encoding = "UTF-8", warn = FALSE)
    starts <- which(grepl("^```r[[:space:]]*$", lines))
    lapply(starts, function(i) {
      closing <- which(grepl("^```[[:space:]]*$", lines) & seq_along(lines) > i)
      if (!length(closing)) stop("Unclosed R fence: ", relative_path)
      paste(lines[seq.int(i + 1L, closing[1L] - 1L)], collapse = "\n")
    })
  }
  t_blocks <- r_blocks("skills/methods-core/t-test/SKILL.md")
  chi_blocks <- r_blocks("skills/methods-core/chi-square/SKILL.md")
  example_blocks <- r_blocks("skills/methods-core/chi-square/references/examples.md")
  stopifnot(length(t_blocks) == 1L, length(chi_blocks) == 1L, length(example_blocks) == 2L)
  t_code <- t_blocks[[1L]]; chi_code <- chi_blocks[[1L]]
  effect_code <- example_blocks[[1L]]; mc_code <- example_blocks[[2L]]
  stopifnot(grepl('policy <- "course"', t_code, fixed = TRUE),
    grepl("sample_or", effect_code, fixed = TRUE), grepl("binom.test", mc_code, fixed = TRUE))
  welch_code <- sub('policy <- "course"', 'policy <- "welch"', t_code, fixed = TRUE)
  csv_names <- c("tablet_assay.csv", "bioeq_cmax.csv", "adverse_events.csv")
  raw_paths <- file.path(repo_root, "datasets/teaching", csv_names)
  read_raw <- function(path) readBin(path, "raw", n = file.info(path)$size)
  raw_before <- lapply(raw_paths, read_raw)
  root <- tempfile("medstats-R-templates-")
  dir.create(file.path(root, "datasets/teaching"), recursive = TRUE)
  stopifnot(all(file.copy(raw_paths, file.path(root, "datasets/teaching"))))
  fixture <- read.csv(file.path(root, "datasets/teaching/tablet_assay.csv"),
    fileEncoding = "UTF-8", stringsAsFactors = FALSE)
  a <- fixture$assay_pct[fixture$process == "A_对照工艺"]
  b <- fixture$assay_pct[fixture$process == "B_新工艺"]
  counter <- 0L
  execute <- function(code, bindings = list(), event_fixture = NULL) {
    counter <<- counter + 1L
    work <- file.path(root, sprintf("case-%02d", counter))
    dir.create(file.path(work, "datasets/teaching"), recursive = TRUE)
    stopifnot(all(file.copy(file.path(root, "datasets/teaching", csv_names),
      file.path(work, "datasets/teaching"))))
    if (!is.null(event_fixture)) write.csv(event_fixture,
      file.path(work, "datasets/teaching/adverse_events.csv"), row.names = FALSE, fileEncoding = "UTF-8")
    previous <- setwd(work)
    on.exit(setwd(previous), add = TRUE)
    env <- list2env(bindings, parent = .GlobalEnv)
    dir.create("output/chi_square_R", recursive = TRUE, showWarnings = FALSE)
    eval(parse(text = code), envir = env)
    attr(env, "work_directory") <- work
    env
  }
  check <- function(ok, message = "assertion failed") if (!isTRUE(ok)) stop(message)
  near <- function(actual, expected, tolerance = 1e-8) {
    length(actual) == length(expected) && all(is.finite(actual)) &&
      all(abs(actual - expected) <= tolerance)
  }
  expect_error <- function(expr, pattern = ".") {
    message <- tryCatch({force(expr); NA_character_}, error = function(e) conditionMessage(e))
    check(!is.na(message) && grepl(pattern, message), paste("Expected error matching", pattern, "; got", message))
  }
  results <- list()
  case <- function(name, expr) {
    error <- tryCatch({force(expr); ""}, error = function(e) conditionMessage(e))
    results[[length(results) + 1L]] <<- data.frame(case = name, passed = !nzchar(error), detail = error)
  }
  normal <- NULL
  case("t: submitted data, course and saved output", {
    normal <- execute(t_code, list(a = a, b = b))
    check(normal$use_pooled && near(normal$fit$statistic, 2.337732157502677))
    check(near(normal$fit$parameter, 38) && near(normal$fit$p.value, 0.02476760449216479))
    check(file.exists(file.path(attr(normal, "work_directory"), "output/t_result.csv")))
    check(file.exists(file.path(attr(normal, "work_directory"), "output/t_run.txt")))
  })
  case("t: submitted data, prespecified Welch", {
    env <- execute(welch_code, list(a = a, b = b))
    check(!env$use_pooled && grepl("Welch", env$fit$method))
    check(near(env$fit$parameter, 37.35933792392514))
  })
  case("t: n=2, Shapiro not assessed and Welch computed", {
    env <- execute(welch_code, list(a = 1:2, b = 3:4))
    check(is.finite(env$fit$p.value))
    check(identical(env$diagnostics$shapiro_A$status, "not_assessed"))
    check(identical(env$diagnostics$shapiro_B$status, "not_assessed"))
  })
  case("t: n>5000, Shapiro not assessed and Welch computed", {
    x <- seq_len(5001) / 5001
    env <- execute(welch_code, list(a = x, b = x + 0.25))
    check(is.finite(env$fit$p.value))
    check(identical(env$diagnostics$shapiro_A$status, "not_assessed"))
    check(identical(env$diagnostics$shapiro_B$status, "not_assessed"))
  })
  undefined <- list(a = c(-1, 1, -1, 1), b = c(9, 11, 9, 11))
  case("t: undefined Levene stops course", expect_error(execute(t_code, undefined), "Levene"))
  case("t: undefined Levene does not stop fixed Welch", {
    env <- execute(welch_code, undefined)
    check(is.finite(env$fit$p.value) && !env$use_pooled)
    check(identical(env$diagnostics$levene$status, "not_required_by_prespecified_Welch"))
  })
  case("safe_t: all-zero sample rejected", {
    expect_error(normal$safe_t(rep(0, 3)), "退化")
    check(identical(normal$safe_sw(rep(0, 3))$status, "not_assessed"))
  })
  case("safe_t: zero paired differences rejected", expect_error(normal$safe_t(1:3, 1:3, paired = TRUE), "退化"))
  case("safe_t: constant condition with varying paired differences allowed", {
    fit <- normal$safe_t(rep(1, 4), c(1, 2, 4, 8), paired = TRUE)
    check(is.finite(fit$p.value) && all(is.finite(fit$conf.int)))
  })
  case("safe_t: constant-ratio logarithmic rounding rejected", {
    expect_error(normal$safe_t(log(c(2, 4, 6)), log(c(1, 2, 3)), paired = TRUE), "精度|退化")
  })
  reference_tab <- matrix(c(24, 96, 8, 112), 2, byrow = TRUE)
  case("chi: actual CSV, Pearson direction and exact McNemar", {
    env <- execute(chi_code)
    check(identical(as.numeric(env$tab), as.numeric(reference_tab)))
    check(near(env$primary$statistic, 9.23076923076923))
    check(near(env$primary$p.value, 0.002379816463809706))
    check(near(env$exact$p.value, 0.022655844688415527))
    check(file.exists(file.path(attr(env, "work_directory"), "output/chi_square_R/table.csv")))
  })
  case("effects: normal table retains OR=3.5 and finite intervals", {
    env <- execute(effect_code, list(tab = reference_tab))
    check(near(env$sample_or, 3.5) && near(env$rd, 0.1333333333333333))
    check(near(env$or_ci, c(1.5029542306347092, 8.150614137349166)))
    check(near(env$rd_ci, c(0.04898836268259406, 0.21767830398407267)))
    check(identical(env$ci_status, "Wald_z_1.96"))
  })
  case("effects: sparse positive table omits both Wald intervals", {
    env <- execute(effect_code, list(tab = matrix(c(1, 2, 12, 1), 2, byrow = TRUE)))
    check(near(env$sample_or, 1 / 24) && is.finite(env$rd))
    check(all(is.na(env$or_ci)) && all(is.na(env$rd_ci)))
    check(identical(env$ci_status, "not_estimated_sparse_or_zero_cell"))
  })
  case("effects: zero-cell OR=0 retained without intervals", {
    env <- execute(effect_code, list(tab = matrix(c(0, 20, 4, 16), 2, byrow = TRUE)))
    check(near(env$sample_or, 0) && all(is.na(env$or_ci)) && all(is.na(env$rd_ci)))
  })
  case("effects: zero-cell OR=Inf retained without intervals", {
    env <- execute(effect_code, list(tab = matrix(c(4, 16, 0, 20), 2, byrow = TRUE)))
    check(identical(env$sample_or, Inf) && all(is.na(env$or_ci)) && all(is.na(env$rd_ci)))
  })
  case("effects: degenerate margin rejected", {
    expect_error(execute(effect_code, list(tab = matrix(c(30, 0, 30, 0), 2, byrow = TRUE))))
  })
  case("chi: actual temporary CSV with degenerate margin rejected", {
    bad <- data.frame(subject_id = paste0("D", 1:60), drug = rep(c("A药", "B药"), each = 30), adverse_event = 1)
    expect_error(execute(chi_code, event_fixture = bad), "退化表")
  })
  case("McNemar: example block exact P and saved output", {
    env <- execute(mc_code)
    check(near(env$exact$p.value, 0.022655844688415527))
    check(file.exists(file.path(attr(env, "work_directory"), "output/chi_square_R/mcnemar.txt")))
  })
  case("McNemar: zero discordance describes without exact test", {
    check(grepl("c(42, 18, 6, 54)", mc_code, fixed = TRUE))
    code <- sub("c(42, 18, 6, 54)", "c(42, 0, 0, 54)", mc_code, fixed = TRUE)
    env <- execute(code)
    check(env$m == 0 && !exists("exact", envir = env, inherits = FALSE))
    output <- readLines(file.path(attr(env, "work_directory"), "output/chi_square_R/mcnemar.txt"), encoding = "UTF-8")
    check(any(grepl("无不一致对子", output)))
  })
  case("original CSV bytes unchanged", check(identical(raw_before, lapply(raw_paths, read_raw))))
  report <- do.call(rbind, results)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  output_dir <- normalizePath(output_dir, mustWork = TRUE)
  write.csv(report, file.path(output_dir, "test_results.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  capture.output(sessionInfo(), file = file.path(output_dir, "sessionInfo.txt"))
  # A unique evidence subdirectory prevents files from earlier runs appearing as current output.
  evidence_dir <- file.path(output_dir, "case_outputs", basename(root))
  dir.create(evidence_dir, recursive = TRUE, showWarnings = FALSE)
  for (work in list.dirs(root, recursive = FALSE, full.names = TRUE)) {
    source_output <- file.path(work, "output")
    if (dir.exists(source_output)) {
      destination <- file.path(evidence_dir, basename(work))
      dir.create(destination, recursive = TRUE, showWarnings = FALSE)
      if (!all(file.copy(source_output, destination, recursive = TRUE)))
        stop("Could not preserve case output: ", source_output)
    }
  }
  if (!all(report$passed)) stop(sum(!report$passed), " R template cases failed; inspect ", file.path(output_dir, "test_results.csv"))
  message("Passed ", nrow(report), " R template cases; saved evidence: ", output_dir)
  invisible(list(n_passed = nrow(report), report = report, output_directory = output_dir,
    evidence_directory = evidence_dir))
}
if (sys.nframe() == 0L) run_R_template_tests()
