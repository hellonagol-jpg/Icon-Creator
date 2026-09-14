package com.iconcreator.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotSame
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Unit test for [IconSettings]
 */
class IconSettingsTest {

    @Test
    fun defaultSettings_hasExpectedDefaults() {
        val settings = IconSettings.createDefault()

        assertEquals(50, settings.zoomLevel)
        assertEquals(0, settings.offsetX)
        assertEquals(0, settings.offsetY)
        assertEquals(0.9f, settings.brightness, 0.001f)
        assertEquals(listOf("Icon", "Creator"), settings.titleLines)
        assertTrue(settings.crtEnabled)
        assertTrue(settings.decorEnabled)
    }

    @Test
    fun copySettings_createsIndependentDeepCopy() {
        val original = IconSettings.createDefault()
        original.zoomLevel = 80
        original.titleLines = listOf("Custom", "Title")

        val copied = original.copy()

        assertEquals(80, copied.zoomLevel)
        assertEquals(listOf("Custom", "Title"), copied.titleLines)

        // Modify copied instance and verify original is unaffected
        copied.zoomLevel = 100
        copied.titleLines = listOf("Modified", "Copy")

        assertEquals(80, original.zoomLevel)
        assertEquals(listOf("Custom", "Title"), original.titleLines)
        assertNotSame(original.titleLines, copied.titleLines)
    }
}
