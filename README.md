# Wallet Wise

## 💰 Resumen Financiero Personal

Wallet Wise es una aplicación web diseñada para ayudarte a gestionar tus finanzas personales de manera simple y visual. Permite registrar entradas y salidas de dinero, gestionar ahorros e inversiones, y consultar un resumen de tus movimientos de manera interactiva.

---

## 🛠 Tecnologías usadas

- **Backend:** Python, Django  
- **Base de datos:** PostgreSQL  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap (para componentes y estilos rápidos)
- **Otras herramientas:** **Django Templates** para renderizado del frontend. **Fetch API** para la comunicación asíncrona con el backend.

---

## 🚀 Funcionalidades principales

- Registro y autenticación de usuarios.
- Añadir, editar y eliminar movimientos financieros: entradas, salidas, ahorro e inversiones. 
- Visualización de resúmenes financieros en tarjetas dinámicas.
- Filtrado de movimientos por tipo: entradas, salidas, ahorro e inversiones. 
- Interfaz responsive y moderna con Bootstrap.
- Notificaciones dinámicas para confirmaciones y errores.


## 📦 Instalación

1. Clona el repositorio:
  git clone https://github.com/tu-usuario/walletwise.git
  cd walletwise
2. Crea un entorno virtual e instala dependencias:
  python -m venv venv
  source venv/bin/activate  # Linux / macOS
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
3. Configura la base de datos PostgreSQL y actualiza settings.py con tus credenciales.
4. Aplica migraciones:
  python manage.py makemigrations
  python manage.py migrate
5. Crea un superusuario (opcional):
  python manage.py createsuperuser
6. Ejecuta el servidor de desarrollo:
  python manage.py runserver
  -  Abre tu navegador y navega a http://127.0.0.1:8000/.

## 📂 Estructura del proyecto
walletwise/
├── admin_wallet_wise/      # Aplicación principal
│   ├── migrations/         # Migraciones de la base de datos
│   ├── templates/          # Plantillas HTML
│   ├── static/             # Archivos CSS e imágenes
│   ├── models.py           # Modelos de la base de datos
│   ├── views.py            # Vistas y lógica del backend
│   └── urls.py             # Rutas de la aplicación
├── walletwise/             # Configuración principal de Django
├── manage.py
└── requirements.txt

## 🎨 Diseño y UX
  - Uso de Bootstrap 5 para componentes modernos y responsivos.
  - Tarjetas de resumen financiero con gradientes y animaciones suaves.
  - Modal para agregar movimientos, con validación de campos.
  - Tabla dinámica de movimientos con filtros y botones de acción.

## 📌 Próximas mejoras
  - Exportar movimientos a CSV o PDF.
  - Estadísticas y gráficos de evolución financiera.
  - Autenticación social (Google, Facebook).
