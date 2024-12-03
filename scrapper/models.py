from django.db import models
from django.utils import timezone
from azure.storage.blob import BlobServiceClient
from config.azure_settings import get_secret
import json
import logging

logger = logging.getLogger(__name__)

class Tweet(models.Model):
    """Model for storing tweets and their sentiment analysis"""
    
    # Tweet content
    tid = models.CharField(max_length=100, unique=True)  # Twitter ID
    user = models.CharField(max_length=100)
    tweet = models.TextField()
    timestamp = models.DateTimeField()
    
    # Analysis fields
    sentiment_score = models.IntegerField(default=3)  # 1-5 scale
    sentiment_confidence = models.FloatField(default=0.0)
    is_emergency = models.BooleanField(default=False)
    is_testing_record = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['sentiment_score']),
            models.Index(fields=['is_emergency']),
        ]
    
    def __str__(self):
        return f"{self.user}: {self.tweet[:50]}..."
    
    def to_dict(self):
        """Convert tweet to dictionary format"""
        return {
            'tid': self.tid,
            'user': self.user,
            'tweet': self.tweet,
            'timestamp': self.timestamp.isoformat(),
            'sentiment_score': self.sentiment_score,
            'sentiment_confidence': self.sentiment_confidence,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class TweetArchive:
    """Handler for archiving tweets to Azure Blob Storage"""
    
    def __init__(self):
        connection_string = get_secret('AZURE-STORAGE-CONNECTION-STRING')
        self.container_name = 'tweet-archives'
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {str(e)}")
            raise
    
    def archive_tweets(self, tweets, archive_name=None):
        """
        Archive tweets to Azure Blob Storage
        Args:
            tweets: QuerySet or list of Tweet objects
            archive_name: Optional name for the archive. If not provided, uses timestamp
        """
        try:
            if not archive_name:
                archive_name = f"tweets_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert tweets to dictionary format
            tweet_data = [tweet.to_dict() for tweet in tweets]
            
            # Create JSON string
            json_data = json.dumps(tweet_data, indent=2)
            
            # Upload to blob storage
            blob_client = self.container_client.get_blob_client(archive_name)
            blob_client.upload_blob(json_data, overwrite=True)
            
            logger.info(f"Successfully archived {len(tweet_data)} tweets to {archive_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive tweets: {str(e)}")
            return False
    
    def get_archive(self, archive_name):
        """
        Retrieve archived tweets from Azure Blob Storage
        Args:
            archive_name: Name of the archive file
        Returns:
            list: List of tweet dictionaries
        """
        try:
            blob_client = self.container_client.get_blob_client(archive_name)
            json_data = blob_client.download_blob().readall()
            return json.loads(json_data)
        except Exception as e:
            logger.error(f"Failed to retrieve archive {archive_name}: {str(e)}")
            return None
    
    def list_archives(self, prefix=None):
        """
        List available tweet archives
        Args:
            prefix: Optional prefix to filter archives
        Returns:
            list: List of archive names
        """
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list archives: {str(e)}")
            return []

class EmergencyAlert(models.Model):
    """Model for storing emergency alerts based on tweet analysis"""
    
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    alert_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('CRITICAL', 'Critical Priority'),
    ])
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_level']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.alert_level} Alert: {self.tweet.tweet[:50]}..."
    
    def resolve(self, notes=None):
        """Mark the alert as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()
