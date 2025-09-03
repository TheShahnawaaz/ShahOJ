/**
 * Table Sorting Module for PocketOJ
 * Provides client-side table sorting functionality with visual indicators
 */

class TableSorter {
    constructor(tableId) {
        this.table = document.getElementById(tableId);
        this.currentSort = { column: null, direction: null };
        this.difficultyOrder = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
        
        if (this.table) {
            this.init();
        }
    }

    init() {
        // Add click event listeners to sortable headers
        const headers = this.table.querySelectorAll('.sortable-header');
        headers.forEach(header => {
            header.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSort(header);
            });
        });
    }

    handleSort(header) {
        const column = header.dataset.column;
        const type = header.dataset.type;
        
        // Determine sort direction
        let direction = 'asc';
        if (this.currentSort.column === column && this.currentSort.direction === 'asc') {
            direction = 'desc';
        }
        
        // Add sorting visual feedback
        this.table.classList.add('sorting');
        
        // Update visual indicators
        this.updateSortIndicators(header, direction);
        
        // Perform sort with a slight delay for better UX
        setTimeout(() => {
            this.sortTable(column, type, direction);
            
            // Remove sorting indicator after animation
            setTimeout(() => {
                this.table.classList.remove('sorting');
            }, 600);
        }, 50);
        
        // Update current sort state
        this.currentSort = { column, direction };
    }

    updateSortIndicators(activeHeader, direction) {
        // Reset all headers
        const headers = this.table.querySelectorAll('.sortable-header');
        headers.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Set active header
        activeHeader.classList.add(`sort-${direction}`);
    }

    sortTable(column, type, direction) {
        const tbody = this.table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Store original positions for FLIP animation
        const originalPositions = new Map();
        rows.forEach((row, index) => {
            const rect = row.getBoundingClientRect();
            originalPositions.set(row, {
                top: rect.top,
                index: index
            });
        });
        
        // Sort rows based on data attributes
        rows.sort((a, b) => {
            const aVal = this.getValueForSort(a, column, type);
            const bVal = this.getValueForSort(b, column, type);
            
            let comparison = 0;
            
            switch (type) {
                case 'text':
                    comparison = aVal.localeCompare(bVal);
                    break;
                case 'date':
                    comparison = new Date(aVal) - new Date(bVal);
                    break;
                case 'difficulty':
                    comparison = this.difficultyOrder[aVal] - this.difficultyOrder[bVal];
                    break;
                default:
                    comparison = aVal.localeCompare(bVal);
            }
            
            return direction === 'desc' ? -comparison : comparison;
        });
        
        // Re-append rows in sorted order
        rows.forEach(row => tbody.appendChild(row));
        
        // Animate the reordering using FLIP technique
        this.animateReordering(rows, originalPositions);
    }

    getValueForSort(row, column, type) {
        const dataAttr = `data-${column}`;
        let value = row.getAttribute(dataAttr);
        
        if (!value) {
            // Fallback to text content if data attribute is missing
            const columnIndex = this.getColumnIndex(column);
            const cell = row.cells[columnIndex];
            value = cell ? cell.textContent.trim() : '';
        }
        
        // Clean up value based on type
        switch (type) {
            case 'text':
                return value.toLowerCase();
            case 'date':
                return value || '1900-01-01';
            case 'difficulty':
                return value || 'Medium';
            default:
                return value.toLowerCase();
        }
    }

    getColumnIndex(column) {
        const headers = this.table.querySelectorAll('th');
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].dataset.column === column) {
                return i;
            }
        }
        return 0;
    }

    animateReordering(rows, originalPositions) {
        // FLIP Animation: First, Last, Invert, Play
        const animations = [];
        
        rows.forEach((row, newIndex) => {
            const original = originalPositions.get(row);
            const newRect = row.getBoundingClientRect();
            
            // Calculate the difference in position
            const deltaY = original.top - newRect.top;
            
            // Only animate if the row actually moved
            if (Math.abs(deltaY) > 1) {
                // Invert: Apply the inverse transform to make it appear in original position
                row.style.transform = `translateY(${deltaY}px)`;
                row.style.transition = 'none';
                row.classList.add('reordering');
                
                // Store animation data
                animations.push({
                    element: row,
                    deltaY: deltaY,
                    delay: Math.abs(original.index - newIndex) * 25 // Stagger based on distance moved
                });
            }
        });
        
        // Force reflow to ensure transforms are applied
        this.table.offsetHeight;
        
        // Play: Animate to final position
        animations.forEach(({ element, deltaY, delay }) => {
            setTimeout(() => {
                element.style.transition = 'transform 0.4s cubic-bezier(0.2, 0, 0.2, 1)';
                element.style.transform = 'translateY(0)';
                
                // Clean up after animation completes
                setTimeout(() => {
                    element.style.transition = '';
                    element.style.transform = '';
                    element.classList.remove('reordering');
                }, 400);
            }, delay);
        });
        
        // Add a subtle highlight effect to show sorting is complete
        setTimeout(() => {
            this.addSortCompleteEffect();
        }, 200);
    }

    addSortCompleteEffect() {
        // Add a subtle pulse effect to indicate sorting is complete
        const rows = this.table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            setTimeout(() => {
                row.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
                setTimeout(() => {
                    row.style.backgroundColor = '';
                    row.style.transition = 'background-color 0.3s ease';
                    setTimeout(() => {
                        row.style.transition = '';
                    }, 300);
                }, 100);
            }, index * 20);
        });
    }

    // Legacy method for backward compatibility
    animateSort() {
        // This method is kept for backward compatibility but now uses the new animation
        const rows = this.table.querySelectorAll('tbody tr');
        this.addSortCompleteEffect();
    }

    // Public method to programmatically sort
    sort(column, direction = 'asc') {
        const header = this.table.querySelector(`[data-column="${column}"]`);
        if (header) {
            this.currentSort = { column, direction };
            this.updateSortIndicators(header, direction);
            this.sortTable(column, header.dataset.type, direction);
        }
    }

    // Public method to get current sort state
    getCurrentSort() {
        return this.currentSort;
    }

    // Public method to reset sort
    resetSort() {
        const headers = this.table.querySelectorAll('.sortable-header');
        headers.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        this.currentSort = { column: null, direction: null };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TableSorter;
}

// Global initialization function
window.initTableSorter = function(tableId) {
    return new TableSorter(tableId);
};
