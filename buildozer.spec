name: HISS

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Build with Buildozer
      uses: ArtemSBulgakov/buildozer-action@v1
      id: buildozer
      with:
        workdir: .
        buildozer_version: master
        command: buildozer android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: SentinelMobile-APK
        path: ${{ steps.buildozer.outputs.filename }}