# 📚 Complete Project Overview - Part 3: ML & Recommendation Systems

## 🤖 PHASE 3: Machine Learning Pipeline

### Step 3.1: Data Preprocessing

**Libraries Used: Pandas 2.1.3, NumPy 1.26.2**

```python
# src/preprocess_short.py
# src/data_loader.py

What We Built:
1. Data Loading
   - Load 105k+ products from CSV
   - Load customer data
   - Load transaction history
   
2. Data Cleaning
   - Handle missing values
   - Remove duplicates
   - Type conversions
   
3. Feature Engineering
   - Age binning (18-25, 26-35, etc.)
   - Date parsing
   - Category encoding
   
4. Data Export
   - Save processed data to CSV
   - Optimized for ML pipeline
```

**Key Operations:**
- Memory optimization
- Data validation
- Statistical analysis
- Data quality checks

---

### Step 3.2: Candidate Generation (Retrieval)

**Libraries Used: Pandas, NumPy, scikit-learn**

```python
# src/retrieval.py

Retrieval Strategies:
1. Recent Purchases
   - Time decay scoring: r = a/√x + b*e^(-cx) - d
   - Short window (3 days)
   - Long window (7 days)
   
2. Popular by Age Group
   - Age-based popularity
   - Cold-start solution
   - Normalized scoring
   
3. Bought Together (Market Basket)
   - Co-purchase patterns
   - Complementary products
   - Association rules
   
4. Combined Scoring
   - Weighted combination
   - QuantileTransformer normalization
   - Top-N selection (500 candidates)
```

**Purpose:**
- Reduce search space from 105k to 500 products
- Fast candidate generation
- Multiple retrieval strategies
- Diversity in recommendations

---

### Step 3.3: Feature Engineering

**Libraries Used: Pandas, NumPy, scikit-learn**

```python
# src/features.py

50+ Features Built:
1. User Features
   - Age, age_bin
   - Purchase history count
   - Average purchase value
   - Days since last purchase
   
2. Item Features
   - Price, category
   - Popularity score
   - Purchase frequency
   - Average rating
   
3. User-Item Interaction Features
   - Has user viewed this item?
   - Has user added to cart?
   - Days since last interaction
   - Interaction count
   
4. Temporal Features
   - Day of week
   - Month
   - Season
   - Time since product launch
   
5. Categorical Features
   - Product category
   - Department
   - Age group
```

**Key Techniques:**
- One-hot encoding
- Label encoding
- Normalization
- Missing value imputation

---

### Step 3.4: Training Data Creation

**Libraries Used: Pandas, NumPy**

```python
# src/create_training_data.py

Process:
1. Positive Samples
   - Actual purchases (label = 1)
   - User-item pairs from transactions
   
2. Negative Sampling
   - Random products user didn't buy (label = 0)
   - Ratio: 1:4 (1 positive : 4 negatives)
   
3. Temporal Split
   - Train: Older data (80%)
   - Validation: Recent data (20%)
   - Prevents data leakage
   
4. Feature Joining
   - Merge user features
   - Merge item features
   - Merge interaction features
   
5. Export
   - train_pairs.csv
   - val_pairs.csv
```

**Output:**
- Labeled training data
- Balanced classes
- Ready for ML training

---

