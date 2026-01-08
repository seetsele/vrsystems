import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList, Alert, Animated, Dimensions } from 'react-native';
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
  verified: '#666666',
  uncertain: '#555555',
  flagged: '#444444',
};

// Minimal filter chip
function FilterChip({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) {
  const scale = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scale, { toValue: 0.95, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scale, { toValue: 1, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <TouchableOpacity 
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
      >
        <View style={[styles.filterChip, active && styles.filterChipActive]}>
          <Text style={[styles.filterChipText, active && styles.filterChipTextActive]}>{label}</Text>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

// History item - Eden.so card style
function HistoryCard({ item, index }: { item: any; index: number }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(16)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(translateY, { toValue: 0, duration: 400, useNativeDriver: true }),
      ]).start();
    }, index * 60);
  }, []);

  const handlePressIn = () => {
    Animated.spring(scale, { toValue: 0.98, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scale, { toValue: 1, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return colors.verified;
    if (score >= 40) return colors.uncertain;
    return colors.flagged;
  };

  const getVerdict = (score: number) => {
    if (score >= 70) return 'Verified';
    if (score >= 40) return 'Uncertain';
    return 'Flagged';
  };

  const getTimeAgo = (timestamp: string) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return 'Now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
  };

  return (
    <Animated.View style={[styles.historyCard, { opacity, transform: [{ translateY }, { scale }] }]}>
      <TouchableOpacity 
        activeOpacity={1}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        style={styles.historyCardInner}
      >
        {/* Score ring */}
        <View style={styles.scoreContainer}>
          <Svg width={52} height={52} viewBox="0 0 52 52">
            {/* Background ring */}
            <Circle
              cx="26"
              cy="26"
              r="22"
              fill="none"
              stroke={colors.border}
              strokeWidth="2"
            />
            {/* Progress ring */}
            <Circle
              cx="26"
              cy="26"
              r="22"
              fill="none"
              stroke={getScoreColor(item.score)}
              strokeWidth="2"
              strokeDasharray={`${(item.score / 100) * 138} 138`}
              strokeLinecap="round"
              transform="rotate(-90 26 26)"
            />
          </Svg>
          <View style={styles.scoreInner}>
            <Text style={[styles.scoreValue, { color: getScoreColor(item.score) }]}>{item.score}</Text>
          </View>
        </View>

        {/* Content */}
        <View style={styles.historyContent}>
          <Text style={styles.historyClaimText} numberOfLines={2}>{item.claim}</Text>
          <View style={styles.historyMeta}>
            <Text style={[styles.historyVerdict, { color: getScoreColor(item.score) }]}>
              {item.verdict || getVerdict(item.score)}
            </Text>
            <View style={styles.metaDot} />
            <Text style={styles.historyTime}>{getTimeAgo(item.timestamp)}</Text>
          </View>
        </View>

        {/* Arrow */}
        <View style={styles.historyArrow}>
          <Svg width={16} height={16} viewBox="0 0 24 24">
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
      </TouchableOpacity>
    </Animated.View>
  );
}

export default function HistoryScreen() {
  const { history, clearHistory } = useApp();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'verified' | 'flagged'>('all');

  const headerOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(headerOpacity, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, []);

  const filteredHistory = history.filter(item => {
    const matchSearch = item.claim.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || 
      (filter === 'verified' && item.score >= 70) ||
      (filter === 'flagged' && item.score < 70);
    return matchSearch && matchFilter;
  });

  const handleClear = () => {
    Alert.alert(
      'Clear History', 
      'This will remove all verification history. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Clear', style: 'destructive', onPress: clearHistory },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.header, { opacity: headerOpacity }]}>
        {/* Search bar */}
        <View style={styles.searchRow}>
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={16} color={colors.textSubtle} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search..."
              placeholderTextColor={colors.textSubtle}
              value={search}
              onChangeText={setSearch}
            />
            {search.length > 0 && (
              <TouchableOpacity onPress={() => setSearch('')}>
                <Ionicons name="close-circle" size={16} color={colors.textSubtle} />
              </TouchableOpacity>
            )}
          </View>
          <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
            <Ionicons name="trash-outline" size={18} color={colors.textSubtle} />
          </TouchableOpacity>
        </View>

        {/* Filter chips */}
        <View style={styles.filterRow}>
          <FilterChip label="All" active={filter === 'all'} onPress={() => setFilter('all')} />
          <FilterChip label="Verified" active={filter === 'verified'} onPress={() => setFilter('verified')} />
          <FilterChip label="Flagged" active={filter === 'flagged'} onPress={() => setFilter('flagged')} />
        </View>
      </Animated.View>

      {/* History list or empty state */}
      {filteredHistory.length === 0 ? (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconWrap}>
            <Ionicons name="time-outline" size={28} color={colors.textSubtle} />
          </View>
          <Text style={styles.emptyTitle}>
            {search ? 'No results' : 'No history yet'}
          </Text>
          <Text style={styles.emptyDesc}>
            {search ? 'Try a different search term' : 'Completed verifications appear here'}
          </Text>
          {search && (
            <TouchableOpacity style={styles.clearSearchBtn} onPress={() => setSearch('')}>
              <Text style={styles.clearSearchText}>Clear search</Text>
            </TouchableOpacity>
          )}
        </View>
      ) : (
        <FlatList
          data={filteredHistory}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          renderItem={({ item, index }) => <HistoryCard item={item} index={index} />}
          ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
          ListFooterComponent={<View style={{ height: 40 }} />}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: colors.bg,
  },

  // Header
  header: { 
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 8,
  },

  // Search
  searchRow: { 
    flexDirection: 'row', 
    gap: 10,
  },
  searchContainer: { 
    flex: 1, 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: colors.surface, 
    borderRadius: 12, 
    paddingHorizontal: 14, 
    height: 44, 
    borderWidth: 1, 
    borderColor: colors.border,
    gap: 10,
  },
  searchInput: { 
    flex: 1, 
    color: colors.text, 
    fontSize: 14,
    letterSpacing: 0.1,
  },
  clearButton: { 
    width: 44, 
    height: 44, 
    backgroundColor: colors.surface, 
    borderRadius: 12, 
    justifyContent: 'center', 
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },

  // Filters
  filterRow: { 
    flexDirection: 'row', 
    paddingTop: 14, 
    paddingBottom: 8, 
    gap: 8,
  },
  filterChip: { 
    paddingHorizontal: 16, 
    paddingVertical: 8, 
    borderRadius: 100,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  filterChipActive: { 
    backgroundColor: colors.surfaceHover,
    borderColor: colors.textSubtle,
  },
  filterChipText: { 
    color: colors.textSubtle, 
    fontSize: 13, 
    fontWeight: '500',
    letterSpacing: 0.2,
  },
  filterChipTextActive: { 
    color: colors.text,
  },

  // List
  listContent: { 
    paddingHorizontal: 20, 
    paddingTop: 8,
  },

  // History card
  historyCard: { 
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  historyCardInner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    gap: 14,
  },
  scoreContainer: {
    position: 'relative',
    width: 52,
    height: 52,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreInner: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreValue: { 
    fontSize: 16, 
    fontWeight: '500',
    letterSpacing: -0.5,
  },
  historyContent: { 
    flex: 1,
  },
  historyClaimText: { 
    fontSize: 14, 
    fontWeight: '500', 
    color: colors.text, 
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  historyMeta: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    marginTop: 6,
    gap: 8,
  },
  historyVerdict: { 
    fontSize: 12, 
    fontWeight: '500',
    letterSpacing: 0.2,
  },
  metaDot: {
    width: 3,
    height: 3,
    borderRadius: 1.5,
    backgroundColor: colors.textSubtle,
  },
  historyTime: { 
    fontSize: 12, 
    color: colors.textSubtle,
    letterSpacing: 0.2,
  },
  historyArrow: {
    opacity: 0.4,
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
    letterSpacing: 0.1,
  },
  emptyDesc: { 
    fontSize: 13, 
    color: colors.textSubtle, 
    textAlign: 'center', 
    marginTop: 4,
    letterSpacing: 0.1,
  },
  clearSearchBtn: { 
    marginTop: 16, 
    paddingHorizontal: 16, 
    paddingVertical: 8, 
    backgroundColor: colors.surface, 
    borderRadius: 100,
    borderWidth: 1,
    borderColor: colors.border,
  },
  clearSearchText: { 
    color: colors.textMuted, 
    fontSize: 13, 
    fontWeight: '500',
  },
});
