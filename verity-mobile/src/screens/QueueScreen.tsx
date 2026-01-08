import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Animated, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Circle } from 'react-native-svg';
import { useApp } from '../context/AppContext';

const { width } = Dimensions.get('window');

// Eden.so + Dieter Rams color palette
const colors = {
  bg: '#0a0a0b',
  surface: '#111113',
  surfaceHover: '#161618',
  border: 'rgba(255,255,255,0.06)',
  borderSubtle: 'rgba(255,255,255,0.03)',
  text: '#fafafa',
  textMuted: '#888888',
  textSubtle: '#555555',
  accent: '#ffffff',
  accentMuted: '#cccccc',
};

// Status indicator
function StatusIndicator({ status }: { status: string }) {
  const getColor = () => {
    switch (status) {
      case 'pending': return '#444444';
      case 'sent': return '#555555';
      case 'processing': return '#666666';
      case 'completed': return '#777777';
      default: return '#333333';
    }
  };

  return (
    <View style={[styles.statusIndicator, { backgroundColor: getColor() }]} />
  );
}

// Minimal stat box
function StatBox({ value, label }: { value: number; label: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statBoxValue}>{value}</Text>
      <Text style={styles.statBoxLabel}>{label}</Text>
    </View>
  );
}

// Queue item component
function QueueCard({ item, onRemove, index }: { item: any; onRemove: () => void; index: number }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateX = useRef(new Animated.Value(-20)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(translateX, { toValue: 0, duration: 400, useNativeDriver: true }),
      ]).start();
    }, index * 80);
  }, []);

  const handlePressIn = () => {
    Animated.spring(scale, { toValue: 0.98, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scale, { toValue: 1, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const getTypeIcon = (type: string): keyof typeof Ionicons.glyphMap => {
    switch (type) {
      case 'image': return 'image-outline';
      case 'url': return 'link-outline';
      default: return 'document-text-outline';
    }
  };

  const getTimeAgo = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return 'Now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#666666';
    if (score >= 40) return '#555555';
    return '#444444';
  };

  return (
    <Animated.View style={[styles.queueCard, { opacity, transform: [{ translateX }, { scale }] }]}>
      <TouchableOpacity 
        activeOpacity={1} 
        onPressIn={handlePressIn} 
        onPressOut={handlePressOut}
        style={styles.queueCardInner}
      >
        {/* Type icon and status */}
        <View style={styles.queueIconCol}>
          <View style={styles.queueTypeIcon}>
            <Ionicons name={getTypeIcon(item.type)} size={18} color={colors.textMuted} />
          </View>
          <StatusIndicator status={item.status} />
        </View>

        {/* Content */}
        <View style={styles.queueContent}>
          <Text style={styles.queueTitle} numberOfLines={1}>{item.title || 'Untitled'}</Text>
          <View style={styles.queueMeta}>
            <Text style={styles.queueStatus}>
              {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
            </Text>
            <View style={styles.metaDot} />
            <Text style={styles.queueTime}>{getTimeAgo(item.timestamp)}</Text>
          </View>

          {/* Progress for processing items */}
          {item.status === 'processing' && (
            <View style={styles.progressContainer}>
              <View style={styles.progressTrack}>
                <View style={[styles.progressFill, { width: '60%' }]} />
              </View>
              <Text style={styles.progressText}>Analyzing...</Text>
            </View>
          )}

          {/* Score for completed items */}
          {item.status === 'completed' && item.score !== undefined && (
            <View style={styles.resultRow}>
              <View style={styles.resultScore}>
                <Svg width={32} height={32} viewBox="0 0 32 32">
                  <Circle
                    cx="16"
                    cy="16"
                    r="14"
                    fill="none"
                    stroke={colors.border}
                    strokeWidth="2"
                  />
                  <Circle
                    cx="16"
                    cy="16"
                    r="14"
                    fill="none"
                    stroke={getScoreColor(item.score)}
                    strokeWidth="2"
                    strokeDasharray={`${(item.score / 100) * 88} 88`}
                    strokeLinecap="round"
                    transform="rotate(-90 16 16)"
                  />
                </Svg>
                <Text style={[styles.resultScoreText, { color: getScoreColor(item.score) }]}>
                  {item.score}
                </Text>
              </View>
              <TouchableOpacity style={styles.viewReportBtn}>
                <Text style={styles.viewReportText}>View report</Text>
                <Svg width={14} height={14} viewBox="0 0 24 24">
                  <Path 
                    d="M9 6l6 6-6 6" 
                    fill="none" 
                    stroke={colors.textSubtle} 
                    strokeWidth="1.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                </Svg>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Remove button */}
        <TouchableOpacity style={styles.removeBtn} onPress={onRemove}>
          <Ionicons name="close" size={16} color={colors.textSubtle} />
        </TouchableOpacity>
      </TouchableOpacity>
    </Animated.View>
  );
}

export default function QueueScreen() {
  const { queue, removeFromQueue, desktopConnected } = useApp();

  const headerOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(headerOpacity, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, []);

  const handleRemove = (id: string) => {
    Alert.alert(
      'Remove Item',
      'Remove this from the queue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Remove', style: 'destructive', onPress: () => removeFromQueue(id) },
      ]
    );
  };

  const pendingCount = queue.filter(q => q.status === 'pending').length;
  const processingCount = queue.filter(q => q.status === 'processing').length;
  const completedCount = queue.filter(q => q.status === 'completed').length;

  return (
    <View style={styles.container}>
      {/* Connection status */}
      <Animated.View style={{ opacity: headerOpacity }}>
        <View style={styles.connectionBar}>
          <View style={styles.connectionLeft}>
            <View style={[styles.connectionDot, { backgroundColor: desktopConnected ? '#666666' : '#333333' }]} />
            <Ionicons 
              name={desktopConnected ? 'cloud-done-outline' : 'cloud-offline-outline'} 
              size={16} 
              color={desktopConnected ? colors.textMuted : colors.textSubtle} 
            />
            <Text style={[styles.connectionText, { color: desktopConnected ? colors.textMuted : colors.textSubtle }]}>
              {desktopConnected ? 'Synced' : 'Offline'}
            </Text>
          </View>
          <Svg width={14} height={14} viewBox="0 0 24 24">
            <Path 
              d="M9 6l6 6-6 6" 
              fill="none" 
              stroke={colors.textSubtle} 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </Svg>
        </View>
      </Animated.View>

      {queue.length === 0 ? (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconWrap}>
            <Ionicons name="layers-outline" size={28} color={colors.textSubtle} />
          </View>
          <Text style={styles.emptyTitle}>Queue is empty</Text>
          <Text style={styles.emptyDesc}>Capture content from home to add items</Text>
        </View>
      ) : (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Stats row */}
          <View style={styles.statsRow}>
            <StatBox value={pendingCount} label="Pending" />
            <StatBox value={processingCount} label="Processing" />
            <StatBox value={completedCount} label="Done" />
          </View>

          {/* Queue items */}
          <View style={styles.queueList}>
            {queue.map((item, index) => (
              <QueueCard 
                key={item.id} 
                item={item} 
                onRemove={() => handleRemove(item.id)}
                index={index}
              />
            ))}
          </View>

          <View style={{ height: 40 }} />
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: colors.bg,
  },
  content: { 
    flex: 1, 
    paddingHorizontal: 20,
  },

  // Connection status
  connectionBar: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between',
    marginHorizontal: 20,
    marginVertical: 16,
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  connectionLeft: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 10,
  },
  connectionDot: { 
    width: 6, 
    height: 6, 
    borderRadius: 3,
  },
  connectionText: { 
    fontSize: 13, 
    fontWeight: '500',
    letterSpacing: 0.2,
  },

  // Stats
  statsRow: { 
    flexDirection: 'row', 
    gap: 10, 
    marginBottom: 20, 
    marginTop: 4,
  },
  statBox: { 
    flex: 1, 
    alignItems: 'center', 
    paddingVertical: 16, 
    backgroundColor: colors.surface, 
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statBoxValue: { 
    fontSize: 28, 
    fontWeight: '200', 
    color: colors.text,
    letterSpacing: -1,
  },
  statBoxLabel: { 
    fontSize: 10, 
    color: colors.textSubtle, 
    marginTop: 4, 
    fontWeight: '500',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },

  // Queue list
  queueList: {
    gap: 10,
  },

  // Queue card
  queueCard: { 
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  queueCardInner: { 
    flexDirection: 'row', 
    padding: 14,
    gap: 12,
  },
  queueIconCol: {
    alignItems: 'center',
    gap: 8,
  },
  queueTypeIcon: { 
    width: 40, 
    height: 40, 
    borderRadius: 10, 
    backgroundColor: colors.surfaceHover,
    justifyContent: 'center', 
    alignItems: 'center',
  },
  statusIndicator: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  queueContent: { 
    flex: 1,
  },
  queueTitle: { 
    color: colors.text, 
    fontSize: 15, 
    fontWeight: '500',
    letterSpacing: 0.1,
  },
  queueMeta: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    marginTop: 4, 
    gap: 8,
  },
  queueStatus: { 
    fontSize: 12, 
    fontWeight: '500', 
    color: colors.textSubtle,
    letterSpacing: 0.2,
  },
  metaDot: {
    width: 3,
    height: 3,
    borderRadius: 1.5,
    backgroundColor: colors.textSubtle,
  },
  queueTime: { 
    fontSize: 12, 
    color: colors.textSubtle,
  },
  removeBtn: { 
    width: 32, 
    height: 32, 
    borderRadius: 8, 
    backgroundColor: colors.surfaceHover, 
    justifyContent: 'center', 
    alignItems: 'center',
  },

  // Progress
  progressContainer: { 
    marginTop: 12,
    gap: 6,
  },
  progressTrack: { 
    height: 4, 
    backgroundColor: colors.border, 
    borderRadius: 2, 
    overflow: 'hidden',
  },
  progressFill: { 
    height: '100%', 
    backgroundColor: colors.textMuted, 
    borderRadius: 2,
  },
  progressText: { 
    fontSize: 11, 
    color: colors.textSubtle,
    letterSpacing: 0.2,
  },

  // Result
  resultRow: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    marginTop: 12, 
    gap: 12,
  },
  resultScore: { 
    position: 'relative',
    width: 32, 
    height: 32, 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  resultScoreText: { 
    position: 'absolute',
    fontSize: 11, 
    fontWeight: '600',
    letterSpacing: -0.5,
  },
  viewReportBtn: { 
    flex: 1,
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center',
    paddingVertical: 10, 
    backgroundColor: colors.surfaceHover,
    borderRadius: 10,
    gap: 4,
  },
  viewReportText: { 
    color: colors.textMuted, 
    fontSize: 13, 
    fontWeight: '500',
    letterSpacing: 0.1,
  },

  // Empty state
  emptyState: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    paddingBottom: 100, 
    paddingHorizontal: 40,
  },
  emptyIconWrap: { 
    width: 56, 
    height: 56, 
    borderRadius: 16,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center', 
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyTitle: { 
    fontSize: 15, 
    fontWeight: '500', 
    color: colors.textMuted,
  },
  emptyDesc: { 
    fontSize: 13, 
    color: colors.textSubtle, 
    textAlign: 'center', 
    marginTop: 4,
  },
});
