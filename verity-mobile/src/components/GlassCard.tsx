import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface GlassCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'default' | 'elevated' | 'accent';
  accentColor?: string;
}

export default function GlassCard({ children, style, variant = 'default', accentColor }: GlassCardProps) {
  const getColors = () => {
    switch (variant) {
      case 'elevated':
        return ['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.03)'];
      case 'accent':
        return [`${accentColor}15`, `${accentColor}05`];
      default:
        return ['rgba(255,255,255,0.05)', 'rgba(255,255,255,0.02)'];
    }
  };

  return (
    <View style={[styles.container, style]}>
      <LinearGradient
        colors={getColors() as any}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradient}
      >
        {children}
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  gradient: {
    padding: 16,
  },
});
