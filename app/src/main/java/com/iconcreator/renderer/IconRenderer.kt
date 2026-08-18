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
        const val WIDTH = 512
        const val HEIGHT = 512
        const val RENDER_SIZE = 512
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
        borderShadow: Bitmap? = null
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
            val scale = (0.2f + ((settings.zoomLevel + 100) / 200f) * 1.8f) * 2f // Doubled scale for 512
            val scaledGame = scaleBitmap(game, scale * settings.stretchX, scale * settings.stretchY)
            val brightnessAdjustedGame = applyBrightness(scaledGame, settings.brightness)
            
            val pasteX = (RENDER_SIZE - brightnessAdjustedGame.width) / 2 + settings.offsetX * 2
            val pasteY = (RENDER_SIZE - brightnessAdjustedGame.height) / 2 + settings.offsetY * 2
            canvas.drawBitmap(brightnessAdjustedGame, pasteX.toFloat(), pasteY.toFloat(), null)
        }
        
        kotlinx.coroutines.yield()
        // Draw CRT scanlines
        if (settings.crtEnabled) {
            drawScanlines(canvas, settings.scanlineAlpha)
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
            var tintedFrame = if (settings.borderDirectRgb != null) {
                applyColorTint(frame, settings.borderDirectRgb!!)
            } else {
                applyHueShift(frame, settings.borderHue)
            }
            
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
    
    private fun applyColorTint(bitmap: Bitmap, rgba: IntArray): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, Bitmap.Config.ARGB_8888)
        val paint = Paint()
        val color = if (rgba.size >= 4) {
            Color.argb(rgba[0], rgba[1], rgba[2], rgba[3])
        } else {
            Color.rgb(rgba[0], rgba[1], rgba[2])
        }
        paint.colorFilter = android.graphics.PorterDuffColorFilter(
            color,
            PorterDuff.Mode.SRC_IN
        )
        
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
    
    private fun drawScanlines(canvas: Canvas, alpha: Int) {
        val paint = Paint()
        paint.color = Color.argb(alpha, 0, 0, 0)
        paint.style = Paint.Style.FILL
        
        for (y in 0 until RENDER_SIZE step 2) {
            canvas.drawRect(0f, y.toFloat(), RENDER_SIZE.toFloat(), (y + 1).toFloat(), paint)
        }
    }
    
    private fun drawText(canvas: Canvas, settings: IconSettings, font: Typeface?) {
        val activeLines = settings.titleLines.zip(settings.lineActive).filter { it.second }
        val baseSize = when (activeLines.size) {
            1 -> 88 // Doubled for 512
            2 -> 76
            else -> 64
        }
        
        val paint = TextPaint(Paint.ANTI_ALIAS_FLAG)
        font?.let { paint.typeface = it }
        
        // Center vertically based on number of lines
        // Python used specific Y values: 456 if 1, 416 if 2, 386 if 3 (mapped to 512)
        // Let's use the logic that works with the offsets
        val totalSpacing = settings.lineSpacingOffset * 2
        var yOffset = (RENDER_SIZE * 0.85f).toInt() - ((activeLines.size - 1) * (baseSize + totalSpacing))
        
        for ((line, isActive) in activeLines) {
            if (!isActive) continue
            
            val lineIndex = settings.titleLines.indexOf(line)
            val fontSize = (baseSize + settings.lineFontSpacingOffsets.getOrElse(lineIndex) { 0 } * 2).coerceIn(40, 1000)
            paint.textSize = fontSize.toFloat()
            
            // Get text color
            val color = if (settings.directRgb.containsKey(lineIndex)) {
                val rgba = settings.directRgb[lineIndex]!!
                if (rgba.size >= 4) {
                    Color.argb(rgba[0], rgba[1], rgba[2], rgba[3])
                } else {
                    Color.rgb(rgba[0], rgba[1], rgba[2])
                }
            } else {
                getSolidColor(settings.lineHues.getOrElse(lineIndex) { 0f })
            }
            
            paint.color = color
            
            val textWidth = paint.measureText(line)
            val textX = (RENDER_SIZE - textWidth) / 2 + settings.lineTextOffsetXs.getOrElse(lineIndex) { 0 } * 2
            val textY = yOffset.toFloat() + settings.lineTextOffsetYs.getOrElse(lineIndex) { 4 } * 2
            
            // Draw outline
            if (settings.lineOutlines.getOrElse(lineIndex) { true }) {
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = 6f
                paint.color = Color.BLACK
                canvas.drawText(line, textX, textY, paint)
            }
            
            // Draw main text
            paint.style = Paint.Style.FILL
            paint.color = color
            canvas.drawText(line, textX, textY, paint)
            
            // Draw glow
            if (settings.glowEnabled) {
                val glowPaint = Paint(paint)
                glowPaint.style = Paint.Style.STROKE
                glowPaint.strokeWidth = settings.glowSize.toFloat() * 2f
                glowPaint.maskFilter = android.graphics.BlurMaskFilter(settings.glowSize * settings.glowStrength * 2f, android.graphics.BlurMaskFilter.Blur.OUTER)
                glowPaint.color = getGlowColor(settings)
                canvas.drawText(line, textX, textY, glowPaint)
            }
            
            yOffset += (fontSize + totalSpacing)
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
    
    private fun getGlowColor(settings: IconSettings): Int {
        val glowDirectRgba = settings.glowDirectRgb
        return if (glowDirectRgba != null) {
            if (glowDirectRgba.size >= 4) {
                Color.argb(glowDirectRgba[0], glowDirectRgba[1], glowDirectRgba[2], glowDirectRgba[3])
            } else {
                Color.rgb(glowDirectRgba[0], glowDirectRgba[1], glowDirectRgba[2])
            }
        } else {
            getSolidColor(settings.glowColorHue)
        }
    }
}
