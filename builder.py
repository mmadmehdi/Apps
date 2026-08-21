import re
import subprocess
from pathlib import Path

ROOT = Path.cwd()
REMOTE = "https://github.com/mmadmehdi/Apps.git"


def run(command):
    print("\n>>>", " ".join(command))
    subprocess.run(command, check=True)


# -----------------------------
# Get information
# -----------------------------

app_name = input("App name: ").strip()
package_name = input("Package name: ").strip()

if not app_name:
    raise SystemExit("App name cannot be empty.")

if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", package_name):
    raise SystemExit("Invalid package name.")

if len(package_name.split(".")) < 2:
    raise SystemExit("Package name must be like: com.example.app")


# -----------------------------
# Create folders
# -----------------------------

pkg_path = ROOT / "app/src/main/java" / Path(*package_name.split("."))
pkg_path.mkdir(parents=True, exist_ok=True)

(ROOT / "app/src/main/res/values").mkdir(
    parents=True,
    exist_ok=True
)

(ROOT / ".github/workflows").mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------
# settings.gradle
# -----------------------------

(ROOT / "settings.gradle").write_text(
"""pluginManagement {
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
""",
encoding="utf-8"
)


# -----------------------------
# Root build.gradle
# -----------------------------

(ROOT / "build.gradle").write_text(
"""plugins {
    id 'com.android.application' version '8.6.1' apply false
}
""",
encoding="utf-8"
)


# -----------------------------
# gradle.properties
# -----------------------------

(ROOT / "gradle.properties").write_text(
"""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
""",
encoding="utf-8"
)


# -----------------------------
# app/build.gradle
# -----------------------------

(ROOT / "app").mkdir(exist_ok=True)

(ROOT / "app/build.gradle").write_text(
f"""plugins {{
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
""",
encoding="utf-8"
)


# -----------------------------
# AndroidManifest.xml
# -----------------------------

(ROOT / "app/src/main/AndroidManifest.xml").write_text(
f"""<?xml version="1.0" encoding="utf-8"?>

<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:label="{app_name}"
        android:theme="@style/AppTheme"
        android:allowBackup="false"
        android:supportsRtl="true">

    </application>

</manifest>
""",
encoding="utf-8"
)


# -----------------------------
# strings.xml
# -----------------------------

(ROOT / "app/src/main/res/values/strings.xml").write_text(
f"""<?xml version="1.0" encoding="utf-8"?>

<resources>

    <string name="app_name">{app_name}</string>

</resources>
""",
encoding="utf-8"
)


# -----------------------------
# styles.xml
# -----------------------------

(ROOT / "app/src/main/res/values/styles.xml").write_text(
"""<?xml version="1.0" encoding="utf-8"?>

<resources>

    <style
        name="AppTheme"
        parent="android:style/Theme.Material.Light.NoActionBar">

    </style>

</resources>
""",
encoding="utf-8"
)


# -----------------------------
# MainActivity.java
# -----------------------------

(ROOT / "app/src/main/java").mkdir(
    parents=True,
    exist_ok=True
)

(pkg_path / "MainActivity.java").write_text(
f"""package {package_name};

public class MainActivity {{

}}
""",
encoding="utf-8"
)


# -----------------------------
# GitHub Actions
# -----------------------------

(ROOT / ".github/workflows/build.yml").write_text(
"""name: Build APK

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
""",
encoding="utf-8"
)


# -----------------------------
# Git
# -----------------------------

print("\nSetting up Git...")

run(["git", "init"])
run(["git", "branch", "-M", "main"])

# Set remote
result = subprocess.run(
    ["git", "remote", "get-url", "origin"],
    capture_output=True,
    text=True
)

if result.returncode == 0:

    run([
        "git",
        "remote",
        "set-url",
        "origin",
        REMOTE
    ])

else:

    run([
        "git",
        "remote",
        "add",
        "origin",
        REMOTE
    ])


# -----------------------------
# Commit
# -----------------------------

run(["git", "add", "."])

run([
    "git",
    "commit",
    "-m",
    f"Build {app_name}"
])


# -----------------------------
# Push
# -----------------------------

print("\nUploading project to GitHub...")

run([
    "git",
    "push",
    "-u",
    "origin",
    "main",
    "--force"
])


# -----------------------------
# Done
# -----------------------------

print("\n================================")
print("DONE!")
print("================================")
print("App name:", app_name)
print("Package:", package_name)
print()
print("Source uploaded to GitHub.")
print("GitHub Actions will now build the APK.")
print()
print("Repository:")
print(REMOTE)
print("================================")
