# Filter Panel Usage Guide

## Quick Start

### 1. Restart Backend (Required!)
```bash
# Stop current backend (Ctrl+C)
python main.py
```

### 2. Open Frontend
```bash
cd frontend
npm run dev
```

### 3. Navigate to Home Page
Open: http://localhost:5173

## Filter Panel Location

The filter panel appears at the top of the Home page, above the product grid:

```
┌─────────────────────────────────────────────────────────┐
│  🔍 Filters                              [Reset All]    │
├─────────────────────────────────────────────────────────┤
│  Min Price    Max Price    Department       Sort By     │
│  [$____]      [$____]      [Dropdown ▼]    [Dropdown ▼]│
│                                                          │
│  Quick Filters:                                         │
│  [Under $25] [$25-$50] [$50-$100] [Over $100]          │
└─────────────────────────────────────────────────────────┘
```

## How to Use Each Filter

### Price Range Filter

**Min Price:**
- Type minimum price (e.g., 25)
- Products below this price are hidden
- Leave empty for no minimum

**Max Price:**
- Type maximum price (e.g., 50)
- Products above this price are hidden
- Leave empty for no maximum

**Quick Filters:**
- Click "Under $25" → Sets max_price=25
- Click "$25-$50" → Sets min=25, max=50
- Click "$50-$100" → Sets min=50, max=100
- Click "Over $100" → Sets min=100

### Department Filter

Select from dropdown:
- **All Departments** (default - shows all)
- **Jersey Basic (1676)** - Basic jersey items
- **Shoes (1339)** - Footwear
- **Accessories (1408)** - Accessories
- **Denim (1346)** - Denim products
- **Outdoor (1372)** - Outdoor wear
- **Bags (1494)** - Bags and purses
- **Sportswear (3608)** - Athletic wear
- **Basics (1234)** - Basic items
- **Essentials (1235)** - Essential items
- **Premium (6515)** - Premium products
- **Casual (1334)** - Casual wear
- **Formal (5883)** - Formal wear
- **Seasonal (2032)** - Seasonal items
- **Collection A (4342)** - Special collection
- **Collection B (4343)** - Special collection

### Sort Filter

Select from dropdown:
- **Default Order** - By article ID
- **💰 Price: Low to High** - Cheapest first
- **💎 Price: High to Low** - Most expensive first
- **⭐ Popular Items** - Random/popular order

## Example Use Cases

### Use Case 1: Budget Shopping
**Goal**: Find affordable items under $30

1. Click "Under $25" quick filter
2. Or manually set Max Price: 30
3. Products update automatically
4. URL becomes: `?max_price=30`

### Use Case 2: Department Shopping
**Goal**: Browse only shoes

1. Select "Shoes (1339)" from Department dropdown
2. Products filtered to shoes only
3. URL becomes: `?department=1339`

### Use Case 3: Price Range in Department
**Goal**: Find shoes between $40-$80

1. Set Min Price: 40
2. Set Max Price: 80
3. Select "Shoes (1339)" from Department
4. Select "Price: Low to High" for sorting
5. URL becomes: `?min_price=40&max_price=80&department=1339&sort=price_asc`

### Use Case 4: Find Expensive Items
**Goal**: Browse premium products

1. Click "Over $100" quick filter
2. Select "Price: High to Low" for sorting
3. See most expensive items first
4. URL becomes: `?min_price=100&sort=price_desc`

### Use Case 5: Share Filtered View
**Goal**: Share specific product selection with friend

1. Apply desired filters
2. Copy URL from browser: `http://localhost:5173/?min_price=25&max_price=50&department=1339&sort=price_asc`
3. Send to friend
4. Friend opens URL and sees same filtered view

## Filter Behavior

### Debouncing (300ms)
- Filters wait 300ms after you stop typing
- Prevents excessive API calls
- Smooth typing experience
- Example: Type "50" → waits 300ms → fetches products

### URL Synchronization
- All filters appear in URL
- Browser back/forward works
- Bookmarkable filtered views
- Shareable links

### Pagination Reset
- Changing filters resets to page 1
- Prevents showing empty pages
- Smooth user experience

### Active Filter Indicator
- "Active" badge appears when filters applied
- "Reset All" button shows when filters active
- Visual feedback for current state

## Pagination with Filters

When filters are applied:
1. Total count updates (e.g., "5,234 items")
2. Pagination shows filtered total pages
3. Page numbers work with filters
4. URL includes page: `?min_price=25&page=2`

**Navigation:**
```
[Previous] [1] [2] [3] ... [52] [Next]
           ^^^
        Current page
```

## Resetting Filters

### Reset All Button
- Click "Reset All" in top-right of filter panel
- Clears all filters instantly
- Returns to default view (all products)
- URL becomes: `/` (no query params)

### Individual Reset
- Clear price inputs manually
- Select "All Departments"
- Select "Default Order"

## Keyboard Shortcuts

- **Tab** - Navigate between filter inputs
- **Enter** - Apply filter (in input fields)
- **Escape** - Clear current input (browser default)

## Mobile Experience

On mobile devices:
- Filter panel stacks vertically
- Touch-friendly inputs
- Responsive dropdowns
- Quick filters wrap to multiple rows

## Performance Tips

1. **Use Quick Filters** - Faster than typing
2. **Combine Filters** - Narrow results efficiently
3. **Bookmark Common Filters** - Save frequently used combinations
4. **Share URLs** - Send filtered views to others

## Troubleshooting

### Filters Not Working
**Symptom**: Products don't change when filters applied

**Solution**:
```bash
# Restart backend
python main.py
```

### No Products Found
**Symptom**: "No products found" message

**Possible Causes**:
1. Filters too restrictive (e.g., min=100, max=50)
2. Department has no products in price range
3. Database has no matching products

**Solution**:
- Click "Reset All" to clear filters
- Try broader price range
- Try different department

### URL Not Updating
**Symptom**: URL doesn't show query parameters

**Solution**:
- Check browser console for errors
- Ensure React Router is working
- Hard refresh page (Ctrl+Shift+R)

### Slow Response
**Symptom**: Products take long to load

**Possible Causes**:
1. Large result set
2. Complex filters
3. Database not indexed

**Solution**:
- Add more specific filters
- Use pagination
- Check backend logs

## API Details

### Request Format
```
GET /products/?min_price=25&max_price=50&department=1339&sort=price_asc&page=1&limit=60
```

### Response Format
```json
{
  "products": [
    {
      "article_id": "0123456789",
      "name": "Product Name",
      "price": 29.99,
      "department_no": 1339,
      "product_group_name": "Shoes",
      "image_path": "/images/012/0123456789.jpg"
    }
  ],
  "total": 234,
  "page": 1,
  "limit": 60,
  "total_pages": 4
}
```

## Testing

### Manual Test Checklist
- [ ] Set min price → verify all products >= min
- [ ] Set max price → verify all products <= max
- [ ] Set price range → verify all products in range
- [ ] Select department → verify all products from dept
- [ ] Sort by price asc → verify ascending order
- [ ] Sort by price desc → verify descending order
- [ ] Combine filters → verify all conditions met
- [ ] Change page → verify different products
- [ ] Copy URL → paste in new tab → verify filters preserved
- [ ] Click Reset All → verify all filters cleared

### Automated Tests
```bash
python test_filters.py
```

Expected: All 10 tests pass ✅

## Advanced Tips

### Bookmarklet for Common Filters
Create browser bookmarks for frequent searches:
- Budget Items: `http://localhost:5173/?max_price=25&sort=price_asc`
- Premium Shoes: `http://localhost:5173/?department=1339&min_price=100&sort=price_desc`
- Mid-Range Bags: `http://localhost:5173/?department=1494&min_price=30&max_price=80`

### Filter Combinations
Experiment with combinations:
- **Bargain Hunt**: max_price=20, sort=price_asc
- **Premium Browse**: min_price=150, sort=price_desc
- **Department Sale**: department=1339, max_price=40
- **New Arrivals**: sort=popular (random order)

### URL Hacking
Manually edit URL for quick filter changes:
```
# Change department
?department=1339  →  ?department=1676

# Adjust price range
?min_price=25&max_price=50  →  ?min_price=30&max_price=60

# Change sort
?sort=price_asc  →  ?sort=price_desc
```

## Summary

The filter panel provides:
- ✅ Fast product discovery
- ✅ Precise filtering
- ✅ Shareable results
- ✅ Smooth experience
- ✅ Mobile-friendly

**Start filtering now at**: http://localhost:5173

---

**Need Help?** See `FILTER_FEATURE_COMPLETE.md` for technical details.
