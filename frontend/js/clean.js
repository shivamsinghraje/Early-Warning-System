document.addEventListener('DOMContentLoaded', () => {
    const cleanDataForm = document.getElementById('cleanDataForm');
    const dataFileInput = document.getElementById('dataFile');
    const previewBtn = document.getElementById('previewBtn');
    const resultsSection = document.getElementById('resultsSection');

    let selectedFile = null;
    let cleanedDataUrl = null;

    // Handle file selection
    dataFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            validateFile(file);
            selectedFile = file;
            previewBtn.disabled = false;

            // Read file headers
            await readFileHeaders(file);
        } catch (error) {
            showNotification(error.message, 'error');
            e.target.value = '';
        }
    });

    // Read file headers for column selection
    async function readFileHeaders(file) {
        const reader = new FileReader();

        reader.onload = (e) => {
            const content = e.target.result;
            const lines = content.split('\n');
            const headers = lines[0].split(',').map(h => h.trim());

            // Populate column selectors
            populateColumnSelectors(headers);
        };

        reader.readAsText(file.slice(0, 1024)); // Read first 1KB
    }

    function populateColumnSelectors(headers) {
        const datetimeSelect = document.getElementById('datetimeCol');
        const targetSelect = document.getElementById('targetCol');
        const gndColsContainer = document.getElementById('gndColsContainer');

        // Clear existing options
        datetimeSelect.innerHTML = '<option value="">Select column</option>';
        targetSelect.innerHTML = '<option value="">Select column</option>';
        gndColsContainer.innerHTML = '';

        headers.forEach(header => {
            // Add to datetime and target selectors
            datetimeSelect.innerHTML += `<option value="${header}">${header}</option>`;
            targetSelect.innerHTML += `<option value="${header}">${header}</option>`;

            // Add to ground truth checkboxes
            const checkbox = document.createElement('label');
            checkbox.className = 'checkbox-label';
            checkbox.innerHTML = `
                <input type="checkbox" name="gndCols" value="${header}">
                ${header}
            `;
            gndColsContainer.appendChild(checkbox);
        });
    }

    // Handle form submission
    cleanDataForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!selectedFile) {
            showNotification('Please select a file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        // Get form values
        const projectData = {
            projectName: document.getElementById('projectName').value,
            projectId: document.getElementById('projectId').value,
            datetimeCol: document.getElementById('datetimeCol').value,
            targetCol: document.getElementById('targetCol').value,
            gndCols: Array.from(document.querySelectorAll('input[name="gndCols"]:checked'))
                          .map(cb => cb.value)
        };

        if (projectData.gndCols.length === 0) {
            showNotification('Please select at least one ground truth column', 'error');
            return;
        }

        formData.append('data', JSON.stringify(projectData));

        try {
            showNotification('Cleaning data...', 'info');

            const result = await api.cleanData(formData);

            showNotification('Data cleaned successfully', 'success');
            displayResults(result);

        } catch (error) {
            showNotification(error.message, 'error');
        }
    });

    // Display cleaning results
    function displayResults(result) {
        resultsSection.style.display = 'block';

        // Display cleaning report
        const reportDiv = document.getElementById('cleaningReport');
        reportDiv.innerHTML = `
            <p><strong>Original Rows:</strong> ${result.cleaning_report.original_rows}</p>
            <p><strong>Final Rows:</strong> ${result.final_rows}</p>
            <h5>Cleaning Steps:</h5>
            <ul>
                ${result.cleaning_report.steps.map(step =>
                    `<li>${step.step}: ${step.rows_after} rows</li>`
                ).join('')}
            </ul>
        `;

        // Display statistics
        const statsDiv = document.getElementById('dataStatistics');
        statsDiv.innerHTML = `
            <p><strong>Mean:</strong> ${formatNumber(result.statistics.mean)}</p>
            <p><strong>Std Dev:</strong> ${formatNumber(result.statistics.std)}</p>
            <p><strong>Min:</strong> ${formatNumber(result.statistics.min)}</p>
            <p><strong>Max:</strong> ${formatNumber(result.statistics.max)}</p>
        `;

        // Create comparison plot
        createComparisonPlot(result);

        // Setup download button
        cleanedDataUrl = result.download_url;
        document.getElementById('downloadBtn').onclick = () => {
            window.location.href = cleanedDataUrl;
        };
    }

    function createComparisonPlot(result) {
        // This would create a before/after comparison plot
        // For now, showing a placeholder
        const plotDiv = document.getElementById('comparisonPlot');

        const data = [{
            x: ['Original', 'Cleaned'],
            y: [result.cleaning_report.original_rows, result.final_rows],
            type: 'bar',
            marker: {
                color: ['#64748b', '#2563eb']
            }
        }];

        const layout = {
            title: 'Data Cleaning Results',
            xaxis: { title: 'Dataset' },
            yaxis: { title: 'Number of Rows' }
        };

        Plotly.newPlot(plotDiv, data, layout);
    }
});