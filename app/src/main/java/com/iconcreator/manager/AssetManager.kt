package com.iconcreator.manager

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Typeface
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

/**
 * Manages loading assets from the Android assets folder
 */
class AssetManager(private val context: Context) {
    
    /**
     * List all files in a specific asset directory
     */
    suspend fun listAssetFiles(path: String): List<String> = withContext(Dispatchers.IO) {
        try {
            context.assets.list(path)?.toList() ?: emptyList()
        } catch (e: IOException) {
            emptyList()
        }
    }
    
    /**
     * Load a bitmap from assets
     */
    suspend fun loadBitmap(path: String): Bitmap? = withContext(Dispatchers.IO) {
        try {
            context.assets.open(path).use { inputStream ->
                BitmapFactory.decodeStream(inputStream)
            }
        } catch (e: IOException) {
            null
        }
    }
    
    /**
     * Load a font from assets
     */
    suspend fun loadFont(path: String): Typeface? = withContext(Dispatchers.IO) {
        try {
            Typeface.createFromAsset(context.assets, path)
        } catch (e: RuntimeException) {
            null
        }
    }
    
    /**
     * Load all backgrounds
     */
    suspend fun loadBackgrounds(): List<Bitmap> = withContext(Dispatchers.IO) {
        val files = listAssetFiles("Backgrounds")
        files.mapNotNull { filename ->
            loadBitmap("Backgrounds/$filename")
        }
    }
    
    /**
     * Load all borders/frames
     */
    suspend fun loadBorders(): List<Bitmap> = withContext(Dispatchers.IO) {
        val files = listAssetFiles("Borders")
        files.mapNotNull { filename ->
            loadBitmap("Borders/$filename")
        }
    }
    
    /**
     * Load all fonts
     */
    suspend fun loadFonts(): List<Typeface> = withContext(Dispatchers.IO) {
        val files = listAssetFiles("Fonts")
        files.mapNotNull { filename ->
            loadFont("Fonts/$filename")
        }
    }
    
    /**
     * Load all decorations
     */
    suspend fun loadDecorations(): List<Bitmap> = withContext(Dispatchers.IO) {
        val files = listAssetFiles("Decor")
        files.mapNotNull { filename ->
            loadBitmap("Decor/$filename")
        }
    }
    
    /**
     * Load CRT scanlines image
     */
    suspend fun loadCRT(): Bitmap? = loadBitmap("Images/CRT.png")
    
    /**
     * Load alpha mask
     */
    suspend fun loadAlphaMask(): Bitmap? = loadBitmap("Images/alpha.png")
    
    /**
     * Load second alpha mask (for borders)
     */
    suspend fun loadAlpha2Mask(): Bitmap? = loadBitmap("Images/alpha2.png")
    
    /**
     * Load border shadow
     */
    suspend fun loadBorderShadow(): Bitmap? = loadBitmap("Images/bordershadow.png")
    
    /**
     * Load scanlines pattern
     */
    suspend fun loadScanlines(): Bitmap? = loadBitmap("Images/scanlines.png")
}
