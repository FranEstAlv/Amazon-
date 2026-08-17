# Amazon Shopping 32.13.0.100 — ARM64 / XHDPI split analysis

## Installed split set

This section analyzes the additional APK splits extracted from the same installed package as the previously analyzed `base.apk`.

| Split | Size | SHA-256 | Contents |
|---|---:|---|---|
| `split_config.arm64_v8a.apk` | 73,685,633 bytes | `4cc6ebe964c2edf24279656b3ef43dff5bf0f8e4f54288ba8831e8041080be28` | 78 ARM64 ELF shared libraries |
| `split_config.xhdpi.apk` | 2,915,939 bytes | `54054378f78818cac1d0dd7b60382b17620b749e1ad95e94aadfc139f3edde83` | 920 entries, primarily density-specific resources |

Runtime package metadata supplied from the device: `versionName=32.13.0.100`, `versionCode=1241320016`, `minSdk=31`, `targetSdk=36`, `primaryCpuAbi=arm64-v8a`, splits `[base, config.arm64_v8a, config.xhdpi]`.

## Native architecture conclusions

- **React Native is materially present, not just a Java dependency.** The ABI split includes `libreactnativejni.so`, Fabric renderer libraries, JSI, TurboModules, Yoga, RN codegen, runtime executor and RN instance libraries.
- **Hermes is present as a full native JavaScript runtime** (`libhermes.so`, `libhermes_executor.so`, `libhermesinstancejni.so`). JSC compatibility libraries (`libjscexecutor.so`, `libjscinstance.so`) are also included.
- **React Native New Architecture components are present**, including Fabric, TurboModules, generated RN core bindings and new-architecture defaults. Static presence does not prove every screen uses RN; feature flags / runtime selection can choose different surfaces.
- **Amazon visual-search / AR code is substantial.** `libA9VSMobile.so` is the largest native library (~20 MiB), while `liba9vs_lens_xray_engine.so` directly links TensorFlow Lite CPU/GPU and exposes JNI object-detection functions.
- **Native experimentation infrastructure exists.** `libandroid_amazon_weblab_external_plugin.so` exposes treatment/trigger/local-override JNI calls and contains Amazon Mobile WebLab allocation infrastructure.
- **Native video/live-streaming functionality exists.** `libplayercore.so` contains Amazon IVS/Twitch player code, DRM/license endpoints and playback/network telemetry strings.
- **Native observability is extensive.** Bugsnag NDK/ANR/root-detection libraries and Bitdrift Capture are bundled.

## ARM64 ELF inventory

| Library | Size | JNI exports | Direct DT_NEEDED dependencies |
|---|---:|---:|---|
| `libA9VSMobile.so` | 20,946,264 | 2617 | `libGLESv3.so`, `libEGL.so`, `libz.so`, `libandroid.so`, `liblog.so`, `libmediandk.so`, `libc.so`, `libm.so`, `libdl.so` |
| `liba9vs_lens_xray_engine.so` | 5,101,304 | 8 | `liblog.so`, `libjnigraphics.so`, `libz.so`, `libandroid.so`, `libtensorflowlite_jni.so`, `libtensorflowlite_gpu_jni.so`, `libdl.so`, `libm.so`, `libc.so` |
| `libbarhopper_v3.so` | 4,946,720 | 8 | `libjnigraphics.so`, `liblog.so`, `libdl.so`, `libm.so`, `libc.so` |
| `libgpu_delegate_plugin.so` | 4,821,112 | 0 | `libEGL.so`, `libGLESv2.so`, `libnativewindow.so`, `libdl.so`, `libm.so`, `liblog.so`, `libc.so` |
| `libhermes.so` | 3,652,064 | 0 | `libjsi.so`, `libfbjni.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libplayercore.so` | 3,494,656 | 107 | `liblog.so`, `libm.so`, `libdl.so`, `libc.so` |
| `libtensorflowlite_jni.so` | 3,368,072 | 56 | `libm.so`, `libdl.so`, `liblog.so`, `libc.so` |
| `libcapture.so` | 2,508,824 | 39 | `liblog.so`, `libz.so`, `libdl.so`, `libm.so`, `libc.so` |
| `libandroid_amazon_weblab_external_plugin.so` | 2,468,776 | 9 | `libdl.so`, `libc.so` |
| `libfabricjni.so` | 1,921,272 | 1 | `librrc_textinput.so`, `libreact_render_observers_events.so`, `libreact_performance_timeline.so`, `libreact_codegen_rncore.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `libmapbufferjni.so`, `libreactnativejni.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_uimanager_consistency.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libtensorflowlite_gpu_jni.so` | 1,530,552 | 6 | `libGLESv3.so`, `libEGL.so`, `libnativewindow.so`, `libdl.so`, `libm.so`, `liblog.so`, `libc.so` |
| `libsqlite3x.so` | 1,518,232 | 1 | `libdl.so`, `liblog.so`, `libc.so`, `libm.so`, `libstdc++.so` |
| `libc++_shared.so` | 1,292,904 | 0 | `libc.so`, `libm.so`, `libdl.so` |
| `libbugsnag-ndk.so` | 1,187,392 | 42 | `liblog.so`, `libandroid.so`, `libm.so`, `libdl.so`, `libc.so` |
| `libreact_codegen_rncore.so` | 1,089,424 | 0 | `libreact_render_componentregistry.so`, `librrc_image.so`, `libturbomodulejsijni.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_graphics.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libyoga.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libreact_render_consistency.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libfbjni.so`, `libdl.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `liba518.so` | 1,052,400 | 1 | `libc.so`, `libstdc++.so`, `libm.so`, `libdl.so`, `liblog.so` |
| `libfbjni.so` | 1,051,632 | 1 | `libandroid.so`, `liblog.so`, `libm.so`, `libdl.so`, `libc.so` |
| `libreactnativejni.so` | 944,784 | 1 | `libandroid.so`, `libyoga.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libruntimeexecutor.so`, `libreact_debug.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libreact_featureflags.so`, `libdl.so`, `libfbjni.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libfolly_runtime.so` | 678,520 | 0 | `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libnative-imagetranscoder.so` | 626,336 | 1 | `liblog.so`, `libc.so`, `libm.so`, `libdl.so` |
| `libzstd-jni-1.5.6-7.so` | 600,064 | 144 | `libm.so`, `libdl.so`, `libc.so` |
| `libmmkv.so` | 597,000 | 1 | `liblog.so`, `libz.so`, `libm.so`, `libdl.so`, `libc.so` |
| `librninstance.so` | 555,272 | 1 | `libfabricjni.so`, `libreact_render_observers_events.so`, `libreact_performance_timeline.so`, `libreact_codegen_rncore.so`, `librrc_textinput.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_uimanager_consistency.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_graphics.so`, `libreact_featureflagsjni.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_render_debug.so`, `libreact_render_consistency.so`, `libmapbufferjni.so`, `libreact_render_mapbuffer.so`, `libreact_utils.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libjsinspector.so` | 404,160 | 0 | `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `librrc_view.so` | 385,136 | 0 | `libreact_render_core.so`, `libreact_render_graphics.so`, `libyoga.so`, `libreact_render_mapbuffer.so`, `libreact_render_debug.so`, `libreact_render_consistency.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libdl.so`, `libfbjni.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libopus_wrapper.so` | 371,680 | 3 | `libm.so`, `libdl.so`, `libc.so` |
| `libreact_nativemodule_dom.so` | 370,504 | 0 | `libreact_codegen_rncore.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreact_render_uimanager_consistency.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreactnativejni.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libmapbufferjni.so`, `libyoga.so`, `libfbjni.so`, `libreact_render_mapbuffer.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libdl.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libsnappyjava.so` | 363,568 | 19 | `libm.so`, `libdl.so`, `libc.so` |
| `libjsimodules.so` | 357,224 | 1 | `libc.so`, `libm.so`, `libdl.so` |
| `librrc_textinput.so` | 318,600 | 0 | `librrc_image.so`, `libmapbufferjni.so`, `libreactnativejni.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_uimanager_consistency.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_nativemodule_core.so` | 308,328 | 0 | `libreactnativejni.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libA9VSAndroidNativeCodec.so` | 267,184 | 16 | `libdl.so`, `liblog.so`, `libandroid.so`, `libmediandk.so`, `libOpenMAXAL.so`, `libm.so`, `libc.so` |
| `libreact_render_uimanager_consistency.so` | 245,920 | 0 | `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `libreact_utils.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_render_core.so` | 234,832 | 0 | `libreact_render_graphics.so`, `libreact_render_mapbuffer.so`, `libreact_utils.so`, `libdl.so`, `libandroid.so`, `libfbjni.so`, `libreact_render_debug.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libreact_render_consistency.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `librrc_image.so` | 213,432 | 0 | `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libjscexecutor.so` | 207,544 | 1 | `libreactnativejni.so`, `libjsc.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_debug.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libhermes_executor.so` | 204,728 | 1 | `libreactnativejni.so`, `libhermes.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_debug.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libyoga.so` | 184,096 | 1 | `libfbjni.so`, `liblog.so`, `libandroid.so`, `libdl.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_newarchdefaults.so` | 172,712 | 1 | `libfabricjni.so`, `libreact_featureflagsjni.so`, `libreact_nativemodule_defaults.so`, `libreact_nativemodule_dom.so`, `libreact_nativemodule_featureflags.so`, `libreact_nativemodule_microtasks.so`, `libreact_render_observers_events.so`, `libreact_performance_timeline.so`, `librrc_textinput.so`, `libmapbufferjni.so`, `libreact_render_uimanager_consistency.so`, `libreact_codegen_rncore.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_graphics.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `libandroid.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libreact_render_consistency.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libturbomodulejsijni.so` | 156,240 | 1 | `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libruntimeexecutor.so`, `libjsi.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libfolly_runtime.so`, `libglog.so`, `libreact_featureflags.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libglog.so` | 139,608 | 0 | `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libjsidatastreammodule.so` | 134,352 | 2 | `liblog.so`, `libturbomodulejsijni.so`, `libfbjni.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libjsimshopopentelemetrytracermodule.so` | 130,008 | 2 | `liblog.so`, `libturbomodulejsijni.so`, `libfbjni.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreact_render_componentregistry.so` | 121,848 | 0 | `librrc_legacyviewmanagerinterop.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_devsupportjni.so` | 118,088 | 1 | `libfbjni.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libuimanagerjni.so` | 117,920 | 1 | `libreactnativejni.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_view.so`, `libyoga.so`, `libreact_render_core.so`, `libreact_render_consistency.so`, `libreact_render_mapbuffer.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libdl.so`, `libandroid.so`, `libfbjni.so`, `libreact_utils.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libreact_featureflags.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libjscinstance.so` | 114,240 | 1 | `libfabricjni.so`, `libreact_render_observers_events.so`, `libreact_performance_timeline.so`, `libreact_codegen_rncore.so`, `librrc_textinput.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `libmapbufferjni.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_uimanager_consistency.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_graphics.so`, `libreact_featureflagsjni.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_render_debug.so`, `libreact_render_consistency.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `libandroid.so`, `libreact_utils.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libruntimeexecutor.so`, `libreact_featureflags.so`, `libjsi.so`, `libfolly_runtime.so`, `libjsc.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libjsi.so` | 105,120 | 0 | `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libarcore_sdk_jni.so` | 100,800 | 301 | `libarcore_sdk_c.so`, `libandroid.so`, `liblog.so`, `libdl.so`, `libc.so`, `libm.so` |
| `libreact_nativemodule_defaults.so` | 89,024 | 0 | `libreact_nativemodule_dom.so`, `libreact_nativemodule_featureflags.so`, `libreact_nativemodule_microtasks.so`, `libreact_render_uimanager_consistency.so`, `libmapbufferjni.so`, `libreact_codegen_rncore.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_graphics.so`, `libreact_render_mapbuffer.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `libandroid.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libreact_render_consistency.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `librrc_legacyviewmanagerinterop.so` | 87,272 | 0 | `librrc_view.so`, `libyoga.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libdl.so`, `liblog.so`, `libandroid.so`, `libfbjni.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_performance_timeline.so` | 81,784 | 0 | `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libreact_debug.so`, `libfolly_runtime.so`, `libglog.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreact_featureflagsjni.so` | 81,776 | 1 | `libreactnativejni.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libreact_debug.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libmapbufferjni.so` | 77,072 | 1 | `libreact_render_mapbuffer.so`, `libreact_utils.so`, `libyoga.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libhermesinstancejni.so` | 73,472 | 1 | `librninstance.so`, `libfabricjni.so`, `libreact_render_observers_events.so`, `libreact_performance_timeline.so`, `libreact_codegen_rncore.so`, `librrc_textinput.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `libreact_render_uimanager_consistency.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_graphics.so`, `libreact_featureflagsjni.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_render_debug.so`, `libreact_render_consistency.so`, `libmapbufferjni.so`, `libreact_render_mapbuffer.so`, `libreact_utils.so`, `libyoga.so`, `libfbjni.so`, `libreact_debug.so`, `libhermes.so`, `libdl.so`, `libandroid.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libarcore_sdk_c.so` | 68,040 | 2 | `libandroid.so`, `liblog.so`, `libdl.so`, `libc.so`, `libm.so` |
| `libreact_nativemodule_featureflags.so` | 66,712 | 0 | `libreact_codegen_rncore.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_graphics.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libreact_render_consistency.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_featureflags.so` | 56,016 | 0 | `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreact_nativemodule_microtasks.so` | 53,056 | 0 | `libreact_codegen_rncore.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_image.so`, `libreact_render_imagemanager.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_graphics.so`, `libturbomodulejsijni.so`, `libreact_nativemodule_core.so`, `libreactnativejni.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libreact_render_consistency.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libfbjni.so`, `libdl.so`, `liblog.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_render_mapbuffer.so` | 51,120 | 0 | `libreact_debug.so`, `liblog.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreactnativeblob.so` | 49,272 | 1 | `libreactnativejni.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_debug.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_render_observers_events.so` | 48,904 | 0 | `libreact_performance_timeline.so`, `libreact_render_uimanager_consistency.so`, `libreact_render_componentregistry.so`, `librrc_legacyviewmanagerinterop.so`, `librrc_view.so`, `libreact_render_core.so`, `libreact_render_graphics.so`, `libmapbufferjni.so`, `libreact_render_mapbuffer.so`, `libreactnativejni.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_debug.so`, `libreact_featureflags.so`, `libreact_render_debug.so`, `libreact_render_consistency.so`, `libyoga.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libdl.so`, `liblog.so`, `libfbjni.so`, `libandroid.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_render_imagemanager.so` | 48,768 | 0 | `librrc_view.so`, `libreact_render_core.so`, `libreact_render_mapbuffer.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_render_graphics.so`, `libreact_utils.so`, `libreact_debug.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_render_graphics.so` | 45,456 | 0 | `libfbjni.so`, `libreact_utils.so`, `libdl.so`, `libandroid.so`, `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libreact_utils.so` | 38,368 | 0 | `libreact_debug.so`, `liblog.so`, `libjsinspector.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libjsijniprofiler.so` | 35,808 | 1 | `libhermes.so`, `libreactnativejni.so`, `libreact_render_consistency.so`, `libreact_render_debug.so`, `libreact_utils.so`, `libjsinspector.so`, `libreact_debug.so`, `libreact_featureflags.so`, `libruntimeexecutor.so`, `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libyoga.so`, `libdl.so`, `libfbjni.so`, `libandroid.so`, `liblog.so`, `libm.so`, `libc++_shared.so`, `libc.so` |
| `libimage_processing_util_jni.so` | 29,008 | 6 | `liblog.so`, `libandroid.so`, `libjnigraphics.so`, `libm.so`, `libdl.so`, `libc.so` |
| `libnative-filters.so` | 23,752 | 1 | `liblog.so`, `libjnigraphics.so`, `libc.so`, `libm.so`, `libdl.so` |
| `libbugsnag-plugin-android-anr.so` | 13,832 | 3 | `liblog.so`, `libm.so`, `libdl.so`, `libc.so` |
| `libandroidx.graphics.path.so` | 10,096 | 1 | `libm.so`, `libdl.so`, `libc.so` |
| `libimagepipeline.so` | 8,776 | 1 | `liblog.so`, `libjnigraphics.so`, `libc.so`, `libm.so`, `libdl.so` |
| `libdatastore_shared_counter.so` | 7,112 | 4 | `libm.so`, `libdl.so`, `libc.so` |
| `libbugsnag-root-detection.so` | 5,032 | 1 | `libm.so`, `libdl.so`, `libc.so` |
| `libreact_debug.so` | 4,400 | 0 | `liblog.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libkeys.so` | 4,248 | 1 | `libc.so`, `libm.so`, `libdl.so` |
| `libruntimeexecutor.so` | 4,128 | 0 | `libjsi.so`, `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreact_render_debug.so` | 3,848 | 0 | `libfolly_runtime.so`, `libglog.so`, `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |
| `libreact_render_consistency.so` | 3,784 | 0 | `libm.so`, `libc++_shared.so`, `libdl.so`, `libc.so` |

## JNI highlights

### `libA9VSMobile.so`

- JNI symbol count detected statically: **2617**.
- `JNI_OnLoad`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSIndexBuffer_1indexBuffer_1get`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSIndexBuffer_1indexBuffer_1set`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSIndexBuffer_1indexCount`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSIndexBuffer_1indexTriangleCount`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSIndexBuffer_1isValid`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1findNodeWithName`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1getLocalAxisAlignedBoundingBox`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1getRootNode`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1getXmpJsonLd`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1isEmpty`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNodeGroup_1setAnimationTime`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1approximateWorldPose`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1attachPhysicsObject`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1detachPhysicsObject`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getCategoryBitMask`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getChildNodes`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getLocalAxisAlignedBoundingBox`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getLocalTransform`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getMesh_1_1SWIG_10`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getMesh_1_1SWIG_11`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getName`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getNumMaterials`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getOpacity`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSMobileJNI_A9VSNode_1getParentNode`
- … 2592 additional JNI symbols omitted from this readable summary.

### `libA9VSAndroidNativeCodec.so`

- JNI symbol count detected statically: **16**.
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1destroy`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1fromSurface`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1open`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1pause`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1play`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1registerSampleDecryptionDelegate`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_A9VSAndroidNDKCodec_1seekToFrame`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_SampleDecryptionDelegate_1change_1ownership`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_SampleDecryptionDelegate_1decryptSample`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_SampleDecryptionDelegate_1decryptSampleSwigExplicitSampleDecryptionDelegate`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_SampleDecryptionDelegate_1director_1connect`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_delete_1A9VSAndroidNDKCodec`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_delete_1SampleDecryptionDelegate`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_new_1A9VSAndroidNDKCodec`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_new_1SampleDecryptionDelegate`
- `Java_com_a9_vs_mobile_library_impl_jni_A9VSNativeCodecJNI_swig_1module_1init`

### `liba9vs_lens_xray_engine.so`

- JNI symbol count detected statically: **8**.
- `JNI_OnLoad`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_createXRayInstance`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_destroyXRayEngineInstance`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_detectObjects`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_loadTensorFlowModel`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_onAppPaused`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_onAppResumed`
- `Java_com_amazon_vsearch_lens_core_internal_search_camera_live_XRayEngineObjectDetectorJNI_resetTracking`

### `libandroid_amazon_weblab_external_plugin.so`

- JNI symbol count detected statically: **9**.
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_flush`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_getTreatment`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_getTreatmentNoTrigger`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_hasLocalOverride`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_init`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_initWithConfig`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_recordTrigger`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_removeLocalOverride`
- `Java_android_amazon_1weblab_1external_1plugin_WeblabAndroidClient_setLocalOverride`

### `libplayercore.so`

- JNI symbol count detected statically: **107**.
- `JNI_OnLoad`
- `Java_com_amazonaws_ivs_net_NativeReadCallback_getTimeout`
- `Java_com_amazonaws_ivs_net_NativeReadCallback_onBuffer`
- `Java_com_amazonaws_ivs_net_NativeReadCallback_onError`
- `Java_com_amazonaws_ivs_net_NativeResponseCallback_onError`
- `Java_com_amazonaws_ivs_net_NativeResponseCallback_onResponse`
- `Java_com_amazonaws_ivs_net_NetworkLinkInfo_onNetworkAvailable`
- `Java_com_amazonaws_ivs_net_NetworkLinkInfo_onNetworkLost`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getAverageBitrate`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getBandwidthEstimate`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getBufferedPosition`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getChannelMetadata`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getDuration`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getExperiments`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getLiveLatency`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getPath`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getPlaybackRate`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getPosition`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getProtocol`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getQualities`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getQuality`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getSessionId`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getSourceGroup`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getSourceGroups`
- `Java_com_amazonaws_ivs_player_CorePlayerImpl_getState`
- … 82 additional JNI symbols omitted from this readable summary.

### `libcapture.so`

- JNI symbol count detected statically: **39**.
- `JNI_OnLoad`
- `Java_io_bitdrift_capture_CaptureJniLibrary_addLogField`
- `Java_io_bitdrift_capture_CaptureJniLibrary_createLogger`
- `Java_io_bitdrift_capture_CaptureJniLibrary_debugDebug`
- `Java_io_bitdrift_capture_CaptureJniLibrary_debugError`
- `Java_io_bitdrift_capture_CaptureJniLibrary_destroyLogger`
- `Java_io_bitdrift_capture_CaptureJniLibrary_flush`
- `Java_io_bitdrift_capture_CaptureJniLibrary_getDeviceId`
- `Java_io_bitdrift_capture_CaptureJniLibrary_getSdkStatus`
- `Java_io_bitdrift_capture_CaptureJniLibrary_getSessionId`
- `Java_io_bitdrift_capture_CaptureJniLibrary_isTracingActive`
- `Java_io_bitdrift_capture_CaptureJniLibrary_previousMemoryPressureLevel`
- `Java_io_bitdrift_capture_CaptureJniLibrary_processAndPersistANR`
- `Java_io_bitdrift_capture_CaptureJniLibrary_processAndPersistJavaScriptError`
- `Java_io_bitdrift_capture_CaptureJniLibrary_processIssueReports`
- `Java_io_bitdrift_capture_CaptureJniLibrary_removeLogField`
- `Java_io_bitdrift_capture_CaptureJniLibrary_reportError`
- `Java_io_bitdrift_capture_CaptureJniLibrary_setEntityId`
- `Java_io_bitdrift_capture_CaptureJniLibrary_setFeatureFlagExposure`
- `Java_io_bitdrift_capture_CaptureJniLibrary_setSleepModeEnabled`
- `Java_io_bitdrift_capture_CaptureJniLibrary_shouldWriteAppUpdateLog`
- `Java_io_bitdrift_capture_CaptureJniLibrary_shutdown`
- `Java_io_bitdrift_capture_CaptureJniLibrary_startLogger`
- `Java_io_bitdrift_capture_CaptureJniLibrary_startNewSession`
- `Java_io_bitdrift_capture_CaptureJniLibrary_writeAppLaunchTTILog`
- … 14 additional JNI symbols omitted from this readable summary.

### `libbarhopper_v3.so`

- JNI symbol count detected statically: **8**.
- `Java_com_google_android_libraries_barhopper_BarhopperV3_closeNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_createNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_createNativeWithClientOptions`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_recognizeBitmapNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_recognizeBufferNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_recognizeNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_recognizeStridedBufferNative`
- `Java_com_google_android_libraries_barhopper_BarhopperV3_recognizeStridedNative`

### `libtensorflowlite_jni.so`

- JNI symbol count detected statically: **56**.
- `Java_org_tensorflow_lite_InterpreterFactoryImpl_nativeRuntimeVersion`
- `Java_org_tensorflow_lite_InterpreterFactoryImpl_nativeSchemaVersion`
- `Java_org_tensorflow_lite_NativeInterpreterWrapperExperimental_resetVariableTensors`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_allocateTensors`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_allowBufferHandleOutput`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_allowFp16PrecisionForFp32`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_createCancellationFlag`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_createErrorReporter`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_createInterpreter`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_createModel`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_createModelWithBuffer`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_delete`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_deleteCancellationFlag`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getExecutionPlanLength`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getInputCount`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getInputNames`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getInputTensorIndex`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getOutputCount`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getOutputNames`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getOutputTensorIndex`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_getSignatureKeys`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_hasUnresolvedFlexOp`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_resizeInput`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_run`
- `Java_org_tensorflow_lite_NativeInterpreterWrapper_setCancelled`
- … 31 additional JNI symbols omitted from this readable summary.

## Native URL / endpoint strings

These are literal URL-like strings recovered from ARM64 `.so` files. They may be production endpoints, templates, SDK documentation, test strings or dormant code; static presence alone does not prove runtime use.

| Library | URL/string |
|---|---|
| `libA9VSMobile.so` | `https://github.com/opencv/opencv/issues/16739` |
| `libA9VSMobile.so` | `https://github.com/opencv/opencv/issues/19634` |
| `libA9VSMobile.so` | `https://github.com/opencv/opencv/issues/21326` |
| `libA9VSMobile.so` | `https://github.com/opencv/opencv/issues/5412` |
| `liba9vs_lens_xray_engine.so` | `https://github.com/opencv/opencv/issues/16739` |
| `libandroid_amazon_weblab_external_plugin.so` | `https://docs.rs/getrandom#nodejs-es-module-supportrecursive` |
| `libandroid_amazon_weblab_external_plugin.so` | `https://m.media-amazon.com/images/S/mobile-weblab-allocations-{stage}/allocations/v2/{domain}/a?app_id={app_id}{stage}!triggers-redirecthttps://{app_id}.triggers-v1.{stage}.mobile.weblab.a2z.com!allocations-redirect!treatment-assignment-overrides-redirect-v2https://m.media-amazon.com/images/S/mobile-weblab-` |
| `libbarhopper_v3.so` | `http://http` |
| `libbarhopper_v3.so` | `https://www.tensorflow.org/lite/guide/ops_custom` |
| `libbarhopper_v3.so` | `https://www.tensorflow.org/lite/guide/ops_select` |
| `libgpu_delegate_plugin.so` | `https://www.tensorflow.org/lite/guide/ops_custom` |
| `libgpu_delegate_plugin.so` | `https://www.tensorflow.org/lite/guide/ops_select` |
| `libjsinspector.so` | `https://reactnative.dev/docs/debugging` |
| `libplayercore.so` | `http://canary.assets.clips.twitchcdn.net` |
| `libplayercore.so` | `http://clips-` |
| `libplayercore.so` | `http://clips.twitch.tv/` |
| `libplayercore.so` | `http://production.assets.clips.twitchcdn.net` |
| `libplayercore.so` | `http://schemas.microsoft.com/DRM/2007/03/protocols/AcquireLicense` |
| `libplayercore.so` | `https://canary.assets.clips.twitchcdn.net` |
| `libplayercore.so` | `https://clips-` |
| `libplayercore.so` | `https://clips.twitch.tv/` |
| `libplayercore.so` | `https://fairplay.twitch.keyos.com/api/v4/getLicense` |
| `libplayercore.so` | `https://global.poe.live-video.net/` |
| `libplayercore.so` | `https://gql.twitch.tv/gql` |
| `libplayercore.so` | `https://player.stats.live-video.net/` |
| `libplayercore.so` | `https://playready.twitch.keyos.com/api/v4/getLicense` |
| `libplayercore.so` | `https://production.assets.clips.twitchcdn.net` |
| `libplayercore.so` | `https://widevine.twitch.keyos.com/api/v4/getLicense` |
| `libtensorflowlite_jni.so` | `https://www.tensorflow.org/lite/guide/ops_custom` |
| `libtensorflowlite_jni.so` | `https://www.tensorflow.org/lite/guide/ops_select` |

## `split_config.xhdpi.apk` resource census

- Total ZIP entries: **920**.
- Resource extensions: `.webp`=719, `.png`=153, `.xml`=42.

Largest resource qualifier groups:

- `res/drawable-xhdpi-v4/`: **805** files
- `res/drawable-anydpi-v21/`: **36** files
- `res/drawable-hdpi-v4/`: **19** files
- `res/drawable-xxhdpi-v4/`: **10** files
- `res/drawable-ldrtl-xhdpi-v17/`: **5** files
- `res/drawable-ja-xhdpi-v4/`: **4** files
- `res/drawable-ar-xhdpi-v4/`: **3** files
- `res/drawable-zh-xhdpi-v4/`: **3** files
- `res/drawable/`: **2** files
- `res/drawable-de-xhdpi-v4/`: **2** files
- `res/drawable-es-rMX-xhdpi-v4/`: **2** files
- `res/drawable-es-rUS-night-xhdpi-v8/`: **2** files
- `res/drawable-es-rUS-xhdpi-v4/`: **2** files
- `res/drawable-fr-xhdpi-v4/`: **2** files
- `res/drawable-it-xhdpi-v4/`: **2** files
- `res/drawable-night-xhdpi-v8/`: **2** files
- `res/drawable-nodpi-v4/`: **2** files
- `res/drawable-pt-rBR-xhdpi-v4/`: **2** files
- `res/drawable-rca-xhdpi-v4/`: **2** files
- `res/drawable-anydpi-v24/`: **1** files
- `res/drawable-en-rCA-xhdpi-v4/`: **1** files
- `res/drawable-en-rGB-xhdpi-v4/`: **1** files
- `res/drawable-es-hdpi-v4/`: **1** files
- `res/drawable-es-xhdpi-v4/`: **1** files
- `res/drawable-fr-rCA-xhdpi-v4/`: **1** files
- `res/drawable-xxxhdpi-v4/`: **1** files

### Notable density-split resource families

- Amazon marketplace/logo/no-image resources for multiple locales, including Mexico (`es-rMX`).
- Search entry UI assets and magnifier/spinner graphics.
- Amazon Pay / QR-related assets (`ic_amazon_pay_lens_qrcode`, `quick_pay_showmyqr`, flash controls).
- Discover and Your Orders widget previews.
- Media/ExoPlayer control icons and playback resources.
- Haul/Bazaar assets and marketplace-specific branding.

## Revised architecture assessment

The complete installed package is not accurately described by a single label such as “native” or “WebView”. Static evidence supports a **multi-renderer architecture**:

1. Android native Java/Kotlin/AndroidX/Compose infrastructure in `base.apk`.
2. A first-class WebView platform (MASH/SMASH/Cordova + JS bridges + pooled/prewarmed WebViews).
3. React Native/Fabric/JSI/TurboModules with Hermes available natively in the ARM64 split.
4. Specialized C/C++ native engines for visual search, AR/3D, ML, video/live streaming, storage/compression and diagnostics.

The presence of all these engines does **not** mean a given screen simultaneously uses all of them. Amazon can route surfaces through feature flags/WebLabs, marketplace rules, account state and server configuration. Dynamic tracing is required to map a particular screen (Home/Search/PDP/Cart/Checkout) to its active renderer with certainty.

## Updated limitations

- Static ELF analysis can identify capabilities, dependencies, JNI entry points and embedded strings, but not prove which code paths execute for a specific session.
- Stripped C++ symbols and dynamically registered JNI can hide additional native entry points.
- Literal native URLs are not equivalent to observed network traffic. Runtime TLS/network instrumentation is required for definitive endpoint attribution.
- Resource splits contain presentation assets but generally not the business logic deciding when they are used.
