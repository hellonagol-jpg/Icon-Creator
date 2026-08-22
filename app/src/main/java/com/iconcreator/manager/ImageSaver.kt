package com.iconcreator.manager

import android.content.Context
import android.graphics.Bitmap
import android.net.Uri
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Handles saving images to device storage
 */
class ImageSaver(private val context: Context) {
    
    /**
     * Save a bitmap as PNG to a provided URI
     */
    suspend fun saveBitmapToUri(bitmap: Bitmap, uri: Uri): Boolean = withContext(Dispatchers.IO) {
        try {
            context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Save a bitmap as ICO to a provided URI
     */
    suspend fun saveIcoToUri(bitmap: Bitmap, uri: Uri): Boolean = withContext(Dispatchers.IO) {
        try {
            val icoData = encodeIco(bitmap)
            context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                outputStream.write(icoData)
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Internal method to encode a bitmap into multi-size ICO bytes
     */
    private fun encodeIco(bitmap: Bitmap): ByteArray {
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
        
        return icoBuffer.toByteArray()
    }
}
