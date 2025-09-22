/**
 * Shared Submission Modal Component for PocketOJ
 * Used in both My Submissions page and Problem Detail page
 */

class SubmissionModal {
    static show(submissionId) {
        console.log('SubmissionModal.show called with ID:', submissionId);
        
        fetch(`/api/submissions/${submissionId}`)
            .then(response => {
                console.log('API response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('API response data:', data);
                if (data.success) {
                    this.render(data.submission);
                } else {
                    console.error('API returned error:', data.error);
                    alert('Failed to load submission: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading submission:', error);
                alert('Network error loading submission: ' + error.message);
            });
    }

    static render(submission) {
        console.log('SubmissionModal.render called with submission:', submission);
        
        // Remove existing modal if present
        const existingModal = document.getElementById('sharedSubmissionModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'sharedSubmissionModal';
        modal.innerHTML = this.getModalHTML(submission);
        
        console.log('Modal HTML created, appending to body');
        document.body.appendChild(modal);
        
        // Render content
        console.log('Rendering modal content');
        this.renderContent(submission);
        
        // Show modal
        console.log('Showing Bootstrap modal');
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up on hide
        modal.addEventListener('hidden.bs.modal', () => {
            console.log('Modal hidden, cleaning up');
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        });
    }

    static getModalHTML(submission) {
        const verdict = (submission.verdict || submission.status || '').toUpperCase();
        return `
            <div class="modal-dialog modal-xl">
                <div class="modal-content submission-modal-content">
                    <div class="modal-header submission-modal-header">
                        <h5 class="modal-title submission-modal-title">
                            <i class="fas fa-code me-2"></i>Submission 
                            <span class="chip chip-${verdict} ms-2">${verdict || '—'}</span>
                        </h5>
                        <button type="button" class="btn-close submission-modal-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body submission-modal-body">
                        <div id="shared-submission-details"></div>
                    </div>
                </div>
            </div>
        `;
    }

    static renderContent(sub) {
        const containerId = 'shared-submission-details';
        
        function escapeHtml(str) {
            if (str === null || str === undefined) return '';
            return String(str).replace(/[&<>"']/g, s => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[s]));
        }

        function normalizeTimestamp(ts) {
            if (!ts) return '';
            let value = String(ts).trim();
            if (!value) return '';
            if (value.includes(' ')) {
                value = value.replace(' ', 'T');
            }
            if (!/[zZ]|[+-]\d{2}:\d{2}$/.test(value)) {
                value = `${value}Z`;
            }
            return value;
        }

        function formatTime(ts) {
            const normalized = normalizeTimestamp(ts);
            if (!normalized) return '';
            try {
                const date = new Date(normalized);
                return date.toLocaleString('en-IN', {
                    timeZone: 'Asia/Kolkata',
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                });
            } catch (e) {
                return ts;
            }
        }

        let summary = null;
        try { 
            if (sub.result_summary_json) {
                summary = JSON.parse(sub.result_summary_json); 
            }
        } catch(e) {
            console.warn('Failed to parse result summary JSON:', e);
            // Try to extract basic stats from corrupted JSON if possible
            if (sub.result_summary_json && sub.result_summary_json.includes('"statistics"')) {
                try {
                    const match = sub.result_summary_json.match(/"statistics":\s*{[^}]*"total_tests":\s*(\d+)[^}]*"passed":\s*(\d+)[^}]*"failed":\s*(\d+)[^}]*"total_time_ms":\s*([\d.]+)/);
                    if (match) {
                        summary = {
                            statistics: {
                                total_tests: parseInt(match[1]),
                                passed: parseInt(match[2]),
                                failed: parseInt(match[3]),
                                total_time_ms: parseFloat(match[4])
                            }
                        };
                    }
                } catch(e2) {
                    // If even regex parsing fails, continue without summary
                }
            }
        }

        const meta = `
            <div class="submission-meta-grid">
                <div class="submission-meta-card">
                    <div class="submission-meta-label">
                        <i class="fas fa-puzzle-piece me-1"></i>Problem
                    </div>
                    <div class="submission-meta-value">
                        <a href="/problem/${escapeHtml(sub.problem_slug)}">${escapeHtml(sub.problem_slug)}</a>
                    </div>
                </div>
                <div class="submission-meta-card">
                    <div class="submission-meta-label">
                        <i class="fas fa-code me-1"></i>Language
                    </div>
                    <div class="submission-meta-value">
                        ${escapeHtml((sub.language||'').toUpperCase())}
                    </div>
                </div>
                <div class="submission-meta-card">
                    <div class="submission-meta-label">
                        <i class="fas fa-clock me-1"></i>Submitted
                    </div>
                    <div class="submission-meta-value">
                        ${formatTime(sub.created_at_ist || sub.created_at)}
                    </div>
                </div>
                <div class="submission-meta-card">
                    <div class="submission-meta-label">
                        <i class="fas fa-stopwatch me-1"></i>Exec Time
                    </div>
                    <div class="submission-meta-value">
                        ${sub.time_ms ?? '—'} ms
                    </div>
                </div>
                <div class="submission-meta-card">
                    <div class="submission-meta-label">
                        <i class="fas fa-hammer me-1"></i>Compile Time
                    </div>
                    <div class="submission-meta-value">
                        ${sub.compile_time_ms ?? '—'} ms
                    </div>
                </div>
            </div>`;

        const codeBlock = `
            <div class="submission-section-header">
                <h6><i class="fas fa-file-code me-2 text-primary"></i>Source Code</h6>
                <button class="btn btn-sm submission-btn-copy" onclick="SubmissionModal.copyWithFeedback(this, \`${escapeHtml(sub.source_code || '').replace(/`/g, '\\`')}\`)">
                    <i class="fas fa-copy me-1"></i>Copy Code
                </button>
            </div>
            <pre class="submission-code-block"><code>${escapeHtml(sub.source_code || '')}</code></pre>`;

        let compileOut = '';
        if (sub.compile_output) {
            compileOut = `
                <div class="submission-section-header">
                    <h6><i class="fas fa-terminal me-2 text-warning"></i>Compilation Output</h6>
                    <button class="btn btn-sm submission-btn-copy" onclick="SubmissionModal.copyWithFeedback(this, \`${escapeHtml(sub.compile_output || '').replace(/`/g, '\\`')}\`)">
                        <i class="fas fa-copy me-1"></i>Copy Output
                    </button>
                </div>
                <pre class="submission-code-block"><code>${escapeHtml(sub.compile_output)}</code></pre>`;
        }

        let runtimeErr = '';
        if (sub.runtime_stderr) {
            runtimeErr = `
                <div class="submission-section-header">
                    <h6><i class="fas fa-bug me-2 text-danger"></i>Runtime Error</h6>
                    <button class="btn btn-sm submission-btn-copy" onclick="SubmissionModal.copyWithFeedback(this, \`${escapeHtml(sub.runtime_stderr || '').replace(/`/g, '\\`')}\`)">
                        <i class="fas fa-copy me-1"></i>Copy Error
                    </button>
                </div>
                <pre class="submission-code-block"><code>${escapeHtml(sub.runtime_stderr)}</code></pre>`;
        }

        let summaryHtml = '';
        if (summary && summary.statistics) {
            const s = summary.statistics;
            
            summaryHtml = `
                <div class="submission-section-header">
                    <h6><i class="fas fa-chart-line me-2 text-info"></i>Results Summary</h6>
                </div>
                <div class="submission-meta-grid">
                    <div class="submission-meta-card">
                        <div class="submission-meta-label"><i class="fas fa-list-ol me-1"></i>Total Tests</div>
                        <div class="submission-meta-value">${s.total_tests}</div>
                    </div>
                    <div class="submission-meta-card">
                        <div class="submission-meta-label"><i class="fas fa-check-circle me-1"></i>Passed</div>
                        <div class="submission-meta-value text-success">${s.passed}</div>
                    </div>
                    <div class="submission-meta-card">
                        <div class="submission-meta-label"><i class="fas fa-times-circle me-1"></i>Failed</div>
                        <div class="submission-meta-value text-danger">${s.failed}</div>
                    </div>
                    <div class="submission-meta-card">
                        <div class="submission-meta-label"><i class="fas fa-stopwatch me-1"></i>Total Time</div>
                        <div class="submission-meta-value">${s.total_time_ms} ms</div>
                    </div>
                </div>
            `;
            
            // Show ALL test results by category
            if (summary.test_results_summary) {
                Object.keys(summary.test_results_summary).forEach(category => {
                    const tests = summary.test_results_summary[category];
                    if (tests && tests.length > 0) {
                        const categoryStats = summary.categories[category] || {};
                        const categoryClass = categoryStats.failed === 0 ? 'success' : 'danger';
                        
                        summaryHtml += `
                            <div class="mt-3">
                                <div class="submission-section-header">
                                    <h6><i class="fas fa-vial me-2 text-${categoryClass === 'success' ? 'success' : 'danger'}"></i>${category.charAt(0).toUpperCase() + category.slice(1)} Tests (${categoryStats.passed || 0}/${categoryStats.count || tests.length} passed)</h6>
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th><i class="fas fa-hashtag me-1"></i>Test</th>
                                                <th><i class="fas fa-gavel me-1"></i>Verdict</th>
                                                <th><i class="fas fa-clock me-1"></i>Time (ms)</th>
                                                <th><i class="fas fa-memory me-1"></i>Memory (KB)</th>
                                                ${tests.some(t => t.details) ? '<th><i class="fas fa-info-circle me-1"></i>Details</th>' : ''}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${tests.map(test => {
                                                const verdict = test.verdict || '—';
                                                const verdictClass = verdict === 'AC' ? 'success' : 
                                                                   verdict === 'WA' ? 'danger' : 
                                                                   verdict === 'TLE' ? 'warning' : 'secondary';
                                                return `<tr class="${verdict === 'AC' ? 'table-success' : verdict === 'WA' ? 'table-danger' : verdict === 'TLE' ? 'table-warning' : ''}">
                                                    <td><strong>${String(test.test_num || '').padStart(2, '0')}</strong></td>
                                                    <td><span class="badge bg-${verdictClass} ${verdict === 'TLE' ? 'text-dark' : ''}">${verdict}</span></td>
                                                    <td>${(test.time_ms || 0).toFixed(1)}ms</td>
                                                    <td>${test.memory_kb || '—'}</td>
                                                    ${test.details ? `<td><small class="text-muted">${escapeHtml(test.details)}</small></td>` : tests.some(t => t.details) ? '<td>—</td>' : ''}
                                                </tr>`;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    }
                });
            }
        }

        document.getElementById(containerId).innerHTML = meta + codeBlock + compileOut + runtimeErr + summaryHtml;
    }

    static copyWithFeedback(button, text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text || '').then(() => {
                // Store original content
                const originalHtml = button.innerHTML;
                
                // Show success feedback
                button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                button.style.background = '#28a745';
                button.style.borderColor = '#28a745';
                button.style.color = 'white';
                
                // Restore original after 1 second
                setTimeout(() => {
                    button.innerHTML = originalHtml;
                    button.style.background = '';
                    button.style.borderColor = '';
                    button.style.color = '';
                }, 1000);
            }).catch(err => {
                console.error('Failed to copy:', err);
                // Show error feedback
                const originalHtml = button.innerHTML;
                button.innerHTML = '<i class="fas fa-times me-1"></i>Failed';
                button.style.background = '#dc3545';
                button.style.borderColor = '#dc3545';
                button.style.color = 'white';
                
                setTimeout(() => {
                    button.innerHTML = originalHtml;
                    button.style.background = '';
                    button.style.borderColor = '';
                    button.style.color = '';
                }, 1000);
            });
        }
    }
}

// Export for global use
window.SubmissionModal = SubmissionModal;

// Debug: Confirm export
console.log('SubmissionModal exported to window:', typeof window.SubmissionModal);

// Fallback function for direct calls
window.showSubmissionModal = function(submissionId) {
    console.log('showSubmissionModal fallback called with ID:', submissionId);
    if (window.SubmissionModal) {
        window.SubmissionModal.show(submissionId);
    } else {
        console.error('SubmissionModal not available');
        alert('Modal component not loaded. Please refresh the page.');
    }
};
