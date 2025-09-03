# Monaco Editor Component for ShahOJ

A comprehensive, reusable Monaco Editor integration with advanced features for the ShahOJ competitive programming platform.

## 🚀 Features

### ✨ Core Features
- **Multiple Language Support**: C++, Python, Markdown, Plain Text
- **Resizable Editor**: Drag-to-resize with visual handles
- **Code Folding**: Enhanced folding with always-visible controls
- **Zoom Support**: Cmd+Scroll/Ctrl+Scroll zoom functionality
- **Smart Templates**: Pre-configured templates for different use cases
- **Fallback Support**: Graceful degradation to textarea when Monaco fails

### 🎨 Enhanced UI
- **Visual Resize Handle**: Professional drag handle with hover effects
- **Language-specific Theming**: Different border colors for different languages
- **Responsive Design**: Mobile-friendly with larger touch targets
- **Dark/Light Theme Support**: Automatic theme detection
- **Print Friendly**: Special print styles for documentation

## 📁 File Structure

```
static/
├── js/
│   ├── monaco-editor-component.js      # Core reusable component
│   ├── monaco-editor-presets.js        # Pre-configured editor setups
│   └── edit-page-integration-example.js # Example integration
├── css/
│   └── monaco-editor-component.css     # Component styles
```

## 🔧 Installation & Setup

### 1. Include Dependencies in HTML

```html
<!-- In the <head> section -->
<link rel="stylesheet" data-name="vs/editor/editor.main" 
      href="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/editor/editor.main.css">
<link rel="stylesheet" href="{{ url_for('static', filename='css/monaco-editor-component.css') }}">

<!-- Before closing </body> -->
<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/loader.js"></script>
<script src="{{ url_for('static', filename='js/monaco-editor-component.js') }}"></script>
<script src="{{ url_for('static', filename='js/monaco-editor-presets.js') }}"></script>
```

### 2. HTML Structure

```html
<div class="editor-resize-container">
    <div class="monaco-editor-container" id="my-editor"></div>
    <div class="editor-resize-handle" id="my-editor-resize-handle"></div>
</div>
```

## 📖 Usage Examples

### Basic Usage

```javascript
// Create a basic C++ editor
const editor = new MonacoEditorComponent({
    containerId: 'my-editor',
    language: 'cpp',
    height: 600,
    defaultValue: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello World!" << endl;\n    return 0;\n}'
});
```

### Using Presets (Recommended)

```javascript
// C++ Solution Editor
const cppEditor = MonacoEditorPresets.createCppSolutionEditor('cpp-editor');

// Python Solution Editor  
const pythonEditor = MonacoEditorPresets.createPythonSolutionEditor('python-editor');

// Markdown Statement Editor
const markdownEditor = MonacoEditorPresets.createStatementEditor('statement-editor');

// Test Generator
const generatorEditor = MonacoEditorPresets.createGeneratorEditor('generator-editor');

// Input Validator
const validatorEditor = MonacoEditorPresets.createValidatorEditor('validator-editor');
```

### Advanced Configuration

```javascript
const editor = new MonacoEditorComponent({
    containerId: 'advanced-editor',
    language: 'cpp',
    theme: 'vs-dark',
    height: 800,
    minHeight: 400,
    maxHeight: 1000,
    resizable: true,
    showMinimap: true,
    readOnly: false,
    fontSize: 16,
    onReady: (monacoEditor) => {
        console.log('Editor is ready!');
        // Configure additional settings
    },
    monacoOptions: {
        // Custom Monaco Editor options
        wordWrap: 'bounded',
        rulers: [80, 120]
    }
});
```

## 🎯 Pre-configured Editor Types

### 1. C++ Solution Editor
- **Use Case**: Competitive programming solutions
- **Language**: C++
- **Features**: Full template with I/O handling, debugging functions
- **Default Height**: 600px

```javascript
MonacoEditorPresets.createCppSolutionEditor('container-id');
```

### 2. Python Solution Editor
- **Use Case**: Python competitive programming solutions
- **Language**: Python
- **Features**: Clean template with proper I/O
- **Default Height**: 500px

```javascript
MonacoEditorPresets.createPythonSolutionEditor('container-id');
```

### 3. Statement Editor
- **Use Case**: Problem statements in Markdown
- **Language**: Markdown
- **Features**: Problem template with sections
- **Default Height**: 500px

```javascript
MonacoEditorPresets.createStatementEditor('container-id');
```

### 4. Test Generator
- **Use Case**: Python test case generators
- **Language**: Python
- **Features**: Template with random test generation
- **Default Height**: 400px

```javascript
MonacoEditorPresets.createGeneratorEditor('container-id');
```

### 5. Input Validator
- **Use Case**: Input validation scripts
- **Language**: Python
- **Features**: Template with constraint checking
- **Default Height**: 400px

```javascript
MonacoEditorPresets.createValidatorEditor('container-id');
```

### 6. Special Judge (Checker)
- **Use Case**: Custom output checkers
- **Language**: C++
- **Features**: testlib.h integration template
- **Default Height**: 400px

```javascript
MonacoEditorPresets.createCheckerEditor('container-id');
```

## 🔧 API Reference

### MonacoEditorComponent Class

#### Constructor Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `containerId` | string | 'monaco-editor' | DOM element ID |
| `language` | string | 'cpp' | Programming language |
| `theme` | string | 'vs-light' | Editor theme |
| `height` | number | 600 | Initial height in pixels |
| `minHeight` | number | 300 | Minimum height for resizing |
| `maxHeight` | number | 1200 | Maximum height for resizing |
| `defaultValue` | string | '' | Initial content |
| `resizable` | boolean | true | Enable resize functionality |
| `showMinimap` | boolean | true | Show code minimap |
| `readOnly` | boolean | false | Read-only mode |
| `fontSize` | number | 14 | Font size |
| `onReady` | function | null | Callback when editor is ready |
| `monacoOptions` | object | {} | Additional Monaco options |

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `getValue()` | Get editor content | string |
| `setValue(value)` | Set editor content | void |
| `focus()` | Focus the editor | void |
| `layout()` | Trigger layout update | void |
| `foldAll()` | Fold all code blocks | void |
| `unfoldAll()` | Unfold all code blocks | void |
| `formatDocument()` | Format the code | void |
| `insertText(text)` | Insert text at cursor | void |
| `destroy()` | Clean up and destroy editor | void |

## 🔄 Migration from Existing Code

### Before (Old Implementation)
```javascript
// Old Monaco setup - hundreds of lines of boilerplate
require.config({ paths: { vs: '...' }});
require(['vs/editor/editor.main'], () => {
    // Lots of manual configuration...
});
```

### After (New Component)
```javascript
// New implementation - clean and simple
const editor = MonacoEditorPresets.createCppSolutionEditor('my-editor');
```

### Benefits of Migration
- ✅ **90% less code** - From ~200 lines to ~5 lines
- ✅ **Consistent behavior** across all pages
- ✅ **Easier maintenance** - Single source of truth
- ✅ **Better features** - Resizing, folding, zoom out of the box
- ✅ **Type safety** - Better error handling and fallbacks

## 🛠️ Integration in Existing Pages

### Test Solution Page (Already Integrated)
```javascript
class SolutionTester {
    constructor() {
        this.cppEditor = MonacoEditorPresets.createCppSolutionEditor('cpp-solution-editor');
    }
}
```

### Edit Problem Page (Example)
```javascript
class EditPageIntegration {
    initializeEditors() {
        this.editors = {
            statement: MonacoEditorPresets.createStatementEditor('statement-editor'),
            solution: MonacoEditorPresets.createPythonSolutionEditor('solution-editor'),
            generator: MonacoEditorPresets.createGeneratorEditor('generator-editor'),
            validator: MonacoEditorPresets.createValidatorEditor('validator-editor'),
            checker: MonacoEditorPresets.createCheckerEditor('checker-editor')
        };
    }
}
```

## 🎨 Customization

### Custom Templates
```javascript
// Add custom templates to presets
MonacoEditorPresets.createCustomEditor = function(containerId, options = {}) {
    return new MonacoEditorComponent({
        containerId: containerId,
        language: 'cpp',
        defaultValue: 'your custom template here',
        ...options
    });
};
```

### Theme Customization
```css
/* Custom theme colors */
.monaco-editor-container.language-cpp {
    border-color: #your-color;
}
```

## 🚨 Error Handling

The component includes comprehensive error handling:

1. **Monaco Load Failure**: Falls back to textarea
2. **Container Not Found**: Logs warning and gracefully fails
3. **Invalid Configuration**: Uses sensible defaults
4. **Runtime Errors**: Continues operation with reduced functionality

## 📱 Mobile Support

- **Responsive Design**: Adapts to screen size
- **Touch-friendly Resize**: Larger touch targets on mobile
- **Optimized Performance**: Reduced features on mobile devices

## 🔧 Development & Testing

### Testing the Component
```javascript
// Create test editor
const testEditor = new MonacoEditorComponent({
    containerId: 'test-container',
    language: 'cpp',
    onReady: (editor) => {
        console.log('Test editor ready');
        // Run tests
    }
});
```

### Debugging
```javascript
// Enable debug mode
const editor = new MonacoEditorComponent({
    containerId: 'debug-editor',
    onReady: (editor) => {
        // Add debug logging
        editor.onDidChangeModelContent(() => {
            console.log('Content changed:', editor.getValue().length);
        });
    }
});
```

## 🤝 Contributing

To extend the component:

1. Add new presets to `monaco-editor-presets.js`
2. Update CSS for new themes in `monaco-editor-component.css`
3. Test thoroughly across different browsers
4. Update this documentation

## 📄 License

Part of the ShahOJ project. See main project license for details.
