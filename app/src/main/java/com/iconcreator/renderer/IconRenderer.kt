package com.iconcreator.renderer

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.ColorMatrix
import android.graphics.ColorMatrixColorFilter
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.PorterDuffXfermode
import android.graphics.Rect
import android.graphics.Typeface
import android.text.TextPaint
import com.iconcreator.model.IconSettings

/**
 * Handles all image rendering operations for the icon creator.
 * Port of PIL-based rendering to Android Bitmap/Canvas.
 */
class IconRenderer {
    
    companion object {
        const val WIDTH = 1024
        const val HEIGHT = 1024
        const val RENDER_SIZE = 1024
        const val PREVIEW_SIZE = 512
    }
    
    /**
     * Render the complete icon with all layers and effects
     */
    suspend fun renderIcon(
        settings: IconSettings,
        gameImage: Bitmap?,
        backgroundImage: Bitmap?,
        frameImage: Bitmap?,
        decorImage: Bitmap?,
        font: Typeface?,
        alphaMask: Bitmap? = null,
        alpha2Mask: Bitmap? = null,
        borderShadow: Bitmap? = null,
        scanlineOverlay: Bitmap? = null
    ): Bitmap = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Default) {
        val baseBitmap = Bitmap.createBitmap(WIDTH, HEIGHT, Bitmap.Config.ARGB_8888)
        kotlinx.coroutines.yield()
        val scaledBase = Bitmap.createScaledBitmap(baseBitmap, RENDER_SIZE, RENDER_SIZE, true)
        val canvas = Canvas(scaledBase)
        
        // Draw background
        backgroundImage?.let { bg ->
            kotlinx.coroutines.yield()
            // First scale background to fill RENDER_SIZE
            val baseScale = RENDER_SIZE.toFloat() / bg.width.coerceAtLeast(bg.height)
            val fillBg = scaleBitmap(bg, baseScale * settings.bgScale)
            
            val hueShiftedBg = applyHueShift(fillBg, settings.bgHue)
            val brightnessAdjustedBg = applyBrightness(hueShiftedBg, settings.bgBrightness)
            
            val pasteX = (RENDER_SIZE - brightnessAdjustedBg.width) / 2 + settings.bgOffsetX * 2 // Doubled offset for 512
            val pasteY = (RENDER_SIZE - brightnessAdjustedBg.height) / 2 + settings.bgOffsetY * 2
            canvas.drawBitmap(brightnessAdjustedBg, pasteX.toFloat(), pasteY.toFloat(), null)
        }
        
        // Draw game image
        gameImage?.let { game ->
            kotlinx.coroutines.yield()
            // Base scale to fit the image inside RENDER_SIZE
            val baseScale = RENDER_SIZE.toFloat() / Math.max(game.width, game.height)
            // Zoom multiplier (centered at 50 for 1x fit)
            val zoomFactor = if (settings.zoomLevel >= 50) {
                1f + (settings.zoomLevel - 50) / 50f // 50->1x, 100->2x, 200->4x
            } else {
                (settings.zoomLevel + 100) / 150f // 50->1x, 0->0.66x, -100->0x
            }
            val scale = baseScale * zoomFactor
            
            val scaledGame = scaleBitmap(game, scale * settings.stretchX, scale * settings.stretchY)
            val brightnessAdjustedGame = applyBrightness(scaledGame, settings.brightness)
            
            val gamePaint = Paint().apply {
                alpha = (settings.imageAlpha * 255).toInt().coerceIn(0, 255)
            }
            
            val pasteX = (RENDER_SIZE - brightnessAdjustedGame.width) / 2 + settings.offsetX * 2
            val pasteY = (RENDER_SIZE - brightnessAdjustedGame.height) / 2 + settings.offsetY * 2
            canvas.drawBitmap(brightnessAdjustedGame, pasteX.toFloat(), pasteY.toFloat(), gamePaint)
        }
        
        kotlinx.coroutines.yield()
        // Draw CRT scanlines
        if (settings.crtEnabled && scanlineOverlay != null) {
            drawScanlines(canvas, scanlineOverlay, settings.scanlineAlpha)
        }
        
        // Draw text
        drawText(canvas, settings, font)
        
        kotlinx.coroutines.yield()
        // Draw decoration
        if (settings.decorEnabled && decorImage != null) {
            val margin = 44f // Doubled margin for 512
            val scaledDecor = scaleBitmap(decorImage, settings.decorScale * 2f)
            val decorX = RENDER_SIZE - scaledDecor.width - margin + settings.decorOffsetX * 2
            val decorY = RENDER_SIZE - scaledDecor.height - margin + settings.decorOffsetY * 2
            canvas.drawBitmap(scaledDecor, decorX, decorY, null)
        }
        
        // Draw Border Shadow (over background/game as per user instruction)
        borderShadow?.let { shadow ->
            kotlinx.coroutines.yield()
            val shadowOpacity = settings.shadowOpacity
            val shadowPaint = Paint().apply {
                alpha = (shadowOpacity * 2.55f).toInt().coerceIn(0, 255)
            }
            val scaledShadow = Bitmap.createScaledBitmap(shadow, RENDER_SIZE, RENDER_SIZE, true)
            canvas.drawBitmap(scaledShadow, 0f, 0f, shadowPaint)
        }

        // Draw frame (Border) on top of shadow
        frameImage?.let { frame ->
            kotlinx.coroutines.yield()
            var tintedFrame = applyHueShift(frame, settings.borderHue)
            
            // Recreate Python's frame.putalpha(alpha2) using luminance
            alpha2Mask?.let { mask ->
                val maskBitmap = applyLuminanceToAlpha(mask, tintedFrame.width, tintedFrame.height)
                val maskedFrame = Bitmap.createBitmap(tintedFrame.width, tintedFrame.height, Bitmap.Config.ARGB_8888)
                val mCanvas = Canvas(maskedFrame)
                mCanvas.drawBitmap(tintedFrame, 0f, 0f, null)
                
                val maskPaint = Paint().apply {
                    xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_IN)
                }
                mCanvas.drawBitmap(maskBitmap, 0f, 0f, maskPaint)
                tintedFrame = maskedFrame
            }
            
            val framePaint = Paint().apply {
                alpha = (settings.borderAlpha * 255).toInt().coerceIn(0, 255)
            }
            
            val scaledFrame = Bitmap.createScaledBitmap(tintedFrame, RENDER_SIZE, RENDER_SIZE, true)
            val frameX = (RENDER_SIZE - scaledFrame.width) / 2 + settings.frameOffsetX
            val frameY = (RENDER_SIZE - scaledFrame.height) / 2 + settings.frameOffsetY
            canvas.drawBitmap(scaledFrame, frameX.toFloat(), frameY.toFloat(), framePaint)
        }
        
        kotlinx.coroutines.yield()
        // Create final output with alpha mask
        val result = Bitmap.createBitmap(RENDER_SIZE, RENDER_SIZE, Bitmap.Config.ARGB_8888)
        val resultCanvas = Canvas(result)
        resultCanvas.drawBitmap(scaledBase, 0f, 0f, null)
        
        // Apply alpha mask to the final icon (Python: inner.putalpha(self.alpha_mask_img))
        alphaMask?.let { mask ->
            kotlinx.coroutines.yield()
            val maskBitmap = applyLuminanceToAlpha(mask, RENDER_SIZE, RENDER_SIZE)
            val maskPaint = Paint().apply {
                xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_IN)
            }
            resultCanvas.drawBitmap(maskBitmap, 0f, 0f, maskPaint)
        }
        
        kotlinx.coroutines.yield()
        Bitmap.createScaledBitmap(result, PREVIEW_SIZE, PREVIEW_SIZE, true)
    }

    /**
     * Converts a grayscale/color bitmap into an alpha mask based on luminance.
     * Mimics PIL's putalpha() when used with an "L" mode image.
     */
    private fun applyLuminanceToAlpha(mask: Bitmap, width: Int, height: Int): Bitmap {
        val scaledMask = Bitmap.createScaledBitmap(mask, width, height, true)
        val result = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(result)
        val paint = Paint()
        
        // Matrix to move RGB luminance into the Alpha channel:
        // A' = 0.2126*R + 0.7152*G + 0.0722*B
        val matrix = ColorMatrix(floatArrayOf(
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            0.2126f, 0.7152f, 0.0722f, 0f, 0f
        ))
        paint.colorFilter = ColorMatrixColorFilter(matrix)
        canvas.drawBitmap(scaledMask, 0f, 0f, paint)
        return result
    }
    
    private fun scaleBitmap(bitmap: Bitmap, scaleX: Float, scaleY: Float = scaleX): Bitmap {
        val newWidth = (bitmap.width * scaleX).toInt().coerceAtLeast(1)
        val newHeight = (bitmap.height * scaleY).toInt().coerceAtLeast(1)
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }
    
    private fun applyHueShift(bitmap: Bitmap, hue: Float): Bitmap {
        if (hue == 0f) return bitmap
        
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, Bitmap.Config.ARGB_8888)
        val matrix = ColorMatrix()
        
        // Proper hue rotation matrix
        val cos = Math.cos(hue.toDouble() * Math.PI / 180.0).toFloat()
        val sin = Math.sin(hue.toDouble() * Math.PI / 180.0).toFloat()
        
        val lumR = 0.213f
        val lumG = 0.715f
        val lumB = 0.072f
        
        matrix.set(floatArrayOf(
            lumR + cos * (1 - lumR) + sin * (-lumR), lumG + cos * (-lumG) + sin * (-lumG), lumB + cos * (-lumB) + sin * (1 - lumB), 0f, 0f,
            lumR + cos * (-lumR) + sin * (0.143f), lumG + cos * (1 - lumG) + sin * (0.140f), lumB + cos * (-lumB) + sin * (-0.283f), 0f, 0f,
            lumR + cos * (-lumR) + sin * (-(1 - lumR)), lumG + cos * (-lumG) + sin * (lumG), lumB + cos * (1 - lumB) + sin * (lumG), 0f, 0f,
            0f, 0f, 0f, 1f, 0f
        ))
        
        val paint = Paint()
        paint.colorFilter = ColorMatrixColorFilter(matrix)
        
        val canvas = Canvas(result)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        
        return result
    }
    
    private fun applyBrightness(bitmap: Bitmap, brightness: Float): Bitmap {
        if (brightness == 1.0f) return bitmap
        
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, Bitmap.Config.ARGB_8888)
        val colorMatrix = ColorMatrix()
        colorMatrix.setScale(brightness, brightness, brightness, 1f)
        
        val paint = Paint()
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        
        val canvas = Canvas(result)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        
        return result
    }
    
    private fun drawScanlines(canvas: Canvas, overlay: Bitmap, alpha: Int) {
        val paint = Paint().apply {
            this.alpha = (alpha * 2.55f).toInt().coerceIn(0, 255)
        }
        val scaledOverlay = Bitmap.createScaledBitmap(overlay, RENDER_SIZE, RENDER_SIZE, true)
        canvas.drawBitmap(scaledOverlay, 0f, 0f, paint)
    }
    
    private fun drawText(canvas: Canvas, settings: IconSettings, font: Typeface?) {
        val activeLinesIndices = settings.lineActive.indices.filter { settings.lineActive[it] }
        val baseSize = when (activeLinesIndices.size) {
            1 -> 88 // Doubled for 512
            2 -> 76
            else -> 64
        }
        
        val paint = TextPaint(Paint.ANTI_ALIAS_FLAG)
        font?.let { paint.typeface = it }
        
        val totalSpacing = settings.lineSpacingOffset * 2
        var yOffset = (RENDER_SIZE * 0.85f).toInt() - ((activeLinesIndices.size - 1) * (baseSize + totalSpacing))
        
        for (lineIndex in activeLinesIndices) {
            val line = settings.titleLines.getOrElse(lineIndex) { "" }
            var fontSize = (baseSize + settings.lineFontSpacingOffsets.getOrElse(lineIndex) { 0 } * 2).coerceIn(10, 1000).toFloat()
            paint.textSize = fontSize
            
            // Apply letter spacing
            val letterSpacing = settings.lineLetterSpacings.getOrElse(lineIndex) { 0f }
            paint.letterSpacing = letterSpacing / fontSize
            
            // Auto-resize if text is too wide
            val maxWidth = RENDER_SIZE * 0.9f
            var textWidth = paint.measureText(line)
            if (textWidth > maxWidth) {
                val scale = maxWidth / textWidth
                fontSize *= scale
                paint.textSize = fontSize
                textWidth = paint.measureText(line)
            }
            
            // Get text color
            val color = getSolidColor(settings.lineHues.getOrElse(lineIndex) { 0f })
            paint.color = color
            
            val textX = (RENDER_SIZE - textWidth) / 2 + settings.lineTextOffsetXs.getOrElse(lineIndex) { 0 } * 2
            val textY = yOffset.toFloat() + settings.lineTextOffsetYs.getOrElse(lineIndex) { 4 } * 2
            
            // Apply Rainbow effect if enabled
            if (settings.lineRainbows.getOrElse(lineIndex) { false }) {
                val rainbowShader = android.graphics.LinearGradient(
                    textX, textY - fontSize/2, textX + textWidth, textY - fontSize/2,
                    intArrayOf(
                        Color.RED, 
                        Color.rgb(255, 165, 0), // Orange
                        Color.YELLOW, 
                        Color.GREEN, 
                        Color.BLUE, 
                        Color.rgb(75, 0, 130), // Indigo
                        Color.rgb(238, 130, 238) // Violet
                    ),
                    null,
                    android.graphics.Shader.TileMode.CLAMP
                )
                paint.shader = rainbowShader
            } else {
                paint.shader = null
            }
            
            // Draw glow (now before outline and text)
            if (settings.lineGlows.getOrElse(lineIndex) { false }) {
                val glowPaint = Paint(paint)
                glowPaint.style = Paint.Style.STROKE
                // Reduced size and strength for a less intense glow
                glowPaint.strokeWidth = settings.glowSize.toFloat() * 1.2f
                glowPaint.maskFilter = android.graphics.BlurMaskFilter(settings.glowSize * settings.glowStrength * 1.0f, android.graphics.BlurMaskFilter.Blur.NORMAL)
                
                // Match text color/effect for glow
                if (settings.lineRainbows.getOrElse(lineIndex) { false }) {
                    val rainbowShader = android.graphics.LinearGradient(
                        textX, textY - fontSize/2, textX + textWidth, textY - fontSize/2,
                        intArrayOf(
                            Color.RED, Color.rgb(255, 165, 0), Color.YELLOW, 
                            Color.GREEN, Color.BLUE, Color.rgb(75, 0, 130), Color.rgb(238, 130, 238)
                        ),
                        null,
                        android.graphics.Shader.TileMode.CLAMP
                    )
                    glowPaint.shader = rainbowShader
                } else {
                    glowPaint.color = color 
                    glowPaint.shader = null
                }
                
                canvas.drawText(line, textX, textY, glowPaint)
            }
            
            // Draw outline
            if (settings.lineOutlines.getOrElse(lineIndex) { true }) {
                val originalShader = paint.shader
                paint.shader = null // Outline should be solid black
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = fontSize * 0.08f // Relative stroke width
                paint.color = Color.BLACK
                canvas.drawText(line, textX, textY, paint)
                paint.shader = originalShader
            }
            
            // Draw main text
            paint.style = Paint.Style.FILL
            paint.color = color
            canvas.drawText(line, textX, textY, paint)
            
            yOffset += (fontSize + totalSpacing).toInt()
        }
    }
    
    private fun getSolidColor(hue: Float): Int {
        val t = (hue / 360f).coerceIn(0f, 1f)
        return when {
            t < 0.25f -> {
                val tt = t / 0.25f
                Color.rgb(255, (255 * (1 - tt * 0.6)).toInt(), (255 * (1 - tt * 0.15)).toInt())
            }
            t < 0.45f -> {
                val tt = (t - 0.25f) / 0.20f
                Color.rgb(255, (153 * (1 - tt)).toInt(), (204 * (1 - tt)).toInt())
            }
            t < 0.65f -> {
                val tt = (t - 0.45f) / 0.20f
                Color.rgb(255, (tt * 255).toInt(), 0)
            }
            t < 0.80f -> {
                val tt = (t - 0.65f) / 0.15f
                Color.rgb((255 * (1 - tt)).toInt(), 255, (tt * 255).toInt())
            }
           t < 0.90f -> {
                val tt = (t - 0.80f) / 0.10f
                Color.rgb((255 * (1 - tt * 2)).toInt(), (255 * (1 - tt * 1.5)).toInt(), 255)
            }
            else -> {
                val tt = (t - 0.90f) / 0.10f
                val gray = (200 * (1 - tt)).toInt()
                Color.rgb(gray, gray, gray)
            }
        }
    }
}
