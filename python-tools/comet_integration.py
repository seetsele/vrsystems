"""
Verity Systems - Comet ML Integration
Track AI model performance, experiments, and verification accuracy

GitHub Education: Comet provides free tier for students/academics
Use for: Tracking model performance, A/B testing providers, accuracy metrics
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger('VerityCometML')

# ============================================================
# COMET ML CONFIGURATION
# ============================================================

_comet_experiment = None
_comet_configured = False

COMET_API_KEY = os.getenv('COMET_API_KEY')
COMET_PROJECT_NAME = os.getenv('COMET_PROJECT_NAME', 'verity-fact-checking')
COMET_WORKSPACE = os.getenv('COMET_WORKSPACE', 'verity-systems')


def configure_comet(
    api_key: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace: Optional[str] = None,
    experiment_name: Optional[str] = None,
    auto_log: bool = True
) -> bool:
    """
    Initialize Comet ML for experiment tracking.
    
    Args:
        api_key: Comet API key (or set COMET_API_KEY env var)
        project_name: Comet project name
        workspace: Comet workspace
        experiment_name: Name for this experiment run
        auto_log: Whether to auto-log code, parameters, etc.
    
    Returns:
        True if configured successfully, False otherwise
    """
    global _comet_experiment, _comet_configured
    
    api_key = api_key or COMET_API_KEY
    project_name = project_name or COMET_PROJECT_NAME
    workspace = workspace or COMET_WORKSPACE
    
    if not api_key:
        logger.warning("Comet API key not configured - ML tracking disabled")
        logger.info("Set COMET_API_KEY environment variable or pass api_key parameter")
        return False
    
    try:
        from comet_ml import Experiment, init
        
        # Initialize Comet
        init(api_key=api_key, project_name=project_name, workspace=workspace)
        
        # Create experiment
        _comet_experiment = Experiment(
            api_key=api_key,
            project_name=project_name,
            workspace=workspace,
            auto_metric_logging=auto_log,
            auto_param_logging=auto_log,
            auto_histogram_weight_logging=False,
            log_code=auto_log,
            log_graph=False,
            log_env_details=True,
            log_env_host=False,
            log_git_metadata=True,
            log_git_patch=False,
        )
        
        if experiment_name:
            _comet_experiment.set_name(experiment_name)
        else:
            _comet_experiment.set_name(f"verity-run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")
        
        # Log initial system info
        _comet_experiment.log_other("environment", os.getenv('ENVIRONMENT', 'development'))
        _comet_experiment.log_other("use_localstack", os.getenv('USE_LOCALSTACK', 'false'))
        
        _comet_configured = True
        logger.info("✅ Comet ML experiment tracking initialized")
        logger.info(f"   Project: {workspace}/{project_name}")
        return True
        
    except ImportError:
        logger.warning("Comet ML package not installed: pip install comet-ml")
        return False
    except Exception as e:
        logger.error(f"Failed to configure Comet ML: {e}")
        return False


def get_experiment():
    """Get the current Comet experiment instance"""
    return _comet_experiment


def is_comet_enabled() -> bool:
    """Check if Comet ML is configured and enabled"""
    return _comet_configured and _comet_experiment is not None


# ============================================================
# VERIFICATION METRICS TRACKING
# ============================================================

class VerificationMetricsTracker:
    """Track fact-checking verification metrics in Comet ML"""
    
    def __init__(self):
        self.verification_count = 0
        self.provider_metrics = {}
        self.verdict_distribution = {
            'TRUE': 0, 'FALSE': 0, 'MIXED': 0, 
            'UNVERIFIED': 0, 'MISLEADING': 0
        }
        self.confidence_scores = []
        
    def log_verification(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        providers_used: List[str],
        response_time_ms: float,
        metadata: Optional[Dict] = None
    ):
        """
        Log a single verification result to Comet ML.
        
        Args:
            claim: The claim that was verified
            verdict: The verification verdict
            confidence: Confidence score (0-100)
            providers_used: List of AI providers used
            response_time_ms: Total response time in milliseconds
            metadata: Additional metadata to log
        """
        if not is_comet_enabled():
            return
        
        exp = get_experiment()
        step = self.verification_count
        
        # Log main metrics
        exp.log_metric("verification_count", step + 1, step=step)
        exp.log_metric("confidence_score", confidence, step=step)
        exp.log_metric("response_time_ms", response_time_ms, step=step)
        exp.log_metric("providers_used_count", len(providers_used), step=step)
        
        # Log verdict distribution
        if verdict.upper() in self.verdict_distribution:
            self.verdict_distribution[verdict.upper()] += 1
        for v, count in self.verdict_distribution.items():
            exp.log_metric(f"verdict_{v.lower()}_count", count, step=step)
        
        # Track confidence score distribution
        self.confidence_scores.append(confidence)
        if len(self.confidence_scores) > 0:
            avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores)
            exp.log_metric("avg_confidence", avg_confidence, step=step)
        
        # Log per-provider metrics
        for provider in providers_used:
            if provider not in self.provider_metrics:
                self.provider_metrics[provider] = {'count': 0, 'total_time': 0}
            self.provider_metrics[provider]['count'] += 1
            exp.log_metric(f"provider_{provider}_usage_count", 
                          self.provider_metrics[provider]['count'], step=step)
        
        # Log verification as text for review
        exp.log_text(f"Claim: {claim[:200]}...\nVerdict: {verdict}\nConfidence: {confidence}%",
                    step=step)
        
        # Log additional metadata
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    exp.log_metric(f"meta_{key}", value, step=step)
                else:
                    exp.log_other(f"meta_{key}", str(value))
        
        self.verification_count += 1
        logger.debug(f"Logged verification #{step + 1} to Comet ML")
    
    def log_provider_performance(
        self,
        provider: str,
        response_time_ms: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log individual provider performance metrics"""
        if not is_comet_enabled():
            return
        
        exp = get_experiment()
        
        if provider not in self.provider_metrics:
            self.provider_metrics[provider] = {
                'count': 0,
                'total_time': 0,
                'success_count': 0,
                'error_count': 0
            }
        
        metrics = self.provider_metrics[provider]
        metrics['count'] += 1
        metrics['total_time'] += response_time_ms
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1
        
        # Log metrics
        step = metrics['count']
        exp.log_metric(f"{provider}/response_time_ms", response_time_ms, step=step)
        exp.log_metric(f"{provider}/success_rate", 
                      metrics['success_count'] / metrics['count'] * 100, step=step)
        exp.log_metric(f"{provider}/avg_response_time", 
                      metrics['total_time'] / metrics['count'], step=step)
        
        if error_message:
            exp.log_other(f"{provider}/last_error", error_message)
    
    def log_batch_summary(self, batch_id: str, claims_count: int, total_time_ms: float):
        """Log batch verification summary"""
        if not is_comet_enabled():
            return
        
        exp = get_experiment()
        
        exp.log_metric("batch_claims_count", claims_count)
        exp.log_metric("batch_total_time_ms", total_time_ms)
        exp.log_metric("batch_avg_time_per_claim_ms", total_time_ms / claims_count if claims_count > 0 else 0)
        exp.log_other("batch_id", batch_id)
    
    def finalize(self):
        """Finalize and save all metrics"""
        if not is_comet_enabled():
            return
        
        exp = get_experiment()
        
        # Log final summary
        exp.log_other("total_verifications", self.verification_count)
        exp.log_other("verdict_distribution", json.dumps(self.verdict_distribution))
        
        if self.confidence_scores:
            exp.log_metric("final_avg_confidence", 
                          sum(self.confidence_scores) / len(self.confidence_scores))
            exp.log_metric("min_confidence", min(self.confidence_scores))
            exp.log_metric("max_confidence", max(self.confidence_scores))
        
        # Log provider summary
        for provider, metrics in self.provider_metrics.items():
            exp.log_other(f"{provider}/total_calls", metrics['count'])
            if metrics['count'] > 0:
                exp.log_other(f"{provider}/final_avg_time", 
                            metrics['total_time'] / metrics['count'])


# Global tracker instance
_metrics_tracker = None


def get_metrics_tracker() -> VerificationMetricsTracker:
    """Get or create the global metrics tracker"""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = VerificationMetricsTracker()
    return _metrics_tracker


# ============================================================
# MODEL COMPARISON & A/B TESTING
# ============================================================

class ModelComparison:
    """Compare different AI provider configurations"""
    
    def __init__(self, comparison_name: str):
        self.comparison_name = comparison_name
        self.config_results = {}
    
    def log_config_result(
        self,
        config_name: str,
        accuracy: float,
        avg_confidence: float,
        avg_response_time_ms: float,
        total_cost_usd: float = 0,
        sample_size: int = 0
    ):
        """Log results for a specific provider configuration"""
        if not is_comet_enabled():
            return
        
        exp = get_experiment()
        
        self.config_results[config_name] = {
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'avg_response_time_ms': avg_response_time_ms,
            'total_cost_usd': total_cost_usd,
            'sample_size': sample_size
        }
        
        # Log as parameters for comparison
        exp.log_parameter(f"config_{config_name}_accuracy", accuracy)
        exp.log_parameter(f"config_{config_name}_confidence", avg_confidence)
        exp.log_parameter(f"config_{config_name}_response_time", avg_response_time_ms)
        exp.log_parameter(f"config_{config_name}_cost", total_cost_usd)
        
        # Log as metrics for charts
        exp.log_metric(f"comparison/{config_name}/accuracy", accuracy)
        exp.log_metric(f"comparison/{config_name}/confidence", avg_confidence)
        exp.log_metric(f"comparison/{config_name}/response_time", avg_response_time_ms)
    
    def get_best_config(self, metric: str = 'accuracy') -> Optional[str]:
        """Get the best performing configuration based on a metric"""
        if not self.config_results:
            return None
        
        best_config = max(
            self.config_results.items(),
            key=lambda x: x[1].get(metric, 0)
        )
        return best_config[0]
    
    def log_comparison_summary(self):
        """Log comparison summary to Comet"""
        if not is_comet_enabled() or not self.config_results:
            return
        
        exp = get_experiment()
        
        exp.log_other("comparison_name", self.comparison_name)
        exp.log_other("configs_tested", list(self.config_results.keys()))
        exp.log_other("best_accuracy_config", self.get_best_config('accuracy'))
        exp.log_other("best_speed_config", self.get_best_config('avg_response_time_ms'))
        
        # Log full results as JSON
        exp.log_other("comparison_results", json.dumps(self.config_results, indent=2))


# ============================================================
# DECORATORS FOR AUTOMATIC TRACKING
# ============================================================

def track_verification(func):
    """Decorator to automatically track verification calls"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = None
        error = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            
            if is_comet_enabled() and result:
                tracker = get_metrics_tracker()
                
                # Extract claim from args/kwargs
                claim = kwargs.get('claim') or (args[0] if args else 'unknown')
                if hasattr(claim, 'text'):
                    claim = claim.text
                
                # Extract result data
                if hasattr(result, '__dict__'):
                    verdict = getattr(result, 'verdict', 'UNKNOWN')
                    confidence = getattr(result, 'confidence', 0)
                    providers = getattr(result, 'providers_used', [])
                elif isinstance(result, dict):
                    verdict = result.get('verdict', 'UNKNOWN')
                    confidence = result.get('confidence', 0)
                    providers = result.get('providers_used', [])
                else:
                    verdict = 'UNKNOWN'
                    confidence = 0
                    providers = []
                
                tracker.log_verification(
                    claim=str(claim)[:500],
                    verdict=str(verdict),
                    confidence=float(confidence),
                    providers_used=providers,
                    response_time_ms=elapsed_ms,
                    metadata={'error': str(error) if error else None}
                )
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = None
        error = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            
            if is_comet_enabled() and result:
                tracker = get_metrics_tracker()
                claim = kwargs.get('claim') or (args[0] if args else 'unknown')
                
                if isinstance(result, dict):
                    tracker.log_verification(
                        claim=str(claim)[:500],
                        verdict=result.get('verdict', 'UNKNOWN'),
                        confidence=result.get('confidence', 0),
                        providers_used=result.get('providers_used', []),
                        response_time_ms=elapsed_ms
                    )
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def track_provider_call(provider_name: str):
    """Decorator to track individual provider API calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                
                if is_comet_enabled():
                    tracker = get_metrics_tracker()
                    tracker.log_provider_performance(
                        provider=provider_name,
                        response_time_ms=elapsed_ms,
                        success=success,
                        error_message=error_msg
                    )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                
                if is_comet_enabled():
                    tracker = get_metrics_tracker()
                    tracker.log_provider_performance(
                        provider=provider_name,
                        response_time_ms=elapsed_ms,
                        success=success,
                        error_message=error_msg
                    )
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# ============================================================
# CONTEXT MANAGERS
# ============================================================

@contextmanager
def comet_experiment_context(
    experiment_name: str,
    api_key: Optional[str] = None,
    project_name: Optional[str] = None
):
    """Context manager for Comet experiment lifecycle"""
    try:
        configure_comet(
            api_key=api_key,
            project_name=project_name,
            experiment_name=experiment_name
        )
        yield get_experiment()
    finally:
        if is_comet_enabled():
            get_metrics_tracker().finalize()
            get_experiment().end()
            logger.info("✅ Comet ML experiment ended and saved")


# ============================================================
# INTEGRATION WITH VERITY API SERVER
# ============================================================

def register_comet_with_fastapi(app):
    """Register Comet ML tracking with FastAPI application"""
    from fastapi import Request
    
    @app.on_event("startup")
    async def startup_comet():
        configure_comet()
    
    @app.on_event("shutdown")
    async def shutdown_comet():
        if is_comet_enabled():
            get_metrics_tracker().finalize()
            get_experiment().end()
    
    @app.middleware("http")
    async def comet_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        
        if is_comet_enabled() and "/verify" in request.url.path:
            elapsed_ms = (time.time() - start_time) * 1000
            exp = get_experiment()
            exp.log_metric("api/request_time_ms", elapsed_ms)
            exp.log_metric("api/status_code", response.status_code)
        
        return response
    
    logger.info("✅ Comet ML registered with FastAPI")


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_comet_integration():
        # Initialize Comet (will use COMET_API_KEY env var)
        configured = configure_comet(experiment_name="test-run")
        
        if not configured:
            print("⚠️ Comet ML not configured. Set COMET_API_KEY to enable.")
            print("   Get your API key at: https://www.comet.com/")
            return
        
        tracker = get_metrics_tracker()
        
        # Simulate some verifications
        test_verifications = [
            ("The Earth is round", "TRUE", 98.5, ["anthropic", "groq", "wikipedia"]),
            ("Water boils at 50°C", "FALSE", 99.2, ["anthropic", "openai"]),
            ("Exercise is good for health", "TRUE", 95.0, ["groq", "perplexity"]),
        ]
        
        for claim, verdict, confidence, providers in test_verifications:
            tracker.log_verification(
                claim=claim,
                verdict=verdict,
                confidence=confidence,
                providers_used=providers,
                response_time_ms=250 + (confidence * 2),
                metadata={"test": True}
            )
            print(f"✓ Logged: {claim[:30]}... -> {verdict}")
        
        # Log provider performance
        tracker.log_provider_performance("anthropic", 150.5, True)
        tracker.log_provider_performance("groq", 80.2, True)
        tracker.log_provider_performance("openai", 200.0, False, "Rate limit exceeded")
        
        # Finalize
        tracker.finalize()
        get_experiment().end()
        
        print("\n✅ Comet ML integration test complete!")
        print("   View your experiment at: https://www.comet.com/")
    
    asyncio.run(test_comet_integration())
