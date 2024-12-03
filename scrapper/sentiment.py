from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config.azure_settings import AZURE_COGNITIVE_ENDPOINT, AZURE_COGNITIVE_KEY
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.client = self._authenticate_client()

    def _authenticate_client(self):
        """Authenticate with Azure Cognitive Services"""
        try:
            credential = AzureKeyCredential(AZURE_COGNITIVE_KEY)
            return TextAnalyticsClient(
                endpoint=AZURE_COGNITIVE_ENDPOINT, 
                credential=credential
            )
        except Exception as e:
            logger.error(f"Failed to authenticate with Azure Cognitive Services: {str(e)}")
            raise

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using Azure Cognitive Services
        Returns: 
            - score (int): 1-5 (1 being very negative, 5 being very positive)
            - confidence (float): confidence score of the analysis
        """
        try:
            if not text:
                return 3, 0.0  # Neutral sentiment for empty text
                
            response = self.client.analyze_sentiment([text])[0]
            
            # Convert Azure sentiment scores to 1-5 scale
            if response.confidence_scores.positive > 0.8:
                return 5, response.confidence_scores.positive
            elif response.confidence_scores.positive > 0.6:
                return 4, response.confidence_scores.positive
            elif response.confidence_scores.neutral > 0.6:
                return 3, response.confidence_scores.neutral
            elif response.confidence_scores.negative > 0.6:
                return 2, response.confidence_scores.negative
            else:
                return 1, response.confidence_scores.negative
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return 3, 0.0  # Return neutral sentiment in case of error

    def analyze_batch_sentiment(self, texts):
        """
        Analyze sentiment for a batch of texts
        Args:
            texts (list): List of texts to analyze
        Returns:
            list: List of (score, confidence) tuples
        """
        try:
            if not texts:
                return []
                
            # Filter out empty texts
            valid_texts = [text for text in texts if text]
            if not valid_texts:
                return [(3, 0.0)] * len(texts)
                
            # Azure Cognitive Services has a limit of 10 texts per batch
            batch_size = 10
            results = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                responses = self.client.analyze_sentiment(batch)
                
                for response in responses:
                    if response.confidence_scores.positive > 0.8:
                        results.append((5, response.confidence_scores.positive))
                    elif response.confidence_scores.positive > 0.6:
                        results.append((4, response.confidence_scores.positive))
                    elif response.confidence_scores.neutral > 0.6:
                        results.append((3, response.confidence_scores.neutral))
                    elif response.confidence_scores.negative > 0.6:
                        results.append((2, response.confidence_scores.negative))
                    else:
                        results.append((1, response.confidence_scores.negative))
                        
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing batch sentiment: {str(e)}")
            return [(3, 0.0)] * len(texts)  # Return neutral sentiment in case of error

# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test single text analysis
    test_text = "The train service was excellent and on time!"
    score, confidence = analyzer.analyze_sentiment(test_text)
    print(f"Single text analysis:")
    print(f"Text: {test_text}")
    print(f"Sentiment score: {score}/5")
    print(f"Confidence: {confidence:.2f}")
    
    # Test batch analysis
    test_texts = [
        "The train was delayed by 2 hours, terrible service!",
        "Clean and comfortable journey, highly recommended",
        "Average experience, nothing special"
    ]
    results = analyzer.analyze_batch_sentiment(test_texts)
    print("\nBatch analysis:")
    for text, (score, confidence) in zip(test_texts, results):
        print(f"Text: {text}")
        print(f"Sentiment score: {score}/5")
        print(f"Confidence: {confidence:.2f}\n")
