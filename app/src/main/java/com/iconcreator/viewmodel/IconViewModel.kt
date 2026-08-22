package com.iconcreator.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import android.graphics.Bitmap
import android.graphics.Typeface
import androidx.lifecycle.viewModelScope
import com.iconcreator.manager.AssetManager
import com.iconcreator.manager.ImageSaver
import com.iconcreator.manager.TemplateManager
import com.iconcreator.manager.TemplateData
import com.iconcreator.model.IconSettings
import com.iconcreator.renderer.IconRenderer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * ViewModel for managing icon creator state and business logic
 */
class IconViewModel(application: Application) : AndroidViewModel(application) {
    
    private val renderer = IconRenderer()
    private val assetManager = AssetManager(application)
    private val imageSaver = ImageSaver(application)
    private val templateManager = TemplateManager(application)
    
    // UI State
    private val _uiState = MutableStateFlow(IconUiState())
    val uiState: StateFlow<IconUiState> = _uiState.asStateFlow()
    
    // Icon settings
    private val _settings = MutableStateFlow(IconSettings.createDefault())
    val settings: StateFlow<IconSettings> = _settings.asStateFlow()
    
    // Loaded assets lists
    private val _backgrounds = MutableStateFlow<List<Bitmap>>(emptyList())
    val backgrounds: StateFlow<List<Bitmap>> = _backgrounds.asStateFlow()
    
    private val _borders = MutableStateFlow<List<Bitmap>>(emptyList())
    val borders: StateFlow<List<Bitmap>> = _borders.asStateFlow()
    
    private val _fonts = MutableStateFlow<List<Typeface>>(emptyList())
    val fonts: StateFlow<List<Typeface>> = _fonts.asStateFlow()
    
    private val _fontNames = MutableStateFlow<List<String>>(emptyList())
    val fontNames: StateFlow<List<String>> = _fontNames.asStateFlow()
    
    private val _decorations = MutableStateFlow<List<Bitmap>>(emptyList())
    val decorations: StateFlow<List<Bitmap>> = _decorations.asStateFlow()
    
    private val _templates = MutableStateFlow<List<TemplateData>>(emptyList())
    val templates: StateFlow<List<TemplateData>> = _templates.asStateFlow()
    
    // Currently loaded assets
    private val _gameImage = MutableStateFlow<Bitmap?>(null)
    val gameImage: StateFlow<Bitmap?> = _gameImage.asStateFlow()
    
    private val _backgroundImage = MutableStateFlow<Bitmap?>(null)
    val backgroundImage: StateFlow<Bitmap?> = _backgroundImage.asStateFlow()
    
    private val _frameImage = MutableStateFlow<Bitmap?>(null)
    val frameImage: StateFlow<Bitmap?> = _frameImage.asStateFlow()
    
    private val _decorImage = MutableStateFlow<Bitmap?>(null)
    val decorImage: StateFlow<Bitmap?> = _decorImage.asStateFlow()
    
    private val _font = MutableStateFlow<Typeface?>(null)
    val font: StateFlow<Typeface?> = _font.asStateFlow()
    
    private val _alphaMask = MutableStateFlow<Bitmap?>(null)
    private val _alpha2Mask = MutableStateFlow<Bitmap?>(null)
    private val _borderShadow = MutableStateFlow<Bitmap?>(null)
    private val _scanlineOverlay = MutableStateFlow<Bitmap?>(null)
    
    private val _navL = MutableStateFlow<Bitmap?>(null)
    val navL: StateFlow<Bitmap?> = _navL.asStateFlow()
    
    private val _navR = MutableStateFlow<Bitmap?>(null)
    val navR: StateFlow<Bitmap?> = _navR.asStateFlow()
    
    private val _rainbowIcon = MutableStateFlow<Bitmap?>(null)
    val rainbowIcon: StateFlow<Bitmap?> = _rainbowIcon.asStateFlow()
    
    private val _outlineIcon = MutableStateFlow<Bitmap?>(null)
    val outlineIcon: StateFlow<Bitmap?> = _outlineIcon.asStateFlow()
    
    private val _glowIcon = MutableStateFlow<Bitmap?>(null)
    val glowIcon: StateFlow<Bitmap?> = _glowIcon.asStateFlow()
    
    private val _mainBackground = MutableStateFlow<Bitmap?>(null)
    val mainBackground: StateFlow<Bitmap?> = _mainBackground.asStateFlow()
    
    private val _borderX = MutableStateFlow<Bitmap?>(null)
    val borderX: StateFlow<Bitmap?> = _borderX.asStateFlow()
    
    // Rendered preview
    private val _previewBitmap = MutableStateFlow<Bitmap?>(null)
    val previewBitmap: StateFlow<Bitmap?> = _previewBitmap.asStateFlow()
    
    private var renderJob: kotlinx.coroutines.Job? = null
    
    init {
        loadAssets()
    }
    
    /**
     * Load all assets from the assets folder
     */
    private fun loadAssets() {
        viewModelScope.launch {
            updateUiState { isLoading = true; loadingProgress = 0f }
            
            _backgrounds.value = assetManager.loadBackgrounds()
            updateUiState { loadingProgress = 0.1f }
            
            _borders.value = assetManager.loadBorders()
            updateUiState { loadingProgress = 0.2f }
            
            val fontFiles = assetManager.listAssetFiles("Fonts")
            _fontNames.value = fontFiles
            _fonts.value = fontFiles.mapNotNull { assetManager.loadFont("Fonts/$it") }
            updateUiState { loadingProgress = 0.4f }
            
            _decorations.value = assetManager.loadDecorations()
            updateUiState { loadingProgress = 0.5f }
            
            _alphaMask.value = assetManager.loadAlphaMask()
            _alpha2Mask.value = assetManager.loadAlpha2Mask()
            _borderShadow.value = assetManager.loadBorderShadow()
            _scanlineOverlay.value = assetManager.loadScanlines()
            _navL.value = assetManager.loadNavL()
            _navR.value = assetManager.loadNavR()
            _rainbowIcon.value = assetManager.loadRainbowIcon()
            _outlineIcon.value = assetManager.loadOutlineIcon()
            _glowIcon.value = assetManager.loadGlowIcon()
            _mainBackground.value = assetManager.loadBitmap("Images/mainbackground.png")
            _borderX.value = assetManager.loadBitmap("Images/borderx.png")
            updateUiState { loadingProgress = 0.8f }
            
            loadTemplates()
            updateUiState { loadingProgress = 0.9f }
            
            // Load initial assets
            if (_backgrounds.value.isNotEmpty()) {
                _backgroundImage.value = _backgrounds.value[0]
            }
            if (_borders.value.isNotEmpty()) {
                _frameImage.value = _borders.value[0]
            }
            if (_fonts.value.isNotEmpty()) {
                _font.value = _fonts.value[0]
            }
            if (_decorations.value.isNotEmpty()) {
                _decorImage.value = _decorations.value[0]
            }
            
            renderPreview()
            updateUiState { loadingProgress = 1.0f; isLoading = false }
        }
    }
    
    /**
     * Update a specific setting and re-render
     */
    fun updateSetting(update: IconSettings.() -> Unit) {
        _settings.value = _settings.value.copy().apply(update)
        renderPreview()
    }
    
    /**
     * Set the game image
     */
    fun setGameImage(bitmap: Bitmap?) {
        _gameImage.value = bitmap
        if (bitmap != null) {
            updateSetting {
                zoomLevel = 50 // Default to "fit"
                // Stretch to fill the 512x512 square exactly
                val maxDim = Math.max(bitmap.width, bitmap.height).toFloat()
                stretchX = maxDim / bitmap.width
                stretchY = maxDim / bitmap.height
                offsetX = 0
                offsetY = 0
            }
        }
        renderPreview()
    }
    
    /**
     * Set the background image
     */
    fun setBackgroundImage(bitmap: Bitmap?) {
        _backgroundImage.value = bitmap
        renderPreview()
    }
    
    /**
     * Set the frame image
     */
    fun setFrameImage(bitmap: Bitmap?) {
        _frameImage.value = bitmap
        renderPreview()
    }
    
    /**
     * Set the decoration image
     */
    fun setDecorImage(bitmap: Bitmap?) {
        _decorImage.value = bitmap
        renderPreview()
    }
    
    /**
     * Set the font
     */
    fun setFont(typeface: Typeface?) {
        _font.value = typeface
        renderPreview()
    }
    
    /**
     * Render the icon preview
     */
    private fun renderPreview() {
        renderJob?.cancel()
        renderJob = viewModelScope.launch {
            val preview = renderer.renderIcon(
                settings = _settings.value,
                gameImage = _gameImage.value,
                backgroundImage = _backgroundImage.value,
                frameImage = _frameImage.value,
                decorImage = _decorImage.value,
                font = _font.value,
                alphaMask = _alphaMask.value,
                alpha2Mask = _alpha2Mask.value,
                borderShadow = _borderShadow.value,
                scanlineOverlay = _scanlineOverlay.value
            )
            _previewBitmap.value = preview
        }
    }
    
    /**
     * Reset all settings to default
     */
    fun resetToDefault() {
        _settings.value = IconSettings.createDefault()
        _gameImage.value = null
        renderPreview()
    }
    
    /**
     * Randomize settings
     */
    fun randomizeSettings() {
        val backgrounds = _backgrounds.value
        val borders = _borders.value
        val decorations = _decorations.value
        
        _settings.value = _settings.value.copy().apply {
            bgHue = (0..360).random().toFloat()
            borderHue = (0..360).random().toFloat()
            lineHues = lineHues.map { (0..360).random().toFloat() }
            
            if (backgrounds.isNotEmpty()) {
                currentBgIndex = backgrounds.indices.random()
                _backgroundImage.value = backgrounds[currentBgIndex]
            }
            if (borders.isNotEmpty()) {
                currentFrameIndex = borders.indices.random()
                _frameImage.value = borders[currentFrameIndex]
            }
            if (decorations.isNotEmpty()) {
                currentDecorIndex = decorations.indices.random()
                _decorImage.value = decorations[currentDecorIndex]
            }
        }
        renderPreview()
    }
    
    /**
     * Update UI state (loading, error messages, etc.)
     */
    fun updateUiState(update: IconUiState.() -> Unit) {
        _uiState.value = _uiState.value.copy().apply(update)
    }
    
    /**
     * Navigate to next background
     */
    fun nextBackground() {
        val backgrounds = _backgrounds.value
        if (backgrounds.isNotEmpty()) {
            val currentIndex = _settings.value.currentBgIndex
            val nextIndex = (currentIndex + 1) % backgrounds.size
            _backgroundImage.value = backgrounds[nextIndex]
            updateSetting { currentBgIndex = nextIndex }
        }
    }
    
    /**
     * Navigate to previous background
     */
    fun prevBackground() {
        val backgrounds = _backgrounds.value
        if (backgrounds.isNotEmpty()) {
            val currentIndex = _settings.value.currentBgIndex
            val prevIndex = if (currentIndex - 1 < 0) backgrounds.size - 1 else currentIndex - 1
            _backgroundImage.value = backgrounds[prevIndex]
            updateSetting { currentBgIndex = prevIndex }
        }
    }
    
    /**
     * Navigate to next border/frame
     */
    fun nextBorder() {
        val borders = _borders.value
        if (borders.isNotEmpty()) {
            val currentIndex = _settings.value.currentFrameIndex
            val nextIndex = (currentIndex + 1) % borders.size
            _frameImage.value = borders[nextIndex]
            updateSetting { currentFrameIndex = nextIndex }
        }
    }
    
    /**
     * Navigate to previous border/frame
     */
    fun prevBorder() {
        val borders = _borders.value
        if (borders.isNotEmpty()) {
            val currentIndex = _settings.value.currentFrameIndex
            val prevIndex = if (currentIndex - 1 < 0) borders.size - 1 else currentIndex - 1
            _frameImage.value = borders[prevIndex]
            updateSetting { currentFrameIndex = prevIndex }
        }
    }
    
    /**
     * Navigate to next font
     */
    fun nextFont() {
        val fonts = _fonts.value
        if (fonts.isNotEmpty()) {
            val currentIndex = _settings.value.currentFontIndex
            val nextIndex = (currentIndex + 1) % fonts.size
            _font.value = fonts[nextIndex]
            updateSetting { currentFontIndex = nextIndex }
        }
    }
    
    /**
     * Navigate to previous font
     */
    fun prevFont() {
        val fonts = _fonts.value
        if (fonts.isNotEmpty()) {
            val currentIndex = _settings.value.currentFontIndex
            val prevIndex = if (currentIndex - 1 < 0) fonts.size - 1 else currentIndex - 1
            _font.value = fonts[prevIndex]
            updateSetting { currentFontIndex = prevIndex }
        }
    }
    
    /**
     * Navigate to next decoration
     */
    fun nextDecor() {
        val decorations = _decorations.value
        if (decorations.isNotEmpty()) {
            val currentIndex = _settings.value.currentDecorIndex
            val nextIndex = (currentIndex + 1) % decorations.size
            _decorImage.value = decorations[nextIndex]
            updateSetting { currentDecorIndex = nextIndex }
        }
    }
    
    /**
     * Navigate to previous decoration
     */
    fun prevDecor() {
        val decorations = _decorations.value
        if (decorations.isNotEmpty()) {
            val currentIndex = _settings.value.currentDecorIndex
            val prevIndex = if (currentIndex - 1 < 0) decorations.size - 1 else currentIndex - 1
            _decorImage.value = decorations[prevIndex]
            updateSetting { currentDecorIndex = prevIndex }
        }
    }
    
    /**
     * Save the current icon as PNG
     */
    fun saveAsPNG(filename: String? = null) {
        viewModelScope.launch {
            val preview = _previewBitmap.value ?: return@launch
            val name = filename ?: generateCustomFilename()
            val result = imageSaver.saveAsPNG(preview, name)
            if (result != null) {
                updateUiState { 
                    successMessage = "Saved as PNG: $result"
                    lastSavedUri = result
                }
            } else {
                updateUiState { errorMessage = "Failed to save PNG" }
            }
        }
    }
    
    /**
     * Save the current icon as ICO
     */
    fun saveAsICO(filename: String? = null) {
        viewModelScope.launch {
            val preview = _previewBitmap.value ?: return@launch
            val name = filename ?: generateCustomFilename()
            val result = imageSaver.saveAsICO(preview, name)
            if (result != null) {
                updateUiState { 
                    successMessage = "Saved as ICO: $result"
                    lastSavedUri = result
                }
            } else {
                updateUiState { errorMessage = "Failed to save ICO" }
            }
        }
    }
    
    /**
     * Generate a filename based on text lines and date
     */
    private fun generateCustomFilename(): String {
        val lines = _settings.value.titleLines.filter { it.isNotBlank() }
        val sentence = lines.joinToString("_") { it.trim().replace(Regex("[^a-zA-Z0-9]"), "") }
        val dateFormat = SimpleDateFormat("MMdd", Locale.getDefault())
        val dateSuffix = dateFormat.format(Date())
        return if (sentence.isNotEmpty()) "${sentence}_$dateSuffix" else "icon_$dateSuffix"
    }
    
    /**
     * Save current state as a template
     */
    fun saveTemplate(templateName: String) {
        viewModelScope.launch {
            val result = templateManager.saveTemplate(
                settings = _settings.value,
                gameImage = _gameImage.value,
                backgroundImage = _backgroundImage.value,
                frameImage = _frameImage.value,
                decorImage = _decorImage.value,
                previewImage = _previewBitmap.value,
                templateName = templateName
            )
            if (result) {
                loadTemplates()
                updateUiState { successMessage = "Template saved: $templateName" }
            } else {
                updateUiState { errorMessage = "Failed to save template" }
            }
        }
    }
    
    /**
     * Load all templates from storage
     */
    private fun loadTemplates() {
        viewModelScope.launch {
            val names = templateManager.getTemplateNames()
            val loadedTemplates = names.mapNotNull { templateManager.loadTemplate(it) }
            _templates.value = loadedTemplates
        }
    }
    
    /**
     * Load a template
     */
    fun loadTemplate(templateName: String) {
        viewModelScope.launch {
            val templateData = templateManager.loadTemplate(templateName)
            templateData?.let { data ->
                _settings.value = data.settings
                
                // Load images
                _gameImage.value = data.gameImage
                _backgroundImage.value = data.backgroundImage
                _frameImage.value = data.frameImage
                _decorImage.value = data.decorImage
                
                // Load font by index
                val fonts = _fonts.value
                if (data.fontIndex in fonts.indices) {
                    _font.value = fonts[data.fontIndex]
                }
                
                renderPreview()
                updateUiState { successMessage = "Template loaded: $templateName" }
            } ?: run {
                updateUiState { errorMessage = "Failed to load template" }
            }
        }
    }
    
    /**
     * Get list of template names
     */
    suspend fun getTemplateNames(): List<String> {
        return templateManager.getTemplateNames()
    }
    
    /**
     * Delete a template
     */
    fun deleteTemplate(templateName: String) {
        viewModelScope.launch {
            val result = templateManager.deleteTemplate(templateName)
            if (result) {
                loadTemplates()
                updateUiState { successMessage = "Template deleted: $templateName" }
            } else {
                updateUiState { errorMessage = "Failed to delete template" }
            }
        }
    }
    
    /**
     * Clear the last saved URI after it has been handled by the UI
     */
    fun clearLastSavedUri() {
        updateUiState { lastSavedUri = null }
    }
}

/**
 * UI state for the icon creator screen
 */
data class IconUiState(
    var isLoading: Boolean = true,
    var loadingProgress: Float = 0f,
    var errorMessage: String? = null,
    var successMessage: String? = null,
    var lastSavedUri: String? = null
)
