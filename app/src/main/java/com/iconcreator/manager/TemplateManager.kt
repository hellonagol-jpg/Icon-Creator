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

    /**
     * Export a template to a ZIP bundle (.icontemplate)
     */
    suspend fun exportTemplateBundle(templateName: String, outputStream: java.io.OutputStream): Boolean = withContext(Dispatchers.IO) {
        try {
            val templateDir = File(templatesDir, templateName)
            if (!templateDir.exists()) return@withContext false
            
            java.util.zip.ZipOutputStream(outputStream).use { zos ->
                templateDir.listFiles()?.forEach { file ->
                    val entry = java.util.zip.ZipEntry(file.name)
                    zos.putNextEntry(entry)
                    file.inputStream().use { it.copyTo(zos) }
                    zos.closeEntry()
                }
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Import a template from a ZIP bundle (.icontemplate)
     */
    suspend fun importTemplateBundle(inputStream: java.io.InputStream, name: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val templateDir = File(templatesDir, name)
            if (templateDir.exists()) {
                templateDir.deleteRecursively()
            }
            templateDir.mkdirs()
            
            java.util.zip.ZipInputStream(inputStream).use { zis ->
                var entry = zis.nextEntry
                while (entry != null) {
                    val file = File(templateDir, entry.name)
                    // Ensure we don't escape the directory (Zip Slip vulnerability)
                    if (file.canonicalPath.startsWith(templateDir.canonicalPath)) {
                        file.outputStream().use { zis.copyTo(it) }
                    }
                    zis.closeEntry()
                    entry = zis.nextEntry
                }
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Export a template to a text string (Legacy)
     */
    suspend fun exportTemplate(templateName: String): String? = withContext(Dispatchers.IO) {
        try {
            val data = loadTemplate(templateName) ?: return@withContext null
            val sb = StringBuilder()
            
            sb.append("ICON_CREATOR_TEMPLATE_V1\n")
            sb.append("NAME:${data.name}\n")
            
            // Settings
            sb.append("SETTINGS_START\n")
            sb.append(settingsToText(data.settings))
            sb.append("SETTINGS_END\n")
            
            // Images
            sb.append("IMAGES_START\n")
            data.gameImage?.let { sb.append("GAME_IMAGE:${bitmapToBase64(it)}\n") }
            data.backgroundImage?.let { sb.append("BACKGROUND:${bitmapToBase64(it)}\n") }
            data.frameImage?.let { sb.append("FRAME:${bitmapToBase64(it)}\n") }
            data.decorImage?.let { sb.append("DECOR:${bitmapToBase64(it)}\n") }
            data.previewImage?.let { sb.append("PREVIEW:${bitmapToBase64(it)}\n") }
            sb.append("IMAGES_END\n")
            
            sb.toString()
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Import a template from a text string
     */
    suspend fun importTemplate(templateText: String): Boolean = withContext(Dispatchers.IO) {
        try {
            if (!templateText.startsWith("ICON_CREATOR_TEMPLATE_V1")) return@withContext false
            
            var name = "ImportedTemplate"
            var settings = IconSettings.createDefault()
            var gameImage: Bitmap? = null
            var backgroundImage: Bitmap? = null
            var frameImage: Bitmap? = null
            var decorImage: Bitmap? = null
            var previewImage: Bitmap? = null
            
            val lines = templateText.lines()
            var inSettings = false
            var inImages = false
            
            val settingsBuilder = StringBuilder()
            
            for (line in lines) {
                when {
                    line.startsWith("NAME:") -> name = line.substringAfter("NAME:")
                    line == "SETTINGS_START" -> inSettings = true
                    line == "SETTINGS_END" -> {
                        inSettings = false
                        settings = textToSettings(settingsBuilder.toString())
                    }
                    line == "IMAGES_START" -> inImages = true
                    line == "IMAGES_END" -> inImages = false
                    inSettings -> settingsBuilder.append(line).append("\n")
                    inImages -> {
                        when {
                            line.startsWith("GAME_IMAGE:") -> gameImage = base64ToBitmap(line.substringAfter("GAME_IMAGE:"))
                            line.startsWith("BACKGROUND:") -> backgroundImage = base64ToBitmap(line.substringAfter("BACKGROUND:"))
                            line.startsWith("FRAME:") -> frameImage = base64ToBitmap(line.substringAfter("FRAME:"))
                            line.startsWith("DECOR:") -> decorImage = base64ToBitmap(line.substringAfter("DECOR:"))
                            line.startsWith("PREVIEW:") -> previewImage = base64ToBitmap(line.substringAfter("PREVIEW:"))
                        }
                    }
                }
            }
            
            saveTemplate(settings, gameImage, backgroundImage, frameImage, decorImage, previewImage, name)
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    private fun settingsToText(settings: IconSettings): String {
        val sb = StringBuilder()
        
        fun add(key: String, value: Any) = sb.append("$key:$value\n")
        
        add("zoomLevel", settings.zoomLevel)
        add("offsetX", settings.offsetX)
        add("offsetY", settings.offsetY)
        add("stretchX", settings.stretchX)
        add("stretchY", settings.stretchY)
        add("brightness", settings.brightness)
        add("imageAlpha", settings.imageAlpha)
        add("bgHue", settings.bgHue)
        add("bgBrightness", settings.bgBrightness)
        add("bgScale", settings.bgScale)
        add("bgOffsetX", settings.bgOffsetX)
        add("bgOffsetY", settings.bgOffsetY)
        add("currentBgIndex", settings.currentBgIndex)
        add("borderHue", settings.borderHue)
        add("borderAlpha", settings.borderAlpha)
        add("frameOffsetX", settings.frameOffsetX)
        add("frameOffsetY", settings.frameOffsetY)
        add("currentFrameIndex", settings.currentFrameIndex)
        add("titleLines", settings.titleLines.joinToString("|"))
        add("lineHues", settings.lineHues.joinToString("|"))
        add("lineRainbows", settings.lineRainbows.joinToString("|"))
        add("lineOutlines", settings.lineOutlines.joinToString("|"))
        add("lineGlows", settings.lineGlows.joinToString("|"))
        add("lineActive", settings.lineActive.joinToString("|"))
        add("lineFontSpacingOffsets", settings.lineFontSpacingOffsets.joinToString("|"))
        add("lineLetterSpacings", settings.lineLetterSpacings.joinToString("|"))
        add("lineTextOffsetXs", settings.lineTextOffsetXs.joinToString("|"))
        add("lineTextOffsetYs", settings.lineTextOffsetYs.joinToString("|"))
        add("lineSpacingOffset", settings.lineSpacingOffset)
        add("fontPositionStep", settings.fontPositionStep)
        add("currentFontIndex", settings.currentFontIndex)
        add("glowStrength", settings.glowStrength)
        add("glowColorHue", settings.glowColorHue)
        add("glowSize", settings.glowSize)
        add("crtEnabled", settings.crtEnabled)
        add("scanlineAlpha", settings.scanlineAlpha)
        add("decorEnabled", settings.decorEnabled)
        add("currentDecorIndex", settings.currentDecorIndex)
        add("decorScale", settings.decorScale)
        add("decorOffsetX", settings.decorOffsetX)
        add("decorOffsetY", settings.decorOffsetY)
        add("shadowOpacity", settings.shadowOpacity)
        add("glitchEnabled", settings.glitchEnabled)
        add("chromaticAberration", settings.chromaticAberration)
        add("noiseOpacity", settings.noiseOpacity)
        add("glitchDisplacement", settings.glitchDisplacement)
        
        return sb.toString()
    }

    private fun textToSettings(text: String): IconSettings {
        val map = text.lines().filter { it.contains(":") }.associate { 
            it.substringBefore(":") to it.substringAfter(":") 
        }
        
        fun getInt(key: String, default: Int) = map[key]?.toIntOrNull() ?: default
        fun getFloat(key: String, default: Float) = map[key]?.toFloatOrNull() ?: default
        fun getBool(key: String, default: Boolean) = map[key]?.toBoolean() ?: default
        fun getListStr(key: String, default: List<String>) = map[key]?.split("|") ?: default
        fun getListInt(key: String, default: List<Int>) = map[key]?.split("|")?.mapNotNull { it.toIntOrNull() } ?: default
        fun getListFloat(key: String, default: List<Float>) = map[key]?.split("|")?.mapNotNull { it.toFloatOrNull() } ?: default
        fun getListBool(key: String, default: List<Boolean>) = map[key]?.split("|")?.map { it.toBoolean() } ?: default

        return IconSettings(
            zoomLevel = getInt("zoomLevel", 50),
            offsetX = getInt("offsetX", 0),
            offsetY = getInt("offsetY", 0),
            stretchX = getFloat("stretchX", 1.0f),
            stretchY = getFloat("stretchY", 1.0f),
            brightness = getFloat("brightness", 0.9f),
            imageAlpha = getFloat("imageAlpha", 1.0f),
            bgHue = getFloat("bgHue", 0f),
            bgBrightness = getFloat("bgBrightness", 1.0f),
            bgScale = getFloat("bgScale", 1.0f),
            bgOffsetX = getInt("bgOffsetX", 0),
            bgOffsetY = getInt("bgOffsetY", 0),
            currentBgIndex = getInt("currentBgIndex", 0),
            borderHue = getFloat("borderHue", 0f),
            borderAlpha = getFloat("borderAlpha", 1.0f),
            frameOffsetX = getInt("frameOffsetX", 0),
            frameOffsetY = getInt("frameOffsetY", 0),
            currentFrameIndex = getInt("currentFrameIndex", 0),
            titleLines = getListStr("titleLines", listOf("Icon", "Creator")),
            lineHues = getListFloat("lineHues", listOf(0f, 0f, 0f)),
            lineRainbows = getListBool("lineRainbows", listOf(false, false, false)),
            lineOutlines = getListBool("lineOutlines", listOf(true, true, true)),
            lineGlows = getListBool("lineGlows", listOf(false, false, false)),
            lineActive = getListBool("lineActive", listOf(true, true, false)),
            lineFontSpacingOffsets = getListInt("lineFontSpacingOffsets", listOf(0, 0, 0)),
            lineLetterSpacings = getListFloat("lineLetterSpacings", listOf(0f, 0f, 0f)),
            lineTextOffsetXs = getListInt("lineTextOffsetXs", listOf(0, 0, 0)),
            lineTextOffsetYs = getListInt("lineTextOffsetYs", listOf(4, 4, 4)),
            lineSpacingOffset = getInt("lineSpacingOffset", -10),
            fontPositionStep = getInt("fontPositionStep", 1),
            currentFontIndex = getInt("currentFontIndex", 0),
            glowStrength = getFloat("glowStrength", 1.0f),
            glowColorHue = getFloat("glowColorHue", 0f),
            glowSize = getInt("glowSize", 5),
            crtEnabled = getBool("crtEnabled", true),
            scanlineAlpha = getInt("scanlineAlpha", 20),
            decorEnabled = getBool("decorEnabled", true),
            currentDecorIndex = getInt("currentDecorIndex", 0),
            decorScale = getFloat("decorScale", 1.0f),
            decorOffsetX = getInt("decorOffsetX", 0),
            decorOffsetY = getInt("decorOffsetY", 0),
            shadowOpacity = getInt("shadowOpacity", 100),
            glitchEnabled = getBool("glitchEnabled", false),
            chromaticAberration = getFloat("chromaticAberration", 0f),
            noiseOpacity = getInt("noiseOpacity", 0),
            glitchDisplacement = getFloat("glitchDisplacement", 0f)
        )
    }

    private fun bitmapToBase64(bitmap: Bitmap): String {
        val outputStream = java.io.ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
        return android.util.Base64.encodeToString(outputStream.toByteArray(), android.util.Base64.DEFAULT).replace("\n", "")
    }

    private fun base64ToBitmap(base64: String): Bitmap? {
        return try {
            val bytes = android.util.Base64.decode(base64, android.util.Base64.DEFAULT)
            android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        } catch (e: Exception) {
            null
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
        
        // Glitch settings
        json.put("glitchEnabled", settings.glitchEnabled)
        json.put("chromaticAberration", settings.chromaticAberration)
        json.put("noiseOpacity", settings.noiseOpacity)
        json.put("glitchDisplacement", settings.glitchDisplacement)
        
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
            
            shadowOpacity = json.optInt("shadowOpacity", 100),
            
            glitchEnabled = json.optBoolean("glitchEnabled", false),
            chromaticAberration = json.optDouble("chromaticAberration", 0.0).toFloat(),
            noiseOpacity = json.optInt("noiseOpacity", 0),
            glitchDisplacement = json.optDouble("glitchDisplacement", 0.0).toFloat()
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
