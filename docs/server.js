/**
 * IconCreator Website Backend Server (Node.js / Express)
 * Handles template file uploads, static asset serving, and community template API.
 */

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Multer Storage Configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadsDir);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(__dirname));

// Data File Path
const DATA_FILE = path.join(__dirname, 'api', 'templates.json');

function getTemplatesData() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            return [];
        }
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (e) {
        return [];
    }
}

function saveTemplatesData(data) {
    const dir = path.dirname(DATA_FILE);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
}

// GET /api/templates - List all community templates on the server
app.get('/api/templates', (req, res) => {
    const templates = getTemplatesData();
    res.json({ success: true, templates: templates });
});

// POST /api/templates/upload - Handle template bundle upload to website server
app.post('/api/templates/upload', upload.fields([
    { name: 'previewFile', maxCount: 1 },
    { name: 'bundleFile', maxCount: 1 }
]), (req, res) => {
    try {
        const { title, author, description } = req.body;

        if (!title) {
            return res.status(400).json({ success: false, message: 'Template title is required.' });
        }

        const previewFile = req.files['previewFile'] ? req.files['previewFile'][0] : null;
        const bundleFile = req.files['bundleFile'] ? req.files['bundleFile'][0] : null;

        const previewUrl = previewFile ? `uploads/${previewFile.filename}` : 'assets/iconcreator.png';
        const bundleUrl = bundleFile ? `uploads/${bundleFile.filename}` : 'assets/iconcreator.icontemplate';
        const bundleFilename = bundleFile ? bundleFile.originalname : `${title.toLowerCase().replace(/\s+/g, '_')}.icontemplate`;
        const size = bundleFile ? Math.round(bundleFile.size / 1024) + ' KB' : 'Custom Bundle';

        const newTemplate = {
            id: 'server_tpl_' + Date.now(),
            title: title,
            author: author || 'Community Contributor',
            description: description || 'Custom .icontemplate bundle submitted to website server.',
            previewUrl: previewUrl,
            bundleUrl: bundleUrl,
            bundleFilename: bundleFilename,
            size: size,
            isFeatured: false,
            createdAt: new Date().toISOString()
        };

        const templates = getTemplatesData();
        templates.unshift(newTemplate); // Add to top
        saveTemplatesData(templates);

        console.log(`[Server] New template uploaded to website: ${title}`);

        return res.json({
            success: true,
            message: 'Template uploaded successfully to the server!',
            template: newTemplate
        });
    } catch (error) {
        console.error('[Server Upload Error]:', error);
        return res.status(500).json({ success: false, message: 'Server upload error: ' + error.message });
    }
});

// Start Server
app.listen(PORT, () => {
    console.log(`IconCreator Website Server running on http://localhost:${PORT}`);
});
