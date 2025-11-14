[app]

# Title of the application
title = FileGlance

# Package name
package.name = fileglance

# Package domain
package.domain = com.fileglance

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# Application versioning
version = 1.0

# Application requirements
requirements = python3,kivy,opencv-python,numpy,android,jnius,pillow

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Android API level
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# Android architecture
android.archs = arm64-v8a,armeabi-v7a

# Application icon (if you have one)
#icon.filename = %(source.dir)s/icon.png

# Presplash (if you have one)
#presplash.filename = %(source.dir)s/presplash.png

# Android services
#services = 

# Add Java classes
android.add_src = 

# Android gradle dependencies
android.gradle_dependencies = androidx.documentfile:documentfile:1.0.1

# Android meta-data
android.meta_data = 

# Entrypoint
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# Enable AndroidX
android.enable_androidx = True

# Logcat filters
android.logcat_filters = *:S python:D

# Copy libraries
android.copy_libs = 1

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Binary directory
bin_dir = ./bin
