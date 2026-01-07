"""
GLIS v4.0 - Cognitive Legal Assistant API
Ghana's AI-powered legal intelligence system
Run with: python main.py
"""
import logging
import sys
from pathlib import Path
import argparse
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.semantic_search import router as semantic_search_router
import uvicorn

# Initialize FastAPI app for v4.0
app = FastAPI(
    title="GLIS v4.0 - Cognitive Legal Assistant",
    description="AI-powered legal intelligence system for Ghana",
    version="4.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "service": "GLIS - Cognitive Legal Assistant"
    }

# Include routers
app.include_router(semantic_search_router)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Ghana Legal Scraper - Supreme Court Case Collector',
        epilog='Examples:\n'
               '  python main.py scrape          # Start scraping campaign\n'
               '  python main.py scrape --test   # Test with 10 cases\n'
               '  python main.py api             # Start API server\n'
               '  python main.py api --port 8080 # Start API on custom port\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Run scraping campaign')
    scrape_parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (limited to 10 cases)'
    )

    # API command
    api_parser = subparsers.add_parser('api', help='Start REST API server')
    api_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API host (default: 0.0.0.0)'
    )
    api_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API port (default: 8000)'
    )
    api_parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload on code changes'
    )

    # Test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    test_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'scrape':
        logger.info("=" * 70)
        logger.info("GHANA LEGAL SCRAPER - SCRAPING CAMPAIGN")
        logger.info("=" * 70)

        crawler = GhanaLegalCrawler()

        try:
            stats = crawler.run_scraping_campaign(test_mode=args.test)
            crawler.save_scraped_urls()

            logger.info("\nCampaign Complete!")
            logger.info(f"Total attempted: {stats['total_attempted']}")
            logger.info(f"Total valid: {stats['total_valid']}")
            logger.info(f"Total errors: {stats['total_errors']}")

        except KeyboardInterrupt:
            logger.warning("\nScraping interrupted by user")
            crawler.save_scraped_urls()
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
            sys.exit(1)

    elif args.command == 'api':
        logger.info("=" * 70)
        logger.info("GHANA LEGAL SCRAPER - API SERVER")
        logger.info("=" * 70)
        logger.info(f"Starting API on {args.host}:{args.port}")
        logger.info(f"Visit: http://{args.host}:{args.port}/docs for API documentation")

        try:
            uvicorn.run(
                'api.main:app',
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level='info'
            )
        except KeyboardInterrupt:
            logger.info("API server stopped")
            sys.exit(0)

    elif args.command == 'test':
        logger.info("=" * 70)
        logger.info("GHANA LEGAL SCRAPER - TEST SUITE")
        logger.info("=" * 70)

        import pytest
        pytest_args = ['tests/test_scraper.py', '-v']
        if args.verbose:
            pytest_args.append('-vv')
        pytest_args.append('--tb=short')

        exit_code = pytest.main(pytest_args)
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
