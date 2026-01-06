"""
Utility functions for monitoring, logging, and progress tracking
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from config.settings import STATS_DIR, LOGS_DIR


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track scraping progress and generate reports"""

    def __init__(self):
        self.stats = {
            'start_time': datetime.utcnow(),
            'cases_processed': 0,
            'cases_valid': 0,
            'cases_skipped': 0,
            'errors': 0,
            'current_year': 2000
        }

    def update(self, processed: int = 0, valid: int = 0, skipped: int = 0, errors: int = 0):
        """Update progress statistics"""
        self.stats['cases_processed'] += processed
        self.stats['cases_valid'] += valid
        self.stats['cases_skipped'] += skipped
        self.stats['errors'] += errors
        self.stats['last_updated'] = datetime.utcnow()

    def get_progress(self) -> Dict:
        """Get current progress"""
        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        rate = self.stats['cases_valid'] / elapsed if elapsed > 0 else 0

        return {
            'processed': self.stats['cases_processed'],
            'valid': self.stats['cases_valid'],
            'skipped': self.stats['cases_skipped'],
            'errors': self.stats['errors'],
            'elapsed_seconds': elapsed,
            'rate_per_hour': rate * 3600,
            'timestamp': self.stats.get('last_updated', datetime.utcnow()).isoformat()
        }

    def save_progress(self, filename: str = 'progress.json'):
        """Save progress to file"""
        try:
            filepath = STATS_DIR / filename
            with open(filepath, 'w') as f:
                json.dump(self.get_progress(), f, indent=2)
            logger.info(f"Progress saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def log_error(self, case_id: str, error_msg: str):
        """Log individual error"""
        self.stats['errors'] += 1
        error_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'case_id': case_id,
            'error': error_msg
        }
        
        try:
            error_log = LOGS_DIR / 'errors.jsonl'
            with open(error_log, 'a') as f:
                f.write(json.dumps(error_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to error log: {e}")


class QualityReporter:
    """Generate quality reports"""

    @staticmethod
    def generate_report(cases: List[Dict]) -> Dict:
        """Generate quality assessment report"""
        if not cases:
            return {}

        total = len(cases)
        scores = [c.get('data_quality_score', 0) for c in cases]
        avg_score = sum(scores) / total if scores else 0

        # Analyze missing fields
        mandatory_fields = ['case_id', 'case_name', 'date_decided', 'coram', 'full_text']
        missing_analysis = {}

        for field in mandatory_fields:
            missing_count = len([c for c in cases if not c.get(field)])
            if missing_count > 0:
                missing_analysis[field] = {
                    'count': missing_count,
                    'percentage': (missing_count / total) * 100
                }

        report = {
            'generated': datetime.utcnow().isoformat(),
            'summary': {
                'total_cases': total,
                'average_quality': round(avg_score, 2),
                'min_quality': min(scores) if scores else 0,
                'max_quality': max(scores) if scores else 0
            },
            'quality_distribution': {
                'excellent_100': len([s for s in scores if s == 100]),
                'good_80_99': len([s for s in scores if 80 <= s < 100]),
                'fair_60_79': len([s for s in scores if 60 <= s < 80]),
                'poor_below_60': len([s for s in scores if s < 60])
            },
            'missing_fields': missing_analysis
        }

        return report

    @staticmethod
    def save_report(report: Dict, filename: str = 'quality_report.json'):
        """Save report to file"""
        try:
            filepath = STATS_DIR / filename
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")


class Monitor:
    """Monitoring dashboard data generator"""

    @staticmethod
    def get_dashboard_data(storage) -> Dict:
        """Get all data needed for monitoring dashboard"""
        try:
            stats = storage.get_stats()

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'database': {
                    'total_cases': stats.get('total_cases', 0),
                    'average_quality': stats.get('average_quality', 0),
                    'cases_by_year': stats.get('cases_by_year', {}),
                    'top_judges': stats.get('top_judges', {})
                },
                'health': {
                    'database_size': 'Unknown',
                    'last_update': datetime.utcnow().isoformat(),
                    'status': 'operational'
                }
            }
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {}
