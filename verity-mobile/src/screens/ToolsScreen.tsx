import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const TOOLS = [
  { id: 'source', title: 'Source Checker', desc: 'Evaluate website credibility', icon: 'link', color: '#06b6d4' },
  { id: 'moderate', title: 'Content Moderator', desc: 'Detect harmful content', icon: 'shield', color: '#8b5cf6' },
  { id: 'research', title: 'Research Assistant', desc: 'AI-powered research', icon: 'book', color: '#ec4899' },
  { id: 'social', title: 'Social Monitor', desc: 'Track misinformation trends', icon: 'notifications', color: '#f59e0b' },
  { id: 'stats', title: 'Stats Validator', desc: 'Verify statistical claims', icon: 'bar-chart', color: '#10b981' },
  { id: 'realtime', title: 'Realtime Stream', desc: 'Live fact-check feed', icon: 'pulse', color: '#3b82f6' },
];

export default function ToolsScreen() {
  return (
    <View style={styles.container}>
      <LinearGradient colors={['#09090b', '#0f1419', '#09090b']} style={StyleSheet.absoluteFill} />
      <View style={styles.orbContainer}>
        <View style={[styles.orb, styles.orb1]} />
        <View style={[styles.orb, styles.orb2]} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.headerTitle}>AI Tools Suite</Text>
        <Text style={styles.headerSubtitle}>Powerful fact-checking tools at your fingertips</Text>

        {TOOLS.map(tool => (
          <TouchableOpacity key={tool.id} style={styles.toolCard} activeOpacity={0.7}>
            <View style={[styles.toolIcon, { backgroundColor: tool.color + '20' }]}>
              <Ionicons name={tool.icon as any} size={28} color={tool.color} />
            </View>
            <View style={styles.toolContent}>
              <Text style={styles.toolTitle}>{tool.title}</Text>
              <Text style={styles.toolDesc}>{tool.desc}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#52525b" />
          </TouchableOpacity>
        ))}

        {/* API Section */}
        <View style={styles.apiSection}>
          <View style={styles.apiHeader}>
            <Ionicons name="code-slash" size={24} color="#06b6d4" />
            <Text style={styles.apiTitle}>Developer API</Text>
          </View>
          <Text style={styles.apiDesc}>
            Access all verification tools programmatically. Perfect for integrating fact-checking into your applications.
          </Text>
          <TouchableOpacity style={styles.apiButton}>
            <Text style={styles.apiButtonText}>View Documentation</Text>
            <Ionicons name="arrow-forward" size={16} color="#06b6d4" />
          </TouchableOpacity>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#09090b' },
  orbContainer: { position: 'absolute', width: '100%', height: '100%' },
  orb: { position: 'absolute', borderRadius: 999 },
  orb1: { width: 200, height: 200, backgroundColor: 'rgba(139, 92, 246, 0.1)', top: 100, right: -60 },
  orb2: { width: 180, height: 180, backgroundColor: 'rgba(6, 182, 212, 0.08)', bottom: 200, left: -40 },
  content: { flex: 1, padding: 20 },

  headerTitle: { fontSize: 28, fontWeight: '700', color: '#fafafa', marginBottom: 4 },
  headerSubtitle: { fontSize: 15, color: '#71717a', marginBottom: 24 },

  toolCard: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: 'rgba(255,255,255,0.05)', 
    borderRadius: 16, 
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  toolIcon: { width: 56, height: 56, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  toolContent: { flex: 1, marginLeft: 16 },
  toolTitle: { fontSize: 16, fontWeight: '600', color: '#fafafa' },
  toolDesc: { fontSize: 13, color: '#71717a', marginTop: 2 },

  apiSection: { 
    backgroundColor: 'rgba(6, 182, 212, 0.08)', 
    borderRadius: 20, 
    padding: 24, 
    marginTop: 12,
    borderWidth: 1,
    borderColor: 'rgba(6, 182, 212, 0.2)',
  },
  apiHeader: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 12 },
  apiTitle: { fontSize: 18, fontWeight: '700', color: '#fafafa' },
  apiDesc: { fontSize: 14, color: '#a1a1aa', lineHeight: 22, marginBottom: 16 },
  apiButton: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  apiButtonText: { color: '#06b6d4', fontSize: 14, fontWeight: '600' },
});
