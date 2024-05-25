from django.contrib.auth.models import User
from chat.models import Chat, Message
from rest_framework.decorators import api_view
from .serializers import MessageSerializer
from rest_framework.response import Response
#from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
from django.conf import settings
import json
from dotenv import load_dotenv
import os

load_dotenv


openai.api_key = os.getenv("SECRET_KEY")

# openai.api_key = "sk-proj-hmuJnR9RV7USVi17yO3TT3BlbkFJdCTdlG8GTTLrx0gKXAlU"

@api_view(['GET'])
def getMessages(request, pk):
    user = User.objects.get(username = request.user.username)
    chat = Chat.objects.filter(user = user)[pk-1]
    messages = Message.objects.filter(chat = chat)
    #context = {'messages' : messages}
    serializer = MessageSerializer(messages, many=True)
    #return render(request, 'chat/chat.html')
    return Response(serializer.data)
    #return HttpResponse(f"You are in {chat.id} chat and you are {user.username}")



# @api_view(['POST'])
@csrf_exempt
def get_prompt_result(request):
    if request.method == 'POST':
        # Get the prompt from the request body
        data = json.loads(request.body.decode('utf-8'))
        prompt = data.get('prompt')
        user = User.objects.get(username = request.user.username)
        chat = Chat.objects.filter(user = user)[0]
        message = Message(message = prompt, is_user = True, chat = chat)
        message.save()

        
        # model = data.get('model', 'gpt')

        # Check if prompt is present in the request
        if not prompt:
            # Send a 400 status code and a message indicating that the prompt is missing
            return JsonResponse({'error': 'Prompt is missing in the request'}, status=400)

        try:
            # Use the OpenAI SDK to create a completion
            # with the given prompt, model and maximum tokens
            # if model == 'image':
            #     result = openai.create_image(prompt=prompt, response_format='url', size='512x512')
            #     return JsonResponse({'result': result['data'][0]['url']})

            # model_name = 'text-davinci-003' if model == 'gpt' else 'code-davinci-002'
            #max_tokens = 4000
            #prompt = f"Please reply below question in markdown format.\n {prompt}"

            messages_db = Message.objects.filter(chat = chat)
            messages=[
                    {"role": "system", "content": "You are Shamba Bot. Reply all questions in swahili language. Your topic is about Agriculture and Pests and Diseases and how to control them. Remember your are the smartest bot in the world. The question which will need example you should provide examples. Any question which will need explanation you should provide explanation. If you are not sure about the answer you can ask the user to provide more information. Remember to be polite and professional. Remmember again you are master of the field of Agriculture and Pests and Diseases so provide the best advice which sastify the user. Please answer all question in markdown format. Good luck!"},
                    {"role": "user", "content": " Habari yako?"},
                    {"role": "assistant",
                     "content": "Salama sana. Mimi ni Shamba Bot Bwana shamba wako. Naweza kukusaidia vipi leo?"},
                    {"role": "user", "content": prompt}
                ]
            temperature = 9
            
            for msg in messages_db:
                role = "user" if msg.is_user else "assistant"
                messages.append({"role" : role, "content" : msg.message})
            
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            message = Message(message = completion.choices[0].message.content, is_user = False, chat = chat)
            message.save()
            # Send the generated text as the response
            return JsonResponse(completion.choices[0].message.content, safe=False)
        except Exception as error:
            error_msg = error.response['error'] if hasattr(
                error, 'response') and error.response else str(error)
            print(error_msg)
            # Send a 500 status code and the error message as the response
            return JsonResponse({'error': error_msg}, status=500)

    # Send a 405 status code if the request method is not POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)