from django.http import JsonResponse

def error_404(request, exception):
    message = 'The endpoint is not found'
    
    response = JsonResponse(data={'message': message, 'status_code': 404})
    response.status_code =404
    return response

def error_500(request):
    message = 'An error occured. Please try again later'
    
    response = JsonResponse(data={'message': message, 'status_code': 404})
    response.status_code =404
    return response