/**
 * Reusable Monaco Editor Component for ShahOJ
 * Supports C++, Python, Markdown with resizing, folding, and zoom features
 */
class MonacoEditorComponent {
    constructor(config = {}) {
        // Default configuration
        this.config = {
            containerId: config.containerId || 'monaco-editor',
            language: config.language || 'cpp',
            theme: config.theme || 'vs-light',
            height: config.height || 600,
            minHeight: config.minHeight || 300,
            maxHeight: config.maxHeight || 1200,
            defaultValue: config.defaultValue || '',
            resizable: config.resizable !== false, // Default true
            showMinimap: config.showMinimap !== false, // Default true
            readOnly: config.readOnly || false,
            fontSize: config.fontSize || 14,
            ...config.monacoOptions // Allow custom Monaco options
        };
        
        this.editor = null;
        this.resizeListeners = null;
        this.isInitialized = false;
        
        if (config.autoInit !== false) {
            this.init();
        }
    }
    
    async init() {
        try {
            console.log('Initializing Monaco Editor Component...');
            
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize Monaco with delay
            setTimeout(async () => {
                await this.initMonaco();
                this.isInitialized = true;
                console.log('Monaco Editor Component initialized successfully');
            }, 100);
            
        } catch (error) {
            console.error('Failed to initialize Monaco Editor Component:', error);
            this.createFallbackEditor();
        }
    }
    
    async waitForDOM() {
        return new Promise(resolve => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve);
            }
        });
    }
    
    async initMonaco() {
        return new Promise((resolve, reject) => {
            try {
                // Configure Monaco loader
                require.config({ 
                    paths: { 
                        vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' 
                    }
                });
                
                // Load Monaco Editor
                require(['vs/editor/editor.main'], () => {
                    console.log('Monaco Editor loaded successfully');
                    this.createMonacoEditor();
                    resolve();
                }, (error) => {
                    console.error('Failed to load Monaco Editor:', error);
                    this.createFallbackEditor();
                    resolve(); // Still resolve to continue
                });
            } catch (error) {
                console.error('Monaco initialization error:', error);
                this.createFallbackEditor();
                resolve();
            }
        });
    }
    
    createMonacoEditor() {
        const container = document.getElementById(this.config.containerId);
        if (!container) {
            console.warn(`Monaco container not found: ${this.config.containerId}`);
            return;
        }
        
        try {
            // Ensure container has proper dimensions
            container.style.width = '100%';
            container.style.height = this.config.height + 'px';
            
            // Create Monaco Editor with comprehensive configuration
            this.editor = monaco.editor.create(container, {
                value: this.config.defaultValue,
                language: this.config.language,
                theme: this.config.theme,
                automaticLayout: true,
                minimap: { enabled: this.config.showMinimap },
                scrollBeyondLastLine: true,
                fontSize: this.config.fontSize,
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                wordWrap: 'on',
                readOnly: this.config.readOnly,
                
                // Enhanced Code Folding Features
                folding: true,
                foldingStrategy: 'indentation',
                foldingHighlight: true,
                unfoldOnClickAfterEndOfLine: true,
                showFoldingControls: 'always',
                
                // Enhanced Bracket Matching and Selection
                bracketMatching: 'always',
                matchBrackets: 'always',
                autoIndent: 'full',
                formatOnPaste: true,
                formatOnType: true,
                selectOnLineNumbers: true,
                roundedSelection: true,
                cursorStyle: 'line',
                glyphMargin: true,
                
                // Code Structure Enhancement
                renderIndentGuides: true,
                highlightActiveIndentGuide: true,
                
                // Language-specific settings
                suggest: {
                    insertMode: 'replace',
                    showFunctions: true,
                    showConstructors: true,
                    showClasses: true,
                    showStructs: true
                },
                quickSuggestions: {
                    other: true,
                    comments: false,
                    strings: false
                },
                
                // Code Lens and Hover
                codeLens: true,
                hover: { enabled: true },
                
                // Smooth Scrolling and Zoom
                smoothScrolling: true,
                mouseWheelZoom: true, // Cmd+Scroll / Ctrl+Scroll zoom
                
                // Multi-cursor support
                multiCursorModifier: 'ctrlCmd',
                
                // Enhanced Find/Replace
                find: {
                    seedSearchStringFromSelection: 'always',
                    autoFindInSelection: 'always'
                },
                
                // Apply any custom Monaco options
                ...this.config.monacoOptions
            });
            
            // Force layout after creation
            setTimeout(() => {
                this.editor.layout();
            }, 100);

            // Apply current app theme to Monaco
            const applyCurrentThemeToMonaco = () => {
                const htmlTheme = document.documentElement.getAttribute('data-theme');
                const monacoTheme = htmlTheme === 'dark' ? 'vs-dark' : 'vs-light';
                try { monaco.editor.setTheme(monacoTheme); } catch (e) {}
            };
            applyCurrentThemeToMonaco();

            // Listen for theme changes
            this.handleThemeChange = (e) => {
                const next = (e && e.detail && e.detail.theme) ? e.detail.theme : document.documentElement.getAttribute('data-theme');
                const monacoTheme = next === 'dark' ? 'vs-dark' : 'vs-light';
                try { monaco.editor.setTheme(monacoTheme); } catch (e) {}
            };
            document.addEventListener('theme:changed', this.handleThemeChange);
            
            // Add resize functionality if enabled
            if (this.config.resizable) {
                this.addResizeFeature();
            }
            
            // Set up auto-save functionality
            this.setupAutoSave();
            
            // Trigger ready callback if provided
            if (this.config.onReady) {
                this.config.onReady(this.editor);
            }
            
            console.log(`Monaco ${this.config.language} editor created successfully`);
        } catch (error) {
            console.error('Failed to create Monaco editor:', error);
            this.createFallbackEditor();
        }
    }
    
    createFallbackEditor() {
        console.log('Creating fallback textarea editor');
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        const textarea = document.createElement('textarea');
        textarea.className = 'form-control code-editor';
        textarea.style.width = '100%';
        textarea.style.height = this.config.height + 'px';
        textarea.style.fontFamily = 'Monaco, Consolas, "Courier New", monospace';
        textarea.style.fontSize = this.config.fontSize + 'px';
        textarea.style.lineHeight = '1.4';
        textarea.style.backgroundColor = '#1e1e1e';
        textarea.style.color = '#d4d4d4';
        textarea.style.padding = '10px';
        textarea.style.borderRadius = '8px';
        textarea.style.border = 'none';
        textarea.style.resize = this.config.resizable ? 'vertical' : 'none';
        textarea.readOnly = this.config.readOnly;
        textarea.value = this.config.defaultValue;
        
        container.innerHTML = '';
        container.appendChild(textarea);
        
        // Store reference with Monaco-like interface
        this.editor = {
            getValue: () => textarea.value,
            setValue: (value) => { textarea.value = value; },
            focus: () => textarea.focus(),
            layout: () => {},
            getAction: () => ({ run: () => {} }) // Dummy action for compatibility
        };
        
        // Add resize functionality for fallback editor if enabled
        if (this.config.resizable) {
            this.addResizeFeature();
        }
        
        // Set up auto-save for fallback editor
        this.setupAutoSave();
        
        // Trigger ready callback if provided
        if (this.config.onReady) {
            this.config.onReady(this.editor);
        }
    }
    
    addResizeFeature() {
        const resizeHandleId = this.config.containerId + '-resize-handle';
        const resizeHandle = document.getElementById(resizeHandleId);
        const editorContainer = document.getElementById(this.config.containerId);
        
        if (!resizeHandle || !editorContainer) {
            console.warn('Resize handle or container not found for resizing feature');
            return;
        }
        
        let isResizing = false;
        let startY = 0;
        let startHeight = 0;
        
        const handleMouseDown = (e) => {
            isResizing = true;
            startY = e.clientY;
            startHeight = parseInt(document.defaultView.getComputedStyle(editorContainer).height, 10);
            
            editorContainer.classList.add('resizing');
            document.body.style.cursor = 'ns-resize';
            document.body.style.userSelect = 'none';
            
            e.preventDefault();
        };
        
        const handleMouseMove = (e) => {
            if (!isResizing) return;
            
            const currentY = e.clientY;
            const deltaY = currentY - startY;
            const newHeight = Math.max(
                this.config.minHeight, 
                Math.min(this.config.maxHeight, startHeight + deltaY)
            );
            
            editorContainer.style.height = newHeight + 'px';
            
            // Trigger Monaco layout update
            if (this.editor && typeof this.editor.layout === 'function') {
                requestAnimationFrame(() => {
                    this.editor.layout();
                });
            }
            
            e.preventDefault();
        };
        
        const handleMouseUp = () => {
            if (!isResizing) return;
            
            isResizing = false;
            editorContainer.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            
            // Final layout update
            if (this.editor && typeof this.editor.layout === 'function') {
                setTimeout(() => {
                    this.editor.layout();
                }, 50);
            }
        };
        
        // Add event listeners
        resizeHandle.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        
        // Store references for cleanup
        this.resizeListeners = {
            handle: resizeHandle,
            mousedown: handleMouseDown,
            mousemove: handleMouseMove,
            mouseup: handleMouseUp
        };
        
        console.log('Editor resize feature initialized');
    }
    
    // Public API methods
    getValue() {
        return this.editor ? this.editor.getValue() : '';
    }
    
    setValue(value) {
        if (this.editor) {
            this.editor.setValue(value);
        }
    }
    
    focus() {
        if (this.editor) {
            this.editor.focus();
        }
    }
    
    layout() {
        if (this.editor && typeof this.editor.layout === 'function') {
            this.editor.layout();
        }
    }
    
    getAction(actionId) {
        return this.editor && this.editor.getAction ? this.editor.getAction(actionId) : null;
    }
    
    insertText(text) {
        if (this.editor && this.editor.trigger) {
            const selection = this.editor.getSelection();
            this.editor.executeEdits('insert-text', [{
                range: selection,
                text: text
            }]);
        }
    }
    
    // Utility methods for common actions
    foldAll() {
        const action = this.getAction('editor.foldAll');
        if (action) action.run();
    }
    
    unfoldAll() {
        const action = this.getAction('editor.unfoldAll');
        if (action) action.run();
    }
    
    formatDocument() {
        const action = this.getAction('editor.action.formatDocument');
        if (action) action.run();
    }
    
    setupAutoSave() {
        if (!this.editor || this.config.disableAutoSave) {
            return;
        }
        
        // Generate storage key based on current page and editor type
        const currentPath = window.location.pathname;
        const storageKey = `monaco_autosave_${this.config.containerId}_${currentPath}`;
        
        // Load saved content on initialization
        const savedContent = localStorage.getItem(storageKey);
        if (savedContent && savedContent.trim() !== '') {
            // Only load if it's different from default template
            const currentContent = this.editor.getValue();
            if (savedContent !== currentContent) {
                this.editor.setValue(savedContent);
                
                // Show a subtle notification that content was restored
                this.showAutoSaveNotification('Content restored from previous session', 'info');
            }
        }
        
        // Set up auto-save on content change
        let saveTimeout;
        
        // Handle both Monaco editor and fallback textarea
        if (this.editor.onDidChangeModelContent) {
            // Monaco editor
            this.editor.onDidChangeModelContent(() => {
                // Clear previous timeout
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }
                
                // Save after 2 seconds of inactivity
                saveTimeout = setTimeout(() => {
                    const content = this.editor.getValue();
                    localStorage.setItem(storageKey, content);
                    
                    // Show subtle save indicator
                    this.showAutoSaveNotification('Progress saved', 'success');
                }, 2000);
            });
        } else {
            // Fallback textarea
            const textarea = document.querySelector(`#${this.config.containerId} textarea`);
            if (textarea) {
                textarea.addEventListener('input', () => {
                    // Clear previous timeout
                    if (saveTimeout) {
                        clearTimeout(saveTimeout);
                    }
                    
                    // Save after 2 seconds of inactivity
                    saveTimeout = setTimeout(() => {
                        const content = this.editor.getValue();
                        localStorage.setItem(storageKey, content);
                        
                        // Show subtle save indicator
                        this.showAutoSaveNotification('Progress saved', 'success');
                    }, 2000);
                });
            }
        }
        
        // Save immediately when user leaves the page
        window.addEventListener('beforeunload', () => {
            const content = this.editor.getValue();
            localStorage.setItem(storageKey, content);
        });
        
        // Clear saved content when user explicitly clears the editor
        const clearButton = document.getElementById('clearCodeBtn');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                localStorage.removeItem(storageKey);
            });
        }
    }
    
    showAutoSaveNotification(message, type = 'info') {
        // Create or update notification element
        let notification = document.getElementById('monaco-autosave-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'monaco-autosave-notification';
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
                background: var(--bs-success);
                color: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            `;
            document.body.appendChild(notification);
        }
        
        // Set message and style based on type
        notification.textContent = message;
        if (type === 'success') {
            notification.style.background = '#28a745';
        } else if (type === 'info') {
            notification.style.background = '#17a2b8';
        }
        
        // Show notification
        notification.style.opacity = '1';
        
        // Hide after 2 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
        }, 2000);
    }
    
    // Cleanup method
    destroy() {
        // Remove theme listener
        if (this.handleThemeChange) {
            document.removeEventListener('theme:changed', this.handleThemeChange);
            this.handleThemeChange = null;
        }
        if (this.resizeListeners) {
            const { handle, mousedown, mousemove, mouseup } = this.resizeListeners;
            if (handle) handle.removeEventListener('mousedown', mousedown);
            document.removeEventListener('mousemove', mousemove);
            document.removeEventListener('mouseup', mouseup);
        }
        
        if (this.editor && this.editor.dispose) {
            this.editor.dispose();
        }
        
        this.editor = null;
        this.isInitialized = false;
    }
}

// Export for use in other files
window.MonacoEditorComponent = MonacoEditorComponent;
