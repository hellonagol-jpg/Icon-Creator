package com.iconcreator.ui

import android.graphics.Bitmap
import androidx.compose.foundation.background
import androidx.compose.foundation.Image
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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.iconcreator.model.IconSettings
import com.iconcreator.ui.theme.IconCreatorTheme
import com.iconcreator.viewmodel.IconViewModel
import com.iconcreator.viewmodel.IconUiState

@Composable
fun IconCreatorScreen(
    viewModel: IconViewModel,
    uiState: IconUiState,
    previewBitmap: Bitmap?
) {
    val settings by viewModel.settings.collectAsState()
    
    Scaffold(
        modifier = Modifier.fillMaxSize()
    ) { paddingValues ->
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Color(0xFF1A1A1A))
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
                            .background(Color(0xFF1A1A1A))
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        PreviewBox(
                            previewBitmap = previewBitmap,
                            modifier = Modifier.fillMaxWidth(0.7f) // Slightly smaller on mobile to leave room
                        )
                    }
                    
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
fun LeftPanel(
    viewModel: IconViewModel,
    previewBitmap: Bitmap?,
    modifier: Modifier = Modifier
) {
    // This function is now partially redundant but kept for compatibility if called elsewhere
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        PreviewBox(previewBitmap = previewBitmap)
        Spacer(modifier = Modifier.height(16.dp))
        ActionButtons(viewModel)
    }
}

@Composable
fun ActionButtons(viewModel: IconViewModel) {
    val imagePicker = rememberImagePicker(viewModel)
    var showSaveDialog by androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(false) }
    var showTemplateDialog by androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(false) }
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Button(
            onClick = imagePicker,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3498DB))
        ) {
            Text("Upload Image")
        }
        
        Button(
            onClick = { showSaveDialog = true },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2ECC71))
        ) {
            Text("Save")
        }
        
        Button(
            onClick = { showTemplateDialog = true },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3498DB))
        ) {
            Text("Templates")
        }
        
        Button(
            onClick = { viewModel.resetToDefault() },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE74C3C))
        ) {
            Text("Reset")
        }
        
        Button(
            onClick = { viewModel.randomizeSettings() },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF69B4))
        ) {
            Text("Randomize")
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
        text = { Text("Choose save format:") },
        confirmButton = {
            Button(onClick = onSavePNG) {
                Text("Save as PNG")
            }
        },
        dismissButton = {
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
                                val name = template.settings.titleLines.joinToString(" ") { it }.takeIf { it.isNotBlank() } ?: "Unnamed Template"
                                
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
    
    Column(
        modifier = modifier
            .fillMaxHeight()
            .then(scrollModifier)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Image Settings
        Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)) {
            SectionHeader("Image Settings", Color(0xFF3498DB))
            ImageSettingsSection(viewModel, settings)
        }
        
        // Background & Border
        Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)) {
            SectionHeader("Background & Border", Color(0xFFE67E22))
            BackgroundSection(viewModel, settings)
        }
        
        // Text Settings
        Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)) {
            SectionHeader("Text Settings", Color(0xFFE74C3C))
            TextSettingsSection(viewModel, settings)
        }
        
        // CRT Effects
        Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)) {
            SectionHeader("CRT Effects", Color(0xFF16A085))
            CRTSection(viewModel, settings)
        }
        
        // Decoration Settings
        Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(8.dp)) {
            SectionHeader("Decoration Settings", Color(0xFF27AE60))
            DecorationSection(viewModel, settings)
        }
    }
}

@Composable
fun SectionHeader(text: String, color: Color) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(color, shape = MaterialTheme.shapes.medium)
            .padding(12.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            color = Color.White
        )
    }
}

@Composable
fun ImageSettingsSection(viewModel: IconViewModel, settings: IconSettings) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        SliderWithLabel(
            label = "Brightness",
            value = settings.brightness,
            valueRange = 0.1f..2.0f,
            onValueChange = { viewModel.updateSetting { brightness = it } }
        )
        
        SliderWithLabel(
            label = "Zoom",
            value = settings.zoomLevel.toFloat(),
            valueRange = -100f..200f,
            onValueChange = { viewModel.updateSetting { zoomLevel = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "X Offset",
            value = settings.offsetX.toFloat(),
            valueRange = -140f..140f,
            onValueChange = { viewModel.updateSetting { offsetX = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "Y Offset",
            value = settings.offsetY.toFloat(),
            valueRange = -140f..140f,
            onValueChange = { viewModel.updateSetting { offsetY = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "Stretch X",
            value = settings.stretchX,
            valueRange = 0.5f..2.0f,
            onValueChange = { viewModel.updateSetting { stretchX = it } }
        )
        
        SliderWithLabel(
            label = "Stretch Y",
            value = settings.stretchY,
            valueRange = 0.5f..2.0f,
            onValueChange = { viewModel.updateSetting { stretchY = it } }
        )
    }
}

@Composable
fun BackgroundSection(viewModel: IconViewModel, settings: IconSettings) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Background navigation
        NavigationRow(
            label = "Background",
            currentIndex = settings.currentBgIndex,
            totalCount = viewModel.backgrounds.collectAsState().value.size,
            onNext = { viewModel.nextBackground() },
            onPrev = { viewModel.prevBackground() }
        )
        
        SliderWithLabel(
            label = "BG Brightness",
            value = settings.bgBrightness,
            valueRange = 0.2f..2.0f,
            onValueChange = { viewModel.updateSetting { bgBrightness = it } }
        )
        
        SliderWithLabel(
            label = "BG Hue",
            value = settings.bgHue,
            valueRange = 0f..360f,
            onValueChange = { viewModel.updateSetting { bgHue = it } }
        )
        
        SliderWithLabel(
            label = "BG Scale",
            value = settings.bgScale,
            valueRange = 0.5f..2.0f,
            onValueChange = { viewModel.updateSetting { bgScale = it } }
        )
        
        SliderWithLabel(
            label = "BG Offset X",
            value = settings.bgOffsetX.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { viewModel.updateSetting { bgOffsetX = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "BG Offset Y",
            value = settings.bgOffsetY.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { viewModel.updateSetting { bgOffsetY = it.toInt() } }
        )
        
        // Border navigation
        NavigationRow(
            label = "Border",
            currentIndex = settings.currentFrameIndex,
            totalCount = viewModel.borders.collectAsState().value.size,
            onNext = { viewModel.nextBorder() },
            onPrev = { viewModel.prevBorder() }
        )
        
        SliderWithLabel(
            label = "Border Hue",
            value = settings.borderHue,
            valueRange = 0f..360f,
            onValueChange = { viewModel.updateSetting { borderHue = it } }
        )
        
        SliderWithLabel(
            label = "Border Alpha",
            value = settings.borderAlpha,
            valueRange = 0f..1f,
            onValueChange = { viewModel.updateSetting { borderAlpha = it } }
        )
        
        // RGB entry for border color
        val borderRgba = settings.borderDirectRgb ?: intArrayOf(255, 255, 255, 255)
        RGBEntryRow(
            label = "Border ARGB",
            rgba = borderRgba,
            onValueChange = { 
                viewModel.updateSetting { borderDirectRgb = it }
            }
        )
        
        SliderWithLabel(
            label = "Frame Offset X",
            value = settings.frameOffsetX.toFloat(),
            valueRange = -50f..50f,
            onValueChange = { viewModel.updateSetting { frameOffsetX = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "Frame Offset Y",
            value = settings.frameOffsetY.toFloat(),
            valueRange = -50f..50f,
            onValueChange = { viewModel.updateSetting { frameOffsetY = it.toInt() } }
        )
        
        SliderWithLabel(
            label = "Shadow Opacity",
            value = settings.shadowOpacity.toFloat(),
            valueRange = 0f..100f,
            onValueChange = { viewModel.updateSetting { shadowOpacity = it.toInt() } }
        )
    }
}

@Composable
fun TextSettingsSection(viewModel: IconViewModel, settings: IconSettings) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Font navigation
        NavigationRow(
            label = "Font",
            currentIndex = settings.currentFontIndex,
            totalCount = viewModel.fonts.collectAsState().value.size,
            onNext = { viewModel.nextFont() },
            onPrev = { viewModel.prevFont() }
        )
        
        // Text line inputs
        for (i in 0..2) {
            val lineText = settings.titleLines.getOrElse(i) { "" }
            val isActive = settings.lineActive.getOrElse(i) { true }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                androidx.compose.material3.Checkbox(
                    checked = isActive,
                    onCheckedChange = { 
                        viewModel.updateSetting {
                            lineActive = lineActive.toMutableList().apply { set(i, it) }
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
                                if (size <= i) add(it) else set(i, it)
                            }
                        }
                    },
                    label = { Text("Line ${i + 1}") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    textStyle = androidx.compose.material3.MaterialTheme.typography.bodySmall
                )
            }
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
                    // Remove direct RGB overrides for active lines when using hue
                    lineActive.forEachIndexed { index, active ->
                        if (active) directRgb.remove(index)
                    }
                } 
            }
        )
        
        // RGB entry for text color
        val firstActiveIdx = settings.lineActive.indexOf(true).coerceAtLeast(0)
        val textRgba = settings.directRgb[firstActiveIdx] ?: intArrayOf(255, 255, 255, 255)
        RGBEntryRow(
            label = "Text RGB",
            rgba = textRgba,
            showAlpha = false,
            onValueChange = { newRgb ->
                viewModel.updateSetting {
                    lineActive.forEachIndexed { index, active ->
                        if (active) {
                            directRgb[index] = newRgb
                        }
                    }
                }
            }
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
            onValueChange = { 
                viewModel.updateSetting {
                    lineFontSpacingOffsets = lineFontSpacingOffsets.toMutableList().apply { set(0, it.toInt()) }
                }
            }
        )
        
        // Letter spacing
        SliderWithLabel(
            label = "Letter Spacing: ${settings.lineFontSpacingOffsets.getOrElse(0) { -1 }}px",
            value = settings.lineFontSpacingOffsets.getOrElse(0) { -1 }.toFloat(),
            valueRange = -10f..20f,
            onValueChange = { 
                viewModel.updateSetting {
                    lineFontSpacingOffsets = lineFontSpacingOffsets.toMutableList().apply { set(0, it.toInt()) }
                }
            }
        )
        
        // Line spacing
        SliderWithLabel(
            label = "Line Spacing: ${settings.lineSpacingOffset}px",
            value = settings.lineSpacingOffset.toFloat(),
            valueRange = -30f..30f,
            onValueChange = { viewModel.updateSetting { lineSpacingOffset = it.toInt() } }
        )
        
        // Text position X
        SliderWithLabel(
            label = "Text Offset X",
            value = settings.lineTextOffsetXs.getOrElse(0) { 0 }.toFloat(),
            valueRange = -100f..100f,
            onValueChange = { 
                viewModel.updateSetting {
                    lineTextOffsetXs = lineTextOffsetXs.toMutableList().apply { set(0, it.toInt()) }
                }
            }
        )
        
        // Text position Y
        SliderWithLabel(
            label = "Text Offset Y",
            value = settings.lineTextOffsetYs.getOrElse(0) { 4 }.toFloat(),
            valueRange = -50f..50f,
            onValueChange = { 
                viewModel.updateSetting {
                    lineTextOffsetYs = lineTextOffsetYs.toMutableList().apply { set(0, it.toInt()) }
                }
            }
        )
        
        // Checkboxes
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            CheckboxWithLabel(
                label = "Rainbow",
                checked = settings.lineRainbows.getOrElse(0) { false },
                onCheckedChange = { 
                    viewModel.updateSetting {
                        lineRainbows = lineRainbows.toMutableList().apply { set(0, it) }
                    }
                }
            )
            
            CheckboxWithLabel(
                label = "Outline",
                checked = settings.lineOutlines.getOrElse(0) { true },
                onCheckedChange = { 
                    viewModel.updateSetting {
                        lineOutlines = lineOutlines.toMutableList().apply { set(0, it) }
                    }
                }
            )
        }
        
        // Glow controls
        CheckboxWithLabel(
            label = "Glow Text",
            checked = settings.glowEnabled,
            onCheckedChange = { viewModel.updateSetting { glowEnabled = it } }
        )
        
        if (settings.glowEnabled) {
            SliderWithLabel(
                label = "Glow Strength",
                value = settings.glowStrength,
                valueRange = 0f..2f,
                onValueChange = { viewModel.updateSetting { glowStrength = it } }
            )
            
            SliderWithLabel(
                label = "Glow Color Hue",
                value = settings.glowColorHue,
                valueRange = 0f..360f,
                onValueChange = { viewModel.updateSetting { glowColorHue = it } }
            )
            
            // RGB entry for glow color
            val glowRgba = settings.glowDirectRgb ?: intArrayOf(255, 255, 255, 255)
            RGBEntryRow(
                label = "Glow ARGB",
                rgba = glowRgba,
                onValueChange = { 
                    viewModel.updateSetting { glowDirectRgb = it }
                }
            )
            
            SliderWithLabel(
                label = "Glow Size",
                value = settings.glowSize.toFloat(),
                valueRange = 1f..10f,
                onValueChange = { viewModel.updateSetting { glowSize = it.toInt() } }
            )
        }
    }
}

@Composable
fun CRTSection(viewModel: IconViewModel, settings: IconSettings) {
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
                onValueChange = { viewModel.updateSetting { scanlineAlpha = it.toInt() } }
            )
        }
    }
}

@Composable
fun DecorationSection(viewModel: IconViewModel, settings: IconSettings) {
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
                onNext = { viewModel.nextDecor() },
                onPrev = { viewModel.prevDecor() }
            )
            
            SliderWithLabel(
                label = "Decor Scale",
                value = settings.decorScale,
                valueRange = 0.5f..2.0f,
                onValueChange = { viewModel.updateSetting { decorScale = it } }
            )
            
            SliderWithLabel(
                label = "Decor Offset X",
                value = settings.decorOffsetX.toFloat(),
                valueRange = -30f..30f,
                onValueChange = { viewModel.updateSetting { decorOffsetX = it.toInt() } }
            )
            
            SliderWithLabel(
                label = "Decor Offset Y",
                value = settings.decorOffsetY.toFloat(),
                valueRange = -30f..30f,
                onValueChange = { viewModel.updateSetting { decorOffsetY = it.toInt() } }
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
fun RGBEntryRow(
    label: String,
    rgba: IntArray,
    showAlpha: Boolean = true,
    onValueChange: (IntArray) -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = Color.White
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            val a = if (rgba.size >= 4) rgba[0] else 255
            val r = if (rgba.size >= 4) rgba[1] else rgba.getOrElse(0) { 255 }
            val g = if (rgba.size >= 4) rgba[2] else rgba.getOrElse(1) { 255 }
            val b = if (rgba.size >= 4) rgba[3] else rgba.getOrElse(2) { 255 }

            if (showAlpha) {
                RGBEntryField(value = a, onValueChange = { onValueChange(intArrayOf(it, r, g, b)) }, label = "A", modifier = Modifier.weight(1f))
            }
            RGBEntryField(value = r, onValueChange = { 
                if (showAlpha) onValueChange(intArrayOf(a, it, g, b)) 
                else onValueChange(intArrayOf(it, g, b)) 
            }, label = "R", modifier = Modifier.weight(1f))
            
            RGBEntryField(value = g, onValueChange = { 
                if (showAlpha) onValueChange(intArrayOf(a, r, it, b)) 
                else onValueChange(intArrayOf(r, it, b)) 
            }, label = "G", modifier = Modifier.weight(1f))
            
            RGBEntryField(value = b, onValueChange = { 
                if (showAlpha) onValueChange(intArrayOf(a, r, g, it)) 
                else onValueChange(intArrayOf(r, g, it)) 
            }, label = "B", modifier = Modifier.weight(1f))
        }
    }
}

@Composable
fun RGBEntryField(
    value: Int,
    onValueChange: (Int) -> Unit,
    label: String,
    modifier: Modifier = Modifier
) {
    var text by androidx.compose.runtime.remember(value) { androidx.compose.runtime.mutableStateOf(value.toString()) }
    
    androidx.compose.material3.OutlinedTextField(
        value = text,
        onValueChange = { newText ->
            text = newText
            newText.toIntOrNull()?.let { if (it in 0..255) onValueChange(it) }
        },
        label = { Text(label) },
        modifier = modifier,
        singleLine = true,
        textStyle = androidx.compose.material3.MaterialTheme.typography.bodySmall
    )
}

@Composable
fun SliderWithLabel(
    label: String,
    value: Float,
    valueRange: ClosedFloatingPointRange<Float>,
    onValueChange: (Float) -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = "$label: %.2f".format(value),
            style = MaterialTheme.typography.bodySmall,
            color = Color.White
        )
        Slider(
            value = value,
            valueRange = valueRange,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

@Composable
fun NavigationRow(
    label: String,
    currentIndex: Int,
    totalCount: Int,
    onNext: () -> Unit,
    onPrev: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = androidx.compose.foundation.layout.Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(
            onClick = onPrev,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                imageVector = Icons.Default.ArrowBack,
                contentDescription = "Previous",
                tint = Color(0xFF3498DB)
            )
        }
        
        Text(
            text = "$label: ${currentIndex + 1}/$totalCount",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.White
        )
        
        IconButton(
            onClick = onNext,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                imageVector = Icons.Default.ArrowForward,
                contentDescription = "Next",
                tint = Color(0xFF3498DB)
            )
        }
    }
}
