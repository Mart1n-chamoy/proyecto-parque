from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    """Vista raíz de la API con información general"""
    return Response({
        'message': 'Bienvenido a la API de Proyecto-Parque',
        'version': '1.0',
        'endpoints': {
            'clients': '/api/clients/',
            'calls': '/api/calls/',
            'call_batches': '/api/calls/batches/',
            'admin': '/admin/',
        },
        'documentation': 'https://github.com/Mart1n-chamoy/proyecto-parque',
    })
