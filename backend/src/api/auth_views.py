"""
Authentication views for user registration, login, and profile management
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
import logging

from .models import UserProfile

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    try:
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        # Validation
        if not username or not email or not password:
            return Response({
                'error': 'Username, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                medical_history=[],
                allergies=[],
                current_conditions=[],
                medications=[],
                emergency_contact={},
                preferences={}
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'status': 'success',
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat()
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return Response({
            'error': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens"""
    try:
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'last_login': user.last_login.isoformat()
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token"""
    try:
        refresh_token = request.data.get('refresh', '').strip()
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            
            return Response({
                'status': 'success',
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            })
            
        except Exception as e:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return Response({
            'error': f'Token refresh failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get authenticated user's profile"""
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'profile': {
                'medical_history': profile.medical_history,
                'allergies': profile.allergies,
                'current_conditions': profile.current_conditions,
                'medications': profile.medications,
                'emergency_contact': profile.emergency_contact,
                'preferences': profile.preferences,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat()
            },
            'activity_summary': profile.get_activity_summary()
        })
        
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=user,
            medical_history=[],
            allergies=[],
            current_conditions=[],
            medications=[],
            emergency_contact={},
            preferences={}
        )
        
        return Response({
            'status': 'success',
            'message': 'Profile created',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'profile': {
                'medical_history': profile.medical_history,
                'allergies': profile.allergies,
                'current_conditions': profile.current_conditions,
                'medications': profile.medications,
                'emergency_contact': profile.emergency_contact,
                'preferences': profile.preferences,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat()
            },
            'activity_summary': profile.get_activity_summary()
        })
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return Response({
            'error': f'Failed to get profile: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update authenticated user's profile"""
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        # Update user fields
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        # Update profile fields
        profile.medical_history = request.data.get('medical_history', profile.medical_history)
        profile.allergies = request.data.get('allergies', profile.allergies)
        profile.current_conditions = request.data.get('current_conditions', profile.current_conditions)
        profile.medications = request.data.get('medications', profile.medications)
        profile.emergency_contact = request.data.get('emergency_contact', profile.emergency_contact)
        profile.preferences = request.data.get('preferences', profile.preferences)
        profile.save()
        
        return Response({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'profile': {
                'medical_history': profile.medical_history,
                'allergies': profile.allergies,
                'current_conditions': profile.current_conditions,
                'medications': profile.medications,
                'emergency_contact': profile.emergency_contact,
                'preferences': profile.preferences,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat()
            },
            'activity_summary': profile.get_activity_summary()
        })
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return Response({
            'error': f'Failed to update profile: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user (blacklist refresh token)"""
    try:
        refresh_token = request.data.get('refresh', '').strip()
        
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as e:
                logger.warning(f"Failed to blacklist token: {e}")
        
        return Response({
            'status': 'success',
            'message': 'Logout successful'
        })
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return Response({
            'error': f'Logout failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """Verify if the current token is valid"""
    try:
        user = request.user
        return Response({
            'status': 'success',
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return Response({
            'error': f'Token verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
