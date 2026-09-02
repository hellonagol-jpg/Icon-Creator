package com.iconcreator.model

import android.graphics.Bitmap

/**
 * Data class representing all settings for the icon creator
 */
data class IconSettings(
    // Image settings
    var zoomLevel: Int = 50,
    var offsetX: Int = 0,
    var offsetY: Int = 0,
    var stretchX: Float = 1.0f,
    var stretchY: Float = 1.0f,
    var brightness: Float = 0.9f,
    var imageAlpha: Float = 1.0f,
    
    // Background settings
    var bgHue: Float = 0f,
    var bgBrightness: Float = 1.0f,
    var bgScale: Float = 1.0f,
    var bgOffsetX: Int = 0,
    var bgOffsetY: Int = 0,
    var currentBgIndex: Int = 0,
    
    // Border/Frame settings
    var borderHue: Float = 0f,
    var borderAlpha: Float = 1.0f,
    var frameOffsetX: Int = 0,
    var frameOffsetY: Int = 0,
    var currentFrameIndex: Int = 0,
    
    // Text settings
    var titleLines: List<String> = listOf("Icon", "Creator"),
    var lineHues: List<Float> = listOf(0f, 0f, 0f),
    var lineRainbows: List<Boolean> = listOf(false, false, false),
    var lineOutlines: List<Boolean> = listOf(true, true, true),
    var lineGlows: List<Boolean> = listOf(false, false, false),
    var lineActive: List<Boolean> = listOf(true, true, false),
    var lineFontSpacingOffsets: List<Int> = listOf(0, 0, 0),
    var lineLetterSpacings: List<Float> = listOf(0f, 0f, 0f),
    var lineTextOffsetXs: List<Int> = listOf(0, 0, 0),
    var lineTextOffsetYs: List<Int> = listOf(4, 4, 4),
    var lineSpacingOffset: Int = -10,
    var fontPositionStep: Int = 1,
    var currentFontIndex: Int = 0,
    
    // Glow settings
    var glowStrength: Float = 1.0f,
    var glowColorHue: Float = 0f,
    var glowSize: Int = 5,
    
    // CRT settings
    var crtEnabled: Boolean = true,
    var scanlineAlpha: Int = 20,
    
    // Decoration settings
    var decorEnabled: Boolean = true,
    var currentDecorIndex: Int = 0,
    var decorScale: Float = 1.0f,
    var decorOffsetX: Int = 0,
    var decorOffsetY: Int = 0,
    
    // Shadow settings
    var shadowOpacity: Int = 100,
    
    // Glitch settings
    var glitchEnabled: Boolean = false,
    var chromaticAberration: Float = 5f, // 0 to 20
    var noiseOpacity: Int = 0, // 0 to 100
    var glitchDisplacement: Float = 0f // 0 to 50
) {
    
    companion object {
        fun createDefault(): IconSettings {
            return IconSettings()
        }
    }
    
    fun copy(): IconSettings {
        return IconSettings(
            zoomLevel = zoomLevel,
            offsetX = offsetX,
            offsetY = offsetY,
            stretchX = stretchX,
            stretchY = stretchY,
            brightness = brightness,
            imageAlpha = imageAlpha,
            bgHue = bgHue,
            bgBrightness = bgBrightness,
            bgScale = bgScale,
            bgOffsetX = bgOffsetX,
            bgOffsetY = bgOffsetY,
            currentBgIndex = currentBgIndex,
            borderHue = borderHue,
            borderAlpha = borderAlpha,
            frameOffsetX = frameOffsetX,
            frameOffsetY = frameOffsetY,
            currentFrameIndex = currentFrameIndex,
            titleLines = titleLines.toList(),
            lineHues = lineHues.toList(),
            lineRainbows = lineRainbows.toList(),
            lineOutlines = lineOutlines.toList(),
            lineGlows = lineGlows.toList(),
            lineActive = lineActive.toList(),
            lineFontSpacingOffsets = lineFontSpacingOffsets.toList(),
            lineLetterSpacings = lineLetterSpacings.toList(),
            lineTextOffsetXs = lineTextOffsetXs.toList(),
            lineTextOffsetYs = lineTextOffsetYs.toList(),
            lineSpacingOffset = lineSpacingOffset,
            fontPositionStep = fontPositionStep,
            currentFontIndex = currentFontIndex,
            glowStrength = glowStrength,
            glowColorHue = glowColorHue,
            glowSize = glowSize,
            crtEnabled = crtEnabled,
            scanlineAlpha = scanlineAlpha,
            decorEnabled = decorEnabled,
            currentDecorIndex = currentDecorIndex,
            decorScale = decorScale,
            decorOffsetX = decorOffsetX,
            decorOffsetY = decorOffsetY,
            shadowOpacity = shadowOpacity,
            glitchEnabled = glitchEnabled,
            chromaticAberration = chromaticAberration,
            noiseOpacity = noiseOpacity,
            glitchDisplacement = glitchDisplacement
        )
    }
}
