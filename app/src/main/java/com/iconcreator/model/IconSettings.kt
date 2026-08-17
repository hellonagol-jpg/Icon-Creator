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
    
    // Background settings
    var bgHue: Float = 0f,
    var bgBrightness: Float = 1.0f,
    var bgScale: Float = 1.0f,
    var bgOffsetX: Int = 0,
    var bgOffsetY: Int = 0,
    var currentBgIndex: Int = 0,
    
    // Border/Frame settings
    var borderHue: Float = 0f,
    var borderDirectRgb: IntArray? = null, // RGB values when not using hue
    var borderAlpha: Float = 1.0f,
    var frameOffsetX: Int = 0,
    var frameOffsetY: Int = 0,
    var currentFrameIndex: Int = 0,
    
    // Text settings
    var titleLines: List<String> = listOf("Icon", "Creator"),
    var lineHues: List<Float> = listOf(0f, 0f, 0f),
    var lineRainbows: List<Boolean> = listOf(false, false, false),
    var lineOutlines: List<Boolean> = listOf(true, true, true),
    var lineActive: List<Boolean> = listOf(true, true, false),
    var lineFontSpacingOffsets: List<Int> = listOf(-1, -1, -1),
    var lineTextOffsetXs: List<Int> = listOf(0, 0, 0),
    var lineTextOffsetYs: List<Int> = listOf(4, 4, 4),
    var lineSpacingOffset: Int = -10,
    var fontPositionStep: Int = 1,
    var currentFontIndex: Int = 0,
    
    // Glow settings
    var glowEnabled: Boolean = false,
    var glowStrength: Float = 1.0f,
    var glowColorHue: Float = 0f,
    var glowSize: Int = 5,
    var glowDirectRgb: IntArray? = null, // RGB values when not using hue
    
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
    var shadowOpacity: Int = 100
) {
    // Direct RGB overrides for text lines
    var directRgb: MutableMap<Int, IntArray> = mutableMapOf()
    
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
            bgHue = bgHue,
            bgBrightness = bgBrightness,
            bgScale = bgScale,
            bgOffsetX = bgOffsetX,
            bgOffsetY = bgOffsetY,
            currentBgIndex = currentBgIndex,
            borderHue = borderHue,
            borderDirectRgb = borderDirectRgb?.copyOf(),
            borderAlpha = borderAlpha,
            frameOffsetX = frameOffsetX,
            frameOffsetY = frameOffsetY,
            currentFrameIndex = currentFrameIndex,
            titleLines = titleLines.toList(),
            lineHues = lineHues.toList(),
            lineRainbows = lineRainbows.toList(),
            lineOutlines = lineOutlines.toList(),
            lineActive = lineActive.toList(),
            lineFontSpacingOffsets = lineFontSpacingOffsets.toList(),
            lineTextOffsetXs = lineTextOffsetXs.toList(),
            lineTextOffsetYs = lineTextOffsetYs.toList(),
            lineSpacingOffset = lineSpacingOffset,
            fontPositionStep = fontPositionStep,
            currentFontIndex = currentFontIndex,
            glowEnabled = glowEnabled,
            glowStrength = glowStrength,
            glowColorHue = glowColorHue,
            glowSize = glowSize,
            glowDirectRgb = glowDirectRgb?.copyOf(),
            crtEnabled = crtEnabled,
            scanlineAlpha = scanlineAlpha,
            decorEnabled = decorEnabled,
            currentDecorIndex = currentDecorIndex,
            decorScale = decorScale,
            decorOffsetX = decorOffsetX,
            decorOffsetY = decorOffsetY,
            shadowOpacity = shadowOpacity
        ).also { it.directRgb = directRgb.toMutableMap() }
    }
}
