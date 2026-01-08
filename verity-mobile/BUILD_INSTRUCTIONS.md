# Verity Companion App - Build Instructions

## Quick Start: Use Expo Go (Development)

The fastest way to test the app is using Expo Go:

```bash
cd verity-mobile
npm install
npx expo start
```

Then scan the QR code with:
- **Android**: Expo Go app from Google Play Store
- **iOS**: Camera app (redirects to Expo Go)

---

## Building APK for Android

### Prerequisites

1. **Install Android Studio**: https://developer.android.com/studio
2. **Set environment variables**:
   ```powershell
   # Add to your system environment variables
   ANDROID_HOME = C:\Users\<YOUR_USER>\AppData\Local\Android\Sdk
   Path += %ANDROID_HOME%\platform-tools
   Path += %ANDROID_HOME%\emulator
   ```

3. **Install Java JDK 17**:
   ```powershell
   winget install Microsoft.OpenJDK.17
   ```

### Option 1: Local Build (Recommended)

```bash
cd verity-mobile

# Generate native Android project
npx expo prebuild --platform android

# Build debug APK
cd android
./gradlew assembleDebug

# APK location: android/app/build/outputs/apk/debug/app-debug.apk
```

For release APK:
```bash
./gradlew assembleRelease
# APK location: android/app/build/outputs/apk/release/app-release.apk
```

### Option 2: EAS Build (Cloud Build)

```bash
# Login to Expo
npx expo login

# Build APK in the cloud
npx eas build --platform android --profile preview
```

---

## Building for iOS

### Prerequisites

- **macOS** with Xcode installed
- Apple Developer account (for distribution)

### Option 1: Local Build

```bash
cd verity-mobile

# Generate native iOS project
npx expo prebuild --platform ios

# Open in Xcode
open ios/VerityCompanion.xcworkspace

# Build and run from Xcode
```

### Option 2: EAS Build (Cloud Build)

```bash
npx expo login
npx eas build --platform ios --profile preview
```

---

## App Configuration

The app connects to the Verity API at:
- **Production**: `https://veritysystems-production.up.railway.app`

API endpoint is configured in `src/context/AppContext.tsx`.

---

## Troubleshooting

### "SDK location not found"
Set ANDROID_HOME environment variable to your Android SDK path.

### "JAVA_HOME not set"
Install JDK 17 and set JAVA_HOME:
```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot"
```

### Gradle timeout
Try running with increased timeout:
```bash
./gradlew assembleRelease --no-daemon
```

---

## Distribution

### Android
- Upload APK to Google Play Console
- Or distribute APK directly via download link

### iOS  
- Upload to App Store Connect via Xcode or Transporter
- TestFlight for beta testing

---

## App Store Listings

**Android Package**: `app.veritysystems.companion`
**iOS Bundle ID**: `app.veritysystems.companion`
**App Name**: Verity Companion
**Version**: 1.0.0
