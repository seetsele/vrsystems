import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TextInput, TouchableOpacity, ActivityIndicator, Animated, Easing } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline } from 'react-native-svg';
import { useApp, VerificationResult } from '../context/AppContext';
import { colors } from '../theme/colors';

// Header with logo - matches test site nav
function Header() {
  return (
    <View style={styles.header}>
      <View style={styles.logoRow}>
        <Svg width={28} height={32} viewBox="0 0 100 120">
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
        <Text style={styles.logoText}>Verify</Text>
      </View>
    </View>
  );
}

// Section Label - matches test site .section-label
function SectionLabel({ text }: { text: string }) {
  return (
    <View style={styles.sectionLabel}>
      <Text style={styles.sectionLabelText}>{text}</Text>
    </View>
  );
}

export default function VerifyScreen() {
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const { verifyClaim, isLoading } = useApp();
  
  const inputFocused = useRef(new Animated.Value(0)).current;
  const resultOpacity = useRef(new Animated.Value(0)).current;
  const resultTranslateY = useRef(new Animated.Value(20)).current;

  const handleVerify = async () => {
    if (!claim.trim()) return;
    const res = await verifyClaim(claim);
    setResult(res);
  };

  useEffect(() => {
    if (result) {
      Animated.parallel([
        Animated.timing(resultOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(resultTranslateY, { toValue: 0, duration: 400, useNativeDriver: true, easing: Easing.out(Easing.cubic) }),
      ]).start();
    }
  }, [result]);

  const getScoreColor = (score: number) => {
    if (score >= 70) return colors.green;
    if (score >= 40) return colors.amber;
    return colors.red;
  };

  const getVerdictText = (score: number) => {
    if (score >= 70) return 'VERIFIED TRUE';
    if (score >= 40) return 'MIXED/UNCERTAIN';
    return 'LIKELY FALSE';
  };

  const handleFocus = () => {
    Animated.timing(inputFocused, { toValue: 1, duration: 200, useNativeDriver: false }).start();
  };

  const handleBlur = () => {
    Animated.timing(inputFocused, { toValue: 0, duration: 200, useNativeDriver: false }).start();
  };

  const borderColor = inputFocused.interpolate({
    inputRange: [0, 1],
    outputRange: [colors.border, colors.amber],
  });

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        <Header />

        {/* Input Section - matches test site terminal style */}
        <View style={styles.inputSection}>
          <SectionLabel text="Enter Claim" />
          <Text style={styles.sectionTitle}>What do you want to verify?</Text>
          <Text style={styles.sectionSubtitle}>Paste any statement, headline, quote, or claim to fact-check.</Text>
          
          <Animated.View style={[styles.inputCard, { borderColor }]}>
            <TextInput
              style={styles.textInput}
              placeholder="e.g., The Earth is approximately 4.5 billion years old..."
              placeholderTextColor={colors.textMuted}
              multiline
              numberOfLines={4}
              value={claim}
              onChangeText={setClaim}
              onFocus={handleFocus}
              onBlur={handleBlur}
            />
          </Animated.View>

          {/* Quick Examples */}
          <View style={styles.quickActions}>
            <Text style={styles.quickActionsLabel}>Try an example:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <TouchableOpacity 
                style={styles.quickAction}
                onPress={() => setClaim('The Great Wall of China is visible from space')}
              >
                <Text style={styles.quickActionText}>Great Wall visible from space?</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.quickAction}
                onPress={() => setClaim('Humans only use 10% of their brain')}
              >
                <Text style={styles.quickActionText}>10% brain usage myth</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>

          {/* Verify Button - matches test site .btn-hero */}
          <TouchableOpacity 
            style={[styles.verifyButton, (!claim.trim() || isLoading) && styles.buttonDisabled]} 
            onPress={handleVerify}
            disabled={!claim.trim() || isLoading}
            activeOpacity={0.8}
          >
            {isLoading ? (
              <ActivityIndicator color="#000" />
            ) : (
              <>
                <Ionicons name="shield-checkmark" size={20} color="#000" />
                <Text style={styles.verifyButtonText}>Verify Claim</Text>
                <Ionicons name="arrow-forward" size={18} color="#000" />
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Result Section - matches test site terminal output */}
        {result && (
          <Animated.View style={[styles.resultSection, { opacity: resultOpacity, transform: [{ translateY: resultTranslateY }] }]}>
            <View style={styles.resultCard}>
              {/* Result Header */}
              <View style={styles.resultHeader}>
                <View style={[styles.verdictBadge, { backgroundColor: getScoreColor(result.score) + '20', borderColor: getScoreColor(result.score) + '40' }]}>
                  <Ionicons 
                    name={result.score >= 70 ? 'checkmark-circle' : result.score >= 40 ? 'help-circle' : 'close-circle'} 
                    size={16} 
                    color={getScoreColor(result.score)} 
                  />
                  <Text style={[styles.verdictText, { color: getScoreColor(result.score) }]}>
                    {getVerdictText(result.score)}
                  </Text>
                </View>
                <Text style={styles.confidenceText}>{result.score}% confidence</Text>
              </View>

              {/* Score Circle */}
              <View style={styles.scoreRow}>
                <View style={[styles.scoreCircle, { borderColor: getScoreColor(result.score) }]}>
                  <Text style={[styles.scoreNumber, { color: getScoreColor(result.score) }]}>{result.score}</Text>
                  <Text style={styles.scoreLabel}>Score</Text>
                </View>
                <View style={styles.scoreInfo}>
                  <Text style={styles.resultVerdict}>{result.verdict}</Text>
                  <Text style={styles.resultExplanation} numberOfLines={3}>{result.explanation}</Text>
                </View>
              </View>

              {/* Sources */}
              <View style={styles.sourcesRow}>
                <Ionicons name="documents-outline" size={16} color={colors.textMuted} />
                <Text style={styles.sourcesText}>
                  {result.sources} sources analyzed · Claude, GPT-4, Gemini, Wikipedia
                </Text>
              </View>
            </View>
          </Animated.View>
        )}

        {/* How It Works - matches test site steps */}
        {!result && (
          <View style={styles.howSection}>
            <SectionLabel text="How It Works" />
            <Text style={styles.howTitle}>Triple-Check at Every Level</Text>
            
            <View style={styles.stepsGrid}>
              <View style={styles.stepCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepNumberText}>1</Text>
                </View>
                <Text style={styles.stepTitle}>Data Sources</Text>
                <Text style={styles.stepDesc}>Academic databases, news wires, fact-check organizations.</Text>
              </View>
              
              <View style={styles.stepCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepNumberText}>2</Text>
                </View>
                <Text style={styles.stepTitle}>AI Analysis</Text>
                <Text style={styles.stepDesc}>GPT-4, Claude, Gemini, and 10+ models analyze in parallel.</Text>
              </View>
              
              <View style={styles.stepCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepNumberText}>3</Text>
                </View>
                <Text style={styles.stepTitle}>Validation</Text>
                <Text style={styles.stepDesc}>Cross-model consensus and confidence calibration.</Text>
              </View>
            </View>
          </View>
        )}

        <View style={{ height: 40 }} />
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

  // Header
  header: {
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  logoText: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    letterSpacing: -0.5,
  },

  // Section Label
  sectionLabel: {
    alignSelf: 'flex-start',
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
    fontSize: 28,
    fontWeight: '400',
    color: colors.textPrimary,
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 15,
    color: colors.textSecondary,
    marginBottom: 24,
    lineHeight: 22,
  },

  // Input Section
  inputSection: {
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  inputCard: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderRadius: 16,
    overflow: 'hidden',
  },
  textInput: {
    padding: 18,
    color: colors.textPrimary,
    fontSize: 15,
    minHeight: 120,
    textAlignVertical: 'top',
    lineHeight: 22,
  },

  // Quick Actions
  quickActions: {
    marginTop: 16,
    marginBottom: 24,
  },
  quickActionsLabel: {
    fontSize: 12,
    color: colors.textMuted,
    marginBottom: 10,
  },
  quickAction: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    marginRight: 8,
  },
  quickActionText: {
    fontSize: 13,
    color: colors.textSecondary,
  },

  // Verify Button - matches .btn-hero
  verifyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 16,
    paddingHorizontal: 24,
    backgroundColor: colors.amber,
    borderRadius: 12,
  },
  verifyButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  buttonDisabled: {
    opacity: 0.5,
  },

  // Result Section
  resultSection: {
    paddingHorizontal: 20,
    marginTop: 32,
  },
  resultCard: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    padding: 20,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  verdictBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderRadius: 8,
  },
  verdictText: {
    fontSize: 12,
    fontWeight: '600',
    fontFamily: 'monospace',
  },
  confidenceText: {
    fontSize: 13,
    color: colors.textSecondary,
    fontFamily: 'monospace',
  },

  // Score Row
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 20,
    marginBottom: 20,
  },
  scoreCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreNumber: {
    fontSize: 28,
    fontWeight: '700',
  },
  scoreLabel: {
    fontSize: 10,
    color: colors.textMuted,
  },
  scoreInfo: {
    flex: 1,
  },
  resultVerdict: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 6,
  },
  resultExplanation: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },

  // Sources Row
  sourcesRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  sourcesText: {
    fontSize: 13,
    color: colors.textMuted,
  },

  // How Section
  howSection: {
    paddingHorizontal: 20,
    marginTop: 48,
  },
  howTitle: {
    fontSize: 24,
    fontWeight: '400',
    color: colors.textPrimary,
    marginBottom: 24,
    letterSpacing: -0.5,
  },
  stepsGrid: {
    gap: 12,
  },
  stepCard: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  stepNumber: {
    width: 48,
    height: 48,
    backgroundColor: colors.amberSoft,
    borderWidth: 1,
    borderColor: colors.amberBorder,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
  },
  stepNumberText: {
    fontSize: 20,
    fontWeight: '500',
    color: colors.amber,
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 6,
  },
  stepDesc: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});
