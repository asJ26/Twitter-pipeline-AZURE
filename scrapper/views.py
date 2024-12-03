from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from .models import Tweet, EmergencyAlert, TweetArchive
from .sentiment import SentimentAnalyzer
import logging
import json
from datetime import timedelta

logger = logging.getLogger(__name__)
sentiment_analyzer = SentimentAnalyzer()

@login_required
def dashboard(request):
    """Main dashboard view showing tweet analytics"""
    try:
        # Get time range from request, default to last 24 hours
        time_range = request.GET.get('range', '24h')
        if time_range == '24h':
            start_time = timezone.now() - timedelta(hours=24)
        elif time_range == '7d':
            start_time = timezone.now() - timedelta(days=7)
        elif time_range == '30d':
            start_time = timezone.now() - timedelta(days=30)
        else:
            start_time = timezone.now() - timedelta(hours=24)

        # Get tweets within time range
        tweets = Tweet.objects.filter(timestamp__gte=start_time)

        # Calculate analytics
        analytics = {
            'total_tweets': tweets.count(),
            'avg_sentiment': tweets.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] or 0,
            'emergency_count': tweets.filter(is_emergency=True).count(),
            'sentiment_distribution': tweets.values('sentiment_score').annotate(
                count=Count('sentiment_score')
            ).order_by('sentiment_score'),
        }

        # Get recent emergency alerts
        emergency_alerts = EmergencyAlert.objects.filter(
            is_resolved=False
        ).select_related('tweet')[:5]

        context = {
            'analytics': analytics,
            'emergency_alerts': emergency_alerts,
            'time_range': time_range,
        }
        
        return render(request, 'dashboard/index.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        return render(request, 'dashboard/error.html', {'error': str(e)})

@login_required
def tweets_list(request):
    """View for listing and filtering tweets"""
    try:
        # Get filter parameters
        sentiment = request.GET.get('sentiment')
        emergency = request.GET.get('emergency')
        search = request.GET.get('search')
        
        # Base queryset
        tweets = Tweet.objects.all()
        
        # Apply filters
        if sentiment:
            tweets = tweets.filter(sentiment_score=sentiment)
        if emergency:
            tweets = tweets.filter(is_emergency=emergency.lower() == 'true')
        if search:
            tweets = tweets.filter(tweet__icontains=search)
            
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(tweets, 25)
        tweets_page = paginator.get_page(page)
        
        context = {
            'tweets': tweets_page,
            'filters': {
                'sentiment': sentiment,
                'emergency': emergency,
                'search': search,
            }
        }
        
        return render(request, 'dashboard/tweets.html', context)
        
    except Exception as e:
        logger.error(f"Error in tweets list view: {str(e)}")
        return render(request, 'dashboard/error.html', {'error': str(e)})

@login_required
def analyze_tweet(request):
    """API endpoint for analyzing a single tweet"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        tweet_text = data.get('tweet')
        
        if not tweet_text:
            return JsonResponse({'error': 'Tweet text is required'}, status=400)
            
        # Analyze sentiment
        score, confidence = sentiment_analyzer.analyze_sentiment(tweet_text)
        
        return JsonResponse({
            'sentiment_score': score,
            'confidence': confidence,
        })
        
    except Exception as e:
        logger.error(f"Error analyzing tweet: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def emergency_alerts(request):
    """View for managing emergency alerts"""
    try:
        if request.method == 'POST':
            # Handle alert resolution
            alert_id = request.POST.get('alert_id')
            notes = request.POST.get('notes')
            
            alert = EmergencyAlert.objects.get(id=alert_id)
            alert.resolve(notes=notes)
            
            return JsonResponse({'status': 'success'})
            
        # Get filter parameters
        status = request.GET.get('status', 'active')  # active or resolved
        level = request.GET.get('level')  # alert level filter
        
        # Base queryset
        alerts = EmergencyAlert.objects.select_related('tweet')
        
        # Apply filters
        if status == 'active':
            alerts = alerts.filter(is_resolved=False)
        elif status == 'resolved':
            alerts = alerts.filter(is_resolved=True)
            
        if level:
            alerts = alerts.filter(alert_level=level)
            
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(alerts, 20)
        alerts_page = paginator.get_page(page)
        
        context = {
            'alerts': alerts_page,
            'filters': {
                'status': status,
                'level': level,
            }
        }
        
        return render(request, 'dashboard/emergency_alerts.html', context)
        
    except Exception as e:
        logger.error(f"Error in emergency alerts view: {str(e)}")
        return render(request, 'dashboard/error.html', {'error': str(e)})

@login_required
def archive_management(request):
    """View for managing tweet archives"""
    try:
        archive_handler = TweetArchive()
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create':
                # Create new archive
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                
                tweets = Tweet.objects.filter(
                    timestamp__range=[start_date, end_date]
                )
                
                success = archive_handler.archive_tweets(tweets)
                
                return JsonResponse({
                    'status': 'success' if success else 'error',
                    'message': 'Archive created successfully' if success else 'Failed to create archive'
                })
                
            elif action == 'delete':
                # Delete archive (implement if needed)
                pass
                
        # List available archives
        archives = archive_handler.list_archives()
        
        context = {
            'archives': archives,
        }
        
        return render(request, 'dashboard/archives.html', context)
        
    except Exception as e:
        logger.error(f"Error in archive management view: {str(e)}")
        return render(request, 'dashboard/error.html', {'error': str(e)})
