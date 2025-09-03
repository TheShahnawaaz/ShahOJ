# Table Sorter Module Documentation

## Overview

The Table Sorter module provides client-side sorting functionality for HTML tables in the PocketOJ application. It's designed to be reusable, flexible, and provides visual feedback for user interactions.

## Features

- ✅ **Multi-column sorting** - Sort by Title, Difficulty, Tags, or Created Date
- ✅ **Bi-directional sorting** - Click once for ascending, click again for descending
- ✅ **Visual indicators** - Clear sort arrows showing current sort state
- ✅ **Type-aware sorting** - Different sorting logic for text, dates, and difficulties
- ✅ **Beautiful reordering animations** - FLIP technique for smooth row transitions
- ✅ **Visual feedback** - Sorting indicator bar and row highlighting
- ✅ **Staggered animations** - Rows animate based on distance moved
- ✅ **Performance optimized** - GPU-accelerated transforms and efficient DOM operations
- ✅ **Organized code structure** - Modular ES6 class-based implementation

## Usage

### Basic Implementation

```html
<!-- Include the script -->
<script src="{{ url_for('static', filename='js/table-sorter.js') }}"></script>

<!-- Create a table with sortable headers -->
<table id="myTable">
    <thead>
        <tr>
            <th class="sortable-header" data-column="title" data-type="text">
                Title
                <span class="sort-icon">
                    <i class="fas fa-sort"></i>
                    <i class="fas fa-sort-up"></i>
                    <i class="fas fa-sort-down"></i>
                </span>
            </th>
            <!-- More headers... -->
        </tr>
    </thead>
    <tbody>
        <tr data-title="example title" data-difficulty="Easy">
            <!-- Table content... -->
        </tr>
    </tbody>
</table>

<!-- Initialize the sorter -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const sorter = window.initTableSorter('myTable');
});
</script>
```

### Required HTML Structure

#### Table Headers
- Add `sortable-header` class to `<th>` elements
- Include `data-column` attribute with column identifier
- Include `data-type` attribute with sorting type
- Add sort icons inside each header

#### Table Rows
- Add corresponding `data-{column}` attributes to `<tr>` elements
- Values should be in a format suitable for sorting

### Supported Data Types

1. **text** - Alphabetical sorting (case-insensitive)
2. **date** - Chronological sorting (expects ISO date format)
3. **difficulty** - Custom sorting (Easy → Medium → Hard)

### CSS Classes

Required CSS classes for styling (already included in dashboard.html):

```css
.sortable-header {
    cursor: pointer;
    user-select: none;
    position: relative;
    padding-right: 2rem !important;
}

.sort-icon {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
}

.sortable-header.sort-asc .sort-icon .fa-sort-up { display: inline; }
.sortable-header.sort-desc .sort-icon .fa-sort-down { display: inline; }
/* ... additional styles ... */
```

## API Reference

### TableSorter Class

#### Constructor
```javascript
new TableSorter(tableId)
```
- `tableId` (string): The ID of the table element to make sortable

#### Methods

##### `sort(column, direction)`
Programmatically sort a column
- `column` (string): Column identifier from data-column attribute
- `direction` (string): 'asc' or 'desc'

```javascript
sorter.sort('title', 'asc');
```

##### `getCurrentSort()`
Returns current sort state
```javascript
const { column, direction } = sorter.getCurrentSort();
```

##### `resetSort()`
Clears all sorting and visual indicators
```javascript
sorter.resetSort();
```

### Global Functions

#### `window.initTableSorter(tableId)`
Convenience function to create and return a new TableSorter instance
```javascript
const sorter = window.initTableSorter('problemsTable');
```

## Implementation Details

### Difficulty Sorting Logic
```javascript
difficultyOrder = { 'Easy': 1, 'Medium': 2, 'Hard': 3 }
```

### Animation System
The table sorter uses the FLIP (First, Last, Invert, Play) animation technique for smooth reordering:

1. **First**: Record original positions of all rows
2. **Last**: Sort and reposition rows in DOM
3. **Invert**: Apply transforms to make rows appear in original positions
4. **Play**: Animate transforms to final positions

**Features:**
- GPU-accelerated transforms for smooth 60fps animations
- Staggered animations based on distance moved (25ms per position)
- Cubic-bezier easing for natural motion feel
- Visual feedback with shadows during movement
- Highlight effect on completion

### Data Attribute Fallback
If data attributes are missing, the sorter falls back to:
1. Text content of the corresponding table cell
2. Default values for each data type

## File Structure

```
static/js/
├── table-sorter.js           # Main module
└── README-TableSorter.md     # This documentation
```

## Browser Compatibility

- Modern browsers supporting ES6 classes
- Requires Font Awesome icons for visual indicators
- Tested with Chrome, Firefox, Safari, Edge

## Troubleshooting

### Common Issues

1. **Sorting not working**
   - Ensure data attributes are correctly set on table rows
   - Check that Font Awesome is loaded for icons
   - Verify table has correct ID and structure

2. **Visual indicators not showing**
   - Include the CSS classes from dashboard.html
   - Check Font Awesome icon classes are correct

3. **Date sorting incorrect**
   - Ensure date values are in ISO format (YYYY-MM-DD)
   - Check data-created attributes are set properly

### Debug Mode
```javascript
// Check current sort state
console.log(sorter.getCurrentSort());

// Test sorting programmatically
sorter.sort('title', 'asc');
```

## Future Enhancements

Potential improvements for future versions:
- Multi-column sorting with priority
- Custom sort functions for specific data types
- Persistent sort state in localStorage
- Search/filter integration
- Export sorted data functionality
