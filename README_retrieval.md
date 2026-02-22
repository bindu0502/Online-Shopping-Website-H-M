# Retrieval Module - Candidate Generation

## Overview

The `src/retrieval.py` module implements the **Simple Retrieval Strategy** from the paper (page 7, Fig.6) for generating candidate recommendations.

## Features

### 1. Time Decay Scoring
Implements the paper's time decay formula (page 7):
```
r = a / sqrt(x) + b * exp(-c*x) - d
```
where `x` is days since purchase.

### 2. Retrieval Strategies

**Recent Items:**
- Fetches items purchased by user in last N days (3 and 7 day windows)
- Applies time decay scoring for recency
- Higher scores for more recent purchases

**Popular by Age:**
- Finds top-K popular items within user's age group
- Uses 7-day rolling window for popularity calculation
- Normalized popularity scores
- Cached for performance

**Bought Together:**
- Market basket analysis for co-purchased items
- Finds items frequently bought with user's recent purchases
- Based on customer co-occurrence patterns

### 3. Combined Scoring

- Normalizes each rule's scores using QuantileTransformer
- Weighted combination:
  - Recent purchases: 40%
  - Bought together: 30%
  - Popular by age: 30%
- Saves rule-level scores as JSON for inspection

### 4. Caching

- Caches popular-by-age results in `datasets/cache/`
- Reduces computation time for repeated queries
- Cache files: `popular_age_{age_bin}_{window}d.csv`

## Usage

### Test with Random User
```bash
python src/retrieval.py --data_dir datasets/processed --test
```

### Generate for Specific User
```bash
python src/retrieval.py --data_dir datasets/processed --user_id 12345 --top_n 500
```

### Generate for Multiple Users
```bash
python src/retrieval.py --data_dir datasets/processed --sample_users 100
```

### Disable Caching
```bash
python src/retrieval.py --data_dir datasets/processed --sample_users 10 --no_cache
```

## Output Format

Candidate files saved to `datasets/candidates/{user_id}.csv` with columns:

- `user_id`: Customer ID
- `article_id`: Recommended article ID
- `score`: Combined recommendation score (0-1)
- `reason`: Primary retrieval rule (highest scoring)
- `rule_scores_json`: JSON string with individual rule scores

Example:
```csv
user_id,article_id,score,reason,rule_scores_json
abc123,569526002,0.75,recent_long,"{""bought_together"": 1.0, ""popular_age"": 0.0, ""recent_long"": 1.318, ""recent_short"": 1.318}"
```

## Functions

### Core Functions

- `time_decay_score(x, a, b, c, d)` - Time decay formula from paper
- `recent_items(user_id, transactions_df, days)` - Recent purchase candidates
- `popular_by_age(age_bin, transactions_df, customers_df, k, window_days)` - Age-based popularity
- `bought_together(item_id, transactions_df, top_k)` - Co-purchase candidates
- `get_candidates_for_user(...)` - Main candidate generation function
- `save_candidates(user_id, candidates_df, out_dir)` - Save to CSV

### Helper Functions

- `load_processed_data(data_dir)` - Load preprocessed datasets
- `build_sample_candidates_for_random_user(data_dir, top_n)` - Quick testing

## Performance

- Memory-efficient: processes sampled data only
- Caching reduces repeated computations
- Vectorized pandas operations for speed
- Typical performance: ~0.5-1 second per user

## Next Steps

After candidate generation:

1. **Feature Engineering** (`features.py`)
   - Extract user features (purchase history, demographics)
   - Extract item features (product attributes, popularity)
   - Create user-item interaction features

2. **Model Training** (`model_train.py`)
   - Train LightGBM ranking model
   - Optimize for MAP@12 metric
   - Cross-validation with temporal splits

3. **Evaluation**
   - Implement MAP@12 evaluation
   - Analyze feature importance
   - Test different retrieval strategies
