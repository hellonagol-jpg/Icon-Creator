package com.iconcreator.manager

import android.content.Context
import android.graphics.Bitmap
import android.os.Build
import android.provider.MediaStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Handles saving images to device storage
 */
class ImageSaver(private val context: Context) {
    
    /**
     * Save a bitmap as PNG to the Downloads directory
     */
    suspend fun saveAsPNG(bitmap: Bitmap, filename: String? = null): String? = withContext(Dispatchers.IO) {
        try {
            val displayName = filename ?: generateFilename()
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val contentValues = android.content.ContentValues().apply {
                    put(MediaStore.Downloads.DISPLAY_NAME, "$displayName.png")
                    put(MediaStore.Downloads.MIME_TYPE, "image/png")
                    put(MediaStore.Downloads.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS + "/IconCreator")
                }
                
                val uri = context.contentResolver.insert(
                    MediaStore.Downloads.EXTERNAL_CONTENT_URI,
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
                val downloadsDir = android.os.Environment.getExternalStoragePublicDirectory(
                    android.os.Environment.DIRECTORY_DOWNLOADS
                )
                val appDir = File(downloadsDir, "IconCreator")
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
                
                return@withContext android.net.Uri.fromFile(file).toString()
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
     * Properly encodes multiple sizes into a single .ico file
     */
    suspend fun saveAsICO(bitmap: Bitmap, filename: String? = null): String? = withContext(Dispatchers.IO) {
        try {
            val displayName = filename ?: generateFilename()
            
            // Sizes to include in the ICO: 256, 128, 64, 48, 32, 16
            val sizes = listOf(256, 128, 64, 48, 32, 16)
            val pngs = sizes.map { size ->
                val scaled = Bitmap.createScaledBitmap(bitmap, size, size, true)
                val out = ByteArrayOutputStream()
                scaled.compress(Bitmap.CompressFormat.PNG, 100, out)
                out.toByteArray()
            }
            
            val icoBuffer = ByteArrayOutputStream()
            val header = ByteBuffer.allocate(6).order(ByteOrder.LITTLE_ENDIAN)
            header.putShort(0) // Reserved
            header.putShort(1) // Type (1 for icon)
            header.putShort(sizes.size.toShort()) // Number of images
            icoBuffer.write(header.array())
            
            var offset = 6 + (sizes.size * 16)
            
            for (i in pngs.indices) {
                val size = sizes[i]
                val data = pngs[i]
                
                val entry = ByteBuffer.allocate(16).order(ByteOrder.LITTLE_ENDIAN)
                entry.put(if (size >= 256) 0 else size.toByte()) // Width
                entry.put(if (size >= 256) 0 else size.toByte()) // Height
                entry.put(0) // Color count
                entry.put(0) // Reserved
                entry.putShort(1) // Color planes
                entry.putShort(32) // Bits per pixel
                entry.putInt(data.size) // Image size
                entry.putInt(offset) // Image offset
                icoBuffer.write(entry.array())
                
                offset += data.size
            }
            
            for (data in pngs) {
                icoBuffer.write(data)
            }
            
            val icoData = icoBuffer.toByteArray()
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val contentValues = android.content.ContentValues().apply {
                    put(MediaStore.Downloads.DISPLAY_NAME, "$displayName.ico")
                    put(MediaStore.Downloads.MIME_TYPE, "image/x-icon")
                    put(MediaStore.Downloads.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS + "/IconCreator")
                }
                
                val uri = context.contentResolver.insert(
                    MediaStore.Downloads.EXTERNAL_CONTENT_URI,
                    contentValues
                )
                
                uri?.let {
                    context.contentResolver.openOutputStream(it)?.use { outputStream ->
                        outputStream.write(icoData)
                    }
                    return@withContext it.toString()
                }
            } else {
                val downloadsDir = android.os.Environment.getExternalStoragePublicDirectory(
                    android.os.Environment.DIRECTORY_DOWNLOADS
                )
                val appDir = File(downloadsDir, "IconCreator")
                if (!appDir.exists()) appDir.mkdirs()
                
                val file = File(appDir, "$displayName.ico")
                FileOutputStream(file).use { outputStream ->
                    outputStream.write(icoData)
                }
                
                context.sendBroadcast(
                    android.content.Intent(android.content.Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, android.net.Uri.fromFile(file))
                )
                
                return@withContext android.net.Uri.fromFile(file).toString()
            }
            
            null
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
