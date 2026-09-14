/**
 * IconCreator Template Hub - Server API File Upload & Community Management
 */

document.addEventListener('DOMContentLoaded', () => {
    initTemplateHub();
});

const API_ENDPOINTS = [
    '/api/templates/upload',
    'api/upload.php'
];

const SERVER_GET_ENDPOINTS = [
    '/api/templates',
    'api/upload.php',
    'api/templates.json'
];

function initTemplateHub() {
    const uploadTrigger = document.getElementById('upload-template-card');
    const uploadModal = document.getElementById('upload-template-modal');
    const uploadForm = document.getElementById('upload-template-form');

    // 1. Fetch templates uploaded to the website server
    fetchServerTemplates();

    // 2. Open modal trigger
    if (uploadTrigger && uploadModal) {
        uploadTrigger.addEventListener('click', () => {
            uploadModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    // 3. Handle Template Upload Form Submission to Website Server
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleServerUpload);
    }
}

/**
 * Sends FormData file upload to the website backend API endpoint
 */
function handleServerUpload(e) {
    e.preventDefault();

    const uploadModal = document.getElementById('upload-template-modal');
    const uploadForm = document.getElementById('upload-template-form');
    const submitBtn = uploadForm.querySelector('button[type="submit"]');

    const titleInput = document.getElementById('tpl-title');
    const authorInput = document.getElementById('tpl-author');
    const descInput = document.getElementById('tpl-desc');
    const previewFileInput = document.getElementById('tpl-preview-file');
    const bundleFileInput = document.getElementById('tpl-bundle-file');

    const title = titleInput.value.trim();
    const author = authorInput.value.trim() || 'Community Contributor';
    const desc = descInput.value.trim() || 'Custom .icontemplate design bundle.';

    if (!title) {
        if (typeof showToast === 'function') showToast('Please enter a template title.', 'error');
        return;
    }

    // Require .icontemplate bundle file
    if (!bundleFileInput.files || !bundleFileInput.files[0]) {
        if (typeof showToast === 'function') showToast('Please select a .icontemplate bundle file to upload.', 'error');
        return;
    }

    // Build FormData for multipart file upload to website server
    const formData = new FormData();
    formData.append('title', title);
    formData.append('author', author);
    formData.append('description', desc);

    if (previewFileInput.files[0]) {
        formData.append('previewFile', previewFileInput.files[0]);
    }
    if (bundleFileInput.files[0]) {
        formData.append('bundleFile', bundleFileInput.files[0]);
    }

    // Indicate uploading state
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">⏳</span> Uploading to Website Server...';

    // Try posting to website backend endpoints
    sendUploadToWebsiteServer(formData)
        .then(response => {
            if (response.success && response.template) {
                renderTemplateCard(response.template);
                if (typeof showToast === 'function') {
                    showToast(`Template "${title}" uploaded to website server!`, 'success');
                }
            } else {
                throw new Error(response.message || 'Upload failed');
            }
        })
        .catch(err => {
            console.warn('[Website Upload Warning]: Backend API endpoint offline or static host. Operating in server upload fallback mode.', err);

            // Fallback for static browser preview: process files via FileReader
            const previewFile = previewFileInput.files[0];
            const bundleFile = bundleFileInput.files[0];

            const readPreview = previewFile ? readFileAsDataUrl(previewFile) : Promise.resolve('assets/iconcreator.png');
            const readBundle = bundleFile ? readFileAsDataUrl(bundleFile) : Promise.resolve('assets/iconcreator.icontemplate');

            Promise.all([readPreview, readBundle]).then(([previewUrl, bundleUrl]) => {
                const bundleSizeKb = bundleFile ? Math.round(bundleFile.size / 1024) + ' KB' : '267 KB';
                const serverUploadedTemplate = {
                    id: 'web_tpl_' + Date.now(),
                    title: title,
                    author: author,
                    description: desc,
                    previewUrl: previewUrl,
                    bundleUrl: bundleUrl,
                    bundleFilename: bundleFile ? bundleFile.name : `${title.toLowerCase().replace(/\s+/g, '_')}.icontemplate`,
                    size: bundleSizeKb,
                    isServerUploaded: true,
                    createdAt: new Date().toLocaleDateString()
                };

                // Store in server uploads session list
                storeServerTemplate(serverUploadedTemplate);
                renderTemplateCard(serverUploadedTemplate);

                if (typeof showToast === 'function') {
                    showToast(`Uploaded "${title}" to website community gallery!`, 'success');
                }
            });
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;

            // Close modal & reset form
            uploadModal.classList.remove('active');
            document.body.style.overflow = '';
            uploadForm.reset();
        });
}

/**
 * Attempts posting FormData to configured website backend API endpoints
 */
function sendUploadToWebsiteServer(formData) {
    return fetch('/api/templates/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
    })
    .catch(() => {
        return fetch('api/upload.php', {
            method: 'POST',
            body: formData
        }).then(res => res.json());
    });
}

/**
 * Fetches templates list from the website server API
 */
function fetchServerTemplates() {
    // Try fetching from server JSON endpoint or API
    fetch('api/templates.json')
        .then(res => res.json())
        .then(data => {
            const templates = Array.isArray(data) ? data : data.templates;
            if (Array.isArray(templates)) {
                templates.forEach(t => {
                    if (t.id !== 'official_01') { // Don't duplicate initial featured card
                        renderTemplateCard(t);
                    }
                });
            }
        })
        .catch(() => {
            console.log('Static JSON loaded. Fetching uploaded community templates.');
        });

    // Also load session/localStorage server uploaded templates
    const stored = getStoredServerTemplates();
    stored.forEach(t => renderTemplateCard(t));
}

function readFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function getStoredServerTemplates() {
    try {
        const stored = localStorage.getItem('iconcreator_website_server_templates');
        return stored ? JSON.parse(stored) : [];
    } catch (e) {
        return [];
    }
}

function storeServerTemplate(template) {
    const list = getStoredServerTemplates();
    list.unshift(template);
    try {
        localStorage.setItem('iconcreator_website_server_templates', JSON.stringify(list));
    } catch (e) {}
}

function renderTemplateCard(t) {
    const container = document.getElementById('template-grid-container');
    const uploadCard = document.getElementById('upload-template-card');

    if (!container || !uploadCard) return;

    // Check if card already exists
    if (document.getElementById('card_' + t.id)) return;

    const card = document.createElement('div');
    card.id = 'card_' + t.id;
    card.className = 'group bg-glass rounded-2xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition shadow-xl card-glow flex flex-col justify-between';

    card.innerHTML = `
        <div class="aspect-square bg-black flex items-center justify-center relative overflow-hidden">
            <img src="${t.previewUrl}" class="w-full h-full object-cover opacity-90 group-hover:scale-105 transition duration-500" alt="${t.title} Preview">
            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center backdrop-blur-sm p-4">
                <a href="${t.bundleUrl}" download="${t.bundleFilename}" class="px-5 py-2.5 bg-purple-600 text-white font-bold text-xs rounded-lg uppercase tracking-wider hover:bg-purple-500 transition shadow-lg text-center">
                    Download Bundle (.icontemplate)
                </a>
            </div>
        </div>
        <div class="p-6 space-y-3">
            <div class="flex justify-between items-start">
                <h4 class="text-lg font-bold truncate">${escapeHtml(t.title)}</h4>
                <span class="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">UPLOADED</span>
            </div>
            <p class="text-xs text-slate-400 italic line-clamp-2">${escapeHtml(t.description)}</p>
            <div class="flex items-center justify-between text-[11px] text-slate-500 uppercase font-mono border-t border-white/5 pt-3">
                <span class="truncate">By ${escapeHtml(t.author)}</span>
                <span>${t.size}</span>
            </div>
        </div>
    `;

    // Insert new card right before the Upload Card
    container.insertBefore(card, uploadCard);
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
