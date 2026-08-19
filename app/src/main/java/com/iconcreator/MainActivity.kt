package com.iconcreator

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.iconcreator.ui.IconCreatorScreen
import com.iconcreator.ui.theme.IconCreatorTheme
import com.iconcreator.viewmodel.IconViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        
        enableEdgeToEdge()
        setContent {
            val viewModel: IconViewModel = viewModel { IconViewModel(application) }
            val uiState by viewModel.uiState.collectAsState()
            
            IconCreatorTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val previewBitmap by viewModel.previewBitmap.collectAsState()
                    IconCreatorScreen(
                        viewModel = viewModel,
                        uiState = uiState,
                        previewBitmap = previewBitmap
                    )
                }
            }
        }
    }
}


