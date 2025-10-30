# 📦 Stock Management System

Sistema de gestión de inventario y ventas desarrollado con Flask, diseñado para la administración completa de productos, compras, ventas y reportes.

## 🎯 Características principales

- **Autenticación y autorización**: Sistema de login con roles de usuario (USER y ADMIN)
- **Gestión de productos**: CRUD completo con control de stock
- **Compras**: Registro de compras con actualización automática de stock
- **Ventas**: Registro de ventas con validación de stock disponible
- **Reportes**: Dashboards con métricas de ventas y productos más vendidos
- **Seguridad**: Protección CSRF, hashing de contraseñas, y sesiones seguras
- **Correo electrónico**: Recuperación de contraseña vía email

## 🏗️ Arquitectura

El proyecto está estructurado en módulos siguiendo el patrón de Blueprints de Flask:

```
flaskr/
├── __init__.py          # Factory de la aplicación Flask
├── auth.py              # Autenticación (login, registro, logout)
├── db.py                # Gestión de base de datos
├── security.py          # Decoradores de seguridad
├── schema.sql           # Esquema de base de datos
├── users/               # Gestión de usuarios
├── stock/               # Gestión de productos
├── sales/               # Gestión de ventas
├── shopping/            # Gestión de compras
├── reports/             # Reportes y estadísticas
└── templates/           # Plantillas HTML
```

## 📋 Requisitos previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd stock-project
```

2. **Crear un entorno virtual**:
```bash
python -m venv .venv

# En Windows:
.venv\Scripts\activate

# En Linux/Mac:
source .venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -e .
```

4. **Configurar variables de entorno**:

Crear un archivo `.env` en la raíz del proyecto basado en `.env_example`:

```env
SECRET_KEY=tu-clave-secreta-segura-aqui
SECURITY_PASSWORD_SALT=tu-sal-de-seguridad-aqui
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password-de-gmail
```

**Nota**: Para `MAIL_PASSWORD`, necesitas generar una [contraseña de aplicación de Gmail](https://support.google.com/accounts/answer/185833).

5. **Inicializar la base de datos**:
```bash
flask --app flaskr init-db
```

6. **Ejecutar la aplicación**:
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 👤 Usuario por defecto

Al inicializar la base de datos, se crea automáticamente un usuario administrador:

- **Usuario**: admin
- **Contraseña**: (ver archivo de inicialización)

## 🔐 Roles de usuario

### USER (Usuario regular)
- Consultar productos y stock
- Registrar ventas
- Ver sus propias ventas y compras

### ADMIN (Administrador)
- Todas las funcionalidades de USER
- Gestionar productos (crear, editar, eliminar)
- Gestionar usuarios
- Ver todas las ventas y compras
- Acceder a reportes y estadísticas
- Registrar compras para actualizar stock

## 🗄️ Estructura de la base de datos

### Tablas principales

- **user**: Usuarios del sistema
- **product**: Productos del inventario
- **shopping**: Compras realizadas
- **sales**: Ventas realizadas

### Triggers automáticos

- **Actualización de stock**: Al registrar compras, el stock se incrementa automáticamente
- **Reducción de stock**: Al registrar ventas, el stock se reduce automáticamente
- **Restauración de stock**: Al eliminar una venta, el stock se restaura
- **Timestamps**: Actualización automática de campos `updated_at` y `created_at`

## 🧪 Testing

Ejecutar tests con pytest:

```bash
pytest
```

Con cobertura de código:

```bash
pytest --cov=flaskr
```

## 📦 Despliegue

### Build del proyecto

```bash
pip install flit
flit build
```

El paquete se generará en `dist/flaskr-1.0.0-py2.py3-none-any.whl`

### Producción

Para producción, configurar:

1. `SESSION_COOKIE_SECURE = True` (requiere HTTPS)
2. Variables de entorno seguras
3. Configurar servidor WSGI (por ejemplo, Gunicorn)

## 🛠️ Tecnologías utilizadas

- **Flask 2.3+**: Framework web
- **Flask-WTF**: Formularios y protección CSRF
- **Flask-Mail**: Envío de correos electrónicos
- **SQLite**: Base de datos
- **Werkzeug**: Utilidades de seguridad
- **python-dotenv**: Gestión de variables de entorno

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado como proyecto educativo en Python/Flask.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚠️ Notas importantes

- **Seguridad**: Nunca comitas el archivo `.env` con credenciales reales
- **Base de datos**: El archivo `flaskr.sqlite` se crea automáticamente en `instance/`
- **Sesiones**: La sesión por defecto dura 7 días
- **CSRF**: Los tokens CSRF expiran después de 2 horas

## 📞 Soporte

Para reportar bugs o sugerencias, por favor abre un issue en el repositorio.

