# One-Time Color Editor Guide

## Overview
The One-Time Color Editor allows you to manually edit product colors **ONLY ONCE** per product. After editing, the product is permanently locked and cannot be changed again.

## ⚠️ Important Warning
- **Each product can only be edited ONCE**
- **After saving changes, the product is PERMANENTLY LOCKED**
- **No further edits will ever be possible**
- **This is irreversible**

## Usage

### 1. Check Statistics
See how many products are editable vs locked:
```bash
python src/one_time_color_editor.py --stats
```

### 2. List Editable Products
Show products that can still be edited:
```bash
python src/one_time_color_editor.py --list-editable --limit 20
```

### 3. List Locked Products
Show products that have been permanently locked:
```bash
python src/one_time_color_editor.py --list-locked --limit 20
```

### 4. Search for Products to Edit
Find specific products by name:
```bash
python src/one_time_color_editor.py --search "red dress" --limit 10
```

### 5. Edit a Specific Product (ONE TIME ONLY)
Edit a product by its article ID:
```bash
python src/one_time_color_editor.py --article_id 0108775015
```

## Editing Process

When you edit a product, the system will:

1. **Show Warning**: Display the one-time edit warning
2. **Show Current Info**: Display current color information
3. **Ask Confirmation**: Confirm you want to proceed
4. **Collect New Data**: Ask for new color information
5. **Final Confirmation**: Require typing 'LOCK' to confirm
6. **Save & Lock**: Save changes and permanently lock the product

## Example Edit Session

```
⚠️  ONE-TIME EDIT WARNING
================================================================================
This is a ONE-TIME EDIT opportunity!
After saving changes, this product's colors will be PERMANENTLY LOCKED.
No further edits will be possible.
================================================================================

Product: 0108775015
Name: Strap top
Group: Garment Upper body

Current Color Information:
  Colors: white,black,gray
  Primary Color: white
  Color Description: Primarily white with black and gray accents

Do you want to proceed with editing? This is your ONLY chance! (y/N): y

Enter new color information:
(Press Enter to keep current value)

Colors (comma-separated) [white,black,gray]: red,pink
Primary Color [white]: red
Color Description [Primarily white with black and gray accents]: Vibrant red with soft pink accents

🔒 FINAL CONFIRMATION - PERMANENT LOCK
================================================================================
PROPOSED CHANGES:
Colors: white,black,gray → red,pink
Primary Color: white → red
Color Description: Primarily white with black and gray accents → Vibrant red with soft pink accents

⚠️  WARNING: After saving, this product will be PERMANENTLY LOCKED!
No further color edits will ever be possible.
================================================================================

SAVE AND PERMANENTLY LOCK this product? (type 'LOCK' to confirm): LOCK

🔒 PRODUCT PERMANENTLY LOCKED
================================================================================
✅ Changes saved successfully!
🔒 Product is now permanently locked from further edits.

Final Color Information:
  Colors: red,pink
  Primary Color: red
  Color Description: Vibrant red with soft pink accents
  Status: LOCKED ✅
================================================================================
```

## Attempting to Edit a Locked Product

If you try to edit a product that's already been locked:

```
🔒 PRODUCT LOCKED
================================================================================
Product 0108775015 has already been manually edited.
Color information is permanently locked and cannot be changed.

Current Color Information:
  Colors: red,pink
  Primary Color: red
  Color Description: Vibrant red with soft pink accents
================================================================================
```

## Database Schema

The system adds a `color_manually_edited` field to track locked products:

```sql
ALTER TABLE products ADD COLUMN color_manually_edited BOOLEAN DEFAULT FALSE;
```

- `FALSE` = Product can be edited (one time remaining)
- `TRUE` = Product is permanently locked (already edited)

## Security Features

1. **Double Confirmation**: Requires two confirmations before locking
2. **Clear Warnings**: Multiple warnings about permanent nature
3. **Type-to-Confirm**: Must type 'LOCK' to finalize changes
4. **Status Tracking**: Clear indication of locked vs editable products
5. **Irreversible**: No way to unlock once locked (by design)

## Use Cases

- **Correct Wrong Colors**: Fix automatically generated colors that are incorrect
- **Add Specific Details**: Add more detailed color descriptions
- **Brand Compliance**: Ensure colors match brand standards
- **Quality Control**: One-time manual review and correction

## Best Practices

1. **Review Carefully**: Double-check all information before confirming
2. **Use Sparingly**: Only edit when absolutely necessary
3. **Document Changes**: Keep track of what you've edited and why
4. **Test First**: Use the search and list functions to find the right products

---

**Remember: This is a ONE-TIME opportunity per product. Use it wisely!**