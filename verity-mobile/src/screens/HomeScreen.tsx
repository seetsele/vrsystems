import React, { useEffect, useRef } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Animated, Dimensions, Easing } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline, Text as SvgText, Circle } from 'react-native-svg';
import { useNavigation } from '@react-navigation/native';
import { useApp } from '../context/AppContext';
import { fonts } from '../../App';

const { width, height } = Dimensions.get('window');

// Premium Amber/Gold editorial color palette
const colors = {
  bg: '#0a0a0b',
  bgGradient: '#0d0d0e',
  surface: '#111113',
  surfaceElevated: '#18181b',
  surfaceHover: '#1c1c20',
  border: 'rgba(255,255,255,0.06)',
  borderSubtle: 'rgba(255,255,255,0.04)',
  borderAccent: 'rgba(245,158,11,0.2)',
  text: '#fafafa',
  textMuted: '#a3a3a3',
  textSubtle: '#525252',
  accent: '#f59e0b',
  accentMuted: '#fbbf24',
};

// Floating Shield Animation
function FloatingShield({ delay, scale = 1, x, y }: { delay: number; scale?: number; x: number; y: number }) {
  const translateY = useRef(new Animated.Value(0)).current;
  const rotate = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timeout = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0.04,
        duration: 2000,
        useNativeDriver: true,
        easing: Easing.out(Easing.cubic),
      }).start();

      Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(translateY, { toValue: -12, duration: 4500, useNativeDriver: true, easing: Easing.inOut(Easing.sin) }),
            Animated.timing(rotate, { toValue: 1, duration: 7000, useNativeDriver: true, easing: Easing.inOut(Easing.sin) }),
          ]),
          Animated.parallel([
            Animated.timing(translateY, { toValue: 12, duration: 4500, useNativeDriver: true, easing: Easing.inOut(Easing.sin) }),
            Animated.timing(rotate, { toValue: -1, duration: 7000, useNativeDriver: true, easing: Easing.inOut(Easing.sin) }),
          ]),
        ])
      ).start();
    }, delay);

    return () => clearTimeout(timeout);
  }, []);

  const rotateInterpolate = rotate.interpolate({
    inputRange: [-1, 1],
    outputRange: ['-4deg', '4deg'],
  });

  const size = 50 * scale;

  return (
    <Animated.View style={{ position: 'absolute', left: x, top: y, opacity, transform: [{ translateY }, { rotate: rotateInterpolate }] }}>
      <Svg width={size} height={size * 1.2} viewBox="0 0 100 120">
        <Path 
          fill="none" 
          stroke="rgba(255,255,255,0.5)"
          strokeWidth="2" 
          d="M50 8 L88 28 L88 65 C88 92 50 110 50 110 C50 110 12 92 12 65 L12 28 Z"
        />
        <Polyline 
          fill="none" 
          stroke="rgba(255,255,255,0.5)"
          strokeWidth="3" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          points="32,58 44,72 68,46"
        />
      </Svg>
    </Animated.View>
  );
}

// Refined Verity Logo
function VerityLogo() {
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const logoScale = useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(logoOpacity, { toValue: 1, duration: 800, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
      Animated.spring(logoScale, { toValue: 1, tension: 50, friction: 8, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.logoContainer, { opacity: logoOpacity, transform: [{ scale: logoScale }] }]}>
      <Svg width={150} height={45} viewBox="0 0 300 80">
        <Defs>
          <SvgGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <Stop offset="0%" stopColor="#f59e0b" stopOpacity="1" />
            <Stop offset="50%" stopColor="#fbbf24" stopOpacity="1" />
            <Stop offset="100%" stopColor="#fcd34d" stopOpacity="1" />
          </SvgGradient>
        </Defs>
        <SvgText
          x="150"
          y="55"
          textAnchor="middle"
          fill="url(#logoGradient)"
          fontSize="48"
          fontWeight="300"
          fontFamily="System"
          letterSpacing="8"
        >verity</SvgText>
      </Svg>
      
      {/* Shield mark with gradient */}
      <Svg width={22} height={26} viewBox="0 0 100 120" style={{ marginTop: 14, opacity: 0.65 }}>
        <Defs>
          <SvgGradient id="shieldMarkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor="#f59e0b" stopOpacity="0.9" />
            <Stop offset="100%" stopColor="#d97706" stopOpacity="0.7" />
          </SvgGradient>
        </Defs>
        <Path 
          fill="none" 
          stroke="url(#shieldMarkGrad)" 
          strokeWidth="5" 
          d="M50 8 L88 28 L88 65 C88 92 50 110 50 110 C50 110 12 92 12 65 L12 28 Z"
        />
        <Polyline 
          fill="none" 
          stroke="url(#shieldMarkGrad)" 
          strokeWidth="6" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          points="32,58 44,72 68,46"
        />
      </Svg>
    </Animated.View>
  );
}

// Premium action row with haptic feedback feel
function ActionRow({ icon, label, description, onPress, delay }: any) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(16)).current;
  const scale = useRef(new Animated.Value(1)).current;
  const iconRotate = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 600, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
        Animated.timing(translateY, { toValue: 0, duration: 600, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
      ]).start();
    }, delay);
  }, []);

  const handlePressIn = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 0.97, useNativeDriver: true, tension: 400, friction: 20 }),
      Animated.timing(iconRotate, { toValue: 1, duration: 150, useNativeDriver: true }),
    ]).start();
  };

  const handlePressOut = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 1, useNativeDriver: true, tension: 400, friction: 20 }),
      Animated.timing(iconRotate, { toValue: 0, duration: 200, useNativeDriver: true }),
    ]).start();
  };

  const iconRotateInterpolate = iconRotate.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '-5deg'],
  });

  return (
    <Animated.View style={{ opacity, transform: [{ translateY }, { scale }] }}>
      <TouchableOpacity 
        onPress={onPress} 
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
        style={styles.actionRow}
      >
        <Animated.View style={[styles.actionIconWrap, { transform: [{ rotate: iconRotateInterpolate }] }]}>
          <Ionicons name={icon} size={20} color={colors.text} />
        </Animated.View>
        <View style={styles.actionContent}>
          <Text style={styles.actionLabel}>{label}</Text>
          <Text style={styles.actionDesc}>{description}</Text>
        </View>
        <View style={styles.actionArrow}>
          <Svg width={18} height={18} viewBox="0 0 24 24">
            <Path 
              d="M9 6l6 6-6 6" 
              fill="none" 
              stroke={colors.textMuted} 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </Svg>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

// Enhanced stat display with animated numbers
function StatDisplay({ value, label, delay }: { value: number; label: string; delay: number }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(0.9)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
        Animated.spring(scale, { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      ]).start();
    }, delay);
  }, []);

  return (
    <Animated.View style={[styles.statDisplay, { opacity, transform: [{ scale }] }]}>
      <Text style={styles.statNumber}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </Animated.View>
  );
}

// Queue preview item - eden.so card style
function QueuePreview({ item, delay }: { item: any; delay: number }) {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.timing(opacity, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    }, delay);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing': return '#888888';
      case 'completed': return '#666666';
      default: return '#444444';
    }
  };

  return (
    <Animated.View style={[styles.queuePreview, { opacity }]}>
      <View style={[styles.queueStatusDot, { backgroundColor: getStatusColor(item.status) }]} />
      <View style={styles.queuePreviewContent}>
        <Text style={styles.queuePreviewTitle} numberOfLines={1}>{item.title || 'Untitled'}</Text>
        <Text style={styles.queuePreviewStatus}>{item.status}</Text>
      </View>
      {item.status === 'completed' && item.score !== undefined && (
        <Text style={styles.queuePreviewScore}>{item.score}</Text>
      )}
    </Animated.View>
  );
}

// Section header component
function SectionHeader({ title, action, onAction }: { title: string; action?: string; onAction?: () => void }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {action && (
        <TouchableOpacity onPress={onAction}>
          <Text style={styles.sectionAction}>{action}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  const { queue, history, desktopConnected } = useApp();
  
  const pendingCount = queue.filter(q => q.status === 'pending').length;
  const processingCount = queue.filter(q => q.status === 'processing').length;
  const completedToday = history.filter(h => {
    const today = new Date().toDateString();
    return new Date(h.timestamp).toDateString() === today;
  }).length;

  const fadeIn = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeIn, { toValue: 1, duration: 1000, useNativeDriver: true, easing: Easing.out(Easing.cubic) }).start();
  }, []);

  return (
    <View style={styles.container}>
      {/* Floating product elements */}
      <FloatingShield delay={0} scale={1.3} x={-15} y={80} />
      <FloatingShield delay={600} scale={0.9} x={width - 50} y={200} />
      <FloatingShield delay={1200} scale={0.7} x={30} y={height * 0.6} />
      <FloatingShield delay={1800} scale={0.5} x={width - 70} y={height * 0.75} />
      
      <ScrollView 
        style={styles.scroll} 
        showsVerticalScrollIndicator={false} 
        contentContainerStyle={styles.scrollContent}
      >
        {/* Header with logo */}
        <Animated.View style={[styles.header, { opacity: fadeIn }]}>
          <VerityLogo />
          
          {/* Connection indicator - minimal */}
          <View style={styles.connectionIndicator}>
            <View style={[styles.connectionDot, { backgroundColor: desktopConnected ? '#666666' : '#333333' }]} />
            <Text style={styles.connectionLabel}>
              {desktopConnected ? 'Synced' : 'Offline'}
            </Text>
          </View>
        </Animated.View>

        {/* Stats section - Eden.so inspired large numbers */}
        <View style={styles.statsSection}>
          <SectionHeader title="Today" />
          <View style={styles.statsGrid}>
            <StatDisplay value={pendingCount} label="Queued" delay={200} />
            <View style={styles.statsDivider} />
            <StatDisplay value={processingCount} label="Processing" delay={300} />
            <View style={styles.statsDivider} />
            <StatDisplay value={completedToday} label="Verified" delay={400} />
          </View>
        </View>

        {/* Actions section - refined list */}
        <View style={styles.actionsSection}>
          <SectionHeader title="Verify" />
          <View style={styles.actionsCard}>
            <ActionRow
              icon="camera-outline"
              label="Camera"
              description="Capture and verify visual content"
              onPress={() => navigation.navigate('Capture', { type: 'camera' })}
              delay={300}
            />
            <View style={styles.actionDivider} />
            <ActionRow
              icon="document-text-outline"
              label="Text"
              description="Paste or type content to verify"
              onPress={() => navigation.navigate('Capture', { type: 'text' })}
              delay={350}
            />
            <View style={styles.actionDivider} />
            <ActionRow
              icon="link-outline"
              label="URL"
              description="Analyze articles and web pages"
              onPress={() => navigation.navigate('Capture', { type: 'link' })}
              delay={400}
            />
            <View style={styles.actionDivider} />
            <ActionRow
              icon="share-outline"
              label="Share"
              description="Import content from other apps"
              onPress={() => navigation.navigate('Capture', { type: 'share' })}
              delay={450}
            />
          </View>
        </View>

        {/* Analytics Preview - New Feature */}
        <View style={styles.actionsSection}>
          <SectionHeader title="Insights" action="Details" onAction={() => navigation.navigate('Settings')} />
          <View style={styles.actionsCard}>
            <View style={styles.analyticsRow}>
              <View style={styles.analyticItem}>
                <Text style={styles.analyticValue}>{history.length}</Text>
                <Text style={styles.analyticLabel}>Total Verified</Text>
              </View>
              <View style={styles.analyticDivider} />
              <View style={styles.analyticItem}>
                <Text style={styles.analyticValue}>{history.filter(h => h.score >= 70).length}</Text>
                <Text style={styles.analyticLabel}>True</Text>
              </View>
              <View style={styles.analyticDivider} />
              <View style={styles.analyticItem}>
                <Text style={styles.analyticValue}>{history.filter(h => h.score < 40).length}</Text>
                <Text style={styles.analyticLabel}>False</Text>
              </View>
              <View style={styles.analyticDivider} />
              <View style={styles.analyticItem}>
                <Text style={styles.analyticValue}>{history.length > 0 ? Math.round(history.reduce((a, h) => a + h.score, 0) / history.length) : 0}%</Text>
                <Text style={styles.analyticLabel}>Avg Score</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Queue preview - if items exist */}
        {queue.length > 0 && (
          <View style={styles.queueSection}>
            <SectionHeader 
              title="Queue" 
              action="View all" 
              onAction={() => navigation.navigate('Queue')} 
            />
            <View style={styles.queueCard}>
              {queue.slice(0, 3).map((item, index) => (
                <React.Fragment key={item.id}>
                  {index > 0 && <View style={styles.queueDivider} />}
                  <QueuePreview item={item} delay={500 + index * 50} />
                </React.Fragment>
              ))}
            </View>
          </View>
        )}

        {/* Empty state - minimal */}
        {queue.length === 0 && history.length === 0 && (
          <View style={styles.emptySection}>
            <View style={styles.emptyIconWrap}>
              <Ionicons name="layers-outline" size={28} color={colors.textSubtle} />
            </View>
            <Text style={styles.emptyTitle}>No verifications yet</Text>
            <Text style={styles.emptyDesc}>Select an action above to begin</Text>
          </View>
        )}

        <View style={{ height: 60 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: colors.bg,
  },
  scroll: { flex: 1 },
  scrollContent: { paddingTop: 70 },

  // Header
  header: { 
    alignItems: 'center', 
    paddingHorizontal: 24,
    paddingBottom: 44,
  },
  logoContainer: {
    alignItems: 'center',
  },
  connectionIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 22,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderRadius: 100,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 8,
  },
  connectionDot: { 
    width: 6, 
    height: 6, 
    borderRadius: 3,
  },
  connectionLabel: { 
    color: colors.textSubtle, 
    fontSize: 11, 
    fontFamily: 'Inter_600SemiBold',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },

  // Section headers
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 4,
    marginBottom: 16,
  },
  sectionTitle: {
    color: colors.textMuted,
    fontSize: 11,
    fontFamily: 'Inter_600SemiBold',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },
  sectionAction: {
    color: colors.textMuted,
    fontSize: 12,
    fontFamily: 'Inter_500Medium',
  },

  // Stats section
  statsSection: {
    paddingHorizontal: 24,
    marginBottom: 36,
  },
  statsGrid: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: 28,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 4,
  },
  statDisplay: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    color: colors.text,
    fontSize: 40,
    fontFamily: 'Newsreader_400Regular',
    letterSpacing: -2,
  },
  statLabel: {
    color: colors.textSubtle,
    fontSize: 10,
    fontFamily: 'Inter_600SemiBold',
    letterSpacing: 1.5,
    marginTop: 8,
    textTransform: 'uppercase',
  },
  statsDivider: {
    width: 1,
    height: 50,
    backgroundColor: colors.border,
  },

  // Actions section
  actionsSection: {
    paddingHorizontal: 24,
    marginBottom: 36,
  },
  actionsCard: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 4,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 18,
    paddingHorizontal: 18,
  },
  actionIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionContent: {
    flex: 1,
    marginLeft: 16,
  },
  actionLabel: {
    color: colors.text,
    fontSize: 16,
    fontFamily: 'Inter_500Medium',
    letterSpacing: 0.2,
  },
  actionDesc: {
    color: colors.textSubtle,
    fontSize: 13,
    marginTop: 3,
    letterSpacing: 0.1,
  },
  actionArrow: {
    opacity: 0.6,
  },
  actionDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 78,
  },

  // Analytics section
  analyticsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 10,
  },
  analyticItem: {
    flex: 1,
    alignItems: 'center',
  },
  analyticValue: {
    color: colors.text,
    fontSize: 22,
    fontFamily: 'Newsreader_400Regular',
    letterSpacing: -0.5,
  },
  analyticLabel: {
    color: colors.textSubtle,
    fontSize: 11,
    marginTop: 4,
    letterSpacing: 0.3,
    textTransform: 'uppercase',
  },
  analyticDivider: {
    width: 1,
    height: 32,
    backgroundColor: colors.borderSubtle,
  },

  // Queue section
  queueSection: {
    paddingHorizontal: 24,
    marginBottom: 36,
  },
  queueCard: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 4,
  },
  queuePreview: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 18,
  },
  queueStatusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  queuePreviewContent: {
    flex: 1,
    marginLeft: 16,
  },
  queuePreviewTitle: {
    color: colors.accentMuted,
    fontSize: 15,
    fontFamily: 'Inter_500Medium',
  },
  queuePreviewStatus: {
    color: colors.textSubtle,
    fontSize: 12,
    marginTop: 3,
    textTransform: 'capitalize',
  },
  queuePreviewScore: {
    color: colors.textMuted,
    fontSize: 20,
    fontFamily: 'Newsreader_400Regular',
  },
  queueDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 40,
  },

  // Empty state
  emptySection: {
    alignItems: 'center',
    paddingVertical: 56,
    paddingHorizontal: 24,
  },
  emptyIconWrap: {
    width: 64,
    height: 64,
    borderRadius: 18,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  emptyTitle: {
    color: colors.textMuted,
    fontSize: 16,
    fontFamily: 'Inter_500Medium',
  },
  emptyDesc: {
    color: colors.textSubtle,
    fontSize: 14,
    marginTop: 6,
  },
});
