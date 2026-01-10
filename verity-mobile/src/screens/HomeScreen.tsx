import React, { useEffect, useRef } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Animated, Dimensions, Easing } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline } from 'react-native-svg';
import { useNavigation } from '@react-navigation/native';
import { useApp } from '../context/AppContext';
import { colors } from '../theme/colors';

const { width } = Dimensions.get('window');

// Hero Badge - matches test site .hero-badge
function HeroBadge() {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(translateY, { toValue: 0, duration: 500, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.heroBadge, { opacity, transform: [{ translateY }] }]}>
      <View style={styles.heroBadgeDot} />
      <Text style={styles.heroBadgeText}>All Systems Operational</Text>
    </Animated.View>
  );
}

// Verity Logo with shield
function VerityLogo() {
  const opacity = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 800, useNativeDriver: true }),
      Animated.spring(scale, { toValue: 1, tension: 50, friction: 8, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.logoContainer, { opacity, transform: [{ scale }] }]}>
      <View style={styles.logoRow}>
        <Svg width={32} height={36} viewBox="0 0 100 120">
          <Defs>
            <SvgGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="0%" stopColor={colors.amber} />
              <Stop offset="100%" stopColor={colors.amberLight} />
            </SvgGradient>
          </Defs>
          <Path 
            fill="none" 
            stroke="url(#logoGrad)" 
            strokeWidth="6" 
            d="M50 10 L85 30 L85 70 C85 95 50 105 50 105 C50 105 15 95 15 70 L15 30 Z"
          />
          <Polyline 
            fill="none" 
            stroke="url(#logoGrad)" 
            strokeWidth="7" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            points="35,60 45,72 65,48"
          />
        </Svg>
        <Text style={styles.logoText}>Verity</Text>
      </View>
    </Animated.View>
  );
}

// Hero Section with animated headline
function HeroSection() {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 500, delay: 100, useNativeDriver: true }),
      Animated.timing(translateY, { toValue: 0, duration: 500, delay: 100, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.heroSection, { opacity, transform: [{ translateY }] }]}>
      <Text style={styles.heroTitle}>
        Stop Publishing{'\n'}
        <Text style={styles.heroTitleAccent}>Misinformation.</Text>
      </Text>
      <Text style={styles.heroSubtitle}>
        The only fact-checker that shows its work—every source, every time.
      </Text>
    </Animated.View>
  );
}

// Stats Row - matches test site .hero-stats
function StatsRow() {
  const { history } = useApp();
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(opacity, { toValue: 1, duration: 500, delay: 400, useNativeDriver: true }).start();
  }, []);

  return (
    <Animated.View style={[styles.statsRow, { opacity }]}>
      <View style={styles.statItem}>
        <Text style={styles.statValue}>40+</Text>
        <Text style={styles.statLabel}>AI Models & Sources</Text>
      </View>
      <View style={styles.statItem}>
        <Text style={styles.statValue}>9</Text>
        <Text style={styles.statLabel}>Point Verification</Text>
      </View>
      <View style={styles.statItem}>
        <Text style={styles.statValue}>{history.length}</Text>
        <Text style={styles.statLabel}>Claims Verified</Text>
      </View>
    </Animated.View>
  );
}

// Terminal Demo - matches test site demo
function TerminalDemo() {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 600, delay: 500, useNativeDriver: true }),
      Animated.timing(translateY, { toValue: 0, duration: 600, delay: 500, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.terminal, { opacity, transform: [{ translateY }] }]}>
      <View style={styles.terminalHeader}>
        <View style={styles.terminalDots}>
          <View style={[styles.terminalDot, { backgroundColor: '#ef4444' }]} />
          <View style={[styles.terminalDot, { backgroundColor: '#eab308' }]} />
          <View style={[styles.terminalDot, { backgroundColor: '#22c55e' }]} />
        </View>
        <Text style={styles.terminalTitle}>verity-cli</Text>
        <View style={{ width: 40 }} />
      </View>
      <View style={styles.terminalBody}>
        <View style={styles.terminalLine}>
          <Text style={styles.terminalPrompt}>$</Text>
          <Text style={styles.terminalCommand}>verity verify "The Earth is approximately 4.5 billion years old"</Text>
        </View>
        <View style={styles.terminalOutput}>
          <View style={styles.outputVerdict}>
            <View style={styles.verdictBadge}>
              <Text style={styles.verdictBadgeText}>✓ VERIFIED TRUE</Text>
            </View>
            <Text style={styles.confidence}>98.7%</Text>
          </View>
          <Text style={styles.outputSources}>Sources: 847 · Claude, GPT-4, Gemini, Wikipedia</Text>
        </View>
      </View>
    </Animated.View>
  );
}

// Feature Card - matches test site .feature-card
function FeatureCard({ icon, title, description, delay = 0 }: { icon: string; title: string; description: string; delay?: number }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 500, delay, useNativeDriver: true }),
      Animated.timing(translateY, { toValue: 0, duration: 500, delay, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <Animated.View style={[styles.featureCard, { opacity, transform: [{ translateY }] }]}>
      <View style={styles.featureIcon}>
        <Text style={{ fontSize: 24 }}>{icon}</Text>
      </View>
      <Text style={styles.featureTitle}>{title}</Text>
      <Text style={styles.featureDesc}>{description}</Text>
    </Animated.View>
  );
}

// Section Header - matches test site .section-header
function SectionHeader({ label, title, subtitle }: { label: string; title: string; subtitle?: string }) {
  return (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionLabel}>
        <Text style={styles.sectionLabelText}>{label}</Text>
      </View>
      <Text style={styles.sectionTitle}>{title}</Text>
      {subtitle && <Text style={styles.sectionSubtitle}>{subtitle}</Text>}
    </View>
  );
}

// Provider Card - matches test site .provider-card
function ProviderCard({ icon, name, models }: { icon: string; name: string; models: string }) {
  return (
    <View style={styles.providerCard}>
      <View style={styles.providerIcon}>
        <Text style={{ fontSize: 20 }}>{icon}</Text>
      </View>
      <Text style={styles.providerName}>{name}</Text>
      <Text style={styles.providerModels}>{models}</Text>
    </View>
  );
}

// CTA Section - matches test site .cta-section
function CTASection() {
  const navigation = useNavigation<any>();

  return (
    <View style={styles.ctaSection}>
      <Text style={styles.ctaTitle}>Ready to verify with confidence?</Text>
      <Text style={styles.ctaSubtitle}>Join newsrooms, researchers, and enterprises who trust Verity.</Text>
      <View style={styles.ctaButtons}>
        <TouchableOpacity 
          style={styles.ctaPrimaryBtn}
          onPress={() => navigation.navigate('Verify')}
        >
          <Text style={styles.ctaPrimaryBtnText}>Start Verifying</Text>
          <Ionicons name="arrow-forward" size={18} color="#000" />
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.ctaOutlineBtn}
          onPress={() => navigation.navigate('Tools')}
        >
          <Text style={styles.ctaOutlineBtnText}>View Tools</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  
  return (
    <View style={styles.container}>
      <ScrollView 
        style={styles.scroll} 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Navigation */}
        <View style={styles.nav}>
          <VerityLogo />
          <TouchableOpacity style={styles.navBtn} onPress={() => navigation.navigate('Settings')}>
            <Ionicons name="settings-outline" size={20} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Hero */}
        <View style={styles.hero}>
          <HeroBadge />
          <HeroSection />
          <StatsRow />
        </View>

        {/* Terminal Demo */}
        <View style={styles.demoSection}>
          <TerminalDemo />
        </View>

        {/* Features Section */}
        <View style={styles.featuresSection}>
          <SectionHeader 
            label="Capabilities"
            title="Built for Professionals Who Can't Afford to Be Wrong"
            subtitle="Enterprise-grade verification with complete transparency."
          />
          <View style={styles.featuresGrid}>
            <FeatureCard 
              icon="🔒" 
              title="Your Data Never Leaves Your Control" 
              description="Zero retention policy. AES-256-GCM encryption, GDPR-compliant."
              delay={600}
            />
            <FeatureCard 
              icon="🤖" 
              title="Multi-Model Consensus" 
              description="20+ AI models must agree. We flag uncertainty—never guess."
              delay={700}
            />
            <FeatureCard 
              icon="⚡" 
              title="Sub-Second Verification" 
              description="Parallel processing across 40+ sources."
              delay={800}
            />
            <FeatureCard 
              icon="📋" 
              title="Full Audit Trail" 
              description="Tamper-proof logs with cryptographic verification."
              delay={900}
            />
          </View>
        </View>

        {/* Providers Section */}
        <View style={styles.providersSection}>
          <SectionHeader 
            label="Infrastructure"
            title="World-Class AI Infrastructure"
            subtitle="Aggregate results from leading AI providers."
          />
          <View style={styles.providersGrid}>
            <ProviderCard icon="🧠" name="OpenAI" models="GPT-4, GPT-4o" />
            <ProviderCard icon="🎭" name="Anthropic" models="Claude 3.5" />
            <ProviderCard icon="✨" name="Google" models="Gemini Pro" />
            <ProviderCard icon="⚡" name="Groq" models="Ultra-fast" />
            <ProviderCard icon="🔍" name="Perplexity" models="Real-time" />
            <ProviderCard icon="📚" name="Wikipedia" models="Knowledge" />
          </View>
          <View style={styles.providersSummary}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryCount}>15+</Text>
              <Text style={styles.summaryLabel}>AI Providers</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryCount}>27+</Text>
              <Text style={styles.summaryLabel}>Data Sources</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryCount}>12+</Text>
              <Text style={styles.summaryLabel}>Fact-Check Orgs</Text>
            </View>
          </View>
        </View>

        {/* CTA */}
        <CTASection />

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>© 2026 Verity Systems. All rights reserved.</Text>
        </View>
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
  scrollContent: { paddingBottom: 40 },

  // Navigation
  nav: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  navBtn: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // Logo
  logoContainer: {},
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  logoText: {
    fontSize: 22,
    fontWeight: '600',
    color: colors.textPrimary,
    letterSpacing: -0.5,
  },

  // Hero
  hero: {
    paddingHorizontal: 24,
    paddingTop: 40,
    paddingBottom: 60,
    alignItems: 'center',
  },
  heroBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: colors.greenSoft,
    borderWidth: 1,
    borderColor: colors.greenBorder,
    borderRadius: 100,
    marginBottom: 24,
  },
  heroBadgeDot: {
    width: 6,
    height: 6,
    backgroundColor: colors.green,
    borderRadius: 3,
  },
  heroBadgeText: {
    fontSize: 12,
    color: colors.green,
    fontWeight: '500',
  },

  // Hero Section
  heroSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  heroTitle: {
    fontSize: 36,
    fontWeight: '400',
    color: colors.textPrimary,
    textAlign: 'center',
    lineHeight: 42,
    letterSpacing: -1,
  },
  heroTitleAccent: {
    fontStyle: 'italic',
    color: colors.amber,
  },
  heroSubtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 24,
    paddingHorizontal: 20,
  },

  // Stats
  statsRow: {
    flexDirection: 'row',
    gap: 32,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: '500',
    color: colors.amber,
    letterSpacing: -0.5,
  },
  statLabel: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 4,
    textAlign: 'center',
  },

  // Demo Section
  demoSection: {
    paddingHorizontal: 20,
    marginBottom: 60,
  },

  // Terminal
  terminal: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    overflow: 'hidden',
  },
  terminalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: colors.bgElevated,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  terminalDots: {
    flexDirection: 'row',
    gap: 6,
  },
  terminalDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  terminalTitle: {
    fontSize: 12,
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  terminalBody: {
    padding: 16,
  },
  terminalLine: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 12,
  },
  terminalPrompt: {
    fontSize: 14,
    color: colors.amber,
    fontFamily: 'monospace',
  },
  terminalCommand: {
    fontSize: 13,
    color: colors.textPrimary,
    fontFamily: 'monospace',
    flex: 1,
  },
  terminalOutput: {
    padding: 12,
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.15)',
    borderRadius: 10,
  },
  outputVerdict: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  verdictBadge: {
    paddingVertical: 4,
    paddingHorizontal: 10,
    backgroundColor: colors.greenSoft,
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.25)',
    borderRadius: 6,
  },
  verdictBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.green,
    fontFamily: 'monospace',
  },
  confidence: {
    fontSize: 13,
    color: colors.textSecondary,
    fontFamily: 'monospace',
  },
  outputSources: {
    fontSize: 12,
    color: colors.textMuted,
  },

  // Features Section
  featuresSection: {
    paddingHorizontal: 20,
    marginBottom: 60,
  },
  sectionHeader: {
    alignItems: 'center',
    marginBottom: 32,
  },
  sectionLabel: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    backgroundColor: colors.amberSoft,
    borderWidth: 1,
    borderColor: colors.amberBorder,
    borderRadius: 100,
    marginBottom: 16,
  },
  sectionLabelText: {
    fontSize: 12,
    color: colors.amber,
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 26,
    fontWeight: '400',
    color: colors.textPrimary,
    textAlign: 'center',
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  featuresGrid: {
    gap: 12,
  },
  featureCard: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    padding: 20,
  },
  featureIcon: {
    width: 48,
    height: 48,
    backgroundColor: colors.bgElevated,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 6,
  },
  featureDesc: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },

  // Providers Section
  providersSection: {
    paddingHorizontal: 20,
    marginBottom: 60,
  },
  providersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 20,
  },
  providerCard: {
    width: (width - 60) / 3,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  providerIcon: {
    width: 40,
    height: 40,
    backgroundColor: colors.bgElevated,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  providerName: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 2,
  },
  providerModels: {
    fontSize: 11,
    color: colors.textMuted,
  },
  providersSummary: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 24,
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryCount: {
    fontSize: 24,
    fontWeight: '500',
    color: colors.amber,
  },
  summaryLabel: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: 2,
  },

  // CTA Section
  ctaSection: {
    marginHorizontal: 20,
    padding: 32,
    backgroundColor: 'rgba(245, 158, 11, 0.08)',
    borderWidth: 1,
    borderColor: colors.amberBorder,
    borderRadius: 24,
    alignItems: 'center',
    marginBottom: 40,
  },
  ctaTitle: {
    fontSize: 24,
    fontWeight: '400',
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: 8,
  },
  ctaSubtitle: {
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  ctaButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  ctaPrimaryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: colors.amber,
    borderRadius: 10,
  },
  ctaPrimaryBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
  },
  ctaOutlineBtn: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderWidth: 1,
    borderColor: colors.borderHover,
    borderRadius: 10,
  },
  ctaOutlineBtnText: {
    fontSize: 15,
    fontWeight: '500',
    color: colors.textPrimary,
  },

  // Footer
  footer: {
    paddingVertical: 24,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: colors.border,
    marginHorizontal: 20,
  },
  footerText: {
    fontSize: 13,
    color: colors.textMuted,
  },
});
