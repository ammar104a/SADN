#views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from .discord_notify import send_discord_notification


def index(request):
    """Example index page view."""
    return render(request, 'index.html')

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect


from django.shortcuts import render, get_object_or_404
from .models import Company


def login_view(request):
    """Logs a user in, or shows the login template."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user with Django's built-in auth
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If valid, log user in
            login(request, user)

            # Mark user as checked in
            user.userprofile.checked_in = True
            user.userprofile.save()
            profile = user.userprofile
            profile.session_start = timezone.now()
            profile.save()
            current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            send_discord_notification(f"{user.username} logged in at {current_time}!")


            # Redirect to dialer page
            return redirect('dialer_view')
        else:
            # If invalid credentials, add error message
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')
    else:
        # GET request: show login page
        return render(request, 'login.html')

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def logout_view(request):
    profile = request.user.userprofile
    if profile.session_start:
        delta = timezone.now() - profile.session_start
        # Convert to total seconds
        seconds = int(delta.total_seconds())

        # Add to the user's total_work_seconds
        profile.increment_work_time(seconds)
        # Include date/time in your notification
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        send_discord_notification(f"{request.user.username} just logged out at {current_time}!")
        # Reset session_start
        profile.session_start = None
        profile.save()

    logout(request)
    return redirect('login')  # or wherever you'd like to send them


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Company

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company


@login_required
def dialer_view(request, company_id=None):
    user = request.user
    profile = user.userprofile

    if company_id:
        company = get_object_or_404(Company, id=company_id)
        profile.daily_progress += 1
        profile.last_company = company
        profile.save()
    else:
        if profile.last_company:
            company = profile.last_company
        else:
            company = Company.objects.first()

    # Add this section to handle phone number formatting
    phone_number = company.phone_number.strip() if company.phone_number else None
    tel_url = f"tel:{phone_number}" if phone_number else None

    difference = request.user.userprofile.total_calls - request.user.userprofile.yesterday_calls
    next_company = Company.objects.filter(id__gt=company.id).order_by('id').first()
    prev_company = Company.objects.filter(id__lt=company.id).order_by('-id').first()

    profile = request.user.userprofile
    initial_work_seconds = profile.total_work_seconds

    session_elapsed_seconds = 0
    if profile.session_start:
        delta = timezone.now() - profile.session_start
        session_elapsed_seconds = int(delta.total_seconds())

    context = {
        'user': user,
        'profile': profile,
        'company': company,
        'next_company': next_company,
        'prev_company': prev_company,
        'difference': difference,
        'initial_work_seconds': initial_work_seconds,
        'session_elapsed_seconds': session_elapsed_seconds,
        'tel_url': tel_url  # Add tel_url to the context
    }
    return render(request, 'dialer.html', context)

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import date


@login_required
def checkin_toggle(request):
    profile = request.user.userprofile

    # 1. Possibly reset daily stats if a new day
    profile.check_and_reset_daily_stats()

    if not profile.checked_in:
        # Currently checked out -> Check in
        profile.checked_in = True
        profile.last_checkin_time = timezone.now()
    else:
        # Currently checked in -> Check out
        if profile.last_checkin_time:
            time_diff = timezone.now() - profile.last_checkin_time
            hours_diff = time_diff.total_seconds() / 3600.0
            # 2. Add to total_hours
            profile.total_hours += hours_diff

        # Reset checkin time
        profile.checked_in = False
        profile.last_checkin_time = None

    profile.save()
    return redirect('dialer_view')


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CallOutcome, Company

@login_required
def record_call_outcome(request, company_id):
    user = request.user
    profile = user.userprofile
    company = get_object_or_404(Company, id=company_id)

    outcome_type = request.GET.get('outcome', None)
    if outcome_type not in ['MEETING_SCHEDULED', 'CALLBACK', 'NOT_AVAILABLE']:
        # If invalid outcome, redirect back
        return redirect('dialer_view', company_id=company.id)

    # Create the CallOutcome
    call_outcome = CallOutcome.objects.create(
        company=company,
        user=user,
        outcome_type=outcome_type,
        created_at=timezone.now()
    )
    #call_outcome.save()  # triggers your custom .save() logic
    if outcome_type == 'MEETING_SCHEDULED':
        from main.discord_notify import send_discord_notification
        send_discord_notification(
            f"{request.user.username} scheduled a meeting with {company.name}!"
        )
    # Find the "next" company
    next_company = Company.objects.filter(id__gt=company_id).order_by('id').first()
    if next_company:
        # The user is moving on -> increment daily progress
        profile.daily_progress += 1
        profile.last_company = next_company
        profile.save()
        return redirect('dialer_view', company_id=next_company.id)
    else:
        # No more companies left in the list
        # Optionally set last_company to None so next login restarts at the beginning
        profile.last_company = None
        profile.save()
        return redirect('dialer_view')  # goes to the default or 'last_company'


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company, CompanyComment


@login_required
def add_company_comment(request, company_id):
    """Handle submission of a new comment for a company."""
    if request.method == 'POST':
        company = get_object_or_404(Company, id=company_id)
        comment_text = request.POST.get('comment', '').strip()

        if comment_text:
            CompanyComment.objects.create(
                company=company,
                user=request.user,
                comment=comment_text
            )

        # After saving, redirect back to the same dialer/company view
        return redirect('dialer_view', company_id=company_id)

    # If someone hits this URL via GET, redirect them back
    return redirect('dialer_view', company_id=company_id)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def start_call(request, company_id):
    """Handle call initiation and send Discord notification"""
    company = get_object_or_404(Company, id=company_id)
    user = request.user

    # Format phone number and create tel URL
    phone_number = company.phone_number.strip() if company.phone_number else None
    tel_url = f"tel:{phone_number}" if phone_number else None

    if phone_number:
        # Send Discord notification
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        send_discord_notification(
            f"📞 {user.username} started a call with {company.name} at {current_time}!"
        )

        return JsonResponse({
            'status': 'success',
            'tel_url': tel_url
        })

    return JsonResponse({
        'status': 'error',
        'message': 'No phone number available'
    })


# views.py
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def llama_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Make request to Ollamas
            response = requests.post('http://localhost:11434/api/chat',
                                     json={
                                         "model": "llama3.2",
                                         "messages": [{"role": "user", "content": user_message}],
                                         "stream": False
                                     })

            if response.status_code != 200:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error communicating with LLM'
                }, status=500)

            # Parse the Ollama response
            llm_data = response.json()

            # Return a properly formatted response
            return JsonResponse({
                'status': 'success',
                'message': llm_data['message']['content']
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON in request'
            }, status=400)

        except requests.exceptions.ConnectionError:
            return JsonResponse({
                'status': 'error',
                'message': 'Could not connect to Ollama. Make sure it is running.'
            }, status=503)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)