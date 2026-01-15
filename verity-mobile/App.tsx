import React, { useState, useCallback } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { AppProvider, useApp } from './src/context/AppContext';
import { useFonts } from 'expo-font';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
} from '@expo-google-fonts/inter';
import {
  Newsreader_400Regular,
  Newsreader_500Medium,
  Newsreader_600SemiBold,
} from '@expo-google-fonts/newsreader';
import {
  JetBrainsMono_400Regular,
  JetBrainsMono_500Medium,
} from '@expo-google-fonts/jetbrains-mono';

// Screens - Companion App (Capture & Monitor)
import SplashScreen from './src/screens/SplashScreen';
import HomeScreen from './src/screens/HomeScreen';
import CaptureScreen from './src/screens/CaptureScreen';
import QueueScreen from './src/screens/QueueScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import AuthScreen from './src/screens/AuthScreen';

// Chatbot component
import Chatbot, { ChatbotFAB } from './src/components/Chatbot';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Modern amber/gold editorial color palette
const colors = {
  bg: '#0a0a0b',
  surface: '#111113',
  border: 'rgba(255,255,255,0.06)',
  text: '#fafafa',
  textMuted: '#a3a3a3',
  textSubtle: '#525252',
  accent: '#f59e0b',
};

const DarkTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.bg,
    card: colors.surface,
    text: colors.text,
    border: colors.border,
    primary: colors.text,
  },
};

// Minimal tab bar icon - Eden.so inspired
function TabIcon({ name, focused }: { name: keyof typeof Ionicons.glyphMap; focused: boolean }) {
  if (focused) {
    return (
      <View style={tabStyles.activeIconContainer}>
        <View style={tabStyles.activeBackground} />
        <Ionicons name={name} size={20} color={colors.text} />
      </View>
    );
  }
  return <Ionicons name={name} size={20} color={colors.textSubtle} />;
}

const tabStyles = StyleSheet.create({
  activeIconContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    width: 44,
    height: 28,
  },
  activeBackground: {
    position: 'absolute',
    width: 44,
    height: 28,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.06)',
  },
});

// Tab navigator for main companion screens
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused }) => {
          let iconName: keyof typeof Ionicons.glyphMap;
          switch (route.name) {
            case 'Home': iconName = focused ? 'home' : 'home-outline'; break;
            case 'Queue': iconName = focused ? 'layers' : 'layers-outline'; break;
            case 'History': iconName = focused ? 'checkmark-done-circle' : 'checkmark-done-circle-outline'; break;
            case 'Settings': iconName = focused ? 'cog' : 'cog-outline'; break;
            default: iconName = 'home';
          }
          return <TabIcon name={iconName} focused={focused} />;
        },
        tabBarActiveTintColor: colors.text,
        tabBarInactiveTintColor: colors.textSubtle,
        tabBarStyle: {
          backgroundColor: colors.bg,
          borderTopWidth: 1,
          borderTopColor: colors.border,
          paddingBottom: 10,
          paddingTop: 10,
          height: 70,
          elevation: 0,
          shadowOpacity: 0,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: '500',
          marginTop: 2,
          letterSpacing: 0.3,
        },
        headerStyle: { 
          backgroundColor: colors.bg,
          elevation: 0,
          shadowOpacity: 0,
          borderBottomWidth: 1,
          borderBottomColor: colors.border,
        },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: '500', fontSize: 15, letterSpacing: 0.2 },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ 
          headerShown: false,
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen 
        name="Queue" 
        component={QueueScreen} 
        options={{ title: 'Queue' }}
      />
      <Tab.Screen 
        name="History" 
        component={HistoryScreen} 
        options={{ title: 'Completed' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen} 
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

// Main app navigator that handles auth state
function AppNavigator() {
  const { user } = useApp();

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!user ? (
        // Not logged in - show Auth screen
        <Stack.Screen 
          name="Auth" 
          component={AuthScreen}
          options={{
            headerShown: false,
            animationTypeForReplace: 'pop',
          }}
        />
      ) : (
        // Logged in - show main app
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen 
            name="Capture" 
            component={CaptureScreen}
            options={{
              headerShown: true,
              title: 'Capture',
              headerStyle: { backgroundColor: colors.bg },
              headerTintColor: colors.text,
              presentation: 'modal',
            }}
          />
        </>
      )}
    </Stack.Navigator>
  );
}

// Wrapper to provide context to navigator
function AppWithNavigation() {
  const [chatbotVisible, setChatbotVisible] = useState(false);
  const [showFAB, setShowFAB] = useState(true);

  return (
    <NavigationContainer theme={DarkTheme}>
      <StatusBar style="light" />
      <AppNavigator />
      {showFAB && (
        <ChatbotFAB 
          onPress={() => setChatbotVisible(true)} 
          hasNotification={!chatbotVisible}
        />
      )}
      <Chatbot 
        visible={chatbotVisible} 
        onClose={() => setChatbotVisible(false)} 
      />
    </NavigationContainer>
  );
}

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  
  // Load custom fonts
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
    Newsreader_400Regular,
    Newsreader_500Medium,
    Newsreader_600SemiBold,
    JetBrainsMono_400Regular,
    JetBrainsMono_500Medium,
  });

  // Show splash initially; proceed to app even if fonts are still loading so the app is visible
  if (showSplash) {
    return (
      <>
        <StatusBar style="light" />
        <SplashScreen onFinish={() => setShowSplash(false)} />
      </>
    );
  }

  // If fonts haven't loaded yet, continue rendering the app (fonts will hydrate when available)
  if (!fontsLoaded) {
    console.warn('Fonts not loaded yet; continuing to render UI with fallbacks');
  }

  return (
    <SafeAreaProvider>
      <AppProvider>
        <AppWithNavigation />
      </AppProvider>
    </SafeAreaProvider>
  );
}

// Export font family names for use in screens
export const fonts = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semibold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
  serif: 'Newsreader_400Regular',
  serifMedium: 'Newsreader_500Medium',
  serifSemibold: 'Newsreader_600SemiBold',
  mono: 'JetBrainsMono_400Regular',
  monoMedium: 'JetBrainsMono_500Medium',
};
