package com.iconcreator.ui

import android.graphics.Bitmap
import android.app.DownloadManager
import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.iconcreator.model.IconSettings
import com.iconcreator.ui.theme.IconCreatorTheme
import com.iconcreator.viewmodel.IconViewModel
import com.iconcreator.viewmodel.IconUiState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun IconCreatorScreen(
    viewModel: IconViewModel,
    uiState: IconUiState,
    previewBitmap: Bitmap?
) {
    val context = LocalContext.current
    
    // Auto-open saved folder
    androidx.compose.runtime.LaunchedEffect(uiState.lastSavedUri) {
        uiState.lastSavedUri?.let { uriString ->
            val isIco = uriString.endsWith(".ico", ignoreCase = true)
            val subFolder = if (isIco) "%2Fico" else ""
            val folderPath = "primary%3ADownload%2FIconCreator$subFolder"
            
            try {
                // Try to open the specific folder in Downloads
                val folderUri = Uri.parse("content://com.android.externalstorage.documents/document/$folderPath")
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    setDataAndType(folderUri, "vnd.android.document/directory")
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }
                context.startActivity(intent)
            } catch (e: Exception) {
                // Fallback 1: Open the general downloads folder
                try {
                    val intent = Intent(DownloadManager.ACTION_VIEW_DOWNLOADS).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                    context.startActivity(intent)
                } catch (_: Exception) {
                    // Fallback 2: Open the file itself
                    try {
                        val intent = Intent(Intent.ACTION_VIEW).apply {
                            data = Uri.parse(uriString)
                            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        }
                        context.startActivity(intent)
                    } catch (_2: Exception) {
                        viewModel.updateUiState { 
                            errorMessage = if (isIco) "Saved to Downloads/IconCreator/ico" else "Saved to Downloads/IconCreator" 
                        }
                    }
                }
            }
            viewModel.clearLastSavedUri()
        }
    }

    if (uiState.isLoading) {
        LoadingScreen(uiState.loadingProgress)
        return
    }

    val settings by viewModel.settings.collectAsState()
    
    Scaffold(
        modifier = Modifier.fillMaxSize()
    ) { paddingValues ->
        val mainBackground by viewModel.mainBackground.collectAsState()
        
        Box(modifier = Modifier.fillMaxSize()) {
            // App Background Image
            mainBackground?.let {
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = androidx.compose.ui.layout.ContentScale.Crop
                )
            } ?: Box(modifier = Modifier.fillMaxSize().background(Color(0xFF1A1A1A)))

            BoxWithConstraints(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                val isWide = maxWidth > 600.dp
                
                if (isWide) {
                    Row(modifier = Modifier.fillMaxSize()) {
                        // Left panel - Preview and main actions
                        Column(
                            modifier = Modifier
                                .weight(0.8f)
                                .fillMaxHeight()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            PreviewBox(previewBitmap = previewBitmap)
                            Spacer(modifier = Modifier.height(16.dp))
                            ActionButtons(viewModel)
                        }
                        
                        // Vertical Separator
                        val borderX by viewModel.borderX.collectAsState()
                        RepeatingBorder(
                            bitmap = borderX,
                            isVertical = true,
                            modifier = Modifier.fillMaxHeight().width(24.dp)
                        )

                        // Right panel - Settings (scrollable)
                        RightPanel(
                            viewModel = viewModel,
                            settings = settings,
                            modifier = Modifier.weight(1.2f),
                            isScrollable = true
                        )
                    }
                } else {
                    Column(modifier = Modifier.fillMaxSize()) {
                        // Sticky Preview at the top
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(Color(0xFF1A1A1A).copy(alpha = 0.5f))
                                .padding(16.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            PreviewBox(
                                previewBitmap = previewBitmap,
                                modifier = Modifier.fillMaxWidth(0.7f) // Slightly smaller on mobile to leave room
                            )
                        }
                        
                        // Horizontal Separator
                        val borderX by viewModel.borderX.collectAsState()
                        RepeatingBorder(
                            bitmap = borderX,
                            isVertical = false,
                            modifier = Modifier.fillMaxWidth().height(24.dp)
                        )

                        // Scrollable content (Actions and Settings)
                        Column(
                            modifier = Modifier
                                .weight(1f)
                                .verticalScroll(rememberScrollState())
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            ActionButtons(viewModel)
                            
                            RightPanel(
                                viewModel = viewModel,
                                settings = settings,
                                modifier = Modifier.fillMaxWidth(),
                                isScrollable = false
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun PreviewBox(
    previewBitmap: Bitmap?,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .aspectRatio(1f)
            .fillMaxWidth(),
        contentAlignment = Alignment.Center
    ) {
        previewBitmap?.let { bitmap ->
            AndroidView(
                factory = { context ->
                    android.widget.ImageView(context).apply {
                        setImageBitmap(bitmap)
                        scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
                        // Ensure no padding/background in the view itself
                        setPadding(0, 0, 0, 0)
                        setBackgroundColor(android.graphics.Color.TRANSPARENT)
                    }
                },
                update = { imageView ->
                    imageView.setImageBitmap(bitmap)
                },
                modifier = Modifier.fillMaxSize()
            )
        } ?: Text(
            "No Preview",
            color = Color.Gray
        )
    }
}

@Composable
fun ActionButtons(viewModel: IconViewModel) {
    val imagePicker = rememberImagePicker(viewModel)
    var showSaveDialog by remember { androidx.compose.runtime.mutableStateOf(false) }
    var showTemplateDialog by remember { androidx.compose.runtime.mutableStateOf(false) }
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // 2x2 Grid for main actions
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = imagePicker,
                modifier = Modifier.weight(1f).height(40.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3498DB)),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)
            ) {
                Text("Upload", style = MaterialTheme.typography.bodySmall)
            }
            
            Button(
                onClick = { showSaveDialog = true },
                modifier = Modifier.weight(1f).height(40.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2ECC71)),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)
            ) {
                Text("Save", style = MaterialTheme.typography.bodySmall)
            }
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = { showTemplateDialog = true },
                modifier = Modifier.weight(1f).height(40.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3498DB)),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)
            ) {
                Text("Templates", style = MaterialTheme.typography.bodySmall)
            }
            
            Button(
                onClick = { viewModel.resetToDefault() },
                modifier = Modifier.weight(1f).height(40.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE74C3C)),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)
            ) {
                Text("Reset", style = MaterialTheme.typography.bodySmall)
            }
        }
        
        // Randomize at the bottom, same size (half-width to match grid)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center
        ) {
            Button(
                onClick = { viewModel.randomizeSettings() },
                modifier = Modifier.fillMaxWidth(0.5f).height(40.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF69B4)),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)
            ) {
                Text("Randomize", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
    
    if (showSaveDialog) {
        SaveDialog(
            onSavePNG = { 
                viewModel.saveAsPNG()
                showSaveDialog = false
            },
            onSaveICO = { 
                viewModel.saveAsICO()
                showSaveDialog = false
            },
            onDismiss = { showSaveDialog = false }
        )
    }
    
    if (showTemplateDialog) {
        TemplateDialog(
            viewModel = viewModel,
            onDismiss = { showTemplateDialog = false }
        )
    }
}

@Composable
fun SaveDialog(
    onSavePNG: () -> Unit,
    onSaveICO: () -> Unit,
    onDismiss: () -> Unit
) {
    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Save Icon") },
        text = { 
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Choose save format:")
                Button(
                    onClick = onSavePNG,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Save as PNG")
                }
                Button(
                    onClick = onSaveICO,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Save as ICO (Windows Icon)")
                }
            }
        },
        confirmButton = {
            Button(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@Composable
fun TemplateDialog(
    viewModel: IconViewModel,
    onDismiss: () -> Unit
) {
    val templates by viewModel.templates.collectAsState()
    var showSaveTemplate by androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(false) }
    var newTemplateName by androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf("") }
    
    if (showSaveTemplate) {
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { showSaveTemplate = false },
            title = { Text("Save Template") },
            text = {
                androidx.compose.material3.OutlinedTextField(
                    value = newTemplateName,
                    onValueChange = { newTemplateName = it },
                    label = { Text("Template Name") },
                    singleLine = true
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (newTemplateName.isNotBlank()) {
                            viewModel.saveTemplate(newTemplateName)
                            newTemplateName = ""
                            showSaveTemplate = false
                        }
                    }
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                Button(onClick = { showSaveTemplate = false }) {
                    Text("Cancel")
                }
            }
        )
    } else {
        androidx.compose.material3.AlertDialog(
            onDismissRequest = onDismiss,
            title = { Text("Templates") },
            text = {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(400.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = { showSaveTemplate = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Save New Template")
                    }
                    
                    if (templates.isEmpty()) {
                        Text("No templates saved yet", color = Color.Gray)
                    } else {
                        androidx.compose.foundation.lazy.LazyColumn(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(templates.size) { index ->
                                val template = templates[index]
                                
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .background(Color(0xFF2D2D2D), shape = MaterialTheme.shapes.small)
                                        .padding(8.dp),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    // Small Preview
                                    Box(
                                        modifier = Modifier
                                            .size(64.dp)
                                            .background(Color.Black, shape = MaterialTheme.shapes.extraSmall),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        template.previewImage?.let {
                                            Image(
                                                bitmap = it.asImageBitmap(),
                                                contentDescription = null,
                                                modifier = Modifier.fillMaxSize()
                                            )
                                        } ?: Text("?", color = Color.Gray)
                                    }
                                    
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(template.name, color = Color.White, style = MaterialTheme.typography.bodyMedium)
                                        Text("Font ${template.fontIndex + 1}", color = Color.Gray, style = MaterialTheme.typography.bodySmall)
                                    }
                                    
                                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                        Button(
                                            onClick = {
                                                viewModel.loadTemplate(template.name)
                                                onDismiss()
                                            },
                                            modifier = Modifier.height(32.dp),
                                            contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp)
                                        ) {
                                            Text("Load", style = MaterialTheme.typography.bodySmall)
                                        }
                                        Button(
                                            onClick = {
                                                viewModel.deleteTemplate(template.name)
                                            },
                                            modifier = Modifier.height(32.dp),
                                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE74C3C)),
                                            contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp)
                                        ) {
                                            Text("Del", style = MaterialTheme.typography.bodySmall)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            confirmButton = {
                Button(onClick = onDismiss) {
                    Text("Close")
                }
            }
        )
    }
}

@Composable
fun RightPanel(
    viewModel: IconViewModel,
    settings: IconSettings,
    modifier: Modifier = Modifier,
    isScrollable: Boolean = true
) {
    val scrollModifier = if (isScrollable) Modifier.verticalScroll(rememberScrollState()) else Modifier
    
    var expandedSections by remember { androidx.compose.runtime.mutableStateOf(setOf<String>()) }
    
    fun toggleSection(name: String) {
        expandedSections = if (expandedSections.contains(name)) {
            expandedSections - name
        } else {
            expandedSections + name
        }
    }

    Column(
        modifier = modifier
            .fillMaxHeight()
            .then(scrollModifier)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Image Settings
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionHeader("Image Settings", Color(0xFF3498DB), expandedSections.contains("Image Settings")) { toggleSection("Image Settings") }
            if (expandedSections.contains("Image Settings")) {
                ImageSettingsSection(viewModel, settings)
            }
        }
        
        // Background & Border
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionHeader("Background & Border", Color(0xFFE67E22), expandedSections.contains("Background & Border")) { toggleSection("Background & Border") }
            if (expandedSections.contains("Background & Border")) {
                BackgroundSection(viewModel, settings)
            }
        }
        
        // Text Settings
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionHeader("Text Settings", Color(0xFFE74C3C), expandedSections.contains("Text Settings")) { toggleSection("Text Settings") }
            if (expandedSections.contains("Text Settings")) {
                TextSettingsSection(viewModel, settings)
            }
        }
        
        // CRT Effects
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionHeader("CRT Effects", Color(0xFF16A085), expandedSections.contains("CRT Effects")) { toggleSection("CRT Effects") }
            if (expandedSections.contains("CRT Effects")) {
                CRTSection(viewModel, settings)
            }
        }
        
        // Decoration Settings
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionHeader("Decoration Settings", Color(0xFF27AE60), expandedSections.contains("Decoration Settings")) { toggleSection("Decoration Settings") }
            if (expandedSections.contains("Decoration Settings")) {
                DecorationSection(viewModel, settings)
            }
        }
    }
}

@Composable
fun SectionHeader(text: String, color: Color, isExpanded: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(color.copy(alpha = 0.8f), shape = MaterialTheme.shapes.medium)
            .clickable { onClick() }
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
            Icon(
                imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                contentDescription = null,
                tint = Color.White
            )
        }
    }
}

@Composable
fun ImageSettingsSection(viewModel: IconViewModel, settings: IconSettings) {
    val navL by viewModel.navL.collectAsState()
    val navR by viewModel.navR.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        SliderWithLabel(
            label = "Brightness",
            value = settings.brightness,
            valueRange = 0.1f..2.0f,
            onValueChange = { viewModel.updateSetting { brightness = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "Opacity",
            value = settings.imageAlpha,
            valueRange = 0.0f..1.0f,
            onValueChange = { viewModel.updateSetting { imageAlpha = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "Zoom",
            value = settings.zoomLevel.toFloat(),
            valueRange = -100f..200f,
            onValueChange = { viewModel.updateSetting { zoomLevel = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        SliderWithLabel(
            label = "X Offset",
            value = settings.offsetX.toFloat(),
            valueRange = -140f..140f,
            onValueChange = { viewModel.updateSetting { offsetX = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        SliderWithLabel(
            label = "Y Offset",
            value = settings.offsetY.toFloat(),
            valueRange = -140f..140f,
            onValueChange = { viewModel.updateSetting { offsetY = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        SliderWithLabel(
            label = "Stretch X",
            value = settings.stretchX,
            valueRange = 0.1f..5.0f,
            onValueChange = { viewModel.updateSetting { stretchX = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "Stretch Y",
            value = settings.stretchY,
            valueRange = 0.1f..5.0f,
            onValueChange = { viewModel.updateSetting { stretchY = it } },
            navL = navL, navR = navR
        )
    }
}

@Composable
fun BackgroundSection(viewModel: IconViewModel, settings: IconSettings) {
    val navL by viewModel.navL.collectAsState()
    val navR by viewModel.navR.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Background navigation
        NavigationRow(
            label = "Background",
            currentIndex = settings.currentBgIndex,
            totalCount = viewModel.backgrounds.collectAsState().value.size,
            navL = navL,
            navR = navR,
            onNext = { viewModel.nextBackground() },
            onPrev = { viewModel.prevBackground() }
        )
        
        SliderWithLabel(
            label = "BG Brightness",
            value = settings.bgBrightness,
            valueRange = 0.2f..2.0f,
            onValueChange = { viewModel.updateSetting { bgBrightness = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "BG Hue",
            value = settings.bgHue,
            valueRange = 0f..360f,
            onValueChange = { viewModel.updateSetting { bgHue = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "BG Scale",
            value = settings.bgScale,
            valueRange = 0.5f..2.0f,
            onValueChange = { viewModel.updateSetting { bgScale = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "BG Offset X",
            value = settings.bgOffsetX.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { viewModel.updateSetting { bgOffsetX = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        SliderWithLabel(
            label = "BG Offset Y",
            value = settings.bgOffsetY.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { viewModel.updateSetting { bgOffsetY = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        // Border navigation
        NavigationRow(
            label = "Border",
            currentIndex = settings.currentFrameIndex,
            totalCount = viewModel.borders.collectAsState().value.size,
            navL = navL,
            navR = navR,
            onNext = { viewModel.nextBorder() },
            onPrev = { viewModel.prevBorder() }
        )
        
        SliderWithLabel(
            label = "Border Hue",
            value = settings.borderHue,
            valueRange = 0f..360f,
            onValueChange = { viewModel.updateSetting { borderHue = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "Border Alpha",
            value = settings.borderAlpha,
            valueRange = 0f..1f,
            onValueChange = { viewModel.updateSetting { borderAlpha = it } },
            navL = navL, navR = navR
        )
        
        SliderWithLabel(
            label = "Shadow Opacity",
            value = settings.shadowOpacity.toFloat(),
            valueRange = 0f..100f,
            onValueChange = { viewModel.updateSetting { shadowOpacity = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
    }
}

@Composable
fun TextSettingsSection(viewModel: IconViewModel, settings: IconSettings) {
    var showFontSelector by remember { androidx.compose.runtime.mutableStateOf(false) }
    val navL by viewModel.navL.collectAsState()
    val navR by viewModel.navR.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Font navigation
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Box(modifier = Modifier.weight(1f)) {
                NavigationRow(
                    label = "Font",
                    currentIndex = settings.currentFontIndex,
                    totalCount = viewModel.fonts.collectAsState().value.size,
                    navL = navL,
                    navR = navR,
                    onNext = { viewModel.nextFont() },
                    onPrev = { viewModel.prevFont() }
                )
            }
            
            Button(
                onClick = { showFontSelector = true },
                modifier = Modifier.height(48.dp),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp)
            ) {
                Text("List", style = MaterialTheme.typography.bodySmall)
            }
        }
        
        if (showFontSelector) {
            FontSelectorDialog(
                viewModel = viewModel,
                currentIndex = settings.currentFontIndex,
                onSelect = { index ->
                    viewModel.updateSetting { currentFontIndex = index }
                    viewModel.setFont(viewModel.fonts.value.getOrNull(index))
                    showFontSelector = false
                },
                onDismiss = { showFontSelector = false }
            )
        }
        
        // Text line inputs
        for (i in 0..2) {
            TextLineItem(index = i, settings = settings, viewModel = viewModel)
        }
        
        SliderWithLabel(
            label = "Text Color Hue",
            value = settings.lineHues[0],
            valueRange = 0f..360f,
            onValueChange = { hue ->
                viewModel.updateSetting { 
                    lineHues = lineHues.mapIndexed { index, oldHue -> 
                        if (lineActive.getOrElse(index) { false }) hue else oldHue 
                    }
                } 
            },
            navL = navL, navR = navR
        )
        
        // Font size
        val baseSize = when (settings.titleLines.count { it.isNotEmpty() }) {
            1 -> 44
            2 -> 38
            else -> 32
        }
        val currentFontSize = (baseSize + settings.lineFontSpacingOffsets.getOrElse(0) { 0 }).coerceIn(20, 500)
        
        SliderWithLabel(
            label = "Font Size: ${currentFontSize}px",
            value = settings.lineFontSpacingOffsets.getOrElse(0) { 0 }.toFloat(),
            valueRange = -20f..200f,
            onValueChange = { offset ->
                viewModel.updateSetting {
                    lineFontSpacingOffsets = lineFontSpacingOffsets.toMutableList().apply { 
                        indices.forEach { if (lineActive.getOrElse(it) { false }) set(it, offset.toInt()) }
                    }
                }
            },
            navL = navL, navR = navR,
            step = 1f
        )
        
        // Letter spacing
        SliderWithLabel(
            label = "Letter Spacing: ${settings.lineLetterSpacings.getOrElse(0) { 0f }}px",
            value = settings.lineLetterSpacings.getOrElse(0) { 0f },
            valueRange = -10f..40f,
            onValueChange = { spacing ->
                viewModel.updateSetting {
                    lineLetterSpacings = lineLetterSpacings.toMutableList().apply { 
                        indices.forEach { if (lineActive.getOrElse(it) { false }) set(it, spacing) }
                    }
                }
            },
            navL = navL, navR = navR
        )
        
        // Line spacing
        SliderWithLabel(
            label = "Line Spacing: ${settings.lineSpacingOffset}px",
            value = settings.lineSpacingOffset.toFloat(),
            valueRange = -30f..30f,
            onValueChange = { viewModel.updateSetting { lineSpacingOffset = it.toInt() } },
            navL = navL, navR = navR,
            step = 1f
        )
        
        // Text position X
        SliderWithLabel(
            label = "Text Offset X",
            value = settings.lineTextOffsetXs.getOrElse(0) { 0 }.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { offset ->
                viewModel.updateSetting {
                    lineTextOffsetXs = lineTextOffsetXs.toMutableList().apply { 
                        indices.forEach { if (lineActive.getOrElse(it) { false }) set(it, offset.toInt()) }
                    }
                }
            },
            navL = navL, navR = navR,
            step = 1f
        )
        
        // Text position Y
        SliderWithLabel(
            label = "Text Offset Y",
            value = settings.lineTextOffsetYs.getOrElse(0) { 4 }.toFloat(),
            valueRange = -50f..50f,
            onValueChange = { offset ->
                viewModel.updateSetting {
                    lineTextOffsetYs = lineTextOffsetYs.toMutableList().apply { 
                        indices.forEach { if (lineActive.getOrElse(it) { false }) set(it, offset.toInt()) }
                    }
                }
            },
            navL = navL, navR = navR,
            step = 1f
        )
        
        // Glow parameters (Visible only if at least one line has glow enabled)
        if (settings.lineGlows.any { it }) {
            Spacer(modifier = Modifier.height(8.dp))
            Text("Glow Parameters", style = MaterialTheme.typography.labelLarge, color = Color.White)
            
            SliderWithLabel(
                label = "Glow Strength",
                value = settings.glowStrength,
                valueRange = 0f..2f,
                onValueChange = { viewModel.updateSetting { glowStrength = it } },
                navL = navL, navR = navR
            )
            
            SliderWithLabel(
                label = "Glow Size",
                value = settings.glowSize.toFloat(),
                valueRange = 1f..10f,
                onValueChange = { viewModel.updateSetting { glowSize = it.toInt() } },
                navL = navL, navR = navR,
                step = 1f
            )
        }
    }
}

@Composable
fun TextLineItem(
    index: Int,
    settings: IconSettings,
    viewModel: IconViewModel
) {
    val lineText = settings.titleLines.getOrElse(index) { "" }
    val isActive = settings.lineActive.getOrElse(index) { true }
    val isRainbow = settings.lineRainbows.getOrElse(index) { false }
    val isOutline = settings.lineOutlines.getOrElse(index) { true }
    val isGlow = settings.lineGlows.getOrElse(index) { false }

    Column(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            androidx.compose.material3.Checkbox(
                checked = isActive,
                onCheckedChange = { 
                    viewModel.updateSetting {
                        lineActive = lineActive.toMutableList().apply { 
                            while (size <= index) add(true)
                            set(index, it) 
                        }
                    }
                },
                colors = androidx.compose.material3.CheckboxDefaults.colors(
                    checkedColor = Color(0xFF00FF00),
                    uncheckedColor = Color(0xFF555555)
                )
            )
            
            androidx.compose.material3.OutlinedTextField(
                value = lineText,
                onValueChange = { 
                    viewModel.updateSetting {
                        titleLines = titleLines.toMutableList().apply { 
                            while (size <= index) add("")
                            set(index, it)
                        }
                    }
                },
                label = { Text("Line ${index + 1}") },
                modifier = Modifier.weight(1f),
                singleLine = true,
                textStyle = androidx.compose.material3.MaterialTheme.typography.bodySmall
            )
        }
        
        if (isActive) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(start = 32.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconToggle(
                    icon = viewModel.rainbowIcon.collectAsState().value,
                    label = "Rainbow",
                    checked = isRainbow,
                    onCheckedChange = { 
                        viewModel.updateSetting {
                            lineRainbows = lineRainbows.toMutableList().apply { 
                                while (size <= index) add(false)
                                set(index, it) 
                            }
                        }
                    }
                )
                
                IconToggle(
                    icon = viewModel.outlineIcon.collectAsState().value,
                    label = "Outline",
                    checked = isOutline,
                    onCheckedChange = { 
                        viewModel.updateSetting {
                            lineOutlines = lineOutlines.toMutableList().apply { 
                                while (size <= index) add(true)
                                set(index, it) 
                            }
                        }
                    }
                )
                
                IconToggle(
                    icon = viewModel.glowIcon.collectAsState().value,
                    label = "Glow",
                    checked = isGlow,
                    onCheckedChange = { 
                        viewModel.updateSetting {
                            lineGlows = lineGlows.toMutableList().apply { 
                                while (size <= index) add(false)
                                set(index, it) 
                            }
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun IconToggle(
    icon: Bitmap?,
    label: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    val isGlow = label == "Glow"
    val isRainbow = label == "Rainbow"
    
    androidx.compose.material3.Surface(
        onClick = { onCheckedChange(!checked) },
        shape = MaterialTheme.shapes.small,
        color = if (checked) {
            if (isGlow) Color(0xFFF1C40F).copy(alpha = 0.4f) else Color(0xFF3498DB).copy(alpha = 0.3f)
        } else Color.Transparent,
        border = if (checked) {
            androidx.compose.foundation.BorderStroke(1.dp, if (isGlow) Color(0xFFF1C40F) else Color(0xFF3498DB))
        } else null,
        modifier = Modifier.size(width = 80.dp, height = 40.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxSize().padding(4.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (icon != null) {
                if (isRainbow && checked) {
                    val rainbowBrush = Brush.linearGradient(
                        colors = listOf(
                            Color.Red, Color(0xFFFFA500), Color.Yellow, 
                            Color.Green, Color.Blue, Color(0xFF4B0082), Color(0xFFEE82EE)
                        )
                    )
                    Image(
                        bitmap = icon.asImageBitmap(),
                        contentDescription = label,
                        modifier = Modifier
                            .size(24.dp)
                            .graphicsLayer(alpha = 0.99f)
                            .drawWithCache {
                                onDrawWithContent {
                                    drawContent()
                                    drawRect(rainbowBrush, blendMode = BlendMode.SrcAtop)
                                }
                            }
                    )
                } else {
                    Image(
                        bitmap = icon.asImageBitmap(),
                        contentDescription = label,
                        modifier = Modifier.size(24.dp),
                        colorFilter = if (isGlow && checked) {
                            ColorFilter.lighting(Color(0xFFFFFFFF), Color(0xFFF1C40F))
                        } else null
                    )
                }
            }
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = if (checked) Color.White else Color.Gray,
                maxLines = 1
            )
        }
    }
}

@Composable
fun CRTSection(viewModel: IconViewModel, settings: IconSettings) {
    val navL by viewModel.navL.collectAsState()
    val navR by viewModel.navR.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        CheckboxWithLabel(
            label = "CRT Scanlines",
            checked = settings.crtEnabled,
            onCheckedChange = { viewModel.updateSetting { crtEnabled = it } }
        )
        
        if (settings.crtEnabled) {
            SliderWithLabel(
                label = "Scanline Opacity",
                value = settings.scanlineAlpha.toFloat(),
                valueRange = 0f..100f,
                onValueChange = { viewModel.updateSetting { scanlineAlpha = it.toInt() } },
                navL = navL, navR = navR,
                step = 1f
            )
        }
    }
}

@Composable
fun DecorationSection(viewModel: IconViewModel, settings: IconSettings) {
    val navL by viewModel.navL.collectAsState()
    val navR by viewModel.navR.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        CheckboxWithLabel(
            label = "Show Decoration",
            checked = settings.decorEnabled,
            onCheckedChange = { viewModel.updateSetting { decorEnabled = it } }
        )
        
        if (settings.decorEnabled) {
            NavigationRow(
                label = "Decor",
                currentIndex = settings.currentDecorIndex,
                totalCount = viewModel.decorations.collectAsState().value.size,
                navL = navL,
                navR = navR,
                onNext = { viewModel.nextDecor() },
                onPrev = { viewModel.prevDecor() }
            )
            
            SliderWithLabel(
                label = "Decor Scale",
                value = settings.decorScale,
                valueRange = 0.5f..2.0f,
                onValueChange = { viewModel.updateSetting { decorScale = it } },
                navL = navL, navR = navR
            )
            
            SliderWithLabel(
                label = "Decor Offset X",
                value = settings.decorOffsetX.toFloat(),
                valueRange = -30f..30f,
                onValueChange = { viewModel.updateSetting { decorOffsetX = it.toInt() } },
                navL = navL, navR = navR,
                step = 1f
            )
            
            SliderWithLabel(
                label = "Decor Offset Y",
                value = settings.decorOffsetY.toFloat(),
                valueRange = -30f..30f,
                onValueChange = { viewModel.updateSetting { decorOffsetY = it.toInt() } },
                navL = navL, navR = navR,
                step = 1f
            )
        }
    }
}

@Composable
fun CheckboxWithLabel(
    label: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        androidx.compose.material3.Checkbox(
            checked = checked,
            onCheckedChange = onCheckedChange
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = Color.White
        )
    }
}

@Composable
fun SliderWithLabel(
    label: String,
    value: Float,
    valueRange: ClosedFloatingPointRange<Float>,
    onValueChange: (Float) -> Unit,
    navL: Bitmap? = null,
    navR: Bitmap? = null,
    step: Float = 0.1f
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = "$label: %.2f".format(value),
            style = MaterialTheme.typography.bodySmall,
            color = Color.White
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            RepeatingIconButton(
                onClick = { onValueChange((value - step).coerceIn(valueRange.start, valueRange.endInclusive)) },
                modifier = Modifier.size(32.dp)
            ) {
                if (navL != null) {
                    Image(
                        bitmap = navL.asImageBitmap(),
                        contentDescription = "Decrease",
                        modifier = Modifier.size(20.dp)
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Decrease",
                        tint = Color(0xFF3498DB),
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
            
            Slider(
                value = value,
                valueRange = valueRange,
                onValueChange = onValueChange,
                modifier = Modifier.weight(1f)
            )

            RepeatingIconButton(
                onClick = { onValueChange((value + step).coerceIn(valueRange.start, valueRange.endInclusive)) },
                modifier = Modifier.size(32.dp)
            ) {
                if (navR != null) {
                    Image(
                        bitmap = navR.asImageBitmap(),
                        contentDescription = "Increase",
                        modifier = Modifier.size(20.dp)
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.ArrowForward,
                        contentDescription = "Increase",
                        tint = Color(0xFF3498DB),
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun LoadingScreen(progress: Float) {
    val context = LocalContext.current
    val loadingBitmap = remember {
        try {
            context.assets.open("Images/loading.png").use { 
                android.graphics.BitmapFactory.decodeStream(it)
            }
        } catch (e: Exception) {
            null
        }
    }

    Box(
        modifier = Modifier.fillMaxSize().background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        loadingBitmap?.let {
            Image(
                bitmap = it.asImageBitmap(),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = androidx.compose.ui.layout.ContentScale.Crop
            )
        }

        Column(
            modifier = Modifier
                .fillMaxWidth(0.8f)
                .align(Alignment.BottomCenter)
                .padding(bottom = 64.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Loading Assets... ${(progress * 100).toInt()}%",
                color = Color.White,
                style = MaterialTheme.typography.labelLarge
            )
            
            // Rainbow Progress Bar
            val rainbowBrush = Brush.linearGradient(
                colors = listOf(
                    Color.Red, Color(0xFFFFA500), Color.Yellow, 
                    Color.Green, Color.Blue, Color(0xFF4B0082), Color(0xFFEE82EE)
                )
            )
            
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(16.dp)
                    .background(Color.White.copy(alpha = 0.2f), shape = MaterialTheme.shapes.medium)
                    .padding(2.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(progress.coerceIn(0.01f, 1f))
                        .fillMaxHeight()
                        .background(rainbowBrush, shape = MaterialTheme.shapes.small)
                        .drawWithContent {
                            drawContent()
                            // Video game "glassy" shine effect
                            drawRect(
                                brush = Brush.verticalGradient(
                                    colors = listOf(
                                        Color.White.copy(alpha = 0.5f),
                                        Color.Transparent,
                                        Color.Black.copy(alpha = 0.3f)
                                    )
                                )
                            )
                        }
                )
            }
        }
    }
}

@Composable
fun FontSelectorDialog(
    viewModel: IconViewModel,
    currentIndex: Int,
    onSelect: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    val fonts by viewModel.fonts.collectAsState()
    val fontNames by viewModel.fontNames.collectAsState()
    
    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Select Font") },
        text = {
            androidx.compose.foundation.lazy.grid.LazyVerticalGrid(
                columns = androidx.compose.foundation.lazy.grid.GridCells.Fixed(2),
                modifier = Modifier.fillMaxWidth().height(400.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(fonts.size) { index ->
                    val isSelected = index == currentIndex
                    androidx.compose.material3.Surface(
                        onClick = { onSelect(index) },
                        shape = MaterialTheme.shapes.small,
                        color = if (isSelected) Color(0xFF3498DB).copy(alpha = 0.3f) else Color(0xFF2D2D2D),
                        border = if (isSelected) androidx.compose.foundation.BorderStroke(2.dp, Color(0xFF3498DB)) else null
                    ) {
                        Column(
                            modifier = Modifier.padding(8.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "Abc",
                                style = MaterialTheme.typography.titleLarge.copy(
                                    fontFamily = androidx.compose.ui.text.font.FontFamily(fonts[index])
                                ),
                                color = Color.White
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = fontNames.getOrElse(index) { "Font $index" }.substringAfterLast("/").substringBeforeLast("."),
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.Gray,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                maxLines = 1
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            Button(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}

@Composable
fun RepeatingIconButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    content: @Composable () -> Unit
) {
    val currentOnClick by rememberUpdatedState(onClick)
    val scope = rememberCoroutineScope()
    
    Box(
        modifier = modifier
            .size(48.dp)
            .clickable(
                enabled = enabled,
                onClick = { /* Handle by pointerInput for repeating */ },
                interactionSource = remember { androidx.compose.foundation.interaction.MutableInteractionSource() },
                indication = androidx.compose.material.ripple.rememberRipple(bounded = false)
            )
            .pointerInput(enabled) {
                if (!enabled) return@pointerInput
                detectTapGestures(
                    onPress = {
                        val job = scope.launch {
                            delay(400)
                            while (true) {
                                currentOnClick()
                                delay(100)
                            }
                        }
                        try {
                            currentOnClick()
                            awaitRelease()
                        } finally {
                            job.cancel()
                        }
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        content()
    }
}

@Composable
fun NavigationRow(
    label: String,
    currentIndex: Int,
    totalCount: Int,
    navL: Bitmap?,
    navR: Bitmap?,
    onNext: () -> Unit,
    onPrev: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = androidx.compose.foundation.layout.Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        RepeatingIconButton(
            onClick = onPrev,
            modifier = Modifier.size(48.dp)
        ) {
            if (navL != null) {
                Image(
                    bitmap = navL.asImageBitmap(),
                    contentDescription = "Previous",
                    modifier = Modifier.size(32.dp)
                )
            } else {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Previous",
                    tint = Color(0xFF3498DB)
                )
            }
        }
        
        Text(
            text = "$label: ${currentIndex + 1}/$totalCount",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.White
        )
        
        RepeatingIconButton(
            onClick = onNext,
            modifier = Modifier.size(48.dp)
        ) {
            if (navR != null) {
                Image(
                    bitmap = navR.asImageBitmap(),
                    contentDescription = "Next",
                    modifier = Modifier.size(32.dp)
                )
            } else {
                Icon(
                    imageVector = Icons.Default.ArrowForward,
                    contentDescription = "Next",
                    tint = Color(0xFF3498DB)
                )
            }
        }
    }
}

@Composable
fun RepeatingBorder(
    bitmap: Bitmap?,
    isVertical: Boolean,
    modifier: Modifier = Modifier
) {
    bitmap?.let { b ->
        androidx.compose.foundation.Canvas(modifier = modifier) {
            val paint = android.graphics.Paint().apply {
                isAntiAlias = true
                alpha = (255 * 0.1f).toInt()
            }
            
            val nativeCanvas = drawContext.canvas.nativeCanvas
            val bWidth = b.width.toFloat()
            val bHeight = b.height.toFloat()
            
            if (isVertical) {
                // Scale width to fit the container width
                val scale = size.width / bWidth
                val drawW = size.width
                val drawH = bHeight * scale
                
                var currentY = 0f
                while (currentY < size.height) {
                    nativeCanvas.drawBitmap(
                        b,
                        null,
                        android.graphics.RectF(0f, currentY, drawW, currentY + drawH),
                        paint
                    )
                    currentY += drawH
                }
            } else {
                // Horizontal: Scale height to fit container height
                val scale = size.height / bHeight
                val drawH = size.height
                val drawW = bWidth * scale
                
                var currentX = 0f
                while (currentX < size.width) {
                    nativeCanvas.drawBitmap(
                        b,
                        null,
                        android.graphics.RectF(currentX, 0f, currentX + drawW, drawH),
                        paint
                    )
                    currentX += drawW
                }
            }
        }
    }
}
