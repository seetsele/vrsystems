import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Animated,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  Easing,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

const { width, height } = Dimensions.get('window');

const API_URL = 'https://veritysystems-production.up.railway.app';

// Premium Amber/Gold color palette
const colors = {
  bg: '#0a0a0b',
  surface: '#111113',
  surfaceElevated: '#18181b',
  border: 'rgba(255,255,255,0.08)',
  text: '#fafafa',
  textMuted: '#a3a3a3',
  textSubtle: '#525252',
  accent: '#f59e0b',
  cyan: '#22d3ee',
  violet: '#6366f1',
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
};

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  verification?: {
    verdict: string;
    confidence: number;
  };
}

interface ChatbotProps {
  visible: boolean;
  onClose: () => void;
}

export default function Chatbot({ visible, onClose }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasGreeted, setHasGreeted] = useState(false);
  
  const slideAnim = useRef(new Animated.Value(height)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scrollViewRef = useRef<ScrollView>(null);

  // Animation for opening/closing
  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          useNativeDriver: true,
          tension: 65,
          friction: 11,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();

      // Add welcome message on first open
      if (!hasGreeted) {
        setTimeout(() => {
          addBotMessage("Hi! I'm Verity AI, your mobile verification assistant. I can help you verify claims or answer questions about the app. What would you like to know?");
          setHasGreeted(true);
        }, 500);
      }
    } else {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: height,
          duration: 250,
          useNativeDriver: true,
          easing: Easing.in(Easing.cubic),
        }),
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [visible]);

  const addBotMessage = (text: string, verification?: Message['verification']) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: false,
      verification,
    };
    setMessages(prev => [...prev, newMessage]);
    setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
  };

  const addUserMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
    };
    setMessages(prev => [...prev, newMessage]);
    setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
  };

  const getVerdictColor = (verdict: string) => {
    const v = verdict.toLowerCase();
    if (v === 'true') return colors.success;
    if (v === 'false') return colors.error;
    return colors.warning;
  };

  const getVerdictIcon = (verdict: string) => {
    const v = verdict.toLowerCase();
    if (v === 'true') return 'checkmark-circle';
    if (v === 'false') return 'close-circle';
    return 'alert-circle';
  };

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isTyping) return;

    addUserMessage(text);
    setInputText('');
    setIsTyping(true);

    try {
      // Check if this looks like a verification request
      const isVerification = 
        text.toLowerCase().includes('verify') ||
        text.toLowerCase().includes('is it true') ||
        text.toLowerCase().includes('fact check') ||
        (text.endsWith('?') && text.length > 20) ||
        text.length > 30;

      if (isVerification) {
        // Extract claim to verify
        let claim = text
          .replace(/^(verify|fact check|is it true that|check if)\s*/i, '')
          .replace(/\?$/, '');

        if (claim.length < 10) claim = text;

        // Call verification API
        const response = await fetch(`${API_URL}/v3/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ claim }),
        });

        const result = await response.json();
        
        addBotMessage(
          result.explanation || 'I verified this claim for you.',
          { verdict: result.verdict, confidence: result.confidence }
        );
      } else {
        // Handle general questions
        const response = getGeneralResponse(text);
        addBotMessage(response);
      }
    } catch (error) {
      addBotMessage('Sorry, I encountered an error. Please check your connection and try again.');
    }

    setIsTyping(false);
  };

  const getGeneralResponse = (text: string): string => {
    const lower = text.toLowerCase();

    if (lower.includes('feature') || lower.includes('what can')) {
      return "This companion app lets you:\n\n📸 Capture & queue claims for verification\n📊 View your verification history\n🔔 Get real-time notifications\n⚡ Quick-verify with the camera\n\nUse the tabs below to explore!";
    }

    if (lower.includes('how') && (lower.includes('work') || lower.includes('does'))) {
      return "Verity uses 20+ AI models for multi-source consensus verification:\n\n1️⃣ Capture or type a claim\n2️⃣ Multiple AI providers analyze it\n3️⃣ Our consensus engine synthesizes results\n4️⃣ You get a verdict + confidence score";
    }

    if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
      return "Hello! 👋 I'm here to help you verify claims and navigate the app. What would you like to do?";
    }

    if (lower.includes('thank')) {
      return "You're welcome! 😊 Anything else I can help with?";
    }

    return "I can help you with:\n\n🔍 Verifying claims - just type a statement\n📱 App features - ask about capabilities\n❓ Getting started - I'll guide you\n\nWhat would you like to know?";
  };

  const handleQuickAction = (action: string) => {
    setInputText(action);
    setTimeout(() => handleSend(), 100);
  };

  if (!visible) return null;

  return (
    <Animated.View style={[styles.overlay, { opacity: fadeAnim }]}>
      <TouchableOpacity style={styles.backdrop} onPress={onClose} activeOpacity={1} />
      
      <Animated.View style={[styles.container, { transform: [{ translateY: slideAnim }] }]}>
        {/* Header */}
        <LinearGradient
          colors={['rgba(34,211,238,0.15)', 'rgba(99,102,241,0.05)']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.header}
        >
          <View style={styles.headerLeft}>
            <LinearGradient
              colors={[colors.cyan, colors.violet]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.avatar}
            >
              <Ionicons name="shield-checkmark" size={20} color="white" />
            </LinearGradient>
            <View>
              <Text style={styles.title}>Verity AI</Text>
              <View style={styles.statusRow}>
                <View style={styles.statusDot} />
                <Text style={styles.statusText}>Online</Text>
              </View>
            </View>
          </View>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={20} color={colors.textMuted} />
          </TouchableOpacity>
        </LinearGradient>

        {/* Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.map((message) => (
            <View
              key={message.id}
              style={[
                styles.messageRow,
                message.isUser && styles.messageRowUser,
              ]}
            >
              {!message.isUser && (
                <LinearGradient
                  colors={[colors.cyan, colors.violet]}
                  style={styles.messageAvatar}
                >
                  <Ionicons name="shield-checkmark" size={12} color="white" />
                </LinearGradient>
              )}
              
              <View style={[
                styles.messageBubble,
                message.isUser ? styles.messageBubbleUser : styles.messageBubbleBot,
              ]}>
                <Text style={styles.messageText}>{message.text}</Text>
                
                {message.verification && (
                  <View style={[
                    styles.verificationBox,
                    { borderLeftColor: getVerdictColor(message.verification.verdict) },
                  ]}>
                    <View style={styles.verdictRow}>
                      <Ionicons
                        name={getVerdictIcon(message.verification.verdict)}
                        size={16}
                        color={getVerdictColor(message.verification.verdict)}
                      />
                      <Text style={[
                        styles.verdictText,
                        { color: getVerdictColor(message.verification.verdict) },
                      ]}>
                        {message.verification.verdict.toUpperCase()}
                      </Text>
                    </View>
                    <Text style={styles.confidenceText}>
                      Confidence: {Math.round(message.verification.confidence * 100)}%
                    </Text>
                  </View>
                )}
              </View>
              
              {message.isUser && (
                <View style={styles.messageAvatarUser}>
                  <Ionicons name="person" size={12} color="white" />
                </View>
              )}
            </View>
          ))}

          {isTyping && (
            <View style={styles.messageRow}>
              <LinearGradient
                colors={[colors.cyan, colors.violet]}
                style={styles.messageAvatar}
              >
                <Ionicons name="shield-checkmark" size={12} color="white" />
              </LinearGradient>
              <View style={[styles.messageBubble, styles.messageBubbleBot]}>
                <TypingIndicator />
              </View>
            </View>
          )}
        </ScrollView>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => handleQuickAction('Verify a claim')}
          >
            <Text style={styles.quickActionText}>🔍 Verify</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => handleQuickAction('How does Verity work?')}
          >
            <Text style={styles.quickActionText}>❓ How it works</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => handleQuickAction('What features are available?')}
          >
            <Text style={styles.quickActionText}>✨ Features</Text>
          </TouchableOpacity>
        </View>

        {/* Input */}
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.inputContainer}
        >
          <TextInput
            style={styles.input}
            placeholder="Ask me anything..."
            placeholderTextColor={colors.textSubtle}
            value={inputText}
            onChangeText={setInputText}
            onSubmitEditing={handleSend}
            returnKeyType="send"
            multiline={false}
          />
          <TouchableOpacity
            style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]}
            onPress={handleSend}
            disabled={!inputText.trim() || isTyping}
          >
            <LinearGradient
              colors={[colors.cyan, colors.violet]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.sendButtonGradient}
            >
              <Ionicons name="send" size={16} color="white" />
            </LinearGradient>
          </TouchableOpacity>
        </KeyboardAvoidingView>
      </Animated.View>
    </Animated.View>
  );
}

// Typing indicator component
function TypingIndicator() {
  const dot1 = useRef(new Animated.Value(0)).current;
  const dot2 = useRef(new Animated.Value(0)).current;
  const dot3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animate = (dot: Animated.Value, delay: number) => {
      Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(dot, { toValue: -5, duration: 300, useNativeDriver: true }),
          Animated.timing(dot, { toValue: 0, duration: 300, useNativeDriver: true }),
        ])
      ).start();
    };

    animate(dot1, 0);
    animate(dot2, 150);
    animate(dot3, 300);
  }, []);

  return (
    <View style={styles.typingContainer}>
      <Animated.View style={[styles.typingDot, { transform: [{ translateY: dot1 }] }]} />
      <Animated.View style={[styles.typingDot, { transform: [{ translateY: dot2 }] }]} />
      <Animated.View style={[styles.typingDot, { transform: [{ translateY: dot3 }] }]} />
    </View>
  );
}

// Floating Action Button for opening chatbot
interface ChatbotFABProps {
  onPress: () => void;
  hasNotification?: boolean;
}

export function ChatbotFAB({ onPress, hasNotification = true }: ChatbotFABProps) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.9,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      tension: 300,
      friction: 10,
    }).start();
  };

  return (
    <Animated.View style={[styles.fabContainer, { transform: [{ scale: scaleAnim }] }]}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
      >
        <LinearGradient
          colors={[colors.cyan, colors.violet]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.fab}
        >
          <Ionicons name="chatbubble-ellipses" size={24} color="white" />
        </LinearGradient>
        {hasNotification && <View style={styles.fabNotification} />}
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 1000,
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: height * 0.75,
    backgroundColor: colors.bg,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.success,
  },
  statusText: {
    fontSize: 12,
    color: colors.success,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    gap: 12,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    marginBottom: 8,
  },
  messageRowUser: {
    justifyContent: 'flex-end',
  },
  messageAvatar: {
    width: 24,
    height: 24,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  messageAvatarUser: {
    width: 24,
    height: 24,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  messageBubble: {
    maxWidth: '75%',
    padding: 12,
    borderRadius: 16,
  },
  messageBubbleBot: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderBottomLeftRadius: 4,
  },
  messageBubbleUser: {
    backgroundColor: colors.cyan,
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.text,
  },
  verificationBox: {
    marginTop: 10,
    padding: 10,
    backgroundColor: 'rgba(0,0,0,0.3)',
    borderRadius: 10,
    borderLeftWidth: 3,
  },
  verdictRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 4,
  },
  verdictText: {
    fontSize: 13,
    fontWeight: '600',
  },
  confidenceText: {
    fontSize: 11,
    color: colors.textSubtle,
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  quickActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
  },
  quickActionText: {
    fontSize: 12,
    color: colors.textMuted,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  input: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 14,
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sendButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonGradient: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  typingContainer: {
    flexDirection: 'row',
    gap: 4,
    paddingVertical: 4,
  },
  typingDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.4)',
  },
  fabContainer: {
    position: 'absolute',
    bottom: 90,
    right: 20,
    zIndex: 100,
  },
  fab: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.cyan,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  fabNotification: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.success,
    borderWidth: 2,
    borderColor: colors.bg,
  },
});
