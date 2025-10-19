"""
Performance monitoring utilities for the Peru Congress Laws Scraper
"""
import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_io_read: int = 0
    disk_io_write: int = 0
    network_sent: int = 0
    network_recv: int = 0
    active_threads: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Performance monitoring class"""
    
    def __init__(self, monitoring_interval: float = 1.0, log_file: Optional[Path] = None):
        self.monitoring_interval = monitoring_interval
        self.log_file = log_file or Path("logs/performance.log")
        self.logger = logging.getLogger(__name__)
        
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Baseline metrics for comparison
        self.baseline_metrics = self._get_current_metrics()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_mb': 2048.0,  # 2GB
            'disk_io_read': 1000000,  # 1MB/s
            'disk_io_write': 1000000,  # 1MB/s
        }
    
    def _get_current_metrics(self) -> PerformanceMetrics:
        """Get current system metrics"""
        process = psutil.Process()
        
        # CPU and Memory
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = process.memory_percent()
        
        # Disk I/O
        disk_io = process.io_counters()
        disk_io_read = disk_io.read_bytes if disk_io else 0
        disk_io_write = disk_io.write_bytes if disk_io else 0
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_sent = network_io.bytes_sent if network_io else 0
        network_recv = network_io.bytes_recv if network_io else 0
        
        # Threads
        active_threads = threading.active_count()
        
        return PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_io_read=disk_io_read,
            disk_io_write=disk_io_write,
            network_sent=network_sent,
            network_recv=network_recv,
            active_threads=active_threads
        )
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🚀 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("🛑 Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._get_current_metrics()
                self.metrics_history.append(metrics)
                
                # Check thresholds
                self._check_thresholds(metrics)
                
                # Log to file if specified
                if self.log_file:
                    self._log_metrics_to_file(metrics)
                
                # Keep only last 1000 metrics to prevent memory issues
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.memory_mb > self.thresholds['memory_mb']:
            alerts.append(f"High memory usage: {metrics.memory_mb:.1f}MB")
        
        if alerts:
            self.logger.warning(f"⚠️ Performance alerts: {'; '.join(alerts)}")
    
    def _log_metrics_to_file(self, metrics: PerformanceMetrics):
        """Log metrics to file"""
        try:
            log_entry = {
                'timestamp': metrics.timestamp.isoformat(),
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'memory_mb': metrics.memory_mb,
                'active_threads': metrics.active_threads,
                'custom_metrics': metrics.custom_metrics
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"Error logging metrics to file: {e}")
    
    def add_custom_metric(self, name: str, value: Any):
        """Add custom metric to current monitoring"""
        if self.metrics_history:
            self.metrics_history[-1].custom_metrics[name] = value
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 measurements
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        memory_mb_values = [m.memory_mb for m in recent_metrics]
        
        summary = {
            'monitoring_duration': len(self.metrics_history) * self.monitoring_interval,
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current_percent': memory_values[-1] if memory_values else 0,
                'average_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max_percent': max(memory_values) if memory_values else 0,
                'current_mb': memory_mb_values[-1] if memory_mb_values else 0,
                'average_mb': sum(memory_mb_values) / len(memory_mb_values) if memory_mb_values else 0,
                'max_mb': max(memory_mb_values) if memory_mb_values else 0
            },
            'threads': {
                'current': recent_metrics[-1].active_threads,
                'max': max(m.active_threads for m in recent_metrics)
            }
        }
        
        return summary
    
    def export_metrics(self, output_file: Path):
        """Export metrics to JSON file"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'monitoring_interval': self.monitoring_interval,
                'total_measurements': len(self.metrics_history),
                'metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'cpu_percent': m.cpu_percent,
                        'memory_percent': m.memory_percent,
                        'memory_mb': m.memory_mb,
                        'disk_io_read': m.disk_io_read,
                        'disk_io_write': m.disk_io_write,
                        'network_sent': m.network_sent,
                        'network_recv': m.network_recv,
                        'active_threads': m.active_threads,
                        'custom_metrics': m.custom_metrics
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"📊 Metrics exported to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")


class PerformanceProfiler:
    """Context manager for profiling code sections"""
    
    def __init__(self, name: str, monitor: Optional[PerformanceMonitor] = None):
        self.name = name
        self.monitor = monitor
        self.start_time = None
        self.start_metrics = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        self.start_time = time.time()
        if self.monitor:
            self.start_metrics = self.monitor._get_current_metrics()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        
        if self.monitor:
            end_metrics = self.monitor._get_current_metrics()
            
            # Calculate differences
            cpu_delta = end_metrics.cpu_percent - (self.start_metrics.cpu_percent if self.start_metrics else 0)
            memory_delta = end_metrics.memory_mb - (self.start_metrics.memory_mb if self.start_metrics else 0)
            
            self.logger.info(f"⏱️ {self.name}: {duration:.2f}s (CPU: {cpu_delta:+.1f}%, Memory: {memory_delta:+.1f}MB)")
        else:
            self.logger.info(f"⏱️ {self.name}: {duration:.2f}s")


def profile_function(func):
    """Decorator to profile function execution"""
    def wrapper(*args, **kwargs):
        with PerformanceProfiler(func.__name__):
            return func(*args, **kwargs)
    return wrapper
