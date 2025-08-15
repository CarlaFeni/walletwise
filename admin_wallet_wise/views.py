from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Movimiento
from django.db.models import Sum, DecimalField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import json
from django.http import JsonResponse

def dashboard(request):
    # Si el usuario no está autenticado, mostrar valores cero
    if not request.user.is_authenticated:
        context = {
            'entradas_total': 0,
            'salidas_total': 0,
            'ahorro_total': 0,
            'inversiones_total': 0,
            'saldo_total': 0
        }
        return render(request, 'dashboard.html', context)

    # Calcular totales solo para el usuario actual
    entradas_total = Movimiento.objects.filter(
        usuario=request.user,
        tipo='entrada'
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    salidas_total = Movimiento.objects.filter(
        usuario=request.user,
        tipo='salida'
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    ahorro_total = Movimiento.objects.filter(
        usuario=request.user,
        tipo='ahorro'
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    inversiones_total = Movimiento.objects.filter(
        usuario=request.user,
        tipo='inversion'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_total = entradas_total - salidas_total

    context = {
        'entradas_total': entradas_total,
        'salidas_total': salidas_total,
        'ahorro_total': ahorro_total,
        'saldo_total': saldo_total,
        'inversiones_total': inversiones_total
    }
    return render(request, 'dashboard.html', context)


@csrf_exempt
def add_movement(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

        try:
            # Obtener datos del formulario
            tipo = request.POST.get('tipo')
            #nombre = request.POST.get('nombre')
            monto_str = request.POST.get('monto')
            fecha = request.POST.get('fecha') or timezone.now().date()

            # Validar y convertir monto a Decimal
            try:
                monto = Decimal(monto_str)
            except (TypeError, InvalidOperation, ValueError):
                raise ValidationError('Monto inválido. Debe ser un número válido.')

            # Mapear tipos del frontend al modelo
            tipo_mapping = {
                'entradas': 'entrada',
                'salidas': 'salida',
                'ahorro': 'ahorro',
                'inversiones': 'inversion'
            }

            tipo_modelo = tipo_mapping.get(tipo)
            if not tipo_modelo:
                raise ValidationError(f'Tipo de movimiento inválido: {tipo}')

            # Crear nuevo movimiento
            movimiento = Movimiento(
                usuario=request.user,
                tipo=tipo_modelo,
                #nombre=nombre,
                monto=monto,
                fecha=fecha
            )
            movimiento.full_clean()
            movimiento.save()

            # Recalcular todos los totales
            entradas_total = Movimiento.objects.filter(
                usuario=request.user,
                tipo='entrada'
            ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0')

            salidas_total = Movimiento.objects.filter(
                usuario=request.user,
                tipo='salida'
            ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0')

            ahorro_total = Movimiento.objects.filter(
                usuario=request.user,
                tipo='ahorro'
            ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0')

            inversiones_total = Movimiento.objects.filter(
                usuario=request.user,
                tipo='inversion'
            ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0')

            saldo_total = entradas_total - salidas_total

            return JsonResponse({
                'success': True,
                'message': 'Movimiento registrado correctamente',
                'new_values': {
                    'entradas': float(entradas_total),
                    'salidas': float(salidas_total),
                    'ahorro': float(ahorro_total),
                    'inversiones': float(inversiones_total),
                    'saldo_total': float(saldo_total)
                }
            })
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error: {str(e)}'
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


def register_view(request):
    if request.method == 'POST':
        # Obtener datos como JSON si es posible
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
        except:
            data = request.POST

        try:
            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validaciones básicas
            if not all([username, email, password1, password2]):
                return JsonResponse({
                    'success': False,
                    'error': 'Todos los campos son obligatorios'
                }, status=400)

            if password1 != password2:
                return JsonResponse({
                    'success': False,
                    'error': 'Las contraseñas no coinciden'
                }, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre de usuario ya existe'
                }, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El correo electrónico ya está registrado'
                }, status=400)

            # Crear usuario
            user = User.objects.create_user(username, email, password1)

            # Autenticar e iniciar sesión
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': '/dashboard/'  # Usar URL directa
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Error al iniciar sesión automáticamente'
                }, status=500)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)

# Vista de login tradicional
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')


def get_movements(request):
    if not request.user.is_authenticated:
        return JsonResponse({'movimientos': []}, status=401)

    filter_type = request.GET.get('filter', 'all')

    # Filtrar movimientos del usuario actual
    if filter_type == 'all':
        movements = Movimiento.objects.filter(
            usuario=request.user
        ).order_by('-fecha')
    else:
        movements = Movimiento.objects.filter(
            usuario=request.user,
            tipo=filter_type
        ).order_by('-fecha')

    # Serializar los datos
    movimientos_data = []
    for mov in movements:
        movimientos_data.append({
            'fecha': mov.fecha.isoformat(),
            'nombre': mov.nombre,
            'tipo': mov.tipo,
            'monto': str(mov.monto)  # Convertir a string para serialización
        })

    return JsonResponse({'movimientos': movimientos_data})