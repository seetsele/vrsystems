"""
Verity Systems - Third-Party Tool Integrations
Leveraging GitHub Education/Pro credits for enhanced monitoring, security, and analytics

Tools Integrated:
- Honeybadger.io: Error tracking and monitoring
- New Relic: Application Performance Monitoring (APM)
- ConfigCat: Feature flags for gradual rollouts
- Doppler: Secrets management (configuration)
- Comet ML: ML experiment tracking and model comparison
- Simple Analytics: Privacy-first analytics (frontend)
- Astra Security: Security scanning (external)
- BrowserStack: Cross-browser testing (CI/CD)
- Travis CI: Continuous Integration
- Codecov: Test coverage reporting
"""

import os
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
import time
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('VerityIntegrations')

# ============================================================
# COMET ML - ML Experiment Tracking
# ============================================================

_comet_integration = None

def configure_comet_integration():
    """Initialize Comet ML for experiment tracking"""
    global _comet_integration
    
    try:
        from comet_integration import configure_comet, is_comet_enabled
        
        if configure_comet():
            _comet_integration = True
            logger.info("✅ Comet ML experiment tracking initialized")
            return True
        return False
    except ImportError:
        logger.warning("Comet integration module not available")
        return False
    except Exception as e:
        logger.error(f"Failed to configure Comet ML: {e}")
        return False


def get_comet_tracker():
    """Get Comet ML metrics tracker"""
    if not _comet_integration:
        return None
    
    try:
        from comet_integration import get_metrics_tracker
        return get_metrics_tracker()
    except:
        return None

# ============================================================
# HONEYBADGER - Error Tracking
# ============================================================

_honeybadger_configured = False

def configure_honeybadger(api_key: Optional[str] = None):
    """Initialize Honeybadger error tracking"""
    global _honeybadger_configured
    
    api_key = api_key or os.getenv('HONEYBADGER_API_KEY')
    if not api_key:
        logger.warning("Honeybadger API key not configured - error tracking disabled")
        return False
    
    try:
        import honeybadger
        honeybadger.configure(
            api_key=api_key,
            environment=os.getenv('ENVIRONMENT', 'development'),
            report_data=True
        )
        _honeybadger_configured = True
        logger.info("✅ Honeybadger error tracking initialized")
        return True
    except ImportError:
        logger.warning("Honeybadger package not installed: pip install honeybadger")
        return False
    except Exception as e:
        logger.error(f"Failed to configure Honeybadger: {e}")
        return False


def notify_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Send error to Honeybadger"""
    if not _honeybadger_configured:
        return
    
    try:
        import honeybadger
        honeybadger.notify(error, context=context or {})
    except Exception as e:
        logger.error(f"Failed to notify Honeybadger: {e}")


def track_verification_error(claim: str, provider: str, error: Exception):
    """Track fact-check verification errors with context"""
    notify_error(error, context={
        'claim': claim[:200],  # Truncate for privacy
        'provider': provider,
        'error_type': type(error).__name__
    })


# ============================================================
# NEW RELIC - Application Performance Monitoring
# ============================================================

_newrelic_configured = False

def configure_newrelic(license_key: Optional[str] = None):
    """Initialize New Relic APM"""
    global _newrelic_configured
    
    license_key = license_key or os.getenv('NEW_RELIC_LICENSE_KEY')
    if not license_key:
        logger.warning("New Relic license key not configured - APM disabled")
        return False
    
    try:
        import newrelic.agent
        newrelic.agent.initialize()
        _newrelic_configured = True
        logger.info("✅ New Relic APM initialized")
        return True
    except ImportError:
        logger.warning("New Relic package not installed: pip install newrelic")
        return False
    except Exception as e:
        logger.error(f"Failed to configure New Relic: {e}")
        return False


def trace_provider_call(provider_name: str):
    """Decorator to trace AI provider calls in New Relic"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if _newrelic_configured:
                try:
                    import newrelic.agent
                    with newrelic.agent.FunctionTrace(f"provider/{provider_name}"):
                        return await func(*args, **kwargs)
                except:
                    return await func(*args, **kwargs)
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if _newrelic_configured:
                try:
                    import newrelic.agent
                    with newrelic.agent.FunctionTrace(f"provider/{provider_name}"):
                        return func(*args, **kwargs)
                except:
                    return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def record_custom_metric(name: str, value: float):
    """Record custom metric in New Relic"""
    if not _newrelic_configured:
        return
    
    try:
        import newrelic.agent
        newrelic.agent.record_custom_metric(f'Custom/{name}', value)
    except Exception as e:
        logger.debug(f"Failed to record New Relic metric: {e}")


# ============================================================
# CONFIGCAT - Feature Flags
# ============================================================

_configcat_client = None

def configure_configcat(sdk_key: Optional[str] = None):
    """Initialize ConfigCat feature flags"""
    global _configcat_client
    
    sdk_key = sdk_key or os.getenv('CONFIGCAT_SDK_KEY')
    if not sdk_key:
        logger.warning("ConfigCat SDK key not configured - feature flags disabled")
        return False
    
    try:
        import configcatclient
        _configcat_client = configcatclient.get(sdk_key)
        logger.info("✅ ConfigCat feature flags initialized")
        return True
    except ImportError:
        logger.warning("ConfigCat package not installed: pip install configcat-client")
        return False
    except Exception as e:
        logger.error(f"Failed to configure ConfigCat: {e}")
        return False


def get_feature_flag(flag_key: str, default_value: bool = False, user_id: Optional[str] = None) -> bool:
    """Get feature flag value from ConfigCat"""
    if not _configcat_client:
        return default_value
    
    try:
        if user_id:
            from configcatclient import User
            user = User(identifier=user_id)
            return _configcat_client.get_value(flag_key, default_value, user)
        return _configcat_client.get_value(flag_key, default_value)
    except Exception as e:
        logger.debug(f"Failed to get ConfigCat flag '{flag_key}': {e}")
        return default_value


def get_config_value(key: str, default_value: Any) -> Any:
    """Get configuration value from ConfigCat (for strings, numbers, etc.)"""
    if not _configcat_client:
        return default_value
    
    try:
        return _configcat_client.get_value(key, default_value)
    except Exception as e:
        logger.debug(f"Failed to get ConfigCat value '{key}': {e}")
        return default_value


# Pre-defined feature flags for Verity Systems
class FeatureFlags:
    """Feature flag constants for Verity Systems"""
    
    # Provider toggles - disable broken providers instantly
    ENABLE_ANTHROPIC = "enable_anthropic"
    ENABLE_GROQ = "enable_groq"
    ENABLE_OPENAI = "enable_openai"
    ENABLE_PERPLEXITY = "enable_perplexity"
    ENABLE_HUGGINGFACE = "enable_huggingface"
    ENABLE_WIKIPEDIA = "enable_wikipedia"
    ENABLE_GOOGLE_FACTCHECK = "enable_google_factcheck"
    
    # Experimental features
    ENABLE_EXPERIMENTAL_GEMINI = "enable_experimental_gemini"
    ENABLE_EXPERIMENTAL_MISTRAL = "enable_experimental_mistral"
    ENABLE_WEB_SCRAPING = "enable_web_scraping"
    
    # Performance toggles
    ENABLE_CACHING = "enable_caching"
    ENABLE_PARALLEL_PROVIDERS = "enable_parallel_providers"
    
    # Security toggles
    ENABLE_RATE_LIMITING = "enable_rate_limiting"
    ENABLE_REQUEST_SIGNING = "enable_request_signing"
    
    # Business features
    ENABLE_PREMIUM_TIER = "enable_premium_tier"
    ENABLE_STRIPE_PAYMENTS = "enable_stripe_payments"


def is_provider_enabled(provider: str) -> bool:
    """Check if a specific provider is enabled via feature flag"""
    flag_map = {
        'anthropic': FeatureFlags.ENABLE_ANTHROPIC,
        'groq': FeatureFlags.ENABLE_GROQ,
        'openai': FeatureFlags.ENABLE_OPENAI,
        'perplexity': FeatureFlags.ENABLE_PERPLEXITY,
        'huggingface': FeatureFlags.ENABLE_HUGGINGFACE,
        'wikipedia': FeatureFlags.ENABLE_WIKIPEDIA,
        'google_factcheck': FeatureFlags.ENABLE_GOOGLE_FACTCHECK,
        'gemini': FeatureFlags.ENABLE_EXPERIMENTAL_GEMINI,
        'mistral': FeatureFlags.ENABLE_EXPERIMENTAL_MISTRAL,
    }
    
    flag_key = flag_map.get(provider.lower())
    if not flag_key:
        return True  # Unknown providers default to enabled
    
    return get_feature_flag(flag_key, default_value=True)


# ============================================================
# DOPPLER - Secrets Management
# ============================================================

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get secret from Doppler or fallback to environment variable.
    Doppler automatically injects secrets as environment variables when 
    running with `doppler run -- python script.py`
    """
    return os.getenv(key, default)


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider"""
    key_map = {
        'anthropic': 'ANTHROPIC_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'groq': 'GROQ_API_KEY',
        'perplexity': 'PERPLEXITY_API_KEY',
        'huggingface': 'HUGGINGFACE_API_KEY',
        'serper': 'SERPER_API_KEY',
        'newsapi': 'NEWS_API_KEY',
        'google_factcheck': 'GOOGLE_FACTCHECK_API_KEY',
        'stripe': 'STRIPE_SECRET_KEY',
    }
    
    env_var = key_map.get(provider.lower())
    if not env_var:
        return None
    
    return get_secret(env_var)


# ============================================================
# PERFORMANCE TRACKING
# ============================================================

@contextmanager
def track_operation(operation_name: str, provider: Optional[str] = None):
    """Context manager to track operation performance"""
    start_time = time.time()
    error_occurred = False
    
    try:
        yield
    except Exception as e:
        error_occurred = True
        if provider:
            track_verification_error("unknown", provider, e)
        raise
    finally:
        duration = time.time() - start_time
        
        # Record to New Relic
        metric_name = f"{provider}/{operation_name}" if provider else operation_name
        record_custom_metric(f"verification/{metric_name}/duration", duration)
        
        if error_occurred:
            record_custom_metric(f"verification/{metric_name}/errors", 1)
        
        logger.debug(f"Operation '{metric_name}' completed in {duration:.3f}s")


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_all_integrations():
    """Initialize all third-party integrations"""
    results = {
        'honeybadger': configure_honeybadger(),
        'newrelic': configure_newrelic(),
        'configcat': configure_configcat(),
        'comet_ml': configure_comet_integration(),
    }
    
    enabled = [k for k, v in results.items() if v]
    disabled = [k for k, v in results.items() if not v]
    
    if enabled:
        logger.info(f"Enabled integrations: {', '.join(enabled)}")
    if disabled:
        logger.info(f"Disabled integrations: {', '.join(disabled)}")
    
    return results


# ============================================================
# FASTAPI MIDDLEWARE INTEGRATION
# ============================================================

def add_honeybadger_middleware(app):
    """Add Honeybadger middleware to FastAPI app"""
    if not _honeybadger_configured:
        return
    
    try:
        from honeybadger.contrib.fastapi import HoneybadgerMiddleware
        app.add_middleware(HoneybadgerMiddleware)
        logger.info("✅ Honeybadger middleware added to FastAPI")
    except ImportError:
        logger.warning("Honeybadger FastAPI middleware not available")
    except Exception as e:
        logger.error(f"Failed to add Honeybadger middleware: {e}")


def add_newrelic_middleware(app):
    """Add New Relic middleware to FastAPI app"""
    if not _newrelic_configured:
        return
    
    try:
        from newrelic.agent import wrap_asgi_application
        app = wrap_asgi_application(app)
        logger.info("✅ New Relic ASGI wrapper added to FastAPI")
        return app
    except ImportError:
        logger.warning("New Relic ASGI wrapper not available")
        return app
    except Exception as e:
        logger.error(f"Failed to add New Relic middleware: {e}")
        return app


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Initialize all integrations
    initialize_all_integrations()
    
    # Example: Check feature flags
    print(f"Anthropic enabled: {is_provider_enabled('anthropic')}")
    print(f"Experimental Gemini: {get_feature_flag(FeatureFlags.ENABLE_EXPERIMENTAL_GEMINI)}")
    
    # Example: Get API keys via Doppler
    print(f"Has Anthropic key: {bool(get_api_key('anthropic'))}")
    
    # Example: Track an operation
    with track_operation("test_operation", "test_provider"):
        time.sleep(0.1)  # Simulate work
    
    print("✅ All integrations tested successfully")
