/**
 * Example: How to integrate the reusable Monaco Editor Component in edit.html
 * This shows how to replace the existing Monaco Editor setup with our reusable component
 */

// Example of how the edit page would use our reusable components
class EditPageIntegration {
    constructor() {
        this.editors = {};
        this.init();
    }
    
    init() {
        // Initialize all editors using our reusable components
        this.initializeEditors();
        this.setupEventListeners();
    }
    
    initializeEditors() {
        // 1. Statement Editor (Markdown)
        this.editors.statement = MonacoEditorPresets.createStatementEditor('statement-monaco-editor', {
            height: 500,
            onReady: (editor) => {
                console.log('Statement editor ready');
                this.loadFileContent('statement', editor);
            }
        });
        
        // 2. Solution Editor (Python)
        this.editors.solution = MonacoEditorPresets.createPythonSolutionEditor('solution-monaco-editor', {
            height: 500,
            onReady: (editor) => {
                console.log('Solution editor ready');
                this.loadFileContent('solution', editor);
            }
        });
        
        // 3. Generator Editor (Python)
        this.editors.generator = MonacoEditorPresets.createGeneratorEditor('generator-monaco-editor', {
            height: 400,
            onReady: (editor) => {
                console.log('Generator editor ready');
                this.loadFileContent('generator', editor);
            }
        });
        
        // 4. Validator Editor (Python)
        this.editors.validator = MonacoEditorPresets.createValidatorEditor('validator-monaco-editor', {
            height: 400,
            onReady: (editor) => {
                console.log('Validator editor ready');
                this.loadFileContent('validator', editor);
            }
        });
        
        // 5. Checker Editor (C++)
        this.editors.checker = MonacoEditorPresets.createCheckerEditor('checker-monaco-editor', {
            height: 400,
            onReady: (editor) => {
                console.log('Checker editor ready');
                this.loadFileContent('checker', editor);
            }
        });
    }
    
    setupEventListeners() {
        // Template buttons
        document.querySelectorAll('[data-template]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const template = e.target.dataset.template;
                const fileType = e.target.closest('.file-content').id.replace('-content', '');
                this.applyTemplate(fileType, template);
            });
        });
        
        // Reset buttons
        document.getElementById('resetStatementBtn')?.addEventListener('click', () => {
            this.resetEditor('statement');
        });
        
        document.getElementById('resetSolutionBtn')?.addEventListener('click', () => {
            this.resetEditor('solution');
        });
        
        // Validation buttons
        document.getElementById('validateStatementBtn')?.addEventListener('click', () => {
            this.validateEditor('statement');
        });
        
        // Save all button
        document.getElementById('saveAllBtn')?.addEventListener('click', () => {
            this.saveAllChanges();
        });
    }
    
    loadFileContent(fileType, editor) {
        // Load initial content from the page data
        // This would replace the existing file loading logic
        try {
            const dataElement = document.getElementById('initial-content-data');
            if (dataElement) {
                const contentData = JSON.parse(dataElement.textContent);
                const content = contentData[fileType] || '';
                editor.setValue(content);
            }
        } catch (error) {
            console.warn('Failed to load initial content for', fileType, error);
        }
    }
    
    applyTemplate(fileType, templateName) {
        const editor = this.editors[fileType];
        if (!editor) return;
        
        // Use the built-in templates from our presets
        // Or implement custom template logic here
        console.log(`Applying ${templateName} template to ${fileType}`);
    }
    
    resetEditor(fileType) {
        const editor = this.editors[fileType];
        if (!editor) return;
        
        if (confirm(`Reset ${fileType} editor to default template?`)) {
            // Reset to default template based on file type
            switch (fileType) {
                case 'statement':
                    this.editors.statement = MonacoEditorPresets.createStatementEditor('statement-monaco-editor');
                    break;
                case 'solution':
                    this.editors.solution = MonacoEditorPresets.createPythonSolutionEditor('solution-monaco-editor');
                    break;
                // Add other cases...
            }
        }
    }
    
    validateEditor(fileType) {
        const editor = this.editors[fileType];
        if (!editor) return;
        
        const content = editor.getValue();
        
        // Validate using existing API
        fetch('/api/validate-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: this.getFileName(fileType),
                content: content
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.valid) {
                this.showValidationSuccess(fileType);
            } else {
                this.showValidationError(fileType, result.error);
            }
        });
    }
    
    saveAllChanges() {
        const data = {
            config: this.getConfigData(),
            files: {
                'statement.md': this.editors.statement?.getValue() || '',
                'solution.py': this.editors.solution?.getValue() || '',
                'generator.py': this.editors.generator?.getValue() || '',
                'validator.py': this.editors.validator?.getValue() || '',
                'checker/spj.cpp': this.editors.checker?.getValue() || ''
            }
        };
        
        // Use existing save API
        fetch(`/api/problem/${this.problemSlug}/save-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showSaveSuccess();
            } else {
                this.showSaveError(result.error);
            }
        });
    }
    
    // Utility methods
    getFileName(fileType) {
        const fileNames = {
            statement: 'statement.md',
            solution: 'solution.py',
            generator: 'generator.py',
            validator: 'validator.py',
            checker: 'checker/spj.cpp'
        };
        return fileNames[fileType] || `${fileType}.txt`;
    }
    
    getConfigData() {
        // Collect configuration data from form fields
        return {
            title: document.getElementById('edit_title')?.value || '',
            difficulty: document.getElementById('edit_difficulty')?.value || 'Medium',
            tags: document.getElementById('edit_tags')?.value.split(',').map(t => t.trim()).filter(t => t),
            // ... other config fields
        };
    }
    
    showValidationSuccess(fileType) {
        console.log(`${fileType} validation successful`);
        // Update UI to show validation success
    }
    
    showValidationError(fileType, error) {
        console.error(`${fileType} validation failed:`, error);
        // Update UI to show validation error
    }
    
    showSaveSuccess() {
        console.log('All changes saved successfully');
        // Update UI to show save success
    }
    
    showSaveError(error) {
        console.error('Save failed:', error);
        // Update UI to show save error
    }
}

// How to replace the existing edit page JavaScript:
// 1. Include the Monaco Editor Component scripts in edit.html
// 2. Replace the existing ProblemEditor class with EditPageIntegration
// 3. Update the HTML containers to use the standard naming convention
// 4. Initialize with: window.editPageIntegration = new EditPageIntegration();

/*
Example HTML changes needed in edit.html:

<!-- Add to extra_css block -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/monaco-editor-component.css') }}">

<!-- Add to extra_js block -->
<script src="{{ url_for('static', filename='js/monaco-editor-component.js') }}"></script>
<script src="{{ url_for('static', filename='js/monaco-editor-presets.js') }}"></script>

<!-- Update Monaco containers to include resize handles -->
<div class="editor-resize-container">
    <div class="monaco-editor-container" id="statement-monaco-editor"></div>
    <div class="editor-resize-handle" id="statement-monaco-editor-resize-handle"></div>
</div>

<!-- Initialize the new system -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    window.editPageIntegration = new EditPageIntegration();
});
</script>
*/
