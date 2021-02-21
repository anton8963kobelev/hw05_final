from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context=context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
        'paginator': paginator,
    }
    return render(request, "group.html", context=context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    user = request.user
    if user.is_authenticated:
        following = Follow.objects.filter(user=user, author=author)
        context = {
            'author': author,
            'page': page,
            'post_list': post_list,
            'paginator': paginator,
            'following': following,
        }
        return render(request, 'profile.html', context=context)
    context = {
        'author': author,
        'page': page,
        'post_list': post_list,
        'paginator': paginator,
    }
    return render(request, 'profile.html', context=context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    post_list = author.posts.all()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'post_list': post_list,
        'comments': comments,
        'form': form,
    }
    return render(request, 'post.html', context=context)


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = (PostForm(request.POST or None, files=request.FILES or None,
            instance=post))
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    context = {
        'form': form,
        'post': post,
        'edit': True,
    }
    return render(request, 'new.html', context=context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow = True
    context = {
        'page': page,
        'follow': follow,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context=context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        following, created = Follow.objects.get_or_create(
            user=user, author=author
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect('profile', username)
