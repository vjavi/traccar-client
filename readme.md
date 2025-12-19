# Traccar Client

Cliente web para Traccar con chat de IA integrado.

## 🚀 Deploy en Railway

### Paso 1: Subir a GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/traccar-client.git
git push -u origin main
```

### Paso 2: Crear proyecto en Railway

1. Ve a [railway.app](https://railway.app) y crea una cuenta
2. Click en **"New Project"** → **"Deploy from GitHub repo"**
3. Conecta tu repositorio de GitHub

### Paso 3: Deploy del Backend

1. En Railway, click **"New Service"** → **"GitHub Repo"**
2. Selecciona la carpeta `backend`
3. Configura las variables de entorno:
   - `OPENAI_API_KEY`: Tu API key de OpenAI
4. Railway detectará el Dockerfile y desplegará automáticamente
5. Copia la URL generada (ej: `https://traccar-backend-xxx.railway.app`)

### Paso 4: Deploy del Frontend

1. Click **"New Service"** → **"GitHub Repo"** de nuevo
2. Selecciona la carpeta `frontend`
3. Configura la variable de entorno de build:
   - `VITE_API_URL`: `https://tu-backend-url.railway.app/api`
4. Railway desplegará el frontend

### Paso 5: Configurar CORS (si es necesario)

Si tienes problemas de CORS, actualiza `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend-url.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 💻 Desarrollo Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu OPENAI_API_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📱 Características

- ✅ Visualización de dispositivos GPS en mapa
- ✅ Historial de rutas y viajes
- ✅ Eventos y alertas
- ✅ Chat con IA para análisis de vehículo
- ✅ Interfaz responsive (móvil y desktop)
- ✅ Datos OBD-II integrados

## 🔧 Tecnologías

- **Frontend**: Vue 3, Vite, Tailwind CSS, Leaflet
- **Backend**: Python, FastAPI, OpenAI API
- **Traccar**: API REST para datos GPS
