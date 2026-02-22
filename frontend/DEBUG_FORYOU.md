# For You Feature - Debugging Guide

## Issue: Stuck on "Loading recommendations"

### Quick Fixes

1. **Open Browser Console** (F12 or Right-click → Inspect → Console)
   - Look for any error messages
   - Check what the API is returning

2. **Clear Browser Storage**
   - Open Console (F12)
   - Go to "Application" tab
   - Click "Local Storage" → "http://localhost:5173"
   - Delete the `auth_token` entry
   - Refresh the page and login again

3. **Check if you're logged in**
   - Open Console (F12)
   - Type: `localStorage.getItem('auth_token')`
   - If it returns `null`, you need to login

4. **Test the API directly**
   ```bash
   # In a new terminal
   python test_foryou_login.py
   ```

### Common Issues

#### Double Navbar
- **Fixed!** Removed duplicate NavBar from ForYou component
- App.jsx already renders NavBar at the top level

#### Stuck on Loading
Possible causes:
1. Backend server not running → Start with `python main.py`
2. Invalid/expired token → Logout and login again
3. No user activity → Add items to cart/wishlist first
4. API error → Check browser console for details

### Testing Steps

1. **Start Backend** (if not running)
   ```bash
   python main.py
   ```

2. **Start Frontend** (if not running)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Login to the app**
   - Go to http://localhost:5173
   - Login with your credentials

4. **Add some activity**
   - Add 2-3 products to cart
   - Add 2-3 products to wishlist

5. **Click "For You"**
   - Should show 6-9 recommendations (3 per activity product)

### Browser Console Commands

Check authentication:
```javascript
console.log('Token:', localStorage.getItem('auth_token'));
```

Test API manually:
```javascript
fetch('http://localhost:8000/foryou', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('auth_token')
  }
})
.then(r => r.json())
.then(data => console.log('For You data:', data))
.catch(err => console.error('Error:', err));
```

### Expected API Response

```json
{
  "user_id": 1,
  "recommendations": [
    {
      "article_id": "0108775015",
      "name": "Product Name",
      "price": 29.99,
      "image_path": "/images/0108775015.jpg",
      "product_group_name": "Garment Upper body",
      "primary_color": "blue",
      "color_description": "Deep navy blue...",
      "colors": "blue,white",
      "score": 6.5,
      "reason": "Similar to Product X..."
    }
  ],
  "count": 6,
  "activity_products_count": 2
}
```

### If Still Not Working

1. Check backend logs for errors
2. Verify user has cart/wishlist items
3. Check database has products
4. Ensure CORS is configured correctly
