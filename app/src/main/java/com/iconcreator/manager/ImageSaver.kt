package com.iconcreator.manager

import android.content.Context
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.os.Build
import android.provider.MediaStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Handles saving images to device storage
 */
class ImageSaver(private val context: Context) {
    
    /**
     * Save a bitmap as PNG to the Pictures directory
     */
    suspend fun saveAsPNG(bitmap: Bitmap, filename: String? = null): String? = withContext(Dispatchers.IO) {
        try {
            val displayName = filename ?: generateFilename()
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val contentValues = android.content.ContentValues().apply {
                    put(MediaStore.Images.Media.DISPLAY_NAME, "$displayName.png")
                    put(MediaStore.Images.Media.MIME_TYPE, "image/png")
                    put(MediaStore.Images.Media.RELATIVE_PATH, android.os.Environment.DIRECTORY_PICTURES + "/IconCreator")
                }
                
                val uri = context.contentResolver.insert(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    contentValues
                )
                
                uri?.let {
                    context.contentResolver.openOutputStream(it)?.use { outputStream ->
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
                    }
                    return@withContext it.toString()
                }
            } else {
                // For older Android versions
                val picturesDir = android.os.Environment.getExternalStoragePublicDirectory(
                    android.os.Environment.DIRECTORY_PICTURES
                )
                val appDir = File(picturesDir, "IconCreator")
                if (!appDir.exists()) {
                    appDir.mkdirs()
                }
                
                val file = File(appDir, "$displayName.png")
                FileOutputStream(file).use { outputStream ->
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
                }
                
                // Notify media scanner
                context.sendBroadcast(
                    android.content.Intent(android.content.Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, android.net.Uri.fromFile(file))
                )
                
                return@withContext file.absolutePath
            }
            
            null
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * Generate a filename based on current timestamp
     */
    private fun generateFilename(): String {
        val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault())
        return "icon_${dateFormat.format(Date())}"
    }
    
    /**
     * Save as ICO (Windows icon format)
     * Note: This is a simplified implementation. For full ICO support, you'd need a library.
     */
    suspend fun saveAsICO(bitmap: Bitmap, filename: String? = null): String? = withContext(Dispatchers.IO) {
        try {
            // ICO format is complex, so we'll save as PNG with .ico extension for now
            // In a production app, you'd use a proper ICO library
            val displayName = filename ?: generateFilename()
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val contentValues = android.content.ContentValues().apply {
                    put(MediaStore.Images.Media.DISPLAY_NAME, "$displayName.ico")
                    put(MediaStore.Images.Media.MIME_TYPE, "image/x-icon")
                    put(MediaStore.Images.Media.RELATIVE_PATH, android.os.Environment.DIRECTORY_PICTURES + "/IconCreator")
                }
                
                val uri = context.contentResolver.insert(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    contentValues
                )
                
                uri?.let {
                    context.contentResolver.openOutputStream(it)?.use { outputStream ->
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
                    }
                    return@withContext it.toString()
                }
            } else {
                val picturesDir = android.os.Environment.getExternalStoragePublicDirectory(
                    android.os.Environment.DIRECTORY_PICTURES
                )
                val appDir = File(picturesDir, "IconCreator")
                if (!appDir.exists()) {
                    appDir.mkdirs()
                }
                
                val file = File(appDir, "$displayName.ico")
                FileOutputStream(file).use { outputStream ->
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
                }
                
                context.sendBroadcast(
                    android.content.Intent(android.content.Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, android.net.Uri.fromFile(file))
                )
                
                return@withContext file.absolutePath
            }
            
            null
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
