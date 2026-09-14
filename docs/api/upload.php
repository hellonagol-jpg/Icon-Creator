<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$uploadsDir = __DIR__ . '/../uploads/';
if (!file_exists($uploadsDir)) {
    mkdir($uploadsDir, 0777, true);
}

$jsonFile = __DIR__ . '/templates.json';

function getTemplates() {
    global $jsonFile;
    if (!file_exists($jsonFile)) return [];
    $content = file_get_contents($jsonFile);
    return json_decode($content, true) ?: [];
}

function saveTemplates($data) {
    global $jsonFile;
    file_put_contents($jsonFile, json_encode($data, JSON_PRETTY_PRINT));
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    echo json_encode(['success' => true, 'templates' => getTemplates()]);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = isset($_POST['title']) ? trim($_POST['title']) : '';
    $author = isset($_POST['author']) ? trim($_POST['author']) : 'Community Contributor';
    $desc = isset($_POST['description']) ? trim($_POST['description']) : '';

    if (empty($title)) {
        echo json_encode(['success' => false, 'message' => 'Template title is required.']);
        exit();
    }

    $previewUrl = 'assets/iconcreator.png';
    $bundleUrl = 'assets/iconcreator.icontemplate';
    $bundleFilename = strtolower(str_replace(' ', '_', $title)) . '.icontemplate';
    $size = 'Custom Bundle';

    // Handle Preview Image Upload
    if (isset($_FILES['previewFile']) && $_FILES['previewFile']['error'] === UPLOAD_ERR_OK) {
        $ext = pathinfo($_FILES['previewFile']['name'], PATHINFO_EXTENSION);
        $filename = 'preview_' . time() . '_' . rand(1000, 9999) . '.' . $ext;
        if (move_uploaded_file($_FILES['previewFile']['tmp_name'], $uploadsDir . $filename)) {
            $previewUrl = 'uploads/' . $filename;
        }
    }

    // Handle .icontemplate File Upload
    if (isset($_FILES['bundleFile']) && $_FILES['bundleFile']['error'] === UPLOAD_ERR_OK) {
        $bundleFilename = $_FILES['bundleFile']['name'];
        $ext = pathinfo($bundleFilename, PATHINFO_EXTENSION);
        $filename = 'bundle_' . time() . '_' . rand(1000, 9999) . '.' . $ext;
        if (move_uploaded_file($_FILES['bundleFile']['tmp_name'], $uploadsDir . $filename)) {
            $bundleUrl = 'uploads/' . $filename;
            $size = round($_FILES['bundleFile']['size'] / 1024) . ' KB';
        }
    }

    $newTemplate = [
        'id' => 'php_tpl_' . time(),
        'title' => $title,
        'author' => $author,
        'description' => $desc,
        'previewUrl' => $previewUrl,
        'bundleUrl' => $bundleUrl,
        'bundleFilename' => $bundleFilename,
        'size' => $size,
        'isFeatured' => false,
        'createdAt' => date('Y-m-d H:i:s')
    ];

    $templates = getTemplates();
    array_unshift($templates, $newTemplate);
    saveTemplates($templates);

    echo json_encode([
        'success' => true,
        'message' => 'Template uploaded successfully to the server!',
        'template' => $newTemplate
    ]);
    exit();
}
?>
