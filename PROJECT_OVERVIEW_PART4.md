# 📚 Complete Project Overview - Part 4: ML Model & Advanced Features

## 🎓 PHASE 4: LightGBM Model Training

### Step 4.1: Model Training

**Library Used: LightGBM (Gradient Boosting Framework)**

```python
# src/model_train.py

Model Configuration:
- Algorithm: Gradient Boosting Decision Trees (GBDT)
- Objective: Binary classification
- Metric: AUC (Area Under ROC Curve)
- Features: 50+ engineered features
- Training samples: 100k+ pairs
- Validation samples: 25k+ pairs

Hyperparameters:
- learning_rate: 0.03
- num_leaves: 128
- max_depth: 8
- min_child_samples: 20
- subsample: 0.8
- colsample_bytree: 0.7
- num_boost_round: 2000
- early_stopping_rounds: 50

Training Process:
1. Load training data (train_pairs.csv)
2. Prepare features (handle categorical, missing values)
3. Create LightGBM datasets
4. Train with early stopping
5. Evaluate on validation set
6. Save model (lgbm_v1.pkl)
```

**Evaluation Metrics:**
- AUC Score: ~0.85-0.90
- MAP@K (Mean Average Precision)
- Recall@K
- Feature importance analysis

**Visualizations Generated:**
- ROC curve
- Feature importance plot
- Training/validation curves

---

### Step 4.2: Model Serving (Production API)

**Libraries Used: FastAPI, Joblib, LightGBM**

```python
# src/api_recommend.py

ML Pipeline:
1. Load Model
   - Load lgbm_v1.pkl on startup
   - Cache in memory
   - Reload endpoint available
   
2. Generate Recommendations
   Step 1: Candidate Generation (retrieval.py)
   Step 2: Feature Engineering (features.py)
   Step 3: Model Prediction (LightGBM)
   Step 4: Ranking by score
   Step 5: Return top-K products
   
3. Endpoints
   - GET /recommend/me (authenticated)
   - GET /recommend/user/{user_id} (admin)
   - GET /recommend/health (status check)
   - POST /recommend/reload (reload model)
```

**Performance:**
- Prediction time: ~50-100ms for 500 candidates
- Throughput: ~10-20 requests/second
- Fallback: Uses retrieval scores if model unavailable

---

## 🎨 PHASE 5: Advanced Features

### Step 5.1: Color Detection & Management

**Libraries Used: Pillow (PIL), NumPy, Google Gemini AI**

```python
# src/color_detection.py
# src/color_generator.py
# src/api_color_editor.py

Features Built:
1. Automatic Color Detection
   - Extract dominant colors from product images
   - RGB to color name mapping
   - Primary color identification
   
2. AI-Powered Color Descriptions
   - Google Gemini AI generates descriptions
   - Natural language color descriptions
   - Context-aware descriptions
   
3. Color Editor (Admin Tool)
   - Manual color correction
   - Bulk color updates
   - Color lock (prevent auto-updates)
   
4. Color Search
   - Search products by color
   - Color-based filtering
   - Color similarity matching
```

**Database Fields Added:**
- `colors` - Comma-separated color list
- `primary_color` - Main color
- `color_description` - AI-generated description
- `color_manually_edited` - Lock flag

---

### Step 5.2: AI-Powered Search

**Library Used: Google Generative AI 0.3.2 (Gemini)**

```python
# src/api_search.py

Features Built:
1. Semantic Search
   - Natural language queries
   - "Show me red dresses under $50"
   - "Casual shoes for summer"
   
2. Query Understanding
   - Extract: colors, categories, price range
   - Intent detection
   - Synonym handling
   
3. Fallback Search
   - Traditional text search if AI fails
   - Fuzzy matching
   - Partial matches
   
4. Search Suggestions
   - Auto-complete
   - Popular searches
   - Typo correction
```

**Gemini AI Integration:**
- API key management
- Rate limiting
- Error handling
- Response parsing

---

### Step 5.3: Product Description Generation

**Library Used: Google Gemini AI**

```python
# src/update_product_descriptions.py

Features:
1. Auto-generate product descriptions
   - Based on product name and category
   - SEO-friendly
   - Natural language
   
2. Batch Processing
   - Process 1000s of products
   - Rate limiting
   - Progress tracking
   
3. Database Updates
   - Add description field
   - Migration scripts
   - Bulk updates
```

---

