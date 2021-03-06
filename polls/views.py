"""Views for KU-Polls."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
import logging.config
from .settings import LOGGING
from django.http import HttpResponseRedirect
from .models import Question, Choice, Vote
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.dispatch import receiver


class IndexView(generic.ListView):
    """Class for index view."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions (not including those set to be."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class ResultsView(generic.DetailView):
    """Class for results view."""

    model = Question
    template_name = 'polls/results.html'


def detail(request, question_id):
    """Details to view."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


# For logging options
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('polls')


@login_required
def vote(request, question_id):
    """Vote view."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        if not (question.can_vote()):
            messages.warning(request, "This polls are not allowed. ")
        elif Vote.objects.filter(user=request.user, question=question).exists():
            this_votes = Vote.objects.get(user=request.user, question=question)
            this_votes.choice = selected_choice
            this_votes.save()
        else:
            question.vote_set.create(choice=selected_choice, user=request.user)
        logger.info(
            f'User {request.user.username} voted for question id number {question.id} from {get_client_ip(request)}')
        messages.success(request, "Vote successful, thank you for voting. ")
        request.session['choice'] = selected_choice.id
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def get_client_ip(request):
    """Return client ip address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """Log the detail of user and ip address when user logged in."""
    logger.info(f'User {user.username} logged in from {get_client_ip(request)}')


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    """Log the detail of user and ip address when user logged out."""
    logger.info(f'User {user.username} logged out from {get_client_ip(request)}')


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    """Log the detail of user and ip address when users are failed to login."""
    logger.warning(f'User {request.POST["username"]} login failed from {get_client_ip(request)}')
