"""
============================================================================
AUTHENTICATION VIEWS - Medicine Assistant Application
============================================================================

This file handles all user authentication and profile management endpoints.
Provides JWT token-based authentication for the entire application.

Key Functions:
1. register_user() - Create new user account
2. login_user() - Authenticate and get JWT tokens
3. refresh_token() - Renew access token
4. logout_user() - Invalidate tokens
5. verify_token() - Check token validity
6. get_user_profile() - Fetch user profile and medical data
7. update_user_profile() - Save profile changes

Authentication Flow:
1. User registers → Gets JWT tokens
2. User logs in → Gets JWT tokens
3. Every API call includes token in header: Authorization: Bearer <token>
4. Token expires after 60 minutes → Use refresh token to get new one
5. Refresh token expires after 24 hours → User must login again

Used by:
- Flutter LoginScreen, RegistrationScreen
- Flutter UserProfileScreen, PersonalInfoScreen, MedicalHistoryScreen
- All API endpoints that require authentication

Related Files:
- api/models.py: UserProfile model
- api/urls.py: Routes authentication endpoints here
- medicine_assistant/settings.py: JWT configuration

Frontend Integration:
- Flutter ApiService calls these endpoints
- UserSession stores JWT tokens locally
- All authenticated requests include token
============================================================================
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  # JWT token generation
from django.contrib.auth import authenticate                # User authentication
from django.contrib.auth.models import User                # Django User model
from django.utils import timezone
from django.db import transaction
import logging

from .models import UserProfile  # User medical data model

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # No authentication required for registration
def register_user(request):
    """
    Register a new user account and create associated profile.
    
    URL: POST /api/auth/register/
    Authentication: None required (AllowAny)
    
    Request Body:
    {
        "username": "johndoe",      (required, unique)
        "email": "john@example.com", (required, unique)
        "password": "securepass123", (required, min 8 chars)
        "first_name": "John",        (optional)
        "last_name": "Doe"           (optional)
    }
    
    Returns:
    {
        "status": "success",
        "message": "User registered successfully",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  (JWT access token)
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...", (JWT refresh token)
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    }
    
    Processing Flow:
    1. Extract user data from request
    2. Validate required fields (username, email, password)
    3. Check if username/email already exists
    4. Create User record in database
    5. Create UserProfile record (linked to user)
    6. Generate JWT access and refresh tokens
    7. Return tokens and user data
    
    Called by:
    - Flutter RegistrationScreen (register button)
    - ApiService.register()
    
    Calls:
    - User.objects.create_user() - Django user creation
    - UserProfile.objects.create() - Profile creation
    - RefreshToken.for_user() - JWT token generation
    
    Side Effects:
    - Creates User record in auth_user table
    - Creates UserProfile record in api_userprofile table
    - User is automatically logged in (receives tokens)
    
    Error Handling:
    - Missing fields → 400 Bad Request
    - Username exists → 400 "Username already exists"
    - Email exists → 400 "Email already registered"
    - Server error → 500 Internal Server Error
    
    Frontend Integration:
    - On success: Flutter stores tokens in UserSession
    - On success: Navigates to Dashboard
    - On error: Shows error message in SnackBar
    """
    try:
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        # Medical profile data
        allergies = request.data.get('allergies', [])
        medical_history = request.data.get('medical_history', [])
        emergency_contact = request.data.get('emergency_contact', '')
        
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
            
            # Create user profile with medical data
            UserProfile.objects.create(
                user=user,
                medical_history=medical_history,
                allergies=allergies,
                current_conditions=[],
                medications=[],
                emergency_contact={'contact': emergency_contact} if emergency_contact else {},
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
    """Login user and return JWT tokens - accepts username or email"""
    try:
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        
        if not username_or_email or not password:
            return Response({
                'error': 'Username/email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to authenticate with username first
        user = authenticate(username=username_or_email, password=password)
        
        # If username authentication fails, try email authentication
        if not user and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
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
@permission_classes([IsAuthenticated])  # Requires valid JWT token
def get_user_profile(request):
    """
    Retrieve complete user profile including medical data and activity summary.
    Day 17 Feature - Connected to Flutter frontend.
    
    URL: GET /api/auth/profile/
    Authentication: Required (JWT token)
    
    Request Headers:
    - Authorization: Bearer <access_token>
    
    Returns:
    {
        "status": "success",
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2025-10-01T00:00:00Z",
            "last_login": "2025-10-10T14:30:00Z"
        },
        "profile": {
            "medical_history": ["Surgery 2020", "Diabetes diagnosed 2019"],
            "allergies": ["Penicillin", "Peanuts"],
            "current_conditions": ["Hypertension", "Diabetes Type 2"],
            "medications": ["Metformin 500mg", "Lisinopril 10mg"],
            "emergency_contact": {"name": "Jane Doe", "phone": "555-1234"},
            "preferences": {},
            "created_at": "2025-10-01T00:00:00Z",
            "updated_at": "2025-10-10T14:30:00Z"
        },
        "activity_summary": {
            "total_reminders": 5,
            "active_reminders": 3,
            "total_prescriptions_analyzed": 12,
            "last_activity": "2025-10-10T14:30:00Z"
        }
    }
    
    Processing Flow:
    1. Get authenticated user from JWT token
    2. Retrieve UserProfile from database
    3. Call profile.get_activity_summary() for statistics
    4. Combine user data, profile data, and activity summary
    5. Return complete JSON response
    
    Called by:
    - Flutter UserProfileScreen (on screen open)
    - Flutter MedicalHistoryScreen (loads medical data)
    - Flutter PersonalInfoScreen (loads personal info)
    - ApiService.getUserProfile()
    
    Calls:
    - UserProfile.objects.get() - Get profile from database
    - profile.get_activity_summary() - Calculate statistics
    
    Error Handling:
    - No profile found → Creates empty profile automatically
    - Server error → 500 Internal Server Error
    
    Frontend Integration:
    - Displays user info in UserProfileScreen
    - Loads allergies/medications in MedicalHistoryScreen
    - Shows activity stats in dashboard
    """
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
