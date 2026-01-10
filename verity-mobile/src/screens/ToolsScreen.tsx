import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline } from 'react-native-svg';
import { colors } from '../theme/colors';

const TOOLS = [
  { id: 'source', title: 'Source Checker', desc: 'Evaluate website credibility', icon: 'link', emoji: '🔍' },
  { id: 'moderate', title: 'Content Moderator', desc: 'Detect harmful content', icon: 'shield', emoji: '🛡️' },
  { id: 'research', title: 'Research Assistant', desc: 'AI-powered research', icon: 'book', emoji: '📚' },
  { id: 'social', title: 'Social Monitor', desc: 'Track misinformation trends', icon: 'notifications', emoji: '📡' },
  { id: 'stats', title: 'Stats Validator', desc: 'Verify statistical claims', icon: 'bar-chart', emoji: '📊' },
  { id: 'realtime', title: 'Realtime Stream', desc: 'Live fact-check feed', icon: 'pulse', emoji: '⚡' },
];

// Section Label - matches test site
function SectionLabel({ text }: { text: string }) {
  return (
    <View style={styles.sectionLabel}>
      <Text style={styles.sectionLabelText}>{text}</Text>
    </View>
  );
}

export default function ToolsScreen() {
  return (
    <View style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.logoRow}>
            <Svg width={28} height={32} viewBox="0 0 100 120">
              <Defs>
                <SvgGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <Stop offset="0%" stopColor={colors.amber} />
                  <Stop offset="100%" stopColor={colors.amberLight} />
                </SvgGradient>
              </Defs>
              <Path fill="none" stroke="url(#logoGrad)" strokeWidth="6" d="M50 10 L85 30 L85 70 C85 95 50 105 50 105 C50 105 15 95 15 70 L15 30 Z"/>
              <Polyline fill="none" stroke="url(#logoGrad)" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" points="35,60 45,72 65,48"/>
            </Svg>
            <Text style={styles.logoText}>Tools</Text>
          </View>
        </View>

        {/* Title Section */}
        <View style={styles.titleSection}>
          <SectionLabel text="AI Suite" />
          <Text style={styles.headerTitle}>Professional Verification Tools</Text>
          <Text style={styles.headerSubtitle}>Enterprise-grade tools for comprehensive fact-checking.</Text>
        </View>

        {/* Tools Grid */}
        <View style={styles.toolsGrid}>
          {TOOLS.map(tool => (
            <TouchableOpacity key={tool.id} style={styles.toolCard} activeOpacity={0.7}>
              <View style={styles.toolIcon}>
                <Text style={{ fontSize: 24 }}>{tool.emoji}</Text>
              </View>
              <Text style={styles.toolTitle}>{tool.title}</Text>
              <Text style={styles.toolDesc}>{tool.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* API Section - matches test site CTA */}
        <View style={styles.apiSection}>
          <Text style={styles.apiTitle}>REST API Access</Text>
          <Text style={styles.apiDesc}>
            Simple integration with your existing workflow. SDKs for Python, Node.js, and more.
          </Text>
          <TouchableOpacity style={styles.apiButton}>
            <Text style={styles.apiButtonText}>View API Docs</Text>
            <Ionicons name="arrow-forward" size={16} color="#000" />
          </TouchableOpacity>
        </View>

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
  content: { flex: 1 },
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

  // Title Section
  titleSection: {
    paddingHorizontal: 20,
    marginBottom: 32,
  },
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
  headerTitle: { 
    fontSize: 28, 
    fontWeight: '400', 
    color: colors.textPrimary, 
    marginBottom: 8,
    letterSpacing: -0.5,
  },
  headerSubtitle: { 
    fontSize: 15, 
    color: colors.textSecondary, 
    lineHeight: 22,
  },

  // Tools Grid - matches test site provider grid
  toolsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: 32,
  },
  toolCard: { 
    width: '47%',
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16, 
    padding: 20,
    alignItems: 'center',
  },
  toolIcon: { 
    width: 48, 
    height: 48, 
    backgroundColor: colors.bgElevated,
    borderRadius: 12, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginBottom: 14,
  },
  toolTitle: { 
    fontSize: 14, 
    fontWeight: '600', 
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: 4,
  },
  toolDesc: { 
    fontSize: 12, 
    color: colors.textMuted, 
    textAlign: 'center',
  },

  // API Section - matches test site CTA
  apiSection: { 
    marginHorizontal: 20,
    backgroundColor: 'rgba(245, 158, 11, 0.08)', 
    borderRadius: 24, 
    padding: 28, 
    borderWidth: 1,
    borderColor: colors.amberBorder,
    alignItems: 'center',
  },
  apiTitle: { 
    fontSize: 20, 
    fontWeight: '400', 
    color: colors.textPrimary,
    marginBottom: 8,
  },
  apiDesc: { 
    fontSize: 14, 
    color: colors.textSecondary, 
    lineHeight: 22, 
    textAlign: 'center',
    marginBottom: 20,
  },
  apiButton: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: colors.amber,
    borderRadius: 10,
  },
  apiButtonText: { 
    color: '#000', 
    fontSize: 15, 
    fontWeight: '600',
  },
});
