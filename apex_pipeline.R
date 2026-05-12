# ═══════════════════════════════════════════════════════════════════════════
# APEX CREDIT SENTINEL — R Pipeline (run in RStudio)
# Put borrower_data.csv in the same folder as this script, then Source it.
# ═══════════════════════════════════════════════════════════════════════════

# Auto-install + load packages
needed <- c("dplyr", "ggplot2", "rpart", "randomForest", "pROC", "caret")
missing <- needed[!needed %in% installed.packages()[, "Package"]]
if (length(missing)) install.packages(missing)
invisible(lapply(needed, library, character.only = TRUE))

set.seed(42)
THRESHOLD <- 0.65

# ─── STEP 1: Load dataset ───────────────────────────────────────────────────
cat("STEP 1 — Loading borrower_data.csv...\n")
if (!file.exists("borrower_data.csv")) {
  stop("Put borrower_data.csv in the same folder as this script.")
}
df <- read.csv("borrower_data.csv")
df$Loan_Status <- factor(df$Loan_Status, levels = c(0, 1),
                          labels = c("Default", "Paid"))
cat(sprintf("  Rows: %d | Default rate: %.1f%%\n\n",
            nrow(df), mean(df$Loan_Status == "Default") * 100))

# ─── STEP 2: 70/30 stratified split ─────────────────────────────────────────
cat("STEP 2 — Splitting 70/30 stratified...\n")
train_idx <- createDataPartition(df$Loan_Status, p = 0.70, list = FALSE)
train <- df[train_idx, ]
test  <- df[-train_idx, ]
cat(sprintf("  Train: %d | Test: %d\n\n", nrow(train), nrow(test)))

# ─── STEP 3: Train 3 models ─────────────────────────────────────────────────
cat("STEP 3 — Training 3 models...\n")
m_logit <- glm(Loan_Status ~ ., data = train, family = binomial())
m_tree  <- rpart(Loan_Status ~ ., data = train, method = "class",
                 control = rpart.control(maxdepth = 3, minbucket = 40, cp = 0.005))
m_rf    <- randomForest(Loan_Status ~ ., data = train,
                        ntree = 200, mtry = 4, nodesize = 15)
cat("  ✓ Logistic Regression | Decision Tree | Random Forest trained\n\n")

# ─── STEP 4: Evaluate + Profitability Index ─────────────────────────────────
cat("STEP 4 — Evaluating + Profitability...\n")

profitability <- function(actual, predicted, test_df, rate = 0.18) {
  profit <- 0
  for (i in seq_along(actual)) {
    if (predicted[i] == "Paid" && actual[i] == "Paid") {
      profit <- profit + test_df$Loan_Amount[i] * rate * 2
    } else if (predicted[i] == "Paid" && actual[i] == "Default") {
      profit <- profit - test_df$Loan_Amount[i]
    }
  }
  profit
}

eval_model <- function(name, model, test_df, type) {
  if (type == "glm") {
    proba <- predict(model, newdata = test_df, type = "response")
  } else if (type == "tree") {
    proba <- predict(model, newdata = test_df, type = "prob")[, "Paid"]
  } else {
    proba <- predict(model, newdata = test_df, type = "prob")[, "Paid"]
  }
  pred <- factor(ifelse(proba >= THRESHOLD, "Paid", "Default"),
                  levels = c("Default", "Paid"))
  cm <- confusionMatrix(pred, test_df$Loan_Status, positive = "Paid")
  tn <- cm$table["Default", "Default"]; fp <- cm$table["Paid", "Default"]
  fn <- cm$table["Default", "Paid"];    tp <- cm$table["Paid", "Paid"]
  auc_val <- as.numeric(pROC::auc(roc(test_df$Loan_Status, proba,
                                       levels = c("Default", "Paid"),
                                       direction = "<", quiet = TRUE)))
  list(
    Model = name,
    AUC_ROC = round(auc_val, 3),
    Accuracy = round(as.numeric(cm$overall["Accuracy"]), 3),
    False_Positive_Rate = round(fp / (fp + tn), 3),
    TP = tp, FP = fp, TN = tn, FN = fn,
    Profitability_USD = round(profitability(test_df$Loan_Status, pred, test_df), 0),
    proba = proba
  )
}

r1 <- eval_model("Logistic Regression", m_logit, test, "glm")
r2 <- eval_model("Decision Tree",       m_tree,  test, "tree")
r3 <- eval_model("Random Forest",       m_rf,    test, "rf")

dashboard <- data.frame(
  Model               = c(r1$Model, r2$Model, r3$Model),
  AUC_ROC             = c(r1$AUC_ROC, r2$AUC_ROC, r3$AUC_ROC),
  Accuracy            = c(r1$Accuracy, r2$Accuracy, r3$Accuracy),
  False_Positive_Rate = c(r1$False_Positive_Rate, r2$False_Positive_Rate, r3$False_Positive_Rate),
  TP                  = c(r1$TP, r2$TP, r3$TP),
  FP                  = c(r1$FP, r2$FP, r3$FP),
  TN                  = c(r1$TN, r2$TN, r3$TN),
  FN                  = c(r1$FN, r2$FN, r3$FN),
  Profitability_USD   = c(r1$Profitability_USD, r2$Profitability_USD, r3$Profitability_USD)
)
cat("\n════════════ MANAGER DASHBOARD ════════════\n")
print(dashboard, row.names = FALSE)

winner <- dashboard$Model[which.max(dashboard$Profitability_USD)]
cat(sprintf("\n🏆 WINNER: %s | $%s profit | AUC %.3f\n",
            winner,
            format(max(dashboard$Profitability_USD), big.mark = ","),
            dashboard$AUC_ROC[dashboard$Model == winner]))

write.csv(dashboard, "model_dashboard.csv", row.names = FALSE)

# ─── STEP 5: Charts ─────────────────────────────────────────────────────────
cat("\nSTEP 5 — Plotting charts...\n")
roc1 <- roc(test$Loan_Status, r1$proba, levels = c("Default","Paid"), direction = "<", quiet = TRUE)
roc2 <- roc(test$Loan_Status, r2$proba, levels = c("Default","Paid"), direction = "<", quiet = TRUE)
roc3 <- roc(test$Loan_Status, r3$proba, levels = c("Default","Paid"), direction = "<", quiet = TRUE)

roc_df <- rbind(
  data.frame(Model = sprintf("Logistic Regression (AUC=%.3f)", r1$AUC_ROC),
             FPR = 1 - roc1$specificities, TPR = roc1$sensitivities),
  data.frame(Model = sprintf("Decision Tree (AUC=%.3f)", r2$AUC_ROC),
             FPR = 1 - roc2$specificities, TPR = roc2$sensitivities),
  data.frame(Model = sprintf("Random Forest (AUC=%.3f)", r3$AUC_ROC),
             FPR = 1 - roc3$specificities, TPR = roc3$sensitivities)
)
p_roc <- ggplot(roc_df, aes(FPR, TPR, color = Model)) +
  geom_line(linewidth = 1.1) +
  geom_abline(slope = 1, linetype = "dashed", color = "grey50") +
  labs(title = "ROC Curves — Credit Default Models",
       x = "False Positive Rate", y = "True Positive Rate") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom", legend.title = element_blank(),
        plot.title = element_text(face = "bold"))
print(p_roc)
ggsave("roc_curves.png", p_roc, width = 7, height = 6, dpi = 150)

dashboard$is_winner <- dashboard$Model == winner
p_profit <- ggplot(dashboard, aes(Model, Profitability_USD, fill = is_winner)) +
  geom_col(width = 0.55) +
  geom_text(aes(label = paste0("$", format(Profitability_USD, big.mark = ","))),
            vjust = -0.4, size = 4.2) +
  scale_fill_manual(values = c(`FALSE` = "#C00000", `TRUE` = "#2E7D32"), guide = "none") +
  labs(title = "Profitability Index — Test Portfolio",
       subtitle = "Profit = (TP × Interest) − (FP × Principal)",
       x = NULL, y = "Portfolio Profit (USD)") +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"),
        panel.grid.major.x = element_blank())
print(p_profit)
ggsave("profitability.png", p_profit, width = 8, height = 5, dpi = 150)

imp <- importance(m_rf)
imp_df <- data.frame(Feature = rownames(imp), Importance = imp[, 1])
imp_df <- imp_df[order(imp_df$Importance), ]
imp_df$Feature <- factor(imp_df$Feature, levels = imp_df$Feature)
p_imp <- ggplot(tail(imp_df, 15), aes(Importance, Feature)) +
  geom_col(fill = "#2E75B6") +
  labs(title = "Top 15 Features — Random Forest", x = "Importance", y = NULL) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"))
print(p_imp)
ggsave("feature_importance.png", p_imp, width = 9, height = 6, dpi = 150)

cat("\n═══════════════════════════════════════════════════════════\n")
cat("  ✓ PIPELINE COMPLETE — files saved in:", getwd(), "\n")
cat("═══════════════════════════════════════════════════════════\n")
