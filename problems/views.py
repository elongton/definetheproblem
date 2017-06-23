from django.shortcuts import render
from django.shortcuts import render,get_object_or_404,redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (View, TemplateView,
                                  CreateView, DetailView,
                                  ListView)
from problems.forms import ProblemForm, CommentForm, ReplyForm
from . import models
from operator import itemgetter, attrgetter

#######################
# CLASS BASED VIEWS
#######################
class IndexView(TemplateView):
    template_name = 'sitewide/index.html'

class ProblemCreateView(CreateView):
    model = models.Problem
    fields = ('text','anonymous_author')
    template_name = 'problems/problem_add.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if self.kwargs['pk'] == '0':
                return super(ProblemCreateView, self).get(request, *args, **kwargs)
            else:
                print('you are posting a super problem')
                return super(ProblemCreateView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse("users:login"))
    def get_context_data(self, **kwargs):
        ctx = super(ProblemCreateView, self).get_context_data(**kwargs)
        if self.kwargs['pk'] != '0':
            problem = get_object_or_404(models.Problem,pk=int(self.kwargs['pk']))
            ctx['problem'] = problem
        ctx['pk'] = self.kwargs['pk']
        return ctx
    # def post(self, request, *args, **kwargs):
    #     if self.kwargs['pk'] == '0':
    def form_valid(self, form):
        form.instance.author = self.request.user
        # print(get_object_or_404(models.Problem,pk=int(self.kwargs['pk'])))
        return super(ProblemCreateView, self).form_valid(form)

class ProblemDetailView(DetailView):
    model = models.Problem
    context_object_name = 'problem'
    template_name = 'problems/problem_detail.html'

class ProblemListView(ListView):
    model = models.Problem
    context_object_name = 'problems'
    template_name = 'problems/problem_list.html'

class IndexProblemListView(ListView):
    model = models.Problem
    context_object_name = 'problems'
    template_name = 'sitewide/index.html'

#######################
# FUNCTION BASED VIEWS
#######################


def index_topsix(request):
    problems = models.Problem.objects.all()
    x = []
    for problem in problems:
        x.append((problem, problem.total_votes()))
    x = sorted(x, key=itemgetter(1), reverse=True)
    if len(x) >=9:
        x = x[:9]
    else:
        pass
    problems=x
    return render(request,'sitewide/index.html',{'problems':problems})


def index_upvote(request,pk):
    upvote_problem(request,pk)
    return redirect('problems:home')
def index_downvote(request,pk):
    downvote_problem(request,pk)
    return redirect('problems:home')
def list_upvote(request,pk):
    upvote_problem(request,pk)
    return redirect('problems:list')
def list_downvote(request,pk):
    downvote_problem(request,pk)
    return redirect('problems:list')
def detail_upvote(request,pk):
    problem = upvote_problem(request,pk)
    return redirect('problems:problem_detail',pk=problem.pk)
def detail_downvote(request,pk):
    problem = downvote_problem(request,pk)
    return redirect('problems:problem_detail',pk=problem.pk)


def upvote_problem(request,pk):
    problem = get_object_or_404(models.Problem,pk=pk)
    user=request.user
    if problem.upvotes.filter(id=user.id).exists():
        problem.upvotes.remove(user)
    elif problem.downvotes.filter(id=user.id).exists():
        problem.downvotes.remove(user)
        problem.upvotes.add(user)
    else:
        problem.upvotes.add(user)
    print(problem.upvotes.all())
    return problem

def downvote_problem(request,pk):
    problem = get_object_or_404(models.Problem,pk=pk)
    user=request.user
    if problem.downvotes.filter(id=user.id).exists():
        problem.downvotes.remove(user)
    elif problem.upvotes.filter(id=user.id).exists():
        problem.upvotes.remove(user)
        problem.downvotes.add(user)
    else:
        problem.downvotes.add(user)
    return problem


@login_required
def like_comment(request,pk):
    comment = get_object_or_404(models.Comment,pk=pk)
    user = request.user
    if comment.likes.filter(id=user.id).exists():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)

    return redirect('problems:problem_detail',pk=comment.problem.pk)

@login_required
def like_reply(request,pk):
    reply = get_object_or_404(models.Reply,pk=pk)
    user = request.user
    if reply.likes.filter(id=user.id).exists():
        reply.likes.remove(user)
    else:
        reply.likes.add(user)
    return redirect('problems:problem_detail',pk=reply.comment.problem.pk)

@login_required
def add_reply_to_reply(request,pk):
    base_reply = get_object_or_404(models.Reply,pk=pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = base_reply.comment
            reply.author = request.user
            reply.save()
            return redirect('problems:problem_detail',pk=reply.comment.problem.pk)
    else:
        form = ReplyForm()
    return render(request,'problems/reply_add.html',{'form':form, 'reply':base_reply})

@login_required
def add_reply_to_comment(request,pk):
    comment = get_object_or_404(models.Comment,pk=pk)
    print(comment.pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('problems:problem_detail',pk=comment.problem.pk)
    else:
        form = ReplyForm()
    return render(request,'problems/reply_add.html',{'form':form, 'comment':comment})

@login_required
def add_comment_to_problem(request,pk):
    problem = get_object_or_404(models.Problem,pk=pk)
    print(problem.pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.problem = problem
            comment.author = request.user
            comment.save()
            return redirect('problems:problem_detail',pk=problem.pk)
    else:
        form = CommentForm()
    return render(request,'problems/comment_add.html',{'form':form, 'problem':problem})
