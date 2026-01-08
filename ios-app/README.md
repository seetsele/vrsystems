# Verity iOS App

AI-Powered Fact-Checking Companion App for iOS

## Overview

The Verity iOS app is a companion application that pairs with both the Verity web platform and desktop application. It provides mobile access to all fact-checking features with a beautiful, premium design.

## Features

### 🏠 Home Dashboard
- Quick overview of verification statistics
- Quick action buttons for common tasks
- Recent activity feed
- Desktop pairing status indicator

### ✓ Verify Claims
- Enter any statement or claim to verify
- Toggle deep AI analysis
- Get accuracy scores (0-100)
- View verdict with explanation
- See source citations with credibility scores

### 📜 History
- View all past verifications
- Filter by verified/flagged
- Search through history
- Export or delete records

### 🛠 AI Tools Suite
- **Source Checker**: Evaluate website credibility
- **Content Moderator**: Detect harmful content
- **Research Assistant**: AI-powered research
- **Social Monitor**: Track misinformation trends
- **Stats Validator**: Verify statistics
- **Realtime Stream**: Live fact-check feed

### ⚙️ Settings
- Account management
- Desktop pairing
- API key management
- Data export
- Notification preferences

## Design

The app features:
- Animated gradient backgrounds with floating orbs
- Glass morphism card design
- Premium color palette (Cyan, Purple, Pink)
- Dark mode optimized
- SF Symbols integration
- Smooth animations throughout

## Requirements

- iOS 17.0+
- iPhone or iPad
- Xcode 15.0+ (for development)

## Installation

### For Development

1. Open `Verity.xcodeproj` in Xcode
2. Select your development team in Signing & Capabilities
3. Build and run on your device or simulator

### For Users

The app will be available on the App Store (coming soon).

## Pairing with Desktop

The iOS app automatically attempts to connect to the desktop app when both are on the same network:

1. Launch the Verity desktop app
2. Open the iOS app
3. The status indicator will show "Desktop Paired" when connected

When paired, verifications are synced between devices.

## API Integration

The app connects to:
- Local desktop API (`localhost:8001`) when paired
- Cloud API (`api.veritysystems.app`) as fallback
- Demo mode when offline

## Architecture

```
Verity/
├── VerityApp.swift          # App entry point, state management
├── ContentView.swift        # Main views and components
└── Assets.xcassets/         # App icons and colors
```

### Key Components

- **AppState**: Observable state management
- **NetworkService**: API communication
- **VerificationResult**: Data model for fact-checks
- **AnimatedBackgroundView**: Premium animated background

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Cyan | #06B6D4 | Primary accent |
| Purple | #8B5CF6 | Secondary accent |
| Pink | #EC4899 | Tertiary accent |
| Background | #09090B | Dark theme base |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

Copyright © 2024 Verity Systems. All rights reserved.

## Support

- Email: support@veritysystems.app
- Documentation: https://docs.veritysystems.app
- Status: https://status.veritysystems.app
