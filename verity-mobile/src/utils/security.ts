/**
 * Verity Mobile Security Utilities
 * Enterprise-grade security for sensitive verification data
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// ==========================================
// Security Constants
// ==========================================

// Admin credentials (in production, this would be environment-secured)
const ADMIN_CREDENTIALS = {
  email: 'admin@veritysystems.app',
  passwordHash: hashPassword('VerityAdmin2024!'), // Pre-hashed
};

// Encryption key derivation (simplified for demo - use proper KDF in production)
const ENCRYPTION_KEY_BASE = 'verity_secure_2024';

// Session timeout (30 minutes)
const SESSION_TIMEOUT_MS = 30 * 60 * 1000;

// Max login attempts before lockout
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_DURATION_MS = 15 * 60 * 1000; // 15 minutes

// ==========================================
// Password Hashing
// ==========================================

export function hashPassword(password: string): string {
  // Simple hash for demo - in production use bcrypt/argon2
  let hash = 0;
  const salt = 'verity_salt_2024';
  const salted = password + salt;
  
  for (let i = 0; i < salted.length; i++) {
    const char = salted.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  
  // Convert to hex string
  return Math.abs(hash).toString(16).padStart(8, '0');
}

export function verifyPassword(password: string, storedHash: string): boolean {
  return hashPassword(password) === storedHash;
}

// ==========================================
// Admin Authentication
// ==========================================

export interface AuthResult {
  success: boolean;
  error?: string;
  isAdmin?: boolean;
  sessionToken?: string;
}

export async function authenticateAdmin(email: string, password: string): Promise<AuthResult> {
  // Check for lockout
  const lockoutStatus = await checkLockout();
  if (lockoutStatus.isLocked) {
    const remainingMinutes = Math.ceil(lockoutStatus.remainingMs! / 60000);
    return {
      success: false,
      error: `Too many attempts. Try again in ${remainingMinutes} minute${remainingMinutes > 1 ? 's' : ''}.`,
    };
  }

  // Validate input
  if (!email || !password) {
    return { success: false, error: 'Email and password are required' };
  }

  if (!isValidEmail(email)) {
    return { success: false, error: 'Invalid email format' };
  }

  // Normalize email
  const normalizedEmail = email.toLowerCase().trim();

  // Check admin credentials
  if (normalizedEmail === ADMIN_CREDENTIALS.email.toLowerCase()) {
    const passwordHash = hashPassword(password);
    
    if (passwordHash === ADMIN_CREDENTIALS.passwordHash) {
      // Success - clear failed attempts
      await clearLoginAttempts();
      
      // Generate session token
      const sessionToken = generateSessionToken();
      await storeSession(sessionToken);
      
      return {
        success: true,
        isAdmin: true,
        sessionToken,
      };
    }
  }

  // Failed attempt - increment counter
  await recordFailedAttempt();
  const attempts = await getLoginAttempts();
  const remaining = MAX_LOGIN_ATTEMPTS - attempts;

  if (remaining <= 0) {
    await inititateLockout();
    return {
      success: false,
      error: 'Account locked due to too many failed attempts. Try again in 15 minutes.',
    };
  }

  return {
    success: false,
    error: `Invalid credentials. ${remaining} attempt${remaining > 1 ? 's' : ''} remaining.`,
  };
}

// ==========================================
// Session Management
// ==========================================

export function generateSessionToken(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 15);
  const entropy = Math.random().toString(36).substring(2, 15);
  return `vrt_${timestamp}_${random}${entropy}`;
}

export async function storeSession(token: string): Promise<void> {
  const sessionData = {
    token,
    createdAt: Date.now(),
    expiresAt: Date.now() + SESSION_TIMEOUT_MS,
  };
  await AsyncStorage.setItem('verity_session', JSON.stringify(sessionData));
}

export async function validateSession(): Promise<boolean> {
  try {
    const sessionStr = await AsyncStorage.getItem('verity_session');
    if (!sessionStr) return false;

    const session = JSON.parse(sessionStr);
    
    // Check expiration
    if (Date.now() > session.expiresAt) {
      await clearSession();
      return false;
    }

    // Extend session on activity
    await extendSession();
    return true;
  } catch {
    return false;
  }
}

export async function extendSession(): Promise<void> {
  try {
    const sessionStr = await AsyncStorage.getItem('verity_session');
    if (!sessionStr) return;

    const session = JSON.parse(sessionStr);
    session.expiresAt = Date.now() + SESSION_TIMEOUT_MS;
    await AsyncStorage.setItem('verity_session', JSON.stringify(session));
  } catch {
    // Silent fail
  }
}

export async function clearSession(): Promise<void> {
  await AsyncStorage.removeItem('verity_session');
}

// ==========================================
// Login Attempt Tracking
// ==========================================

interface LockoutStatus {
  isLocked: boolean;
  remainingMs?: number;
}

async function getLoginAttempts(): Promise<number> {
  try {
    const attemptsStr = await AsyncStorage.getItem('verity_login_attempts');
    if (!attemptsStr) return 0;
    return parseInt(attemptsStr, 10);
  } catch {
    return 0;
  }
}

async function recordFailedAttempt(): Promise<void> {
  const current = await getLoginAttempts();
  await AsyncStorage.setItem('verity_login_attempts', (current + 1).toString());
}

async function clearLoginAttempts(): Promise<void> {
  await AsyncStorage.removeItem('verity_login_attempts');
  await AsyncStorage.removeItem('verity_lockout_until');
}

async function inititateLockout(): Promise<void> {
  const lockoutUntil = Date.now() + LOCKOUT_DURATION_MS;
  await AsyncStorage.setItem('verity_lockout_until', lockoutUntil.toString());
}

async function checkLockout(): Promise<LockoutStatus> {
  try {
    const lockoutStr = await AsyncStorage.getItem('verity_lockout_until');
    if (!lockoutStr) return { isLocked: false };

    const lockoutUntil = parseInt(lockoutStr, 10);
    const now = Date.now();

    if (now < lockoutUntil) {
      return {
        isLocked: true,
        remainingMs: lockoutUntil - now,
      };
    }

    // Lockout expired - clear it
    await clearLoginAttempts();
    return { isLocked: false };
  } catch {
    return { isLocked: false };
  }
}

// ==========================================
// Input Validation & Sanitization
// ==========================================

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove potential XSS vectors
    .replace(/javascript:/gi, '')
    .trim()
    .substring(0, 1000); // Limit length
}

export function sanitizeForStorage(data: any): any {
  if (typeof data === 'string') {
    return sanitizeInput(data);
  }
  
  if (Array.isArray(data)) {
    return data.map(sanitizeForStorage);
  }
  
  if (typeof data === 'object' && data !== null) {
    const sanitized: any = {};
    for (const key of Object.keys(data)) {
      sanitized[key] = sanitizeForStorage(data[key]);
    }
    return sanitized;
  }
  
  return data;
}

// ==========================================
// Data Encryption (Simplified)
// ==========================================

export function encryptData(data: string, key?: string): string {
  const encryptionKey = key || ENCRYPTION_KEY_BASE;
  let result = '';
  
  for (let i = 0; i < data.length; i++) {
    const charCode = data.charCodeAt(i) ^ encryptionKey.charCodeAt(i % encryptionKey.length);
    result += String.fromCharCode(charCode);
  }
  
  return btoa(result);
}

export function decryptData(encrypted: string, key?: string): string {
  const encryptionKey = key || ENCRYPTION_KEY_BASE;
  
  try {
    const decoded = atob(encrypted);
    let result = '';
    
    for (let i = 0; i < decoded.length; i++) {
      const charCode = decoded.charCodeAt(i) ^ encryptionKey.charCodeAt(i % encryptionKey.length);
      result += String.fromCharCode(charCode);
    }
    
    return result;
  } catch {
    return '';
  }
}

// ==========================================
// Secure Storage Helpers
// ==========================================

export async function secureStore(key: string, data: any): Promise<void> {
  const sanitized = sanitizeForStorage(data);
  const jsonString = JSON.stringify(sanitized);
  const encrypted = encryptData(jsonString);
  await AsyncStorage.setItem(`secure_${key}`, encrypted);
}

export async function secureRetrieve<T>(key: string): Promise<T | null> {
  try {
    const encrypted = await AsyncStorage.getItem(`secure_${key}`);
    if (!encrypted) return null;
    
    const decrypted = decryptData(encrypted);
    return JSON.parse(decrypted) as T;
  } catch {
    return null;
  }
}

export async function secureDelete(key: string): Promise<void> {
  await AsyncStorage.removeItem(`secure_${key}`);
}

// ==========================================
// Audit Logging
// ==========================================

interface AuditEntry {
  timestamp: string;
  action: string;
  details?: string;
  ip?: string;
}

export async function logAuditEvent(action: string, details?: string): Promise<void> {
  try {
    const entry: AuditEntry = {
      timestamp: new Date().toISOString(),
      action,
      details,
    };

    const logsStr = await AsyncStorage.getItem('verity_audit_log');
    const logs: AuditEntry[] = logsStr ? JSON.parse(logsStr) : [];
    
    // Keep last 100 entries
    logs.unshift(entry);
    if (logs.length > 100) logs.pop();
    
    await AsyncStorage.setItem('verity_audit_log', JSON.stringify(logs));
  } catch {
    // Silent fail - don't break app for logging
  }
}

export async function getAuditLog(): Promise<AuditEntry[]> {
  try {
    const logsStr = await AsyncStorage.getItem('verity_audit_log');
    return logsStr ? JSON.parse(logsStr) : [];
  } catch {
    return [];
  }
}
