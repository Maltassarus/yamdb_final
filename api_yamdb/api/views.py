from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .permissions import IsAdminOrSuperuser, IsCanChangeOrReadOnly, ReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleGetSerializer, TitleSerializer, TokenSerializer,
                          UserAdminSerializer, UserSerializer)


class SignUpViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = SignUpSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if self.is_user_not_existing(request):
            serializer.is_valid(raise_exception=True)
        else:
            serializer.is_valid()
        headers = self.get_success_headers(serializer.data)
        response = Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers,
        )
        user, _ = User.objects.get_or_create(**response.data)
        self.send_confirmation_code(user)
        return response

    def send_confirmation_code(self, user):
        subject = 'Confirmation of registration'
        code = default_token_generator.make_token(user)
        message = f'confirmation_code : "{code}"'
        recipient_list = [user.email]
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=recipient_list,
        )

    def is_user_not_existing(self, request):
        return not (
            User.objects
            .filter(username=request.data.get('username', ''))
            .filter(email=request.data.get('email', ''))
            .exists()
        )


@api_view(['post'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )

    if not default_token_generator.check_token(
        user,
        serializer.validated_data['confirmation_code']
    ):
        error_message = 'Неверный confirmation_code'
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    jwt = AccessToken.for_user(user)
    return Response({'token': str(jwt)}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsCanChangeOrReadOnly]

    def get_review(self):
        id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsCanChangeOrReadOnly]

    def get_title(self):
        id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(title=self.get_title(), author=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSuperuser,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer,
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (ReadOnly | IsAdminOrSuperuser,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (ReadOnly | IsAdminOrSuperuser,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer
