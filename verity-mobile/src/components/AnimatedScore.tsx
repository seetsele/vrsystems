import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, ViewStyle } from 'react-native';
import Svg, { Path, Defs, LinearGradient, Stop, Circle } from 'react-native-svg';

interface AnimatedScoreProps {
  score: number;
  size?: number;
  showLabel?: boolean;
  style?: ViewStyle;
}

export default function AnimatedScore({ score, size = 64, showLabel = true, style }: AnimatedScoreProps) {
  const animatedValue = useRef(new Animated.Value(0)).current;
  const scaleValue = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(animatedValue, {
        toValue: score,
        duration: 1000,
        useNativeDriver: false,
      }),
      Animated.spring(scaleValue, {
        toValue: 1,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, [score]);

  const getColor = () => {
    if (score >= 70) return { primary: '#10b981', secondary: '#059669' };
    if (score >= 40) return { primary: '#f59e0b', secondary: '#d97706' };
    return { primary: '#ef4444', secondary: '#dc2626' };
  };

  const getLabel = () => {
    if (score >= 70) return 'Verified';
    if (score >= 40) return 'Uncertain';
    return 'Flagged';
  };

  const colors = getColor();
  const radius = size / 2 - 4;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <Animated.View style={[styles.container, { transform: [{ scale: scaleValue }] }, style]}>
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Defs>
          <LinearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <Stop offset="0%" stopColor={colors.primary} />
            <Stop offset="100%" stopColor={colors.secondary} />
          </LinearGradient>
        </Defs>
        {/* Background circle */}
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={4}
          fill="none"
        />
        {/* Progress circle */}
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#scoreGradient)"
          strokeWidth={4}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      <View style={[styles.scoreContainer, { width: size, height: size }]}>
        <Text style={[styles.scoreText, { fontSize: size / 3, color: colors.primary }]}>{score}</Text>
        {showLabel && (
          <Text style={[styles.labelText, { color: colors.primary, fontSize: size / 8 }]}>{getLabel()}</Text>
        )}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  scoreContainer: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreText: {
    fontWeight: '700',
  },
  labelText: {
    fontWeight: '600',
    marginTop: -2,
  },
});
