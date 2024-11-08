import os
import random
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from ultralytics import YOLO
from .firebase import db
import cv2

firebase_link = 'https://reconview-1410a-default-rtdb.firebaseio.com/' 
codigos_de_confirmacao = {}
def encontrar_usuario_por_email(email, link):
    """Verifica se o usuário existe no Firebase."""
    try:
        response = requests.get(f'{link}/usuarios.json')
        data = response.json()

        for key, user_data in data.items():
            print(f"Verificando usuário: {user_data.get('email')}")  # Depuração
            if user_data.get('email') == email:
                return key  # Retorna a chave (ID) do usuário no Firebase

        return None  # Retorna None se o usuário não for encontrado
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

# Create your views here.

class Home(TemplateView):
    template_name='tela_login.html'
 
class Cadastro(TemplateView):
    template_name = 'tela_cadastro.html'

"""     def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        celular = request.POST.get('celular')
        senha = request.POST.get('senha')

        doc_ref = db.collection('usuarios').document(email)
        doc_ref.set({
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'celular': celular,
            'senha': senha,
        })

        messages.success(request, 'Cadastro realizado com sucesso!') """

class Usuario(TemplateView):
    template_name='tela_principal.html'
class Clima(TemplateView):
    template_name='tempo.html'
class AnaliseVideo(TemplateView):
    template_name='analiseVideo.html'
class Upload(TemplateView):
    template_name='upload.html'    
class Video(TemplateView):
    template_name='Video.html'
class Perfil(TemplateView):
    template_name='tela_perfil.html'
class UploadIA(TemplateView):
    template_name='upload_video_ia.html'
class Email(TemplateView):
    template_name = 'Email.html'

    def post(self, request, *args, **kwargs):
        destinatario = request.POST.get('destinatario')
        lista_provedores = ["hotmail", "gmail", "outlook"]

        # Verifica se o destinatário foi informado
        if not destinatario:
            messages.error(request, 'Por favor, insira um endereço de e-mail.')
            return self.render_to_response({'codigo_enviado': False})

        # Verifica se o e-mail é válido
        elif "@" not in destinatario or destinatario.split("@")[1].split(".")[0] not in lista_provedores:
            messages.error(request, 'Por favor, insira um endereço de e-mail válido.')
            return self.render_to_response({'codigo_enviado': False})

        # Verifica se o e-mail existe no Firebase
        if not self.usuario_existe(destinatario):
            messages.error(request, 'E-mail não encontrado.')
            return self.render_to_response({'codigo_enviado': False})

        # Gera o código de confirmação
        codigo = str(random.randint(1000, 9999))
        codigos_de_confirmacao[destinatario] = codigo

        # Envia o e-mail
        try:
            send_mail(
                'Código de Confirmação',
                f'Seu código de confirmação é: {codigo}',  # Aqui está o código
                'reconview012@gmail.com',  # Seu e-mail
                [destinatario],  # E-mail do destinatário
                fail_silently=False,
            )
            request.session['destinatario'] = destinatario
            print(f"Código enviado: {codigo} para {destinatario}")  # Depuração
            return render(request, 'redefinicao_senha.html', {'destinatario': destinatario, 'codigo_enviado': True})

        except Exception as e:
            print(f"Erro ao enviar o e-mail: {e}")  # Depuração
            messages.error(request, 'Erro ao enviar o código de confirmação.')
            return self.render_to_response({'codigo_enviado': False})

    def usuario_existe(self, email):
        """Verifica se o usuário existe no Firebase."""
        try:
            response = requests.get(f'{firebase_link}/usuarios.json')
            data = response.json()

            for user_data in data.values():
                if user_data.get('email') == email:
                    return True  # O usuário existe

            return False  # O usuário não existe
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return False

class AtualizarSenha(TemplateView):
    template_name = 'redefinicao_senha.html'

    def post(self, request, *args, **kwargs):
        destinatario = request.session.get('destinatario')  # Recupera o destinatário da sessão
        codigo = request.POST.get('codigo')  # Código fornecido pelo usuário
        nova_senha = request.POST.get('novaSenha')  # Nova senha (agora criptografada)
        senha_confirmacao = request.POST.get('senha1')  # Confirmação da nova senha

        # Log para depuração
        print(f"Destinatário: {destinatario}, Código: {codigo}, Nova Senha: {nova_senha}, Senha Confirmação: {senha_confirmacao}")

        # Verifica se o destinatário e o código estão corretos
        codigo_gerado = codigos_de_confirmacao.get(destinatario)  # Obtém o código gerado

        if nova_senha != senha_confirmacao:
            messages.error(request, 'As senhas não coincidem.')  # Mensagem de erro se as senhas não coincidem
            return self.render_to_response({'codigo_enviado': True, 'destinatario': destinatario})

        if codigo != codigo_gerado:
            messages.error(request, 'Código incorreto.')  # Mensagem de erro se o código estiver incorreto
            return self.render_to_response({'codigo_enviado': True, 'destinatario': destinatario})

        # Atualização da senha no Firebase
        try:
            pasta_do_destinatario = encontrar_usuario_por_email(destinatario, firebase_link)

            if pasta_do_destinatario:
                dados = {'senha': nova_senha}  # Dados a serem enviados para o Firebase

                # Atualiza a senha no nó correto do Firebase
                response = requests.patch(f'{firebase_link}/usuarios/{pasta_do_destinatario}/.json', json=dados)

                if response.status_code == 200:  # Verifica se a atualização foi bem-sucedida
                    messages.success(request, 'Senha atualizada com sucesso!')
                    request.session.pop('destinatario', None)  # Limpa a sessão
                else:
                    messages.error(request, 'Erro ao atualizar a senha no Firebase.')

            else:
                messages.error(request, 'Email não encontrado.')
        except Exception as e:
            print(f"Erro ao atualizar a senha: {e}")
            messages.error(request, 'Ocorreu um erro ao atualizar a senha.')

        return self.render_to_response({'codigo_enviado': True, 'destinatario': destinatario})  # Renderiza o template após a tentativa de atualização

class UploadIA(TemplateView):
    template_name = 'upload_video_ia.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Verifique se um arquivo de vídeo foi enviado
        if 'video' not in request.FILES:
            messages.error(request, "Por favor, envie um arquivo de vídeo.")
            return redirect('uploadIA')

        # Salvar o arquivo enviado
        file = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            # Processa o vídeo com a análise de IA
            result_video_path = self.analise_video(file_path)
            messages.success(request, "Análise de vídeo concluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante a análise do vídeo: {e}")
            return redirect('uploadIA')

        # Renderiza o template com o caminho do vídeo resultante
        return render(request, 'analiseVideo.html', {'result_video_path': result_video_path})

    def analise_video(self, video_path):
        # Carrega o modelo YOLO
        model = YOLO("yolov8n.pt")

        # Configurações do vídeo de entrada
        cap = cv2.VideoCapture(video_path)
        output_path = os.path.join(settings.MEDIA_ROOT, 'result.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            results = model(frame)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        # Libera os recursos
        cap.release()
        out.release()
        
        return output_path

def download(request):
    result_video_path = request.POST.get('result_video_path')
    if not result_video_path:
        messages.error(request, "O vídeo analisado não está disponível para download.")
        return redirect('uploadIA')

    file_path = os.path.join(settings.MEDIA_ROOT, result_video_path)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    else:
        messages.error(request, "O arquivo de vídeo não foi encontrado.")
        return redirect('uploadIA')