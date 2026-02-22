# Product Images Setup Guide

## Overview

Enable product images in your e-commerce frontend by serving them from the H&M dataset.

## Step 1: Update Image Paths in Database

Run the script to update all product records with image paths:

```bash
python src/update_image_paths.py
```

### What it does:
- ✅ Scans all products in the database
- ✅ Checks if image exists in `Project149/datasets/images_128_128/`
- ✅ Updates `image_path` field with URL path
- ✅ Sets to `null` if image doesn't exist
- ✅ Shows progress every 10,000 products

### Expected Output:
```
Updating product image paths...
Found 105542 products to update
Progress: 10000/105542 products processed (Updated: 9876, Missing: 124)
Progress: 20000/105542 products processed (Updated: 19654, Missing: 346)
...
============================================================
Image paths updated!
Updated: 104321 products with images
Missing: 1221 products without images
============================================================
```

## Step 2: Restart Backend

The backend now serves images via `/images` endpoint:

```bash
python main.py
```

### Image URL Format:
```
http://localhost:8000/images/010/0108775015.jpg
```

Where:
- `010` = First 3 digits of article_id (folder)
- `0108775015.jpg` = Full article_id (filename)

## Step 3: Restart Frontend

```bash
cd frontend
npm run dev
```

## Changes Made

### Backend (`main.py`)
- ✅ Added static file mounting for images
- ✅ Serves images from `Project149/datasets/images_128_128/`
- ✅ Accessible via `/images` endpoint

### Frontend Components Updated
- ✅ `ProductCard.jsx` - Shows product images in grid
- ✅ `Product.jsx` - Shows large image on details page
- ✅ `Cart.jsx` - Shows thumbnails in cart
- ✅ All use `product.image_path` field
- ✅ Fallback to "No Image" if missing
- ✅ Error handling for broken images

### Field Name Changes
Updated to match database schema:
- `prod_name` → `name`
- `product_type_name` → `product_group_name`
- `image_url` → `image_path`

## Image Path Structure

### Database Field:
```
image_path: "/images/010/0108775015.jpg"
```

### Frontend Usage:
```javascript
<img src={`http://localhost:8000${product.image_path}`} />
```

### Full URL:
```
http://localhost:8000/images/010/0108775015.jpg
```

## Troubleshooting

**Images still not showing?**
1. Run the update script: `python src/update_image_paths.py`
2. Restart backend: `python main.py`
3. Hard refresh browser: Ctrl+Shift+R
4. Check browser console for errors

**Some images missing?**
- Normal! ~1-2% of products don't have images
- Shows "No Image" placeholder instead

**Images load slowly?**
- First load caches images
- Subsequent loads are faster
- Consider image optimization for production

**404 errors for images?**
- Verify images exist: `Project149/datasets/images_128_128/`
- Check article_id format (10 digits, zero-padded)
- Ensure backend is serving static files

## Image Statistics

From H&M dataset:
- Total products: ~105,542
- Products with images: ~104,321 (98.8%)
- Products without images: ~1,221 (1.2%)
- Image size: 128x128 pixels
- Format: JPEG

## Next Steps

After setup:
1. ✅ Browse products - see images in grid
2. ✅ Click product - see large image
3. ✅ Add to cart - see thumbnail
4. ✅ Checkout - images in order summary

---

**Ready to enable images?** Run:
```bash
python src/update_image_paths.py
```

Then restart both backend and frontend!
