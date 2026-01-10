import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator, Animated, Dimensions, Easing } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Polyline, Text as SvgText, Circle, G, Rect } from 'react-native-svg';
import { useApp } from '../context/AppContext';
import { authenticateAdmin, logAuditEvent, isValidEmail } from '../utils/security';
import { fonts } from '../../App';

const { width, height } = Dimensions.get('window');

// Premium Eden.so + Dieter Rams color palette with subtle depth
const colors = {
  bg: '#08080a',
  bgGradient: '#0c0c0e',
  surface: '#111114',
  surfaceElevated: '#16161a',
  surfaceHover: '#1a1a1f',
  border: 'rgba(255,255,255,0.08)',
  borderSubtle: 'rgba(255,255,255,0.04)',
  borderAccent: 'rgba(255,255,255,0.12)',
  text: '#fafafa',
  textMuted: '#8b8b8b',
  textSubtle: '#5a5a5a',
  accent: '#ffffff',
  accentMuted: '#d0d0d0',
  success: '#3d8c40',
  error: '#c44',
  warning: '#a86c00',
};

// Animated Shield that floats elegantly
function FloatingShield({ delay, scale = 1, x, y }: { delay: number; scale?: number; x: number; y: number }) {
  const translateY = useRef(new Animated.Value(0)).current;
  const rotate = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timeout = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0.08,
        duration: 2500,
        useNativeDriver: true,
        easing: Easing.out(Easing.cubic),
      }).start();

      Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(translateY, {
              toValue: -15,
              duration: 5000,
              useNativeDriver: true,
              easing: Easing.inOut(Easing.sin),
            }),
            Animated.timing(rotate, {
              toValue: 1,
              duration: 8000,
              useNativeDriver: true,
              easing: Easing.inOut(Easing.sin),
            }),
          ]),
          Animated.parallel([
            Animated.timing(translateY, {
              toValue: 15,
              duration: 5000,
              useNativeDriver: true,
              easing: Easing.inOut(Easing.sin),
            }),
            Animated.timing(rotate, {
              toValue: -1,
              duration: 8000,
              useNativeDriver: true,
              easing: Easing.inOut(Easing.sin),
            }),
          ]),
        ])
      ).start();
    }, delay);

    return () => clearTimeout(timeout);
  }, []);

  const rotateInterpolate = rotate.interpolate({
    inputRange: [-1, 1],
    outputRange: ['-5deg', '5deg'],
  });

  const size = 60 * scale;

  return (
    <Animated.View
      style={{
        position: 'absolute',
        left: x,
        top: y,
        opacity,
        transform: [{ translateY }, { rotate: rotateInterpolate }],
      }}
    >
      <Svg width={size} height={size * 1.2} viewBox="0 0 100 120">
        <Defs>
          <SvgGradient id={`shieldGrad${delay}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <Stop offset="0%" stopColor="#ffffff" stopOpacity="0.8" />
            <Stop offset="100%" stopColor="#888888" stopOpacity="0.4" />
          </SvgGradient>
        </Defs>
        <Path 
          fill="none" 
          stroke={`url(#shieldGrad${delay})`}
          strokeWidth="3" 
          d="M50 8 L88 28 L88 65 C88 92 50 110 50 110 C50 110 12 92 12 65 L12 28 Z"
        />
        <Polyline 
          fill="none" 
          stroke={`url(#shieldGrad${delay})`}
          strokeWidth="4" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          points="32,58 44,72 68,46"
        />
      </Svg>
    </Animated.View>
  );
}

// Floating checkmark particle
function FloatingCheck({ delay, x, y }: { delay: number; x: number; y: number }) {
  const translateY = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timeout = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0.06,
        duration: 2000,
        useNativeDriver: true,
      }).start();

      Animated.loop(
        Animated.sequence([
          Animated.timing(translateY, {
            toValue: -25,
            duration: 4500,
            useNativeDriver: true,
            easing: Easing.inOut(Easing.sin),
          }),
          Animated.timing(translateY, {
            toValue: 25,
            duration: 4500,
            useNativeDriver: true,
            easing: Easing.inOut(Easing.sin),
          }),
        ])
      ).start();
    }, delay);

    return () => clearTimeout(timeout);
  }, []);

  return (
    <Animated.View
      style={{
        position: 'absolute',
        left: x,
        top: y,
        opacity,
        transform: [{ translateY }],
      }}
    >
      <Svg width={24} height={24} viewBox="0 0 24 24">
        <Polyline 
          fill="none" 
          stroke="#ffffff" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          points="6,12 10,16 18,8"
        />
      </Svg>
    </Animated.View>
  );
}

// Floating ring particle
function FloatingRing({ delay, x, y, size }: { delay: number; x: number; y: number; size: number }) {
  const scale = useRef(new Animated.Value(0.8)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timeout = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0.05,
        duration: 2000,
        useNativeDriver: true,
      }).start();

      Animated.loop(
        Animated.sequence([
          Animated.timing(scale, {
            toValue: 1.1,
            duration: 4000,
            useNativeDriver: true,
            easing: Easing.inOut(Easing.sin),
          }),
          Animated.timing(scale, {
            toValue: 0.9,
            duration: 4000,
            useNativeDriver: true,
            easing: Easing.inOut(Easing.sin),
          }),
        ])
      ).start();
    }, delay);

    return () => clearTimeout(timeout);
  }, []);

  return (
    <Animated.View
      style={{
        position: 'absolute',
        left: x,
        top: y,
        opacity,
        transform: [{ scale }],
      }}
    >
      <Svg width={size} height={size} viewBox="0 0 100 100">
        <Circle cx="50" cy="50" r="45" fill="none" stroke="#ffffff" strokeWidth="1" />
      </Svg>
    </Animated.View>
  );
}

// Elegant scanline animation
function ScanLine() {
  const translateY = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animate = () => {
      translateY.setValue(0);
      Animated.sequence([
        Animated.timing(opacity, { toValue: 0.15, duration: 200, useNativeDriver: true }),
        Animated.timing(translateY, { toValue: height, duration: 3000, useNativeDriver: true, easing: Easing.linear }),
        Animated.timing(opacity, { toValue: 0, duration: 200, useNativeDriver: true }),
      ]).start(() => setTimeout(animate, 5000));
    };
    
    setTimeout(animate, 2000);
  }, []);

  return (
    <Animated.View
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        height: 2,
        opacity,
        transform: [{ translateY }],
        backgroundColor: 'rgba(255,255,255,0.1)',
        shadowColor: '#fff',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
      }}
    />
  );
}

export default function AuthScreen({ navigation }: any) {
  const { login, register, isLoading: contextLoading } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [loginSuccess, setLoginSuccess] = useState(false);

  // Animations
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(40)).current;
  const logoScale = useRef(new Animated.Value(0.9)).current;
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const cardScale = useRef(new Animated.Value(0.95)).current;
  const successScale = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.parallel([
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
          easing: Easing.out(Easing.cubic),
        }),
        Animated.spring(logoScale, {
          toValue: 1,
          tension: 50,
          friction: 8,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
          easing: Easing.out(Easing.cubic),
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
          easing: Easing.out(Easing.cubic),
        }),
        Animated.spring(cardScale, {
          toValue: 1,
          tension: 60,
          friction: 10,
          useNativeDriver: true,
        }),
      ]),
    ]).start();
  }, []);

  const handleSubmit = async () => {
    setError('');
    
    // Input validation
    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (!password) {
      setError('Password is required');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      // Use secure admin authentication
      const result = await authenticateAdmin(email, password);
      
      if (result.success) {
        await logAuditEvent('LOGIN_SUCCESS', `Admin login: ${email}`);
        
        // Show success animation
        setLoginSuccess(true);
        Animated.spring(successScale, {
          toValue: 1,
          tension: 60,
          friction: 8,
          useNativeDriver: true,
        }).start();

        // Complete login through context
        await login(email, password);
        
        setTimeout(() => {
          navigation.goBack();
        }, 1200);
      } else {
        await logAuditEvent('LOGIN_FAILED', `Failed attempt: ${email}`);
        setError(result.error || 'Authentication failed');
        
        // Shake animation on error
        Animated.sequence([
          Animated.timing(cardScale, { toValue: 1.02, duration: 100, useNativeDriver: true }),
          Animated.timing(cardScale, { toValue: 0.98, duration: 100, useNativeDriver: true }),
          Animated.timing(cardScale, { toValue: 1, duration: 100, useNativeDriver: true }),
        ]).start();
      }
    } catch (err: any) {
      await logAuditEvent('LOGIN_ERROR', err.message);
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const getInputBorderColor = (field: string) => {
    if (focusedField === field) return colors.borderAccent;
    if (error && ((field === 'email' && !email) || (field === 'password' && !password))) {
      return 'rgba(196, 68, 68, 0.4)';
    }
    return colors.border;
  };

  if (loginSuccess) {
    return (
      <View style={styles.container}>
        <Animated.View style={[styles.successContainer, { transform: [{ scale: successScale }] }]}>
          <Svg width={80} height={80} viewBox="0 0 100 100">
            <Circle cx="50" cy="50" r="45" fill="none" stroke={colors.success} strokeWidth="2" />
            <Polyline 
              fill="none" 
              stroke={colors.success} 
              strokeWidth="4" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              points="30,52 44,66 70,38"
            />
          </Svg>
          <Text style={styles.successTitle}>Welcome Back</Text>
          <Text style={styles.successSubtitle}>Authentication successful</Text>
        </Animated.View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Floating product elements */}
      <FloatingShield delay={0} scale={1.2} x={-20} y={height * 0.08} />
      <FloatingShield delay={800} scale={0.8} x={width * 0.75} y={height * 0.15} />
      <FloatingShield delay={1600} scale={0.6} x={width * 0.15} y={height * 0.72} />
      <FloatingCheck delay={400} x={width * 0.85} y={height * 0.45} />
      <FloatingCheck delay={1200} x={20} y={height * 0.55} />
      <FloatingRing delay={600} x={width * 0.6} y={height * 0.7} size={60} />
      <FloatingRing delay={1000} x={width * 0.1} y={height * 0.25} size={40} />
      
      {/* Scan line effect */}
      <ScanLine />
      
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.content}
      >
        {/* Logo */}
        <Animated.View style={[styles.logoSection, { opacity: logoOpacity, transform: [{ scale: logoScale }] }]}>
          <Svg width={180} height={55} viewBox="0 0 360 90">
            <Defs>
              <SvgGradient id="authLogoGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <Stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
                <Stop offset="50%" stopColor="#e0e0e0" stopOpacity="1" />
                <Stop offset="100%" stopColor="#888888" stopOpacity="1" />
              </SvgGradient>
            </Defs>
            <SvgText
              x="180"
              y="62"
              textAnchor="middle"
              fill="url(#authLogoGrad)"
              fontSize="56"
              fontWeight="300"
              fontFamily="System"
              letterSpacing="6"
            >verity</SvgText>
          </Svg>
          
          {/* Animated shield mark */}
          <Svg width={28} height={34} viewBox="0 0 100 120" style={{ marginTop: 16, opacity: 0.5 }}>
            <Defs>
              <SvgGradient id="shieldMarkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <Stop offset="0%" stopColor="#ffffff" stopOpacity="0.8" />
                <Stop offset="100%" stopColor="#666666" stopOpacity="0.6" />
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

          <Text style={styles.tagline}>Secure verification companion</Text>
        </Animated.View>

        {/* Form Card */}
        <Animated.View 
          style={[
            styles.formCard,
            { 
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }, { scale: cardScale }]
            }
          ]}
        >
          {/* Admin Only Notice */}
          <View style={styles.adminNotice}>
            <Ionicons name="shield-checkmark-outline" size={16} color={colors.textMuted} />
            <Text style={styles.adminNoticeText}>Admin access only</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email</Text>
              <View style={[styles.inputWrapper, { borderColor: getInputBorderColor('email') }]}>
                <Ionicons name="mail-outline" size={18} color={focusedField === 'email' ? colors.textMuted : colors.textSubtle} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="admin@veritysystems.app"
                  placeholderTextColor={colors.textSubtle}
                  value={email}
                  onChangeText={(text) => { setEmail(text); setError(''); }}
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  editable={!isLoading}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Password</Text>
              <View style={[styles.inputWrapper, { borderColor: getInputBorderColor('password') }]}>
                <Ionicons name="lock-closed-outline" size={18} color={focusedField === 'password' ? colors.textMuted : colors.textSubtle} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="••••••••••••"
                  placeholderTextColor={colors.textSubtle}
                  value={password}
                  onChangeText={(text) => { setPassword(text); setError(''); }}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                  secureTextEntry={!showPassword}
                  editable={!isLoading}
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)} disabled={isLoading}>
                  <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color={colors.textSubtle} />
                </TouchableOpacity>
              </View>
            </View>

            {error ? (
              <Animated.View style={styles.errorBox}>
                <Ionicons name="alert-circle" size={16} color={colors.error} />
                <Text style={styles.errorText}>{error}</Text>
              </Animated.View>
            ) : null}

            <TouchableOpacity 
              style={[styles.submitBtn, isLoading && styles.submitBtnDisabled]}
              onPress={handleSubmit}
              disabled={isLoading}
              activeOpacity={0.85}
            >
              {isLoading ? (
                <ActivityIndicator color={colors.bg} />
              ) : (
                <>
                  <Ionicons name="shield-checkmark" size={18} color={colors.bg} />
                  <Text style={styles.submitText}>Authenticate</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Security Features */}
        <Animated.View style={[styles.features, { opacity: fadeAnim }]}>
          <View style={styles.featureItem}>
            <Ionicons name="finger-print-outline" size={18} color={colors.textSubtle} />
            <Text style={styles.featureText}>Biometric</Text>
          </View>
          <View style={styles.featureDot} />
          <View style={styles.featureItem}>
            <Ionicons name="lock-closed-outline" size={18} color={colors.textSubtle} />
            <Text style={styles.featureText}>Encrypted</Text>
          </View>
          <View style={styles.featureDot} />
          <View style={styles.featureItem}>
            <Ionicons name="shield-outline" size={18} color={colors.textSubtle} />
            <Text style={styles.featureText}>Secure</Text>
          </View>
        </Animated.View>

        {/* Version footer */}
        <Text style={styles.version}>Verity Companion v1.0.0</Text>
      </KeyboardAvoidingView>
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
    padding: 24, 
    justifyContent: 'center',
  },

  // Success state
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.bg,
  },
  successTitle: {
    color: colors.text,
    fontSize: 24,
    fontFamily: 'Newsreader_400Regular',
    letterSpacing: 1,
    marginTop: 24,
  },
  successSubtitle: {
    color: colors.textMuted,
    fontSize: 14,
    marginTop: 8,
    letterSpacing: 0.5,
  },

  // Logo
  logoSection: { 
    alignItems: 'center', 
    marginBottom: 48,
  },
  tagline: {
    color: colors.textSubtle,
    fontSize: 12,
    fontFamily: 'Inter_500Medium',
    letterSpacing: 2,
    textTransform: 'uppercase',
    marginTop: 20,
  },

  // Form card
  formCard: {
    backgroundColor: colors.surface,
    borderRadius: 24,
    padding: 28,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 24,
    elevation: 8,
  },

  adminNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: colors.bgGradient,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  adminNoticeText: {
    color: colors.textMuted,
    fontSize: 12,
    fontWeight: '500',
    letterSpacing: 0.5,
  },

  form: { 
    gap: 20,
  },
  inputGroup: { 
    gap: 10,
  },
  label: { 
    color: colors.textMuted, 
    fontSize: 12, 
    fontFamily: 'Inter_600SemiBold',
    letterSpacing: 0.5,
    marginLeft: 4,
    textTransform: 'uppercase',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bgGradient,
    borderRadius: 14,
    borderWidth: 1.5,
    paddingHorizontal: 16,
  },
  inputIcon: { 
    marginRight: 12,
  },
  input: {
    flex: 1,
    color: colors.text,
    fontSize: 15,
    fontFamily: 'Inter_400Regular',
    paddingVertical: 16,
    letterSpacing: 0.2,
  },

  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: 'rgba(196, 68, 68, 0.1)',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: 'rgba(196, 68, 68, 0.25)',
  },
  errorText: { 
    color: '#e57373', 
    fontSize: 13, 
    flex: 1,
    letterSpacing: 0.2,
    fontWeight: '500',
  },

  submitBtn: {
    marginTop: 8,
    borderRadius: 14,
    backgroundColor: colors.text,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 16,
    shadowColor: '#fff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
  },
  submitBtnDisabled: { 
    opacity: 0.6,
  },
  submitText: { 
    color: colors.bg, 
    fontSize: 15, 
    fontFamily: 'Inter_600SemiBold',
    letterSpacing: 0.4,
  },

  features: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20,
    marginTop: 36,
  },
  featureItem: { 
    alignItems: 'center', 
    gap: 8,
  },
  featureText: { 
    color: colors.textSubtle, 
    fontSize: 11,
    letterSpacing: 0.4,
    fontWeight: '500',
  },
  featureDot: {
    width: 3,
    height: 3,
    borderRadius: 1.5,
    backgroundColor: colors.textSubtle,
    opacity: 0.5,
  },

  version: {
    color: colors.textSubtle,
    fontSize: 10,
    textAlign: 'center',
    marginTop: 32,
    letterSpacing: 1,
    opacity: 0.6,
  },
});
