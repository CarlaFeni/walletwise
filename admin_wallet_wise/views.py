from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_POST

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
    # Si es GET, mostrar el formulario
    if request.method == 'GET':
        return render(request, 'register.html')

    # Si es POST, procesar los datos
    if request.method == 'POST':
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            if is_ajax:
                # Intentar cargar JSON si el content-type es application/json
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                else:
                    data = request.POST
            else:
                data = request.POST

            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validaciones básicas
            if not all([username, email, password1, password2]):
                error_msg = 'Todos los campos son obligatorios'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                else:
                    # Si no es AJAX, renderizamos de nuevo el formulario con el error
                    return render(request, 'register.html', {'error': error_msg})

            if password1 != password2:
                error_msg = 'Las contraseñas no coinciden'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                else:
                    return render(request, 'register.html', {'error': error_msg})

            if User.objects.filter(username=username).exists():
                error_msg = 'El nombre de usuario ya existe'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                else:
                    return render(request, 'register.html', {'error': error_msg})

            if User.objects.filter(email=email).exists():
                error_msg = 'El correo electrónico ya está registrado'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                else:
                    return render(request, 'register.html', {'error': error_msg})

            # Crear usuario
            user = User.objects.create_user(username, email, password1)

            # Autenticar e iniciar sesión
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
                if is_ajax:
                    dashboard_url = reverse('dashboard')
                    return JsonResponse({'success': True, 'redirect': dashboard_url})
                else:
                    return redirect('dashboard')
            else:
                error_msg = 'Error al iniciar sesión automáticamente'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=500)
                else:
                    return render(request, 'register.html', {'error': error_msg})

        except Exception as e:
            error_msg = f'Error interno: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=500)
            else:
                return render(request, 'register.html', {'error': error_msg})

    # Si no es GET ni POST, devolver error método no permitido
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
    filtro = request.GET.get('filter', 'all')
    user = request.user

    movimientos = Movimiento.objects.filter(usuario=user)

    # Mapear filtros frontend a tipos del modelo
    filter_mapping = {
        'entradas': 'entrada',
        'salidas': 'salida',
        'inversiones': 'inversion'
    }

    if filtro != 'all':
        tipo_filtro = filter_mapping.get(filtro, filtro)
        movimientos = movimientos.filter(tipo=tipo_filtro)

    data = {
        "movimientos": [
            {
                "id": m.id,
                "fecha": m.fecha.isoformat(),
                "tipo": m.get_tipo_display(),
                "monto": float(m.monto),
            }
            for m in movimientos.order_by('-fecha')
        ]
    }
    return JsonResponse(data)
def calcular_total(tipo, user=None):
    """
    Calcula el total de un tipo de movimiento específico para el usuario.
    tipos válidos: 'entradas', 'salidas', 'ahorro', 'inversiones'
    """
    if user is None:
        return 0

    tipo_mapping = {
        "entradas": "entrada",
        "salidas": "salida",
        "ahorro": "ahorro",
        "inversiones": "inversion",
    }

    tipo_modelo = tipo_mapping.get(tipo)
    if not tipo_modelo:
        return 0

    total = Movimiento.objects.filter(
        usuario=user,
        tipo=tipo_modelo
    ).aggregate(Sum("monto"))["monto__sum"] or Decimal("0")

    return float(total)


def calcular_saldo_total(user=None):
    """
    Calcula el saldo total = entradas - salidas para el usuario.
    """
    if user is None:
        return 0

    entradas = calcular_total("entradas", user)
    salidas = calcular_total("salidas", user)

    return float(entradas - salidas)

@csrf_exempt
def delete_movement(request, movement_id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Usuario no autenticado"}, status=401)

        try:
            mov = Movimiento.objects.get(id=movement_id, usuario=request.user)
            mov.delete()

            # Recalcular totales después de borrar SOLO para el usuario actual
            new_values = {
                "saldo_total": calcular_saldo_total(request.user),
                "entradas": calcular_total("entradas", request.user),
                "salidas": calcular_total("salidas", request.user),
                "ahorro": calcular_total("ahorro", request.user),
                "inversiones": calcular_total("inversiones", request.user),
            }

            return JsonResponse({"success": True, "new_values": new_values})
        except Movimiento.DoesNotExist:
            return JsonResponse({"success": False, "error": "Movimiento no encontrado"}, status=404)

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
