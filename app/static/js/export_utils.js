/**
 * Export Utilities for FinGenius
 * Handles client-side export functionality including chart image export
 */

const FinGeniusExport = {
    /**
     * Export chart as PNG image
     * @param {string} chartId - The ID of the chart canvas element
     * @param {string} filename - The filename to use for the download
     */
    exportChartAsPNG: function(chartId, filename = 'chart.png') {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Chart canvas with ID ${chartId} not found`);
            return;
        }
        
        // Create a link element
        const link = document.createElement('a');
        link.download = filename;
        
        // Convert canvas to data URL
        link.href = canvas.toDataURL('image/png');
        
        // Simulate click to trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },
    
    /**
     * Export projection data to server for PDF/Excel/CSV generation
     * @param {Array} data - The projection data to export
     * @param {string} format - The export format ('pdf', 'excel', 'csv')
     */
    exportProjectionData: function(data, format) {
        // Encode data as URL parameter
        const encodedData = encodeURIComponent(JSON.stringify(data));
        
        // Create URL
        const url = `/export/projection/${format}?data=${encodedData}`;
        
        // Open in new window for PDF, or current window for Excel/CSV
        if (format === 'pdf') {
            window.open(url, '_blank');
        } else {
            window.location.href = url;
        }
    },
    
    /**
     * Set up chart export buttons on the page
     */
    setupChartExportButtons: function() {
        document.querySelectorAll('.export-png').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const chartId = this.getAttribute('data-chart-id');
                const filename = this.getAttribute('data-filename') || 'chart.png';
                FinGeniusExport.exportChartAsPNG(chartId, filename);
            });
        });
    },
    
    /**
     * Set up projection export buttons on the page
     * @param {Function} dataProvider - Function that returns the current projection data
     */
    setupProjectionExportButtons: function(dataProvider) {
        document.querySelectorAll('.export-projection').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const format = this.getAttribute('data-format');
                const data = dataProvider();
                FinGeniusExport.exportProjectionData(data, format);
            });
        });
    }
};

// Initialize export functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    FinGeniusExport.setupChartExportButtons();
});
