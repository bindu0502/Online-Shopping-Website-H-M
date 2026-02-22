# Training Data Creation Module

## Overview

The `src/create_training_data.py` module creates labeled training and validation datasets from candidate recommendations and features. It implements temporal labeling and negative sampling for training the recommendation ranking model.

## Labeling Strategy

### Temporal Windows

The module uses temporal windows to create realistic training scenarios:

**Default Windows:**
- `train_window_start`: last_date - 35 days (4 weeks before train_window_end)
- `train_window_end`: last_date - 7 days
- `target_start`: last_date - 6 days
- `target_end`: last_date (most recent date in transactions)

**Labeling Logic:**
- A (user, article) pair is labeled **1** if the user purchased the article in [target_start, target_end]
- Otherwise labeled **0**

This creates a realistic "predict future purchases" scenario where the model learns from past behavior to predict near-future purchases.

### Custom Windows

You can override default windows with CLI arguments:
```bash
python src/create_training_data.py --data_dir datasets \
  --train_window_start 2018-08-01 \
  --train_window_end 2018-09-15 \
  --target_start 2018-09-16 \
  --target_end 2018-09-24
```

## Negative Sampling

### Strategy

The module implements **user-stratified negative sampling** to handle class imbalance:

1. **Keep all positive samples** (actual purchases)
2. **Downsample negatives** to achieve target negative/positive ratio
3. **User-stratified sampling** maintains representation across users
4. **Proportional allocation** - users with more negatives get more samples

### Parameters

- `neg_pos_ratio` (default: 4.0) - Target ratio of negatives to positives
- Higher ratio = more negatives = harder learning task
- Lower ratio = fewer negatives = faster training but potential overfitting

## Functions

### Core Functions

**`calculate_default_windows(transactions_df)`**
- Calculates default time windows based on transaction dates
- Returns dictionary with window timestamps

**`label_candidate_rows(candidates_df, transactions_df, target_start, target_end)`**
- Labels candidate pairs based on future purchases
- Returns DataFrame with added 'label' column (0 or 1)

**`sample_negatives(df, neg_pos_ratio, random_state)`**
- Downsamples negative examples with user stratification
- Maintains all positive examples
- Returns balanced DataFrame

**`create_train_val_splits(labeled_df, val_fraction, random_state)`**
- Splits data into training and validation sets
- Uses stratified sampling to maintain class balance
- Returns tuple of (train_df, val_df)

**`load_or_generate_features(features_file, candidates_dir, data_dir)`**
- Loads features from file or generates them if missing
- Automatically calls feature engineering pipeline if needed
- Returns features DataFrame

**`merge_features_with_candidates(candidates_df, features_df)`**
- Merges features with candidate pairs
- Handles missing features gracefully
- Returns merged DataFrame

**`save_training_stats(train_df, val_df, windows, out_dir)`**
- Saves training statistics to JSON file
- Includes sample counts, class balance, time windows
- Useful for tracking experiments

## Usage

### Basic Usage (Default Settings)
```bash
python src/create_training_data.py --data_dir datasets
```

### Custom Negative Sampling Ratio
```bash
python src/create_training_data.py --data_dir datasets --neg_pos_ratio 5
```

### Custom Validation Fraction
```bash
python src/create_training_data.py --data_dir datasets --val_fraction 0.15
```

### Custom Time Windows
```bash
python src/create_training_data.py --data_dir datasets \
  --target_start 2018-09-18 \
  --target_end 2018-09-24
```

### Custom Output Directory
```bash
python src/create_training_data.py --data_dir datasets --out_dir custom/train
```

## Output Files

### Training Data Files

**Location:** `datasets/train/`

**Files:**
1. `train_pairs.csv` - Training dataset with features and labels
2. `val_pairs.csv` - Validation dataset with features and labels
3. `sample_rows.csv` - Sample rows for quick inspection (10 rows)
4. `training_stats.json` - Statistics and metadata

### File Format

CSV files contain all features plus label:
```csv
user_id,article_id,score,reason,rule_scores_json,user_total_purchases,user_recency_days,user_age_bin,item_popularity_7d,item_popularity_30d,item_price_mean_30d,item_department_no,item_gender_tag,recent_interaction_flag_7d,co_purchase_count_with_last3,retrieval_recent_score,retrieval_bought_together_score,retrieval_popular_age_score,label
```

### Statistics JSON

Example `training_stats.json`:
```json
{
  "creation_timestamp": "2025-12-02T09:21:47.872752",
  "time_windows": {
    "train_window_start": "2018-08-20",
    "train_window_end": "2018-09-17",
    "target_start": "2018-09-18",
    "target_end": "2018-09-24"
  },
  "train_set": {
    "total_samples": 132,
    "positives": 27,
    "negatives": 105,
    "positive_rate": 0.2045,
    "unique_users": 10,
    "unique_articles": 118
  },
  "val_set": {
    "total_samples": 13,
    "positives": 2,
    "negatives": 11,
    "positive_rate": 0.1538,
    "unique_users": 9,
    "unique_articles": 13
  }
}
```

## Example Results

From test run with 10 users:

**Training Set:**
- Total samples: 132
- Positives: 27 (20.5%)
- Negatives: 105 (79.5%)
- Ratio: 3.89:1
- Unique users: 10
- Unique articles: 118

**Validation Set:**
- Total samples: 13
- Positives: 2 (15.4%)
- Negatives: 11 (84.6%)
- Ratio: 5.50:1
- Unique users: 9
- Unique articles: 13

## Class Balance Considerations

### Why Negative Sampling?

In recommendation systems, the natural class distribution is extremely imbalanced:
- **Positives:** Items user actually purchased (rare)
- **Negatives:** Items user didn't purchase (abundant)

Without sampling, the ratio can be 100:1 or higher, making training difficult.

### Choosing neg_pos_ratio

- **4:1 (default)** - Good balance for most cases
- **2:1** - More aggressive downsampling, faster training
- **8:1** - More negatives, harder task, potentially better generalization
- **1:1** - Balanced classes, may not reflect real-world distribution

### User Stratification

User-stratified sampling ensures:
- All users are represented in training data
- Users with more candidates contribute proportionally
- Prevents bias toward high-activity users

## Next Steps

After creating training data:

1. **Model Training** (`model_train.py`)
   - Train LightGBM ranking model
   - Use train_pairs.csv for training
   - Use val_pairs.csv for validation
   - Optimize for MAP@12 metric

2. **Hyperparameter Tuning**
   - Experiment with different neg_pos_ratio values
   - Try different validation fractions
   - Test different time window configurations

3. **Feature Selection**
   - Analyze feature importance from trained model
   - Remove low-importance features
   - Add new features based on insights

4. **Evaluation**
   - Compute MAP@12, Recall@12 on validation set
   - Analyze prediction errors
   - Test on holdout set with different time period

## CLI Arguments Reference

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--data_dir` | str | "datasets" | Base data directory |
| `--features_file` | str | "{data_dir}/features/features_all.csv" | Path to features file |
| `--candidates_dir` | str | "{data_dir}/candidates" | Candidates directory |
| `--train_window_start` | str | auto | Training window start (ISO date) |
| `--train_window_end` | str | auto | Training window end (ISO date) |
| `--target_start` | str | auto | Target period start (ISO date) |
| `--target_end` | str | auto | Target period end (ISO date) |
| `--neg_pos_ratio` | float | 4.0 | Negative to positive ratio |
| `--val_fraction` | float | 0.1 | Validation set fraction |
| `--out_dir` | str | "{data_dir}/train" | Output directory |
| `--random_seed` | int | 42 | Random seed for reproducibility |
