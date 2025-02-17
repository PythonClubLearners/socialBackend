import json
import typing

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpRequest, RawPostDataException
from django.views.decorators.csrf import ensure_csrf_cookie as ensure_csrf_cookie_base
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from api.models import Post
from users.models import User, UserFriend


def ensure_csrf_cookie(view):

    @ensure_csrf_cookie_base
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        response.set_cookie('csrftokenlocal', request.META['CSRF_COOKIE'], domain="localhost")
        return response

    return wrapper

def get_request_data(request: HttpRequest) -> dict:
    try:
        data = request.data  # json.loads(request.body)
    except (json.decoder.JSONDecodeError, RawPostDataException):
        data = dict(request.GET or request.POST)
    return data


error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title='Ошибка',
    required=['message'],
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, title='Текст ошибки')
    }
)

success_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title='Успех',
    required=['message'],
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, title='Текст успеха')
    }
)


@swagger_auto_schema(
    operation_summary='Получение всех постов',
    operation_description='Получение коллекции всех постов',
    methods=['GET'],
    responses={
        200: Post.collection_schema
    },
)
@api_view(['GET'])
@ensure_csrf_cookie
def get_all_posts_view(request):
    return JsonResponse({
        'posts': tuple(map(lambda x: x.json, Post.objects.all()))
    })


@swagger_auto_schema(
    operation_summary='Получение поста',
    operation_description='Получение общей информации о посте',
    methods=['GET'],
    responses={
        200: Post.schema,
        404: error_schema
    },
)
@api_view(['GET'])
@ensure_csrf_cookie
def get_post_view(request, post_id):
    try:
        post: Post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Пост не найден'}, status=404)
    return JsonResponse(post.json)


@swagger_auto_schema(
    operation_summary='Получение постов пользователя',
    operation_description='Получение коллекции всех постов от определенного пользователя с user_id',
    methods=['GET'],
    responses={
        200: Post.collection_schema
    },
)
@api_view(['GET'])
@ensure_csrf_cookie
def get_user_posts_view(request, user_id):
    posts = Post.objects.filter(author__id=user_id).all()

    return JsonResponse({
        'posts': tuple(map(lambda x: x.json, posts))
    })


@swagger_auto_schema(
    operation_summary='Создание поста',
    operation_description='Попытка создать публикацию. Пользователь должен быть авторизован. Описание и изображения '
                          'могут быть пустыми',
    methods=['POST'],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Успешно созданный пост',
            required=['message', 'post_id'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Пост создан'),
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, title='id нового поста'),
            }
        ),
        400: error_schema,
        403: error_schema,
        404: error_schema,
        500: error_schema,
    },
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['title'],
        # format=openapi.,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, title='Заголовок'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='Текст поста'),
            'image': openapi.Schema(type=openapi.TYPE_FILE, title='Изображение')
        }
    )
)
@api_view(['POST'])
@ensure_csrf_cookie
def create_post_view(request):
    try:

        user: User = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': 'Пользователь не авторизован'}, status=403)

        data = get_request_data(request)
        title = data.get('title', None)
        description = data.get('description', '')
        image = request.FILES.get('image', None)

        if not title:
            return JsonResponse({'error': 'Заголовок не может быть пустым'}, status=400)

        post = Post(title=title, description=description, image=image, author=user)

        try:
            post.full_clean()
        except ValidationError as e:
            return JsonResponse({'error': e.message_dict}, status=400)

        post.save()

        return JsonResponse({'message': 'Пост создан', 'post_id': post.id}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@swagger_auto_schema(
    operation_summary='Получение пользователя',
    operation_description='Получение общих данных страницы пользователя',
    methods=['GET'],
    responses={
        200: User.schema,
        404: error_schema
    },
)
@api_view(['GET'])
@ensure_csrf_cookie
def get_user_view(request, user_id):
    try:
        user: User = User.objects.get(id=user_id)

        return JsonResponse(user.json)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)


@swagger_auto_schema(
    operation_summary='Получение текущего пользователя',
    operation_description='Получение общих данных страницы текущего пользователя',
    methods=['GET'],
    responses={
        200: User.schema,
        403: error_schema
    },
)
@api_view(['GET'])
@ensure_csrf_cookie
def get_user_self_view(request):
    user: User = request.user

    if user.is_anonymous:
        return JsonResponse({'error': 'Пользователь не авторизован'}, status=403)

    return JsonResponse(user.json)


@swagger_auto_schema(
    operation_summary='Вход по логину и паролю',
    operation_description='Эндпоинт для входа пользователя по логину и паролю. Данные могут быть переданы в формате '
                          'JSON. При успехе - сервер привязывает пользователя к cookie csrf_token, он отправляется при любом '
                          'запросе, потому вам необходимо его сохранять.',
    methods=['POST'],
    responses={
        200: success_schema,
        400: error_schema,
        404: error_schema,
    },
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, title='Логин пользователя'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, title='Пароль пользователя')
        }
    )
)
@api_view(['POST'])
@ensure_csrf_cookie
def user_login_view(request):
    data = get_request_data(request)

    username: typing.Union[str, None] = data.get('username', None)
    password = data.get('password', None)

    if username is None or password is None:
        return JsonResponse({'error': 'Не указан логин или пароль'}, status=400)

    user = authenticate(request, username=username.lower(), password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Вход подтвержден"})
    else:
        return JsonResponse({'error': 'Пароль или логин не верны'}, status=401)


@swagger_auto_schema(
    operation_summary='Выход из системы',
    operation_description='Отвязывает csrf-токен пользователя от системы',
    methods=['POST'],
    responses={
        200: success_schema,
    }
)
@api_view(['POST'])
@ensure_csrf_cookie
def user_logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Выход выполнен'})


@swagger_auto_schema(
    operation_summary='Получение количества друзей пользователя',
    operation_description='Возвращает объект с количеством друзей',
    methods=['GET'],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Информация о пользователе',
            properties={
                "friendCount": openapi.Schema(type=openapi.TYPE_INTEGER, title='Количество друзей')
            }
        ),
        404: error_schema,
    }
)
@api_view(['GET'])
@ensure_csrf_cookie
def user_friend_count_view(request, user_id):
    try:
        user: User = User.objects.get(id=user_id)

        return JsonResponse({"friendCount": user.friends.count()})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)


@swagger_auto_schema(
    operation_summary='Получение списка друзей пользователя',
    operation_description='Возвращает коллекцию id друзей пользователя',
    methods=['GET'],
    responses={
        200: User.friends_ids_schema,
        404: error_schema,
    }
)
@api_view(['GET'])
@ensure_csrf_cookie
def user_friends_view(request, user_id):
    try:
        user: User = User.objects.get(id=user_id)

        return JsonResponse(User.friends_ids(user.friends.all()))
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)


@swagger_auto_schema(
    operation_summary='Получение списка полученных заявок в друзья пользователя',
    operation_description='Возвращает коллекцию id пользователей которые прислали заявку для дружбы текущему '
                          'пользователю',
    methods=['GET'],
    responses={
        200: User.friends_ids_schema,
        403: error_schema,
        404: error_schema,
    }
)
@api_view(['GET'])
@ensure_csrf_cookie
def user_friends_requests_view(request):
    user: User = request.user

    if user.is_anonymous:
        return JsonResponse({'error': 'Пользователь не авторизован'}, status=403)

    return JsonResponse(User.friends_ids(user.friend_requests.all()))


@swagger_auto_schema(
    operation_summary='Получение списка отправленных заявок в друзья пользователя',
    operation_description='Возвращает коллекцию id пользователей которым были отправлены заявки для дружбы от '
                          'текущего пользователя',
    methods=['GET'],
    responses={
        200: User.friends_ids_schema,
        403: error_schema,
    }
)
@api_view(['GET'])
@ensure_csrf_cookie
def user_friends_requests_send_view(request):
    user: User = request.user

    if user.is_anonymous:
        return JsonResponse({'error': 'Пользователь не авторизован'}, status=403)

    return JsonResponse(User.friends_ids(user.friend_requests_send.all()))


def get_users_pair(request, data):
    current_user: User = request.user
    if current_user.is_anonymous:
        return False, JsonResponse({'error': 'Пользователь не авторизован'}, status=403)
    user_id = data.get('user_id', None)
    if not user_id:
        return False, JsonResponse({'error': 'Не указан id пользователя'}, status=400)

    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False, JsonResponse({'error': 'Пользователь не найден'}, status=404)

    if other_user.id == current_user.id:
        return False, JsonResponse({'error': 'Другой вопрос. Зачем? ЗАЧЕМ? Для чего добавлять себя в друзья? '
                                             'Поддержка тульпы? Не делайте этого, вам того не надо.'
                                    }, status=418)

    return True, (current_user, other_user)


@swagger_auto_schema(
    operation_summary='Отправка запроса в друзья',
    operation_description='Отправляет запрос в друзья от текущего пользователю указанному user_id. Текущий '
                          'пользователь должен быть авторизован',
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, title='id пользователя')
        }
    ),
    responses={
        200: success_schema,
        400: error_schema,
        403: error_schema,
        404: error_schema,
        500: error_schema,
    }
)
@api_view(['POST'])
@ensure_csrf_cookie
def make_friend_view(request):
    try:
        data = get_request_data(request)
        success, result = get_users_pair(request, data)
        if not success:
            return result
        user, friend = result

        UserFriend.objects.create(user=user, friend=friend)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'message': 'Запрос отправлен'})


@swagger_auto_schema(
    operation_summary='Принятие запроса в друзья',
    operation_description='Принимает запрос в друзья текущему пользователю от указанного user_id. Текущий '
                          'пользователь должен быть авторизован',
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, title='id пользователя')
        }
    ),
    responses={
        200: success_schema,
        400: error_schema,
        403: error_schema,
        404: error_schema,
        500: error_schema,
    }
)
@api_view(['POST'])
@ensure_csrf_cookie
def accept_friend_view(request):
    try:
        data = get_request_data(request)
        success, result = get_users_pair(request, data)
        if not success:
            return result
        friend, user = result

        try:
            user_friend = UserFriend.objects.get(user=user, friend=friend, is_friend=False)
        except UserFriend.DoesNotExist:
            return JsonResponse({'error': 'Запрос не найден'}, status=404)
        user_friend.is_friend = True
        user_friend.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'message': 'Запрос принят'})
