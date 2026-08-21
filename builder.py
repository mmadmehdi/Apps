import os
import re
import subprocess
from pathlib import Path

ROOT = Path.cwd()

app_name = input("App name: ").strip()
package_name = input("Package name: ").strip()

if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", package_name):
    print("Invalid package name")
    exit(1)

if len(package_name.split(".")) < 2:
    print("Package name must be like: com.example.app")
    exit(1)

# Package path
pkg_path = ROOT / "app/src/main/java" / Path(*package_name.split("."))
pkg_path.mkdir(parents=True, exist_ok=True)

(ROOT / "app/src/main/res/values").mkdir(parents=True, exist_ok=True)

# settings.gradle
(ROOT / "settings.gradle").write_text("""pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "Apps"
include(":app")
""")

# Root build.gradle
(ROOT / "build.gradle").write_text("""plugins {
    id 'com.android.application' version '8.6.1' apply false
}
""")

# gradle.properties
(ROOT / "gradle.properties").write_text("""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
""")

# App build.gradle
(ROOT / "app").mkdir(exist_ok=True)

(ROOT / "app/build.gradle").write_text(f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{package_name}'
    compileSdk 35

    defaultConfig {{
        applicationId '{package_name}'
        minSdk 23
        targetSdk 35
        versionCode 1
        versionName '1.0'
    }}
}}
""")

# Manifest
(ROOT / "app/src/main/AndroidManifest.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:label="{app_name}"
        android:theme="@style/AppTheme">
    </application>

</manifest>
""")

# Strings
(ROOT / "app/src/main/res/values/strings.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
</resources>
""")

# Theme
(ROOT / "app/src/main/res/values/styles.xml").write_text("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme"
        parent="android:style/Theme.Material.Light.NoActionBar">
    </style>
</resources>
""")

# GitHub Actions
workflow = """name: Build APK

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build APK
        run: gradle assembleDebug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: APK
          path: app/build/outputs/apk/debug/*.apk
"""

(ROOT / ".github/workflows/build.yml").write_text(workflow)

print()
print("Project created!")
print("App:", app_name)
print("Package:", package_name)
print()
print("Now push this project to GitHub.")

