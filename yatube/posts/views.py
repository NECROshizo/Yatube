from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import call_paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    """Представление главной страницы"""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    page_obj = call_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Представление всех постов выбранной группы"""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_group = group.posts.select_related('author')
    page_obj = call_paginator(request, posts_group)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Представление странници пользователя"""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_user = author.posts.select_related('group')
    page_obj = call_paginator(request, posts_user)
    following = (
        request.user.is_authenticated
        and author.following.filter(author=request.user).exists()
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Представление полной информации о записе"""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comment.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Представление формы создания записи"""
    template = 'posts/create_post.html'
    redirect_template = 'posts:profile'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(redirect_template, request.user)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Представление формы редактирования поста"""
    template = 'posts/create_post.html'
    redirect_template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(redirect_template, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect(redirect_template, post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Представление формы добавления коментария"""
    redirect_template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(redirect_template, post_id)


@login_required
def follow_index(request):
    """Представление личной ленты автора"""
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    page_obj = call_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Потписаться на автора"""
    redirect_template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(redirect_template, username)


@login_required
def profile_unfollow(request, username):
    redirect_template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect(redirect_template, username)
