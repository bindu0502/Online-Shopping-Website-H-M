# Product Import Guide

## Overview

Import the full H&M product catalog into your database and use the updated pagination API.

## Step 1: Import Products

Run the import script to load all products from the H&M dataset:

```bash
python src/import_products.py
```

### What it does:
- ✅ Loads `Project149/datasets/articles.csv/articles.csv`
- ✅ Imports all products into the database
- ✅ Sets default price of $29.99 for all products
- ✅ Skips duplicates safely
- ✅ Shows progress every 10,000 rows
- ✅ Prints final statistics

### Expected Output:
```
Initializing database...
Loading products from Project149/datasets/articles.csv/articles.csv...
Loaded 105542 products from CSV
Starting import...
Progress: 10000/105542 rows processed (Imported: 9998, Skipped: 2, Errors: 0)
Progress: 20000/105542 rows processed (Imported: 19995, Skipped: 5, Errors: 0)
...
============================================================
Import complete!
Imported 105542 products into the database.
Skipped 0 duplicates.
============================================================
```

## Step 2: Updated Products API

The `/products` endpoint now supports pagination with two methods:

### Method 1: Page-based (Recommended)
```
GET /products?page=1&limit=20
```

**Response:**
```json
{
  "products": [...],
  "total": 105542,
  "page": 1,
  "limit": 20,
  "total_pages": 5278
}
```

### Method 2: Skip-based
```
GET /products?skip=0&limit=20
```

### Parameters:
- `page` (default: 1) - Page number (starts at 1)
- `limit` (default: 20, max: 100) - Products per page
- `skip` (optional) - Number of products to skip

### Examples:

**Get first page:**
```
GET /products?page=1&limit=20
```

**Get second page:**
```
GET /products?page=2&limit=20
```

**Get 50 products per page:**
```
GET /products?page=1&limit=50
```

**Skip first 100 products:**
```
GET /products?skip=100&limit=20
```

## Step 3: Update Frontend

Update your frontend to use the new pagination response:

```javascript
// Before
const response = await API.get('/products/?limit=20');
setProducts(response.data.products || []);

// After
const response = await API.get('/products/?page=1&limit=20');
setProducts(response.data.products);
setTotalPages(response.data.total_pages);
setCurrentPage(response.data.page);
```

## Product Fields

Each product has:
- `article_id` - Unique identifier (10 digits, zero-padded)
- `name` - Product name (from prod_name or product_type_name)
- `price` - Price (default: $29.99)
- `department_no` - Department number
- `product_group_name` - Product category/group
- `image_path` - Image path (null for now)

## Database Schema

```python
class Product(Base):
    article_id = Column(String(50), primary_key=True)
    name = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    department_no = Column(Integer, nullable=True)
    product_group_name = Column(String(255), nullable=True)
    image_path = Column(String(500), nullable=True)
```

## Troubleshooting

**Import fails with "File not found":**
- Check that `Project149/datasets/articles.csv/articles.csv` exists
- Verify you're running from the project root directory

**Duplicate key errors:**
- The script automatically skips duplicates
- If you want to re-import, delete the database first: `rm project149.db`

**Import is slow:**
- Normal! ~105k products takes a few minutes
- Progress updates every 10,000 rows
- Uses batch commits for better performance

**Frontend not showing products:**
- Make sure backend is running: `python main.py`
- Check the API response: `http://localhost:8000/products?page=1&limit=20`
- Verify products were imported: Check the import script output

## Next Steps

After importing products:

1. ✅ Restart your backend: `python main.py`
2. ✅ Test the API: Visit `http://localhost:8000/docs`
3. ✅ Update frontend to use pagination
4. ✅ Add product images (optional)
5. ✅ Adjust prices (optional)

---

**Ready to import?** Run:
```bash
python src/import_products.py
```
