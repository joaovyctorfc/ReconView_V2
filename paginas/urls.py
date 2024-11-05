from django.urls import path
from.views import Home, Cadastro, Usuario, Clima, AnaliseVideo, Upload, Video, Perfil, UploadIA, Email, AtualizarSenha, download
from . import views

urlpatterns = [
 path('',Home.as_view(),name='login')  ,

 path('cadastro/',Cadastro.as_view(),name='cadastro'),

 path('home/',Usuario.as_view(),name='principal')   ,

 path('clima/',Clima.as_view(),name='clima'),

 path('analiseVideo/',AnaliseVideo.as_view(),name='analiseIa'),

path('upload/',Upload.as_view(),name='upload'),

path('video/',Video.as_view(),name='video'),

path('perfil/',Perfil.as_view(),name='perfil'),

path('email/',Email.as_view(),name='email'),

path('confirmacao/', Email.as_view(), name='confirmacao'),  

path('uploadIA/',UploadIA.as_view(),name='uploadIA'),

 path('download/', views.download, name='download'),

path('atualizar_senha/',AtualizarSenha.as_view(),name='senha'),

]
