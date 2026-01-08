import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import Svg, { Path, Defs, LinearGradient, Stop } from 'react-native-svg';

interface SplashScreenProps {
  onFinish: () => void;
}

export default function SplashScreen({ onFinish }: SplashScreenProps) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Exact heartbeat animation from website:
    // @keyframes heartbeat{0%,100%{transform:scale(1)}14%{transform:scale(1.15)}28%{transform:scale(1)}42%{transform:scale(1.1)}56%{transform:scale(1)}}
    // Duration: 1.2s (1200ms)
    // 14% of 1200ms = 168ms
    // 28% of 1200ms = 336ms
    // 42% of 1200ms = 504ms
    // 56% of 1200ms = 672ms
    // 100% of 1200ms = 1200ms (remaining 528ms at scale 1)

    const heartbeat = Animated.loop(
      Animated.sequence([
        // 0% -> 14%: scale 1 -> 1.15 (168ms)
        Animated.timing(scaleAnim, {
          toValue: 1.15,
          duration: 168,
          useNativeDriver: true,
        }),
        // 14% -> 28%: scale 1.15 -> 1 (168ms)
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 168,
          useNativeDriver: true,
        }),
        // 28% -> 42%: scale 1 -> 1.1 (168ms)
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 168,
          useNativeDriver: true,
        }),
        // 42% -> 56%: scale 1.1 -> 1 (168ms)
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 168,
          useNativeDriver: true,
        }),
        // 56% -> 100%: stay at scale 1 (528ms)
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 528,
          useNativeDriver: true,
        }),
      ])
    );

    heartbeat.start();

    // Transition after 2.5 seconds
    const timer = setTimeout(() => {
      onFinish();
    }, 2500);

    return () => {
      heartbeat.stop();
      clearTimeout(timer);
    };
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View 
        style={[
          styles.logoContainer,
          { transform: [{ scale: scaleAnim }] }
        ]}
      >
        {/* Exact SVG from website */}
        <Svg width={64} height={64} viewBox="-26 -28 52 52" fill="none">
          <Defs>
            <LinearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="0%" stopColor="#22d3ee" />
              <Stop offset="100%" stopColor="#6366f1" />
            </LinearGradient>
          </Defs>
          {/* Shield outline */}
          <Path
            d="M0,-24 L-22,-20 L-22,0 Q-22,16 0,20 Q22,16 22,0 L22,-20 Z"
            stroke="url(#lg)"
            strokeWidth={3.5}
            fill="none"
          />
          {/* Checkmark */}
          <Path
            d="M-6,0 L-2,4 L6,-5"
            stroke="url(#lg)"
            strokeWidth={3.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        </Svg>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050505',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
});
