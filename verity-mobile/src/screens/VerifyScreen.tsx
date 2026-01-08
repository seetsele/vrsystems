import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TextInput, TouchableOpacity, ActivityIndicator, Switch } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useApp, VerificationResult } from '../context/AppContext';

export default function VerifyScreen() {
  const [claim, setClaim] = useState('');
  const [deepAnalysis, setDeepAnalysis] = useState(true);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const { verifyClaim, isLoading } = useApp();

  const handleVerify = async () => {
    if (!claim.trim()) return;
    const res = await verifyClaim(claim);
    setResult(res);
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#10b981';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#09090b', '#0f1419', '#09090b']} style={StyleSheet.absoluteFill} />
      <View style={styles.orbContainer}>
        <View style={[styles.orb, styles.orb1]} />
        <View style={[styles.orb, styles.orb2]} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Input Section */}
        <View style={styles.inputCard}>
          <Text style={styles.inputLabel}>Enter Claim to Verify</Text>
          <TextInput
            style={styles.textInput}
            placeholder="Paste any statement, headline, or quote..."
            placeholderTextColor="#52525b"
            multiline
            numberOfLines={4}
            value={claim}
            onChangeText={setClaim}
          />
          
          <View style={styles.optionRow}>
            <View style={styles.optionLeft}>
              <Ionicons name="flash" size={20} color="#8b5cf6" />
              <Text style={styles.optionText}>Deep AI Analysis</Text>
            </View>
            <Switch
              value={deepAnalysis}
              onValueChange={setDeepAnalysis}
              trackColor={{ false: '#3f3f46', true: '#06b6d4' }}
              thumbColor="#fff"
            />
          </View>

          <TouchableOpacity 
            style={[styles.verifyButton, (!claim.trim() || isLoading) && styles.buttonDisabled]} 
            onPress={handleVerify}
            disabled={!claim.trim() || isLoading}
          >
            <LinearGradient colors={['#06b6d4', '#8b5cf6']} style={styles.buttonGradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}>
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="shield-checkmark" size={20} color="#fff" />
                  <Text style={styles.buttonText}>Verify Claim</Text>
                </>
              )}
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Result */}
        {result && (
          <View style={styles.resultCard}>
            <View style={styles.resultHeader}>
              <View style={[styles.scoreCircle, { borderColor: getScoreColor(result.score) }]}>
                <Text style={[styles.scoreText, { color: getScoreColor(result.score) }]}>{result.score}</Text>
                <Text style={styles.scoreLabel}>Score</Text>
              </View>
              <View style={styles.resultInfo}>
                <Text style={styles.resultVerdict}>{result.verdict}</Text>
                <View style={[styles.verdictBadge, { backgroundColor: getScoreColor(result.score) + '20' }]}>
                  <Text style={[styles.verdictText, { color: getScoreColor(result.score) }]}>
                    {result.score >= 70 ? 'Verified' : result.score >= 40 ? 'Mixed' : 'Flagged'}
                  </Text>
                </View>
              </View>
            </View>
            <Text style={styles.explanation}>{result.explanation}</Text>
            <View style={styles.sourceInfo}>
              <Ionicons name="documents" size={16} color="#71717a" />
              <Text style={styles.sourceText}>{result.sources} sources analyzed</Text>
            </View>
          </View>
        )}

        {/* How It Works */}
        <View style={styles.howItWorks}>
          <Text style={styles.sectionTitle}>How It Works</Text>
          <Step number={1} title="Enter Claim" desc="Paste any statement to verify" icon="create" />
          <Step number={2} title="AI Analysis" desc="Multiple AI models analyze sources" icon="hardware-chip" />
          <Step number={3} title="Get Results" desc="Receive accuracy score & sources" icon="checkmark-done" />
        </View>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

function Step({ number, title, desc, icon }: { number: number; title: string; desc: string; icon: any }) {
  return (
    <View style={styles.step}>
      <View style={styles.stepIcon}>
        <Ionicons name={icon} size={20} color="#06b6d4" />
      </View>
      <View style={styles.stepContent}>
        <Text style={styles.stepTitle}>Step {number}: {title}</Text>
        <Text style={styles.stepDesc}>{desc}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#09090b' },
  orbContainer: { position: 'absolute', width: '100%', height: '100%' },
  orb: { position: 'absolute', borderRadius: 999 },
  orb1: { width: 250, height: 250, backgroundColor: 'rgba(6, 182, 212, 0.12)', top: 50, right: -80 },
  orb2: { width: 200, height: 200, backgroundColor: 'rgba(139, 92, 246, 0.1)', bottom: 150, left: -60 },
  content: { flex: 1, padding: 20 },

  inputCard: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20, padding: 24, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  inputLabel: { fontSize: 16, fontWeight: '600', color: '#fafafa', marginBottom: 12 },
  textInput: { 
    backgroundColor: 'rgba(24, 24, 27, 0.8)', 
    borderRadius: 12, 
    padding: 16, 
    color: '#fafafa', 
    fontSize: 15, 
    minHeight: 120, 
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  optionRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16, marginBottom: 20 },
  optionLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  optionText: { color: '#a1a1aa', fontSize: 14 },
  
  verifyButton: { borderRadius: 12, overflow: 'hidden' },
  buttonGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, paddingVertical: 16 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  buttonDisabled: { opacity: 0.5 },

  resultCard: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20, padding: 24, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  scoreCircle: { width: 80, height: 80, borderRadius: 40, borderWidth: 4, justifyContent: 'center', alignItems: 'center', marginRight: 20 },
  scoreText: { fontSize: 28, fontWeight: '700' },
  scoreLabel: { fontSize: 10, color: '#71717a' },
  resultInfo: { flex: 1 },
  resultVerdict: { fontSize: 20, fontWeight: '700', color: '#fafafa', marginBottom: 8 },
  verdictBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20, alignSelf: 'flex-start' },
  verdictText: { fontSize: 12, fontWeight: '600' },
  explanation: { color: '#a1a1aa', fontSize: 14, lineHeight: 22, marginBottom: 16 },
  sourceInfo: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  sourceText: { color: '#71717a', fontSize: 13 },

  howItWorks: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20, padding: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#fafafa', marginBottom: 16 },
  step: { flexDirection: 'row', alignItems: 'center', padding: 14, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 12, marginBottom: 10 },
  stepIcon: { width: 44, height: 44, borderRadius: 12, backgroundColor: 'rgba(6, 182, 212, 0.15)', justifyContent: 'center', alignItems: 'center' },
  stepContent: { flex: 1, marginLeft: 14 },
  stepTitle: { fontSize: 14, fontWeight: '600', color: '#fafafa' },
  stepDesc: { fontSize: 12, color: '#71717a', marginTop: 2 },
});
