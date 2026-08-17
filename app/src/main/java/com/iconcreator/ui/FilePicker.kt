package com.iconcreator.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import com.iconcreator.viewmodel.IconViewModel

@Composable
fun rememberImagePicker(viewModel: IconViewModel): () -> Unit {
    val context = LocalContext.current
    var selectedUri by remember { mutableStateOf<Uri?>(null) }
    
    val imagePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            selectedUri = it
            // Load the image from URI
            context.contentResolver.openInputStream(it)?.use { inputStream ->
                android.graphics.BitmapFactory.decodeStream(inputStream)?.let { bitmap ->
                    viewModel.setGameImage(bitmap)
                }
            }
        }
    }
    
    return { imagePickerLauncher.launch("image/*") }
}
