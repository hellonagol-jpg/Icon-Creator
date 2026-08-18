package com.iconcreator.manager

import android.content.Context
import android.graphics.Bitmap
import com.iconcreator.model.IconSettings
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream

/**
 * Manages saving and loading templates to/from device storage
 */
class TemplateManager(private val context: Context) {
    
    private val templatesDir: File
        get() = File(context.filesDir, "templates").apply { if (!exists()) mkdirs() }
    
    /**
     * Save the current state as a template
     */
    suspend fun saveTemplate(
        settings: IconSettings,
        gameImage: Bitmap?,
        backgroundImage: Bitmap?,
        frameImage: Bitmap?,
        decorImage: Bitmap?,
        previewImage: Bitmap?,
        templateName: String
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            // Create template directory
            val templateDir = File(templatesDir, templateName)
            if (templateDir.exists()) {
                templateDir.deleteRecursively()
            }
            templateDir.mkdirs()
            
            // Save settings to JSON
            val settingsJson = settingsToJson(settings)
            val settingsFile = File(templateDir, "settings.json")
            settingsFile.writeText(settingsJson)
            
            // Save images
            gameImage?.let { saveBitmap(it, File(templateDir, "game_image.png")) }
            backgroundImage?.let { saveBitmap(it, File(templateDir, "background.png")) }
            frameImage?.let { saveBitmap(it, File(templateDir, "frame.png")) }
            decorImage?.let { saveBitmap(it, File(templateDir, "decor.png")) }
            previewImage?.let { saveBitmap(it, File(templateDir, "preview.png")) }
            
            // Note: Typeface cannot be easily saved, so we save the font name/index instead
            val fontFile = File(templateDir, "font_info.txt")
            fontFile.writeText("font_index: ${settings.currentFontIndex}")
            
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
    
    /**
     * Load a template
     */
    suspend fun loadTemplate(templateName: String): TemplateData? = withContext(Dispatchers.IO) {
        try {
            val templateDir = File(templatesDir, templateName)
            if (!templateDir.exists()) return@withContext null
            
            // Load settings
            val settingsFile = File(templateDir, "settings.json")
            val settings = if (settingsFile.exists()) {
                jsonToSettings(settingsFile.readText())
            } else {
                IconSettings.createDefault()
            }
            
            // Load images
            val gameImage = loadBitmap(File(templateDir, "game_image.png"))
            val backgroundImage = loadBitmap(File(templateDir, "background.png"))
            val frameImage = loadBitmap(File(templateDir, "frame.png"))
            val decorImage = loadBitmap(File(templateDir, "decor.png"))
            val previewImage = loadBitmap(File(templateDir, "preview.png"))
            
            // Font info (font needs to be reloaded from assets)
            val fontFile = File(templateDir, "font_info.txt")
            val fontIndex = if (fontFile.exists()) {
                fontFile.readText().substringAfter("font_index: ").toIntOrNull() ?: 0
            } else {
                0
            }
            
            TemplateData(
                name = templateName,
                settings = settings,
                gameImage = gameImage,
                backgroundImage = backgroundImage,
                frameImage = frameImage,
                decorImage = decorImage,
                previewImage = previewImage,
                fontIndex = fontIndex
            )
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * Get list of all template names
     */
    suspend fun getTemplateNames(): List<String> = withContext(Dispatchers.IO) {
        templatesDir.listFiles()?.map { it.name }?.sorted() ?: emptyList()
    }
    
    /**
     * Delete a template
     */
    suspend fun deleteTemplate(templateName: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val templateDir = File(templatesDir, templateName)
            if (templateDir.exists()) {
                templateDir.deleteRecursively()
                true
            } else {
                false
            }
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
    
    private fun settingsToJson(settings: IconSettings): String {
        val json = JSONObject()
        
        // Image settings
        json.put("zoomLevel", settings.zoomLevel)
        json.put("offsetX", settings.offsetX)
        json.put("offsetY", settings.offsetY)
        json.put("stretchX", settings.stretchX)
        json.put("stretchY", settings.stretchY)
        json.put("brightness", settings.brightness)
        json.put("imageAlpha", settings.imageAlpha)
        
        // Background settings
        json.put("bgHue", settings.bgHue)
        json.put("bgBrightness", settings.bgBrightness)
        json.put("bgScale", settings.bgScale)
        json.put("bgOffsetX", settings.bgOffsetX)
        json.put("bgOffsetY", settings.bgOffsetY)
        json.put("currentBgIndex", settings.currentBgIndex)
        
        // Border settings
        json.put("borderHue", settings.borderHue)
        json.put("borderAlpha", settings.borderAlpha)
        json.put("frameOffsetX", settings.frameOffsetX)
        json.put("frameOffsetY", settings.frameOffsetY)
        json.put("currentFrameIndex", settings.currentFrameIndex)
        
        // Text settings
        json.put("titleLines", JSONArray(settings.titleLines))
        json.put("lineHues", JSONArray(settings.lineHues.map { it.toDouble() }))
        json.put("lineRainbows", JSONArray(settings.lineRainbows))
        json.put("lineOutlines", JSONArray(settings.lineOutlines))
        json.put("lineGlows", JSONArray(settings.lineGlows))
        json.put("lineActive", JSONArray(settings.lineActive))
        json.put("lineFontSpacingOffsets", JSONArray(settings.lineFontSpacingOffsets))
        json.put("lineLetterSpacings", JSONArray(settings.lineLetterSpacings.map { it.toDouble() }))
        json.put("lineTextOffsetXs", JSONArray(settings.lineTextOffsetXs))
        json.put("lineTextOffsetYs", JSONArray(settings.lineTextOffsetYs))
        json.put("lineSpacingOffset", settings.lineSpacingOffset)
        json.put("fontPositionStep", settings.fontPositionStep)
        json.put("currentFontIndex", settings.currentFontIndex)
        
        // Glow settings
        json.put("glowStrength", settings.glowStrength)
        json.put("glowColorHue", settings.glowColorHue)
        json.put("glowSize", settings.glowSize)
        
        // CRT settings
        json.put("crtEnabled", settings.crtEnabled)
        json.put("scanlineAlpha", settings.scanlineAlpha)
        
        // Decoration settings
        json.put("decorEnabled", settings.decorEnabled)
        json.put("currentDecorIndex", settings.currentDecorIndex)
        json.put("decorScale", settings.decorScale)
        json.put("decorOffsetX", settings.decorOffsetX)
        json.put("decorOffsetY", settings.decorOffsetY)
        
        // Shadow settings
        json.put("shadowOpacity", settings.shadowOpacity)
        
        return json.toString(2)
    }
    
    private fun jsonToSettings(jsonString: String): IconSettings {
        val json = JSONObject(jsonString)
        
        return IconSettings(
            zoomLevel = json.optInt("zoomLevel", 50),
            offsetX = json.optInt("offsetX", 0),
            offsetY = json.optInt("offsetY", 0),
            stretchX = json.optDouble("stretchX", 1.0).toFloat(),
            stretchY = json.optDouble("stretchY", 1.0).toFloat(),
            brightness = json.optDouble("brightness", 0.9).toFloat(),
            imageAlpha = json.optDouble("imageAlpha", 1.0).toFloat(),
            
            bgHue = json.optDouble("bgHue", 0.0).toFloat(),
            bgBrightness = json.optDouble("bgBrightness", 1.0).toFloat(),
            bgScale = json.optDouble("bgScale", 1.0).toFloat(),
            bgOffsetX = json.optInt("bgOffsetX", 0),
            bgOffsetY = json.optInt("bgOffsetY", 0),
            currentBgIndex = json.optInt("currentBgIndex", 0),
            
            borderHue = json.optDouble("borderHue", 0.0).toFloat(),
            borderAlpha = json.optDouble("borderAlpha", 1.0).toFloat(),
            frameOffsetX = json.optInt("frameOffsetX", 0),
            frameOffsetY = json.optInt("frameOffsetY", 0),
            currentFrameIndex = json.optInt("currentFrameIndex", 0),
            
            titleLines = json.optJSONArray("titleLines")?.let { array ->
                (0 until array.length()).map { array.optString(it, "") }
            } ?: listOf("Icon", "Creator"),
            
            lineHues = json.optJSONArray("lineHues")?.let { array ->
                (0 until array.length()).map { array.getDouble(it).toFloat() }
            } ?: listOf(0f, 0f, 0f),
            
            lineRainbows = json.optJSONArray("lineRainbows")?.let { array ->
                (0 until array.length()).map { array.getBoolean(it) }
            } ?: listOf(false, false, false),
            
            lineOutlines = json.optJSONArray("lineOutlines")?.let { array ->
                (0 until array.length()).map { array.getBoolean(it) }
            } ?: listOf(true, true, true),
            
            lineGlows = json.optJSONArray("lineGlows")?.let { array ->
                (0 until array.length()).map { array.getBoolean(it) }
            } ?: listOf(false, false, false),
            
            lineActive = json.optJSONArray("lineActive")?.let { array ->
                (0 until array.length()).map { array.getBoolean(it) }
            } ?: listOf(true, true, false),
            
            lineFontSpacingOffsets = json.optJSONArray("lineFontSpacingOffsets")?.let { array ->
                (0 until array.length()).map { array.getInt(it) }
            } ?: listOf(0, 0, 0),
            
            lineLetterSpacings = json.optJSONArray("lineLetterSpacings")?.let { array ->
                (0 until array.length()).map { array.getDouble(it).toFloat() }
            } ?: listOf(0f, 0f, 0f),
            
            lineTextOffsetXs = json.optJSONArray("lineTextOffsetXs")?.let { array ->
                (0 until array.length()).map { array.getInt(it) }
            } ?: listOf(0, 0, 0),
            
            lineTextOffsetYs = json.optJSONArray("lineTextOffsetYs")?.let { array ->
                (0 until array.length()).map { array.getInt(it) }
            } ?: listOf(4, 4, 4),
            
            lineSpacingOffset = json.optInt("lineSpacingOffset", -10),
            fontPositionStep = json.optInt("fontPositionStep", 1),
            currentFontIndex = json.optInt("currentFontIndex", 0),
            
            glowStrength = json.optDouble("glowStrength", 1.0).toFloat(),
            glowColorHue = json.optDouble("glowColorHue", 0.0).toFloat(),
            glowSize = json.optInt("glowSize", 5),
            
            crtEnabled = json.optBoolean("crtEnabled", true),
            scanlineAlpha = json.optInt("scanlineAlpha", 20),
            
            decorEnabled = json.optBoolean("decorEnabled", true),
            currentDecorIndex = json.optInt("currentDecorIndex", 0),
            decorScale = json.optDouble("decorScale", 1.0).toFloat(),
            decorOffsetX = json.optInt("decorOffsetX", 0),
            decorOffsetY = json.optInt("decorOffsetY", 0),
            
            shadowOpacity = json.optInt("shadowOpacity", 100)
        )
    }
    
    private fun saveBitmap(bitmap: Bitmap, file: File) {
        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
    }
    
    private fun loadBitmap(file: File): Bitmap? {
        return if (file.exists()) {
            android.graphics.BitmapFactory.decodeFile(file.absolutePath)
        } else {
            null
        }
    }
}

data class TemplateData(
    val name: String,
    val settings: IconSettings,
    val gameImage: Bitmap?,
    val backgroundImage: Bitmap?,
    val frameImage: Bitmap?,
    val decorImage: Bitmap?,
    val previewImage: Bitmap?,
    val fontIndex: Int
)
