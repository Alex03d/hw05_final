from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect


from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import external_paginator


def index(request):
    post_list = Post.objects.select_related('group', 'author')

    context = {
        'page_obj': external_paginator(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_comment = author.comments.all()
    user = request.user
    following = Follow.objects.filter(author=author, user=request.user.id)

    context = {
        'author': author,
        'page_obj': external_paginator(request, post_list),
        'comments': posts_comment,
        "following": following,
        'user': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    posts_comment = Comment.objects.select_related('post').filter(post=post_id)

    context = {
        'post_info': post_info,
        'post_id': post_id,
        'form': form,
        'comments': posts_comment,
    }
    return render(request, 'posts/post_detail.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()

    context = {
        'group': group,
        'page_obj': external_paginator(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


@login_required
@csrf_protect
def post_create(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': external_paginator(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
        user=request.user, author=author
    ).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
