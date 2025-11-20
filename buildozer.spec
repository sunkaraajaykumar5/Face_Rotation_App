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

# Requirements
requirements = python3,kivy,opencv-python,numpy,android,jnius,pillow

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Android API levels
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# Architectures
android.archs = arm64-v8a,armeabi-v7a

# Icon / presplash (optional)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# Add Java classes (empty)
android.add_src = 

# Gradle dependencies
android.gradle_dependencies = androidx.documentfile:documentfile:1.0.1

# Meta-data
android.meta_data = 

# Entrypoint
android.entrypoint = org.kivy.android.PythonActivity

# Android theme
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

# Warning for running as root
warn_on_root = 1

# Build dir
build_dir = ./.buildozer

# Binary dir
bin_dir = ./bin

