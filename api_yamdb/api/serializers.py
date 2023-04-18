import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class SignUpBaseSerializer(serializers.ModelSerializer):

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать имя \'me\' в качестве username запрещено.'
            )
        return username


class SignUpSerializer(SignUpBaseSerializer):

    class Meta:
        model = User
        fields = ('email', 'username',)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        write_only=True,
    )
    confirmation_code = serializers.CharField(
        max_length=100,
        write_only=True,
    )


class UserMetaBaseSerializer:
    model = User
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )


class UserAdminSerializer(SignUpBaseSerializer):
    class Meta(UserMetaBaseSerializer):
        pass


class UserSerializer(SignUpBaseSerializer):
    class Meta(UserMetaBaseSerializer):
        read_only_fields = ('role',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    review = serializers.SlugRelatedField(
        slug_field='text',
        many=False,
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate(self, attrs):
        if self.context['request'].method != 'POST':
            return attrs

        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        user = self.context['request'].user

        if Review.objects.filter(
            author=user,
            title_id=title
        ).exists():
            raise serializers.ValidationError(
                'Отзыв уже написан'
            )
        return attrs

    class Meta:
        model = Review
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    description = serializers.CharField(required=False)

    def validate_year(self, value):
        year = datetime.datetime.now().year
        if value > year:
            raise serializers.ValidationError(
                'Год не можеть быть больше текущего'
            )
        if value < 0:
            raise serializers.ValidationError(
                'Год не может быть отрицательным'
            )
        return value

    class Meta:
        model = Title
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating'
        )
