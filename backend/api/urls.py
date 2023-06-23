from django.urls import path
from .views import users,boards,teams,boj,db,problems

app_name = "api"
urlpatterns = [
    # users
    path('join/', users.join, name="join"),
    path('login/', users.LoginView.as_view(), name="login"),
    path('users/<int:pk>/rival/', users.handle_rival, name="handle_rival"),
    path('verify/', users.verify_token, name="verify_token"),

    # boards
    path('boards/create/', boards.create_board, name="create_board"),
    path('boards/list/', boards.list_board, name="list_board"),
    path('boards/<int:pk>/', boards.detail_board, name="detail_board"),
    path('boards/<int:pk>/delete/', boards.delete_board, name="delete_board"),
    path('boards/<int:pk>/update/', boards.update_board, name="update_board"),
    path('boards/<int:pk>/like/', boards.like_board, name="like_board"),
    path('boards/<int:pk>/comments/create/', boards.create_comment, name="create_comment"),
    path('boards/<int:pk>/comments/<int:comment_pk>/', boards.delete_comment, name="delete_comment"),

    # teams
    path('team/create/', teams.create_team, name="create_team"),
    path('team/<int:pk>/', teams.detail_team, name="detail_team"),
    path('team/<int:pk>/workbook/create/', teams.create_workbook, name="create_workbook"),
    path('workbook/tag/', teams.problem_tag, name="problem_tag"),
    path('team/<int:pk>/workbook/list/', teams.list_workbook, name="list_workbook"),
    path('team/myteam/', teams.list_my_team, name="list_my_team"),
    path('team/list/', teams.list_team, name="list_team"),
    path('team/<int:pk>/users/', teams.user_accept_invitation, name="user_accept_invitation"),
    path('team/<int:pk>/users/list/', teams.list_user, name="team_list_user"),
    path('team/<int:pk>/req/list/', teams.list_req, name="team_list_user"),
    path('team/<int:team_pk>/users/<int:user_pk>/', teams.team_accept_request, name="team_accept_request"),
    path('team/<int:team_pk>/invite/', teams.invite, name="invite"),
    path('team/req/', teams.req, name="request"),
    path('team/<int:team_pk>/award/',teams.award_list,name="award_list"),
    path('team/<int:team_pk>/achievement/', teams.achievement_award_list, name="achievement_award_list"),
    path('users/invite/list/', teams.list_invite, name="list_invite"),


    # problems
    path('problems/hint/', problems.hint, name="problems_hint"),


    #boj
    path('boj/verify/',boj.verify, name="verify_boj"),


    # db
    path('db/problems/', db.create_problem_db, name="create_problem_db"),
    path('db/users/', db.create_boj_info, name="create_boj_info"),

]
