# LightGBM Model Training Module

## Overview

The `src/model_train.py` module trains a LightGBM binary classifier to predict purchase probability for (user, article) candidate pairs. It includes comprehensive evaluation metrics, feature importance analysis, and MAP@K computation.

## Features

### 1. LightGBM Binary Classification
- Predicts probability of user purchasing an article
- Uses gradient boosting decision trees (GBDT)
- Optimized for AUC metric
- Early stopping to prevent overfitting

### 2. Automatic Feature Preparation
- Automatically identifies feature columns
- Handles categorical features (e.g., user_age_bin)
- Fills missing values appropriately
- Excludes metadata columns (user_id, article_id, etc.)

### 3. Comprehensive Evaluation
- **AUC scores** on train and validation sets
- **ROC curve** visualization
- **Feature importance** analysis (top 15 features)
- **MAP@K metrics** (K=10, 20, 30) for ranking quality

### 4. Model Persistence
- Saves trained model using joblib
- Saves training metadata (params, metrics, timestamp)
- Enables model reloading for evaluation

## Default Parameters

```python
{
    'objective': 'binary',
    'boosting_type': 'gbdt',
    'metric': 'auc',
    'learning_rate': 0.03,
    'num_leaves': 128,
    'max_depth': 8,
    'min_child_samples': 20,
    'subsample': 0.8,
    'colsample_bytree': 0.7,
    'reg_alpha': 0.0,
    'reg_lambda': 0.0,
    'seed': 42
}
```

## Usage

### Basic Training
```bash
python src/model_train.py
```

### Custom Parameters
```bash
python src/model_train.py --num_boost_round 1000 --early_stopping_rounds 30
```

### Custom Data Paths
```bash
python src/model_train.py \
  --train_csv custom/train.csv \
  --val_csv custom/val.csv \
  --model_out models/lgbm_v2.pkl
```

### Evaluate Existing Model
```bash
python src/model_train.py --task evaluate --model_out models/lgbm_v1.pkl
```

### Custom Output Directory
```bash
python src/model_train.py --output_dir custom_outputs
```

## Functions

### Core Functions

**`load_training_data(train_csv, val_csv)`**
- Loads training and validation CSVs
- Returns tuple of (train_df, val_df)

**`prepare_features(df, exclude_cols)`**
- Identifies feature columns automatically
- Handles categorical features
- Fills missing values
- Returns (prepared_df, feature_cols, categorical_features)

**`train_lightgbm(train_df, val_df, feature_cols, categorical_features, params, num_boost_round, early_stopping_rounds)`**
- Trains LightGBM model with early stopping
- Uses validation set for monitoring
- Returns (model, training_info)

**`evaluate_model(model, train_df, val_df, feature_cols, output_dir)`**
- Computes AUC scores
- Generates ROC curve
- Analyzes feature importance
- Computes MAP@K metrics
- Returns evaluation_results dict

**`compute_mapk(model, val_df, feature_cols, k_values)`**
- Computes Mean Average Precision at K
- Ranks candidates by predicted score per user
- Returns MAP@K and Recall@K for each K

**`save_model_and_metadata(model, training_info, evaluation_results, model_out)`**
- Saves model using joblib
- Saves training metadata as JSON
- Includes params, metrics, timestamp

**`load_model(model_path)`**
- Loads trained model from disk
- Returns LightGBM Booster object

### Visualization Functions

**`plot_roc_curve(y_train, train_pred, y_val, val_pred, output_path)`**
- Plots ROC curves for train and validation
- Saves to `outputs/roc_curve.png`

**`plot_feature_importance(model, feature_names, output_path, top_n)`**
- Plots top N features by importance (gain)
- Saves to `outputs/feature_importance.png`

**`save_mapk_table(mapk_results, output_path)`**
- Saves MAP@K results to text file
- Saves to `outputs/mapk_table.txt`

## Output Files

### Model Files

**Location:** `models/`

1. **`lgbm_v1.pkl`** - Trained LightGBM model (joblib format)
2. **`training_metadata.json`** - Training metadata and metrics

### Evaluation Outputs

**Location:** `outputs/`

1. **`roc_curve.png`** - ROC curve visualization
2. **`feature_importance.png`** - Feature importance bar chart
3. **`mapk_table.txt`** - MAP@K and Recall@K results table

### Metadata JSON Structure

```json
{
  "timestamp": "2025-12-02T09:31:10.919688",
  "model_path": "models/lgbm_v1.pkl",
  "training": {
    "best_iteration": 1,
    "best_score": 1.0,
    "num_features": 13,
    "params": { ... }
  },
  "evaluation": {
    "train_auc": 1.0,
    "val_auc": 1.0,
    "mapk_results": {
      "10": {"map": 1.0, "recall": 1.0, "n_users": 2},
      "20": {"map": 1.0, "recall": 1.0, "n_users": 2},
      "30": {"map": 1.0, "recall": 1.0, "n_users": 2}
    }
  }
}
```

## Example Results

From test run with small dataset:

**Training:**
- Training samples: 132 (27 positives, 105 negatives)
- Validation samples: 13 (2 positives, 11 negatives)
- Best iteration: 1 (early stopping due to small data)
- Training AUC: 1.0000
- Validation AUC: 1.0000

**Feature Importance:**
- Top feature: `recent_interaction_flag_7d` (132.00 gain)
- Other features: 0.00 gain (due to small sample size)

**MAP@K Results:**
```
K         MAP@K          Recall@K       N Users
10        1.0000         1.0000         2
20        1.0000         1.0000         2
30        1.0000         1.0000         2
```

**Note:** Perfect scores are due to very small sample size (13 validation samples). With larger datasets, expect more realistic metrics.

## Feature Columns

The model automatically uses these features (from feature engineering):

**User Features:**
- `user_total_purchases`
- `user_recency_days`
- `user_age_bin` (categorical)

**Item Features:**
- `item_popularity_7d`
- `item_popularity_30d`
- `item_price_mean_30d`
- `item_department_no`
- `item_gender_tag`

**Interaction Features:**
- `recent_interaction_flag_7d`
- `co_purchase_count_with_last3`

**Retrieval Scores:**
- `retrieval_recent_score`
- `retrieval_bought_together_score`
- `retrieval_popular_age_score`

## Safety Features

### Large Dataset Warning

If training data exceeds 500K rows and num_boost_round > 1000:
```
WARNING: Large dataset detected!
Training samples: 750,000
Boosting rounds: 2000
Consider reducing --num_boost_round for faster training
```

### Early Stopping

Automatically stops training if validation metric doesn't improve for N rounds (default: 50), preventing overfitting and saving time.

## Performance Tips

### For Small Datasets (<1K samples)
- Reduce `num_boost_round` to 100-500
- Reduce `num_leaves` to 31-64
- Increase `min_child_samples` to 10-20

### For Medium Datasets (1K-100K samples)
- Use default parameters
- Monitor validation AUC for overfitting
- Consider cross-validation

### For Large Datasets (>100K samples)
- Increase `num_boost_round` to 3000-5000
- Use `subsample` and `colsample_bytree` for regularization
- Consider distributed training for very large datasets

## Hyperparameter Tuning

Key parameters to tune:

1. **`learning_rate`** (0.01-0.1)
   - Lower = slower but potentially better
   - Higher = faster but may overfit

2. **`num_leaves`** (31-255)
   - Controls model complexity
   - Higher = more complex model

3. **`max_depth`** (3-12)
   - Limits tree depth
   - Prevents overfitting

4. **`min_child_samples`** (5-100)
   - Minimum samples per leaf
   - Higher = more regularization

5. **`subsample`** (0.5-1.0)
   - Fraction of samples per tree
   - Lower = more regularization

6. **`colsample_bytree`** (0.5-1.0)
   - Fraction of features per tree
   - Lower = more regularization

7. **`reg_alpha`** and **`reg_lambda`** (0.0-10.0)
   - L1 and L2 regularization
   - Higher = more regularization

## CLI Arguments Reference

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--train_csv` | str | "datasets/train/train_pairs.csv" | Training data path |
| `--val_csv` | str | "datasets/train/val_pairs.csv" | Validation data path |
| `--model_out` | str | "models/lgbm_v1.pkl" | Model output path |
| `--num_boost_round` | int | 2000 | Max boosting rounds |
| `--early_stopping_rounds` | int | 50 | Early stopping rounds |
| `--seed` | int | 42 | Random seed |
| `--task` | str | "train" | Task: "train" or "evaluate" |
| `--output_dir` | str | "outputs" | Output directory |

## Next Steps

After training the model:

1. **Analyze Results**
   - Review feature importance
   - Check for overfitting (train vs val AUC)
   - Analyze MAP@K metrics

2. **Hyperparameter Tuning**
   - Use grid search or Bayesian optimization
   - Focus on learning_rate, num_leaves, max_depth
   - Monitor validation metrics

3. **Feature Engineering V2**
   - Add features based on importance analysis
   - Remove low-importance features
   - Create interaction features

4. **Production Deployment**
   - Load model with `load_model()`
   - Generate predictions for new candidates
   - Rank items by predicted probability
   - Return top-K recommendations

5. **A/B Testing**
   - Deploy model to production
   - Compare against baseline
   - Measure business metrics (CTR, conversion, revenue)
