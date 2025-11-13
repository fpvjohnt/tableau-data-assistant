# Store Number Extraction & Cleaning

## Overview
Your CSV cleaner now automatically fixes store numbers! It removes decimal points and extracts missing store numbers from the Summary column.

## What It Does

### 1. Removes Decimal Points
**Before:**
```
Store Number
521.0
545.0
642.0
623.0
```

**After:**
```
Store Number
521
545
642
623
```

### 2. Extracts From Summary
If the Store Number column is blank but the summary contains a store number, it extracts it:

**Examples:**

| Summary | Store Number (Before) | Store Number (After) |
|---------|----------------------|---------------------|
| 521 - Break/Fix IP Upgrade | (blank) | 521 |
| Store 545 - Hirsch issues | (blank) | 545 |
| USB PTZ controller KB | (blank) | (blank) |
| 642 - Open Network Ports | (blank) | 642 |
| Store #623 camera issues | (blank) | 623 |

### 3. Smart Pattern Recognition
Recognizes multiple formats:
- `521 - Description` (number at start)
- `Store 521 Description` (with "Store" prefix)
- `Store #521` (with # symbol)
- `#521` (just # and number)
- `Store number 521` (spelled out)

### 4. Blank When Not Found
If there's no store number in the summary, it stays blank so you can easily see which tickets need manual review:

```
Summary: "USB PTZ controller KB"
Store Number: (blank)
```

## How It Works

### Automatic Process

When you upload a CSV file:

1. **Check existing Store Numbers**
   - Removes `.0` from numbers like `521.0` → `521`
   - Removes any decimals

2. **Extract from Summary**
   - Only for rows where Store Number is blank
   - Searches for patterns in Summary text
   - Validates it's a 3-4 digit number

3. **Report Results**
   - Shows how many were fixed
   - Shows how many were extracted
   - Shows how many are still blank

### Example Output

**Cleaning Report:**
```
✓ Fixed store numbers: removed decimals and extracted 15 missing
  store numbers from summary

Store Number Processing Complete:
  Total rows: 32
  With store numbers: 28 (87.5%)
  Without store numbers (blank): 4 (12.5%)
```

## Benefits

### ✅ Clean Data for Tableau
- No decimal points (521 instead of 521.0)
- Consistent formatting
- Text field (not numeric with decimals)

### ✅ Automatic Extraction
- Recovers missing store numbers
- No manual copy/paste needed
- Saves time on data prep

### ✅ Easy Identification
- Blank cells show which tickets need review
- Can filter in Tableau by blank/non-blank
- Quick visual scan to see coverage

## Use Cases

### Ticket Tracking
```
Upload: ticket_export.csv
Result:
  - 28/32 tickets have store numbers
  - 4 tickets need manual review
  - All decimals removed
```

### Multi-Store Analysis
```
Upload: store_issues.csv
Result:
  - Store numbers extracted from descriptions
  - Ready to group by store in Tableau
  - No data type issues
```

### Quality Reports
```
Upload: work_orders.csv
Result:
  - Clean store numbers
  - Easy to filter by store
  - Blank entries flagged for follow-up
```

## Recognized Patterns

### Pattern Examples
```
✓ "521 - Break/Fix IP Upgrade"
✓ "Store 521 Hirsch troubleshooting"
✓ "Store #521"
✓ "#521 - Camera issues"
✓ "store 521 update"
✓ "Store number 521"
✓ "Store No. 521"
```

### Not Recognized (Stays Blank)
```
✗ "USB PTZ controller KB" (no number)
✗ "General support request" (no number)
✗ "Multiple stores" (ambiguous)
✗ "Store to be determined" (no number)
```

## Technical Details

### Store Number Format
- **Input**: Can be text or number (e.g., "521.0" or 521.0)
- **Output**: Always text without decimals (e.g., "521")
- **Range**: 3-4 digits (e.g., 521, 1234)

### Extraction Logic
1. Search for "Store XXX" pattern
2. Search for "XXX - " pattern at start
3. Search for "#XXX" pattern
4. Validate 3-4 digit length
5. Return first valid match

### Column Requirements
- **Summary column**: Must exist for extraction
- **Store Number column**: Created if doesn't exist
- **Case insensitive**: Matches "Store" or "store"

## What Gets Logged

Example log output:
```
2025-10-20 08:31:33 - Processing store numbers...
2025-10-20 08:31:33 - Extracted store number 521 from: 521 - Break/Fix...
2025-10-20 08:31:33 - Extracted store number 545 from: Store 545 - Hirsch...
2025-10-20 08:31:33 - No store number found in: USB PTZ controller KB
2025-10-20 08:31:33 - Store number processing complete
2025-10-20 08:31:33 - Total rows: 32
2025-10-20 08:31:33 - With store numbers: 28 (87.5%)
2025-10-20 08:31:33 - Without store numbers: 4 (12.5%)
```

## In Tableau

### After Import

Your cleaned CSV will have:
```
Store Number (Text)
521
545
642
623
(blank)
(blank)
```

### Tableau Benefits
- Group by store number
- Filter to specific stores
- Count tickets by store
- Identify tickets without stores
- No data type conversion issues

### Example Calculations
```
// Count tickets with store numbers
IF NOT ISNULL([Store Number])
THEN 1
ELSE 0
END

// Flag missing store numbers
IF ISNULL([Store Number])
THEN "Needs Review"
ELSE "Complete"
END
```

## Tips

### Best Practices
1. **Review blank entries** - Check the 4 blank rows to see if they need store numbers
2. **Consistent format** - All future exports should include store numbers in summary
3. **Quality check** - Verify extracted numbers are correct before analysis

### Common Questions

**Q: What if extraction gets it wrong?**
A: Check the cleaning log - it shows what was extracted from where. You can manually correct in the downloaded file.

**Q: Can I re-run extraction?**
A: Yes! Click "Re-clean" button to run it again.

**Q: What if my summary uses a different format?**
A: The extractor handles many formats, but let me know if you have a specific pattern that's not working.

## Complete Workflow

```
1. Upload CSV with Store Number column containing "521.0"
2. Auto-cleaning runs
3. Decimals removed: "521.0" → "521"
4. Missing numbers extracted from Summary
5. Download cleaned CSV
6. Import to Tableau
7. Use store number for grouping/filtering
```

## Files Involved

- **[utils/store_number_extractor.py](utils/store_number_extractor.py)** - Store number extraction logic
- **[utils/csv_cleaner.py](utils/csv_cleaner.py)** - Integrated into cleaning pipeline
- **Logs**: `/logs/app.log` - Detailed extraction log

## Example: Your Recent Upload

From your file `apt_tickets_complete.csv`:

```
Processed 32 tickets
Found store numbers in summaries like:
  - "521 - Break/Fix IP Upgrade"
  - "Store 545 - Hirsch issues"
  - "642 - Open Network Ports"

Results:
  ✓ Removed decimals from all store numbers
  ✓ Extracted missing store numbers where possible
  ✓ Left blanks for entries without store numbers
  ✓ Ready for Tableau!
```

---

**Your store numbers are now clean and ready for analysis!** 🎉
