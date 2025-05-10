# Monthly Archives Support

This document explains how we added support for monthly archive pages to the blog.

## Overview

The blog has a "バックナンバー" (back number) section in the sidebar that contains links to monthly archives. These links allow users to view blog posts from specific months. We downloaded the monthly archive pages from the original site and processed them to work with our local server.

## Implementation Steps

1. **Download Monthly Archive Pages**
   - Created `download_monthly_archives.py` to download all monthly archive pages
   - Downloaded 37 monthly archive pages to `raw_html/monthly_archives/`
   - Each page represents a specific month (format: YYYYMM)

2. **Process Monthly Archive Pages**
   - Created `process_monthly_archives.py` to process the downloaded pages
   - Fixed asset paths (CSS, JS, images) to point to our local assets
   - Fixed article links to follow our URL structure
   - Fixed other internal links
   - Saved processed pages to `local_html/ikuoikuo_2005/m/` directory

3. **Update Backnumber Links**
   - Found that backnumber links in the sidebar weren't working because they didn't include the `.html` extension
   - Created `fix_backnumber_links.py` to update all links in the backnumber section
   - Updated 8,732 links (37 links in 236 files) to include the `.html` extension
   - Tested and verified that the links now work correctly

## Monthly Archive Structure

Each monthly archive page is stored in the following location:
```
local_html/ikuoikuo_2005/m/YYYYMM.html
```

For example:
- `local_html/ikuoikuo_2005/m/201004.html` (April 2010)
- `local_html/ikuoikuo_2005/m/200911.html` (November 2009)
- etc.

## Testing

We created two test scripts to verify that the monthly archive pages are working correctly:

1. `test_monthly_archives.py`: Tests if all monthly archive pages are accessible through the server
2. `test_backnumber_links.py`: Tests if the backnumber links in the sidebar correctly redirect to the monthly archive pages

Both tests confirmed that the monthly archive functionality is working as expected.

## Conclusion

With the addition of monthly archive support, users can now browse through blog posts by month, providing a better navigation experience. The "バックナンバー" section in the sidebar now correctly links to the respective monthly archive pages. 