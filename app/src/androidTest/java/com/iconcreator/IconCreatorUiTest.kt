package com.iconcreator

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * UI Test using Compose Test Rule and Espresso for [MainActivity]
 */
@RunWith(AndroidJUnit4::class)
class IconCreatorUiTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun mainActivity_launchesAndDisplaysCoreButtons() {
        // Assert that main action controls are rendered on screen
        composeTestRule.onNodeWithText("Upload").assertIsDisplayed()
        composeTestRule.onNodeWithText("Save").assertIsDisplayed()
        composeTestRule.onNodeWithText("Templates").assertIsDisplayed()
        composeTestRule.onNodeWithText("Reset").assertIsDisplayed()
    }
}
