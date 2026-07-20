[app]
title = Sentinel Mobile
package.name = sentinelmobile
package.domain = org.sentinel

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# Requirements needed by your app
requirements = python3,kivy,opencv-python,numpy

orientation = portrait
osx.kivy_version = 2.2.1

[buildozer]
log_level = 2
warn_on_root = 1