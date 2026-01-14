const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generatePDF() {
    const htmlPath = path.join(__dirname, 'COMPREHENSIVE_TEST_ANALYSIS.html');
    const pdfPath = path.join(__dirname, 'COMPREHENSIVE_TEST_ANALYSIS.pdf');
    
    const logger = require('./scripts/logger-node');
    logger.info('🚀 Starting PDF generation...');
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Load the HTML file
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
    
    // Generate PDF
    await page.pdf({
        path: pdfPath,
        format: 'Letter',
        margin: {
            top: '0.75in',
            right: '0.75in',
            bottom: '0.75in',
            left: '0.75in'
        },
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 10px; text-align: center; width: 100%; color: #666;">Verity Systems - Comprehensive Test Analysis Report</div>',
        footerTemplate: '<div style="font-size: 10px; text-align: center; width: 100%; color: #666;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
    });
    
    await browser.close();
    
    const stats = fs.statSync(pdfPath);
    logger.info('✅ PDF created successfully!');
    logger.info('📄 File:', pdfPath);
    logger.info('📊 Size:', `${(stats.size / 1024).toFixed(1)} KB`);
}

generatePDF().catch(err => {
    console.error('Error generating PDF:', err);
    process.exit(1);
});
