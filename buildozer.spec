[app]

# (str) Title of your application
title = Sentinel Mobile

# (str) Package name
package.name = sentinelmobile

# (str) Package domain (needed for android packaging)
package.domain = org.sentinel

# (str) Source code directory
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 1.0.0

# (list) Application requirements
# Enforces native opencv and matching python/kivy versions for cloud compilation stability
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,opencv,numpy

# (str) Supported orientations (one of landscape, portrait or all)
orientation = portrait

# =========================================================
# Android Specific Configurations
# =========================================================

# (list) Android permissions requested by the application
android.permissions = CAMERA, INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Accept SDK license without operator input
android.accept_sdk_license = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (list) List of Java .jar files to add to the libs so that pyjnius can access them
# android.add_jars = foo.jar

# (list) Android AAR archives to add
# android.add_aars =

# (list) Gradle dependencies
# android.gradle_dependencies =

# (bool) Enable AndroidX support (required for newer dependencies)
android.enable_androidx = True

# =========================================================
# Buildozer General Settings
# =========================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1