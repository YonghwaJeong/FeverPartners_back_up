from django import forms
from apps.free_board.models import Post, Comment

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'notice']  # 'notice' 필드 추가
        labels = {
            'title': '제목',
            'content': '내용',
            'notice': '공지글로 설정하기',
        }



class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ['content']
    labels = {
      'content': '답변 내용',
    }