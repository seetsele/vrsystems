/**
 * Verity Systems - Design Theme
 * Matches the production website: https://vrsystemss.vercel.app/
 */

export const colors = {
  // Core backgrounds
  bg: '#0a0a0b',
  bgCard: '#111113',
  bgElevated: '#18181b',
  
  // Borders
  border: 'rgba(255,255,255,0.06)',
  borderHover: 'rgba(255,255,255,0.12)',
  
  // Text
  textPrimary: '#fafafa',
  textSecondary: '#a3a3a3',
  textMuted: '#525252',
  
  // Primary - Amber
  amber: '#f59e0b',
  amberSoft: 'rgba(245, 158, 11, 0.12)',
  amberBorder: 'rgba(245, 158, 11, 0.2)',
  amberHover: '#d97706',
  amberLight: '#fbbf24',
  
  // Success - Green
  green: '#10b981',
  greenSoft: 'rgba(16, 185, 129, 0.12)',
  greenBorder: 'rgba(16, 185, 129, 0.2)',
  
  // Accent colors
  cyan: '#22d3ee',
  violet: '#8b5cf6',
  red: '#ef4444',
  
  // Semantic
  verified: '#10b981',
  mixed: '#f59e0b', 
  flagged: '#ef4444',
};

export const fonts = {
  sans: 'Inter',
  serif: 'Newsreader',
  mono: 'JetBrains Mono',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const radii = {
  sm: 6,
  md: 10,
  lg: 16,
  xl: 20,
  full: 100,
};

export const shadows = {
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 4,
  },
  elevated: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 24,
    elevation: 8,
  },
};

// Button styles matching test website
export const buttonStyles = {
  primary: {
    background: colors.amber,
    color: '#000',
    hoverBackground: colors.amberHover,
  },
  outline: {
    background: 'transparent',
    color: colors.textPrimary,
    border: colors.borderHover,
    hoverBackground: 'rgba(255,255,255,0.05)',
  },
  ghost: {
    color: colors.textSecondary,
    hoverColor: colors.textPrimary,
  },
};

// Card styles matching test website
export const cardStyles = {
  default: {
    backgroundColor: colors.bgCard,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: radii.lg,
  },
  featured: {
    backgroundColor: colors.bgCard,
    borderColor: colors.amberBorder,
    borderWidth: 1,
    borderRadius: radii.xl,
  },
};

export default {
  colors,
  fonts,
  spacing,
  radii,
  shadows,
  buttonStyles,
  cardStyles,
};
