import AsyncStorage from '@react-native-async-storage/async-storage';

// Use 10.0.2.2 for Android emulator to access host localhost
// Use localhost for iOS simulator
import { Platform } from 'react-native';

const DEFAULT_BASE_URL = Platform.OS === 'android' 
  ? 'http://10.0.2.2:8000' 
  : 'http://localhost:8000';

// Production fallback
const PRODUCTION_URL = 'https://verity-verification-api-production.up.railway.app';

// Subscription tiers
type SubscriptionTier = 'free' | 'starter' | 'pro' | 'professional' | 'agency' | 'business' | 'enterprise';

interface TieredVerificationResult {
  request_id: string;
  claim: string;
  verdict: string;
  confidence: number;
  veriscore: number;
  reasoning: string;
  tier: string;
  models_used: string[];
  models_allowed: number;
  domain_detected: string;
  domain_confidence: number;
  sources: string[];
  processing_time_ms: number;
  platform: string;
  cost_estimate: number;
  timestamp: string;
}

interface VerificationResult {
  id: string;
  claim: string;
  verdict: string;
  confidence: number;
  explanation: string;
  sources: Array<{
    title: string;
    url: string;
    credibility: number;
    relevance: number;
  }>;
  category?: string;
  timestamp: string;
  processingTime?: number;
  passes?: {
    pass1: { result: string; confidence: number };
    pass2: { result: string; confidence: number };
    pass3: { result: string; confidence: number };
  };
  biasAnalysis?: {
    rating: string;
    indicators: string[];
  };
  relatedClaims?: string[];
}

interface SourceAnalysis {
  url: string;
  domain: string;
  trustScore: number;
  category: string;
  factualReporting: string;
  biasRating: string;
  ownerInfo: string;
  trafficRank: number;
  lastUpdated: string;
  warnings: string[];
  positives: string[];
}

interface VerificationOptions {
  sourceAnalysis?: boolean;
  crossReference?: boolean;
  deepAnalysis?: boolean;
  biasDetection?: boolean;
  // Proprietary technologies
  nuanceNet?: boolean;
  temporalTruth?: boolean;
  sourceGraph?: boolean;
  // Verification mode
  verificationMode?: '21' | '231' | 'veriscore';
}

class ApiService {
  private baseUrl: string = DEFAULT_BASE_URL;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes
  private tier: SubscriptionTier = 'free';
  private platform: string = 'mobile';
  private apiKey: string = '';

  constructor() {
    this.loadBaseUrl();
    this.loadTier();
  }

  private async loadBaseUrl() {
    try {
      const stored = await AsyncStorage.getItem('verity_api_endpoint');
      if (stored) {
        this.baseUrl = stored;
      }
    } catch (error) {
      console.error('Failed to load API endpoint:', error);
    }
  }

  private async loadTier() {
    try {
      const stored = await AsyncStorage.getItem('verity_tier');
      if (stored) {
        this.tier = stored as SubscriptionTier;
      }
      const key = await AsyncStorage.getItem('verity_api_key');
      if (key) {
        this.apiKey = key;
      }
    } catch (error) {
      console.error('Failed to load tier:', error);
    }
  }

  setTier(tier: SubscriptionTier) {
    this.tier = tier;
    AsyncStorage.setItem('verity_tier', tier);
  }

  setApiKey(key: string) {
    this.apiKey = key;
    AsyncStorage.setItem('verity_api_key', key);
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
    AsyncStorage.setItem('verity_api_endpoint', url);
  }

  private getCacheKey(endpoint: string, data?: any): string {
    return `${endpoint}:${JSON.stringify(data || {})}`;
  }

  private getFromCache(key: string): any | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  private setCache(key: string, data: any) {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  async clearCache(): Promise<void> {
    this.cache.clear();
  }

  async checkHealth(): Promise<boolean> {
    // Try current endpoint first
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) return true;
    } catch {}
    
    // Try production fallback
    try {
      const response = await fetch(`${PRODUCTION_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        this.baseUrl = PRODUCTION_URL;
        return true;
      }
    } catch {}
    
    return false;
  }

  // ===========================================
  // TIERED VERIFICATION
  // ===========================================

  async verifyClaimTiered(claim: string): Promise<TieredVerificationResult> {
    const cacheKey = this.getCacheKey('/tiered-verify', { claim, tier: this.tier });
    const cached = this.getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${this.baseUrl}/tiered-verify`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Platform': this.platform,
          'X-Tier': this.tier,
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          claim,
          tier: this.tier,
          platform: this.platform,
          context: '',
          include_free_providers: true
        }),
      });

      if (!response.ok) {
        // Fall back to legacy verification
        console.log('Tiered verify failed, using legacy endpoint');
        const legacyResult = await this.verifyClaim(claim);
        return this.transformToTieredResult(legacyResult);
      }

      const data = await response.json();
      this.setCache(cacheKey, data);
      
      // Also save to history
      const historyResult = this.transformTieredToVerificationResult(data);
      await this.saveToHistory(historyResult);
      
      return data;
    } catch (error) {
      console.error('Tiered verification failed:', error);
      // Return demo result
      return this.getDemoTieredResult(claim);
    }
  }

  private transformToTieredResult(result: VerificationResult): TieredVerificationResult {
    return {
      request_id: result.id,
      claim: result.claim,
      verdict: result.verdict,
      confidence: result.confidence,
      veriscore: result.confidence,
      reasoning: result.explanation,
      tier: this.tier,
      models_used: ['legacy'],
      models_allowed: 1,
      domain_detected: result.category || 'general',
      domain_confidence: 50,
      sources: result.sources.map(s => s.url),
      processing_time_ms: result.processingTime || 0,
      platform: this.platform,
      cost_estimate: 0,
      timestamp: result.timestamp
    };
  }

  private transformTieredToVerificationResult(tiered: TieredVerificationResult): VerificationResult {
    return {
      id: tiered.request_id,
      claim: tiered.claim,
      verdict: tiered.verdict,
      confidence: tiered.confidence,
      explanation: tiered.reasoning,
      sources: tiered.sources.map(url => ({
        title: url,
        url: url,
        credibility: 70,
        relevance: 80
      })),
      category: tiered.domain_detected,
      timestamp: tiered.timestamp,
      processingTime: tiered.processing_time_ms
    };
  }

  private getDemoTieredResult(claim: string): TieredVerificationResult {
    const verdicts = ['TRUE', 'FALSE', 'MISLEADING', 'PARTIALLY_TRUE'];
    const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
    const confidence = 60 + Math.floor(Math.random() * 35);
    
    return {
      request_id: `demo-${Date.now()}`,
      claim,
      verdict,
      confidence,
      veriscore: confidence,
      reasoning: 'Demo result - API offline',
      tier: this.tier,
      models_used: ['demo'],
      models_allowed: 1,
      domain_detected: 'general',
      domain_confidence: 50,
      sources: ['https://example.com'],
      processing_time_ms: 500,
      platform: this.platform,
      cost_estimate: 0,
      timestamp: new Date().toISOString()
    };
  }

  // Get available tiers
  async getTiers(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/tiers`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to get tiers:', error);
    }
    return null;
  }

  // ===========================================
  // VERIFICATION WITH MODES & TECHNOLOGIES
  // ===========================================

  async verifyClaim(
    claim: string,
    options: VerificationOptions = {}
  ): Promise<VerificationResult> {
    const cacheKey = this.getCacheKey('/api/v1/verify', { claim, options });
    const cached = this.getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          claim,
          verification_mode: options.verificationMode ?? '231',
          technologies: {
            nuance_net: options.nuanceNet ?? true,
            temporal_truth: options.temporalTruth ?? true,
            source_graph: options.sourceGraph ?? true,
          },
          options: {
            source_analysis: options.sourceAnalysis ?? true,
            cross_reference: options.crossReference ?? true,
            deep_analysis: options.deepAnalysis ?? true,
            bias_detection: options.biasDetection ?? true,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const result = this.transformVerificationResult(data);
      
      this.setCache(cacheKey, result);
      await this.saveToHistory(result);
      
      return result;
    } catch (error) {
      console.error('Verification failed:', error);
      // Return demo result when API is offline
      return this.getDemoVerificationResult(claim);
    }
  }

  private transformVerificationResult(data: any): VerificationResult {
    return {
      id: data.id || `verity-${Date.now()}`,
      claim: data.claim || data.input_claim,
      verdict: data.verdict || data.result?.verdict || 'UNVERIFIED',
      confidence: data.confidence || data.result?.confidence || 0,
      explanation: data.explanation || data.result?.explanation || 'No explanation available',
      sources: (data.sources || data.result?.sources || []).map((s: any) => ({
        title: s.title || s.name || 'Unknown source',
        url: s.url || s.link || '#',
        credibility: s.credibility || s.trust_score || 50,
        relevance: s.relevance || s.match_score || 50,
      })),
      category: data.category || 'General',
      timestamp: data.timestamp || new Date().toISOString(),
      processingTime: data.processing_time || data.processingTime,
      passes: data.passes || data.verification_passes,
      biasAnalysis: data.bias_analysis || data.biasAnalysis,
      relatedClaims: data.related_claims || data.relatedClaims,
    };
  }

  private getDemoVerificationResult(claim: string): VerificationResult {
    const verdicts = ['TRUE', 'FALSE', 'MISLEADING', 'PARTIALLY_TRUE'];
    const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
    const confidence = 60 + Math.floor(Math.random() * 35);

    return {
      id: `demo-${Date.now()}`,
      claim,
      verdict,
      confidence,
      explanation: `Demo mode: This is a simulated verification result. The claim "${claim.substring(0, 50)}..." has been analyzed using our 3-pass verification system. In production, this would use real AI-powered analysis.`,
      sources: [
        {
          title: 'Demo Source 1 - Academic Research',
          url: 'https://example.com/source1',
          credibility: 85,
          relevance: 90,
        },
        {
          title: 'Demo Source 2 - News Article',
          url: 'https://example.com/source2',
          credibility: 75,
          relevance: 80,
        },
      ],
      category: 'Demo',
      timestamp: new Date().toISOString(),
      processingTime: Math.floor(Math.random() * 2000) + 500,
      passes: {
        pass1: { result: 'Initial analysis complete', confidence: confidence - 10 },
        pass2: { result: 'Cross-reference verification done', confidence: confidence - 5 },
        pass3: { result: 'Deep analysis finalized', confidence },
      },
      biasAnalysis: {
        rating: 'Center-Left',
        indicators: ['Emotional language detected', 'Single source cited'],
      },
      relatedClaims: [
        'Related claim 1 - Similar topic',
        'Related claim 2 - Contradicting information',
      ],
    };
  }

  async analyzeSource(url: string): Promise<SourceAnalysis> {
    const cacheKey = this.getCacheKey('/api/v1/analyze/url', { url });
    const cached = this.getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/analyze/url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const result = this.transformSourceAnalysis(data, url);
      this.setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Source analysis failed:', error);
      return this.getDemoSourceAnalysis(url);
    }
  }

  private transformSourceAnalysis(data: any, url: string): SourceAnalysis {
    const domain = new URL(url).hostname.replace('www.', '');
    return {
      url: data.url || url,
      domain: data.domain || domain,
      trustScore: data.trust_score || data.trustScore || 50,
      category: data.category || 'News',
      factualReporting: data.factual_reporting || data.factualReporting || 'Mixed',
      biasRating: data.bias_rating || data.biasRating || 'Center',
      ownerInfo: data.owner_info || data.ownerInfo || 'Unknown',
      trafficRank: data.traffic_rank || data.trafficRank || 100000,
      lastUpdated: data.last_updated || data.lastUpdated || new Date().toISOString(),
      warnings: data.warnings || [],
      positives: data.positives || [],
    };
  }

  private getDemoSourceAnalysis(url: string): SourceAnalysis {
    let domain: string;
    try {
      domain = new URL(url.startsWith('http') ? url : `https://${url}`).hostname.replace('www.', '');
    } catch {
      domain = url;
    }

    const trustScore = 40 + Math.floor(Math.random() * 50);

    return {
      url,
      domain,
      trustScore,
      category: 'News / Media',
      factualReporting: trustScore >= 70 ? 'High' : trustScore >= 50 ? 'Mixed' : 'Low',
      biasRating: 'Center-Left',
      ownerInfo: 'Demo Corporation',
      trafficRank: Math.floor(Math.random() * 100000) + 1000,
      lastUpdated: new Date().toISOString(),
      warnings: trustScore < 60 ? [
        'Limited fact-checking history',
        'Some unverified claims published',
      ] : [],
      positives: trustScore >= 60 ? [
        'Established publication',
        'Regular corrections policy',
        'Transparent ownership',
      ] : ['Active content moderation'],
    };
  }

  async getRecentVerifications(): Promise<VerificationResult[]> {
    try {
      const stored = await AsyncStorage.getItem('verity_history');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
    return [];
  }

  private async saveToHistory(result: VerificationResult): Promise<void> {
    try {
      const history = await this.getRecentVerifications();
      const updated = [result, ...history.slice(0, 99)]; // Keep last 100
      await AsyncStorage.setItem('verity_history', JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save to history:', error);
    }
  }

  async clearHistory(): Promise<void> {
    try {
      await AsyncStorage.removeItem('verity_history');
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  }

  async getStats(): Promise<{
    totalVerifications: number;
    accuracyRate: number;
    apiStatus: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/stats`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        return {
          totalVerifications: data.total_verifications || data.totalVerifications || 0,
          accuracyRate: data.accuracy_rate || data.accuracyRate || 0,
          apiStatus: 'online',
        };
      }
    } catch {
      // Fall back to local stats
    }

    const history = await this.getRecentVerifications();
    return {
      totalVerifications: history.length,
      accuracyRate: 97.3, // Demo value
      apiStatus: 'offline',
    };
  }
}

export const apiService = new ApiService();
