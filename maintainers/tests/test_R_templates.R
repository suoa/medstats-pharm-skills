# Rscript maintainers/tests/test_R_templates.R
# 从仓库根目录运行。实际抽取技能文件里的 R 代码块执行，不是另抄一份算法。
# 固定教学数据；通过不代表对一般数据稳健。代码块在临时目录执行，不改动仓库 CSV。
# source() 定义 run_R_template_tests()；无参数直接运行即执行全部用例。
run_R_template_tests <- function(repo_root = getwd()) {
  repo_root <- normalizePath(repo_root, mustWork = TRUE)
  r_blocks <- function(relative_path) {
    lines <- readLines(file.path(repo_root, relative_path), encoding = "UTF-8", warn = FALSE)
    starts <- which(grepl("^```r[[:space:]]*$", lines))
    lapply(starts, function(i) {
      closing <- which(grepl("^```[[:space:]]*$", lines) & seq_along(lines) > i)
      if (!length(closing)) stop("未闭合的 R 代码块: ", relative_path)
      paste(lines[seq.int(i + 1L, closing[1L] - 1L)], collapse = "\n")
    })
  }
  t_blocks <- r_blocks("skills/methods-core/t-test/SKILL.md")
  t_example_blocks <- r_blocks("skills/methods-core/t-test/references/examples.md")
  chi_blocks <- r_blocks("skills/methods-core/chi-square/SKILL.md")
  stopifnot(length(t_blocks) == 1L, length(t_example_blocks) == 1L, length(chi_blocks) == 1L)
  t_code <- t_blocks[[1L]]
  t_example_code <- t_example_blocks[[1L]]
  chi_code <- chi_blocks[[1L]]

  csv_names <- c("tablet_assay.csv", "bioeq_cmax.csv", "adverse_events.csv")
  root <- tempfile("medstats-R-templates-")
  dir.create(file.path(root, "datasets/teaching"), recursive = TRUE)
  file.copy(file.path(repo_root, "datasets/teaching", csv_names),
            file.path(root, "datasets/teaching"), overwrite = TRUE)
  fixture <- read.csv(file.path(root, "datasets/teaching/tablet_assay.csv"),
                      fileEncoding = "UTF-8", stringsAsFactors = FALSE)
  a <- fixture$assay_pct[fixture$process == "A_对照工艺"]
  b <- fixture$assay_pct[fixture$process == "B_新工艺"]

  counter <- 0L
  execute <- function(code, bindings = list()) {
    counter <<- counter + 1L
    work <- file.path(root, sprintf("case-%02d", counter))
    dir.create(file.path(work, "datasets/teaching"), recursive = TRUE)
    file.copy(file.path(root, "datasets/teaching", csv_names),
              file.path(work, "datasets/teaching"), overwrite = TRUE)
    previous <- setwd(work)
    on.exit(setwd(previous), add = TRUE)
    env <- list2env(bindings, parent = .GlobalEnv)
    dir.create("output", recursive = TRUE, showWarnings = FALSE)
    eval(parse(text = code), envir = env)
    attr(env, "work_directory") <- work
    env
  }
  check <- function(ok, message = "assertion failed") if (!isTRUE(ok)) stop(message)
  near <- function(actual, expected, tolerance = 1e-6) {
    length(actual) == length(expected) && all(is.finite(actual)) &&
      all(abs(actual - expected) <= tolerance)
  }
  results <- list()
  case <- function(name, expr) {
    error <- tryCatch({force(expr); ""}, error = function(e) conditionMessage(e))
    results[[length(results) + 1L]] <<- data.frame(case = name, passed = !nzchar(error), detail = error)
  }

  case("t SKILL块: 合并方差 t 复现课本路线", {
    env <- execute(t_code, list(a = a, b = b))
    check(near(env$fit$statistic, 2.337732157502677))
    check(near(env$fit$parameter, 38) && near(env$fit$p.value, 0.02476760449216479))
  })
  case("t 例题块: 读 CSV、保存结果", {
    env <- execute(t_example_code)
    out <- read.csv(file.path(attr(env, "work_directory"), "output/t_independent_result.csv"))
    check(near(out$t, 2.337732157502677) && near(out$p, 0.02476760449216479))
    check(near(out$mean_diff, 0.76))
  })
  reference_tab <- matrix(c(24, 96, 8, 112), 2, byrow = TRUE)
  case("chi SKILL块: 实际 CSV，表方向与 Pearson、精确 McNemar", {
    env <- execute(chi_code)
    check(identical(as.numeric(env$tab), as.numeric(reference_tab)))
    check(near(env$primary$statistic, 9.23076923076923))
    check(near(env$primary$p.value, 0.002379816463809706))
    check(file.exists(file.path(attr(env, "work_directory"), "output/chi_square_R/table.csv")))
    check(file.exists(file.path(attr(env, "work_directory"), "output/chi_square_R/mcnemar_exact.txt")))
  })

  report <- do.call(rbind, results)
  print(report, row.names = FALSE)
  failed <- report[!report$passed, , drop = FALSE]
  if (nrow(failed)) stop(nrow(failed), " 个 R 模板用例失败")
  message("R 模板 ", nrow(report), " 个用例全部通过（临时目录执行，未改动仓库数据）")
  invisible(list(n_checked = nrow(report), passed = TRUE))
}

if (sys.nframe() == 0L) run_R_template_tests()
