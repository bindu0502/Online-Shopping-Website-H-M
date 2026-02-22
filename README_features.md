# Feature Engineering Module

## Overview

The `src/features.py` module builds comprehensive features for (user_id, article_id) candidate pairs to train the recommendation ranking model.

## Feature Set

### User Features
- `user_total_purchases` (int) - Total number of purchases by user
- `user_recency_days` (int) - Days since user's last purchase
- `user_age_bin` (category) - Age group category (e.g., '18-25', '26-35')

### Item Features
- `item_popularity_7d` (int) - Number of purchases in last 7 days
- `item_popularity_30d` (int) - Number of purchases in last 30 days
- `item_price_mean_30d` (float) - Average price in last 30 days
- `item_department_no` (int) - Department number from article metadata
- `item_gender_tag` (int) - Gender tag (0=unisex, 1=women, 2=men)

### User-Item Interaction Features
- `recent_interaction_flag_7d` (0/1) - Whether user purchased this item in last 7 days
- `co_purchase_count_with_last3` (int) - Co-purchase count with user's last 3 items

### Retrieval Rule Scores
- `retrieval_recent_score` (float) - Combined recent purchase scores
- `retrieval_bought_together_score` (float) - Bought-together score
- `retrieval_popular_age_score` (float) - Age-based popularity score

### Original Candidate Data
- `user_id` - Customer ID
- `article_id` - Article ID
- `score` - Combined candidate score from retrieval
- `reason` - Primary retrieval rule
- `rule_scores_json` - JSON string with detailed rule scores

## Functions

### Core Functions

**`load_processed_data(data_dir)`**
- Loads transactions, customers, and articles DataFrames
- Returns tuple of (transactions_df, customers_df, articles_df)

**`load_candidates_for_user(user_id, candidates_dir)`**
- Loads candidate recommendations for a specific user
- Returns DataFrame with candidates

**`build_features_for_candidates(user_id, candidates_df, transactions_df, customers_df, articles_df)`**
- Main feature engineering function
- Combines user, item, and interaction features
- Preserves original candidate scores and metadata
- Returns DataFrame with all features

**`quantile_normalize_features(df, cols_to_normalize, n_quantiles)`**
- Applies quantile normalization using QuantileTransformer
- Handles small sample sizes automatically
- Returns DataFrame with normalized features

**`pipeline_build_features_for_users(user_list, candidates_dir, data_dir, out_path, overwrite)`**
- Batch processing for multiple users
- Combines features into single CSV
- Supports caching and incremental builds

### Helper Functions

**`compute_user_features(user_id, transactions_df, customers_df, max_date)`**
- Computes user-level features
- Returns dictionary with user features

**`compute_item_features(article_ids, transactions_df, articles_df, max_date, cache_dir)`**
- Computes item-level features with caching
- Returns DataFrame indexed by article_id

**`compute_interaction_features(user_id, article_ids, transactions_df, max_date)`**
- Computes user-item interaction features
- Returns DataFrame with interaction features

**`parse_retrieval_scores(rule_scores_json)`**
- Parses JSON retrieval scores
- Returns dictionary with individual rule scores

**`build_and_show_sample(user_id, data_dir, candidates_dir)`**
- Testing helper for quick verification
- Displays top 10 feature rows

## Usage

### Test with Random User
```bash
python src/features.py --data_dir datasets --test
```

### Build Features for Specific User
```bash
python src/features.py --data_dir datasets --user_id 12345
```

### Build Features for Sample Users
```bash
python src/features.py --data_dir datasets --sample_users 10
```

### Build Features for All Users
```bash
python src/features.py --data_dir datasets --overwrite
```

### Custom Output Path
```bash
python src/features.py --data_dir datasets --out_path custom/path/features.csv
```

## Caching

The module caches intermediate computations for performance:

**Cache Location:** `datasets/cache/`

**Cached Files:**
- `item_features_7d.csv` - 7-day item popularity
- `item_features_30d.csv` - 30-day item popularity and prices
- `popular_age_{age_bin}_7d.csv` - Age-based popularity (from retrieval)

Caching significantly speeds up repeated feature generation.

## Output Format

Features saved to `datasets/features/features_all.csv` with 18 columns:

```csv
user_id,article_id,score,reason,rule_scores_json,user_total_purchases,user_recency_days,user_age_bin,item_popularity_7d,item_popularity_30d,item_price_mean_30d,item_department_no,item_gender_tag,recent_interaction_flag_7d,co_purchase_count_with_last3,retrieval_recent_score,retrieval_bought_together_score,retrieval_popular_age_score
```

## Performance

- **Efficient merges:** Vectorized pandas operations
- **Caching:** Reuses computed aggregates
- **Memory-efficient:** Processes users sequentially
- **Typical speed:** ~1-2 seconds per user

## Example Results

From test run with 10 users:
- **Total feature rows:** 2,778
- **Total feature columns:** 18
- **Processing time:** ~90 seconds
- **Output size:** ~790 KB

## Next Steps

After feature engineering:

1. **Model Training** (`model_train.py`)
   - Train LightGBM ranking model
   - Use features as input
   - Optimize for MAP@12 metric
   - Implement temporal cross-validation

2. **Feature Selection**
   - Analyze feature importance
   - Remove low-importance features
   - Test feature combinations

3. **Feature Engineering V2**
   - Add more sophisticated features:
     - User purchase patterns (day of week, time of day)
     - Item category affinity scores
     - Seasonal features
     - Price sensitivity features
     - Diversity features

4. **Evaluation**
   - Validate on holdout set
   - Compute MAP@12, Recall@12
   - Analyze prediction errors
   - A/B test different feature sets
