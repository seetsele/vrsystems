import React, { useState, useEffect, useRef } from 'react';
import { fonts as appFonts } from '../../App';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Switch, Alert, ActivityIndicator, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline, Text as SvgText } from 'react-native-svg';
import { useApp } from '../context/AppContext';
import { useNavigation } from '@react-navigation/native';

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
  destructive: '#666666',
};

// Minimal Verity Logo
function VerityMark({ size = 32 }: { size?: number }) {
  return (
    <Svg width={size} height={size * 1.1} viewBox="0 0 100 120">
      <Defs>
        <SvgGradient id="settingsMarkGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <Stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
          <Stop offset="100%" stopColor="#666666" stopOpacity="1" />
        </SvgGradient>
      </Defs>
      <Path 
        fill="none" 
        stroke="url(#settingsMarkGrad)" 
        strokeWidth="6" 
        d="M50 10 L85 30 L85 70 C85 95 50 105 50 105 C50 105 15 95 15 70 L15 30 Z"
      />
      <Polyline 
        fill="none" 
        stroke="url(#settingsMarkGrad)" 
        strokeWidth="7" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        points="35,60 45,72 65,48"
      />
    </Svg>
  );
}

// Setting row component
function SettingRow({ icon, label, description, onPress, rightElement, delay = 0, destructive = false }: any) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateX = useRef(new Animated.Value(-16)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(translateX, { toValue: 0, duration: 400, useNativeDriver: true }),
      ]).start();
    }, delay);
  }, []);

  const handlePressIn = () => {
    if (onPress) {
      Animated.spring(scale, { toValue: 0.98, useNativeDriver: true, tension: 300, friction: 20 }).start();
    }
  };

  const handlePressOut = () => {
    Animated.spring(scale, { toValue: 1, useNativeDriver: true, tension: 300, friction: 20 }).start();
  };

  const content = (
    <View style={styles.settingRow}>
      <View style={styles.settingLeft}>
        <View style={[styles.settingIcon, destructive && { backgroundColor: 'rgba(255,255,255,0.03)' }]}>
          <Ionicons name={icon} size={18} color={destructive ? colors.destructive : colors.textMuted} />
        </View>
        <View style={styles.settingTextWrap}>
          <Text style={[styles.settingLabel, destructive && { color: colors.destructive }]}>{label}</Text>
          {description && <Text style={styles.settingDesc}>{description}</Text>}
        </View>
      </View>
      {rightElement || (onPress && (
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
      ))}
    </View>
  );

  return (
    <Animated.View style={{ opacity, transform: [{ translateX }, { scale }] }}>
      {onPress ? (
        <TouchableOpacity 
          onPress={onPress} 
          onPressIn={handlePressIn}
          onPressOut={handlePressOut}
          activeOpacity={1}
        >
          {content}
        </TouchableOpacity>
      ) : content}
    </Animated.View>
  );
}

// Section component
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionContent}>
        {children}
      </View>
    </View>
  );
}

// Minimal toggle switch
function MinimalSwitch({ value, onValueChange }: { value: boolean; onValueChange: (v: boolean) => void }) {
  return (
    <Switch 
      value={value} 
      onValueChange={onValueChange} 
      trackColor={{ false: colors.border, true: colors.textMuted }} 
      thumbColor={colors.text}
      ios_backgroundColor={colors.border}
    />
  );
}

export default function SettingsScreen() {
  const navigation = useNavigation<any>();
  const { 
    user, 
    clearHistory, 
    desktopConnected, 
    logout, 
    syncData, 
    toggleSync, 
    isSyncing, 
    syncStatus 
  } = useApp();
  const [notifications, setNotifications] = useState(true);
  const [deepAnalysisDefault, setDeepAnalysisDefault] = useState(true);
  const [saveHistory, setSaveHistory] = useState(true);

  const headerOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(headerOpacity, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, []);

  const handleClearData = () => {
    Alert.alert('Clear All Data', 'This will delete all history and settings.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Clear', style: 'destructive', onPress: clearHistory },
    ]);
  };

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: logout },
    ]);
  };

  const handleSync = async () => {
    await syncData();
  };

  const getTimeAgo = (timestamp: string | undefined) => {
    if (!timestamp) return 'Never';
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Account Card */}
        <Animated.View style={{ opacity: headerOpacity }}>
          {user ? (
            <TouchableOpacity activeOpacity={0.9} style={styles.profileCard}>
              <View style={styles.profileAvatar}>
                <Text style={styles.profileAvatarText}>
                  {user.name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                </Text>
              </View>
              <View style={styles.profileInfo}>
                <Text style={styles.profileName}>{user.name || user.email.split('@')[0]}</Text>
                <Text style={styles.profileEmail}>{user.email}</Text>
                <View style={styles.planBadge}>
                  <Text style={styles.planText}>{user.plan.toUpperCase()}</Text>
                </View>
              </View>
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
            </TouchableOpacity>
          ) : (
            <TouchableOpacity 
              activeOpacity={0.9}
              onPress={() => navigation.navigate('Auth')}
              style={styles.signInCard}
            >
              <View style={styles.signInMark}>
                <VerityMark size={36} />
              </View>
              <View style={styles.signInInfo}>
                <Text style={styles.signInTitle}>Sign in to sync</Text>
                <Text style={styles.signInDesc}>Sync across all your devices</Text>
              </View>
              <Svg width={16} height={16} viewBox="0 0 24 24">
                <Path 
                  d="M9 6l6 6-6 6" 
                  fill="none" 
                  stroke={colors.textMuted} 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </Svg>
            </TouchableOpacity>
          )}
        </Animated.View>

        {/* Sync Section */}
        <Section title="Sync">
          {user && (
            <>
              <SettingRow
                icon="sync-outline"
                label="Auto Sync"
                description="Keep data synchronized"
                rightElement={<MinimalSwitch value={user.syncEnabled} onValueChange={toggleSync} />}
                delay={50}
              />
              <View style={styles.settingDivider} />
              <SettingRow
                icon="cloud-upload-outline"
                label="Sync Now"
                description={syncStatus === 'syncing' ? 'Syncing...' : `Last: ${getTimeAgo(user.lastSync)}`}
                onPress={handleSync}
                rightElement={isSyncing ? (
                  <ActivityIndicator size="small" color={colors.textMuted} />
                ) : (
                  <View style={[styles.syncDot, { 
                    backgroundColor: syncStatus === 'success' ? '#666666' : 
                                     syncStatus === 'error' ? '#555555' : '#444444' 
                  }]} />
                )}
                delay={100}
              />
              <View style={styles.settingDivider} />
            </>
          )}
          <SettingRow
            icon="desktop-outline"
            label="Desktop Connection"
            description={desktopConnected ? 'Connected' : 'Not connected'}
            rightElement={<View style={[styles.statusDot, { backgroundColor: desktopConnected ? '#666666' : '#333333' }]} />}
            delay={user ? 150 : 50}
          />
        </Section>

        {/* Preferences */}
        <Section title="Preferences">
          <SettingRow
            icon="notifications-outline"
            label="Notifications"
            rightElement={<MinimalSwitch value={notifications} onValueChange={setNotifications} />}
            delay={200}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="flash-outline"
            label="Deep Analysis"
            description="Use by default"
            rightElement={<MinimalSwitch value={deepAnalysisDefault} onValueChange={setDeepAnalysisDefault} />}
            delay={250}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="save-outline"
            label="Save History"
            rightElement={<MinimalSwitch value={saveHistory} onValueChange={setSaveHistory} />}
            delay={300}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="language-outline"
            label="Language"
            description="English (US)"
            onPress={() => Alert.alert('Language', 'Choose your preferred language for verifications', [
              { text: 'English (US)', onPress: () => {} },
              { text: 'Spanish', onPress: () => {} },
              { text: 'French', onPress: () => {} },
              { text: 'German', onPress: () => {} },
              { text: 'Cancel', style: 'cancel' },
            ])}
            delay={320}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="globe-outline"
            label="Auto-Translate"
            description="Translate claims to English"
            rightElement={<MinimalSwitch value={true} onValueChange={() => {}} />}
            delay={340}
          />
        </Section>

        {/* Data & Privacy */}
        <Section title="Data">
          <SettingRow
            icon="download-outline"
            label="Export Data"
            description="PDF, CSV, JSON formats"
            onPress={() => Alert.alert('Export', 'Choose export format', [
              { text: 'PDF Report', onPress: () => Alert.alert('Exporting...', 'Your PDF report will be ready shortly') },
              { text: 'CSV Spreadsheet', onPress: () => Alert.alert('Exporting...', 'Your CSV will be ready shortly') },
              { text: 'JSON Data', onPress: () => Alert.alert('Exporting...', 'Your JSON export will be ready shortly') },
              { text: 'Cancel', style: 'cancel' },
            ])}
            delay={350}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="analytics-outline"
            label="View Analytics"
            description="Usage stats and insights"
            onPress={() => Alert.alert('Analytics', `Total verifications: ${user?.stats?.totalVerifications || 0}\nAverage confidence: ${user?.stats?.avgConfidence || 85}%`)}
            delay={380}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="trash-outline"
            label="Clear All Data"
            onPress={handleClearData}
            destructive
            delay={400}
          />
        </Section>

        {/* Account Actions */}
        {user && (
          <Section title="Account">
            <SettingRow
              icon="log-out-outline"
              label="Sign Out"
              onPress={handleLogout}
              destructive
              delay={450}
            />
          </Section>
        )}

        {/* Support */}
        <Section title="Support">
          <SettingRow
            icon="help-circle-outline"
            label="Help Center"
            onPress={() => {}}
            delay={500}
          />
          <View style={styles.settingDivider} />
          <SettingRow
            icon="document-text-outline"
            label="Privacy Policy"
            onPress={() => {}}
            delay={550}
          />
        </Section>

        {/* About */}
        <View style={styles.aboutSection}>
          <VerityMark size={36} />
          <Text style={styles.aboutTitle}>Verity Companion</Text>
          <Text style={styles.aboutVersion}>Version 1.0.0</Text>
          <Text style={styles.aboutCopyright}>© 2026 Verity Systems</Text>
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
  content: { 
    flex: 1, 
    paddingHorizontal: 20,
    paddingTop: 16,
  },

  // Profile card
  profileCard: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: colors.surface,
    borderRadius: 16, 
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 14,
  },
  profileAvatar: { 
    width: 48, 
    height: 48, 
    borderRadius: 14, 
    backgroundColor: colors.surfaceHover,
    justifyContent: 'center', 
    alignItems: 'center',
  },
  profileAvatarText: { 
    color: colors.text, 
    fontSize: 18, 
    fontWeight: '500',
  },
  profileInfo: { 
    flex: 1,
  },
  profileName: { 
    fontSize: 16, 
    fontWeight: '500', 
    color: colors.text,
    letterSpacing: 0.1,
    fontFamily: appFonts.mono,
  },
  profileEmail: { 
    fontSize: 13, 
    color: colors.textSubtle, 
    marginTop: 2,
  },
  planBadge: { 
    backgroundColor: colors.surfaceHover, 
    paddingHorizontal: 8, 
    paddingVertical: 3, 
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginTop: 6,
  },
  planText: { 
    color: colors.textMuted, 
    fontSize: 9, 
    fontWeight: '600', 
    letterSpacing: 0.5,
  },

  // Sign in card
  signInCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 14,
  },
  signInMark: { 
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  signInInfo: { 
    flex: 1,
  },
  signInTitle: { 
    fontSize: 16, 
    fontWeight: '500', 
    color: colors.text,
    letterSpacing: 0.1,
    fontFamily: appFonts.mono,
  },
  signInDesc: { 
    fontSize: 13, 
    color: colors.textSubtle, 
    marginTop: 2,
  },

  // Sections
  section: { 
    marginBottom: 24,
  },
  sectionTitle: { 
    fontSize: 11, 
    fontWeight: '600', 
    color: colors.textSubtle, 
    textTransform: 'uppercase', 
    letterSpacing: 1.5, 
    paddingHorizontal: 4,
    marginBottom: 12,
  },
  sectionContent: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },

  // Setting row
  settingRow: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between',
    padding: 14,
    gap: 12,
  },
  settingLeft: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 12, 
    flex: 1,
  },
  settingIcon: { 
    width: 36, 
    height: 36, 
    borderRadius: 10, 
    backgroundColor: colors.surfaceHover,
    justifyContent: 'center', 
    alignItems: 'center',
  },
  settingTextWrap: { 
    flex: 1,
  },
  settingLabel: { 
    fontSize: 14, 
    fontWeight: '500', 
    color: colors.text,
    letterSpacing: 0.1,
  },
  settingDesc: { 
    fontSize: 12, 
    color: colors.textSubtle, 
    marginTop: 2,
  },
  settingDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 62,
  },
  statusDot: { 
    width: 8, 
    height: 8, 
    borderRadius: 4,
  },
  syncDot: { 
    width: 8, 
    height: 8, 
    borderRadius: 4,
  },

  // About
  aboutSection: { 
    alignItems: 'center', 
    paddingVertical: 32,
    marginTop: 8,
  },
  aboutTitle: { 
    fontSize: 15, 
    fontWeight: '500', 
    color: colors.text, 
    marginTop: 12,
    letterSpacing: 0.1,
  },
  aboutVersion: { 
    fontSize: 12, 
    color: colors.textSubtle, 
    marginTop: 4,
  },
  aboutCopyright: { 
    fontSize: 11, 
    color: colors.textSubtle, 
    marginTop: 2,
  },
});
