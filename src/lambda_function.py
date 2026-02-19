import json
import logging
from src.main import run_scan

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda Handler
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        logger.info("Starting Market Scan from Lambda...")
        run_scan()
        logger.info("Market Scan Completed Successfully.")

        return {
            'statusCode': 200,
            'body': json.dumps('Market Scan Completed Successfully')
        }
    except Exception as e:
        logger.error(f"Error in Lambda execution: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
