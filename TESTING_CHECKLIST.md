# 🧪 Sistema de Monitoreo de Precios - Lista de Pruebas

## ✅ **1. Frontend Angular - Verificación Web**

### **🌐 Sitio Web:**
- **URL**: http://anthonygt-scrappers.com.mx/
- **Verificar**: 
  - [ ] Página carga correctamente
  - [ ] No errores en consola del navegador
  - [ ] Interfaz Angular se muestra
  - [ ] Material Design funciona

### **📱 Responsive Design:**
- [ ] Funciona en desktop
- [ ] Funciona en móvil
- [ ] Navegación funciona

---

## ✅ **2. Base de Datos MySQL - Verificación**

### **🔗 Conexión a Base de Datos:**
```bash
# Verificar conexión local
cd infra
docker-compose up -d
```

### **📊 Verificar Tablas:**
- [ ] Tabla `products` existe
- [ ] Tabla `prices` existe  
- [ ] Tabla `deals` existe
- [ ] Tabla `users` existe

---

## ✅ **3. API FastAPI - Verificación**

### **🚀 Iniciar API Local:**
```bash
cd api
pip install -r requirements.txt
python main.py
```

### **🔍 Endpoints a Probar:**
- [ ] `GET /health` - Estado del sistema
- [ ] `GET /api/deals` - Lista de ofertas
- [ ] `POST /api/auth/login` - Autenticación
- [ ] `GET /api/ai/analyze-deal` - Análisis IA

### **📋 Crear Usuario Admin:**
```bash
cd api
python scripts/create_admin.py
```

---

## ✅ **4. Scrapers - Verificación**

### **🕷️ Probar Scrapers Individuales:**
```bash
cd scraper
pip install -r requirements.txt
python run-all.py
```

### **📊 Verificar:**
- [ ] Scrapers se ejecutan sin errores
- [ ] Datos se guardan en base de datos
- [ ] Análisis de IA funciona
- [ ] Notificaciones de Telegram se envían

---

## ✅ **5. Telegram Bot - Verificación**

### **🤖 Probar Bot:**
- [ ] Bot responde a comandos
- [ ] Notificaciones llegan correctamente
- [ ] Formato de mensajes es correcto
- [ ] Rate limiting funciona

### **📱 Comandos de Prueba:**
- Envía `/start` al bot
- Verifica que responda
- Prueba notificaciones de ofertas

---

## ✅ **6. GitHub Actions - Verificación**

### **🔄 Workflows:**
- [ ] `Deploy to Hostinger` - Ejecutado exitosamente
- [ ] `Run Scrapers` - Programado para cada 2 horas
- [ ] Logs sin errores
- [ ] Deployment automático funciona

### **📊 Monitoreo:**
- Ve a: https://github.com/AnthonyGTH/anthonygt-scrapper/actions
- Verifica que los workflows se ejecuten
- Revisa logs de errores

---

## ✅ **7. Sistema Completo - Prueba End-to-End**

### **🎯 Flujo Completo:**
1. [ ] Scraper ejecuta automáticamente
2. [ ] Datos se guardan en MySQL
3. [ ] IA analiza ofertas
4. [ ] Notificaciones se envían a Telegram
5. [ ] Frontend muestra datos
6. [ ] Usuario puede hacer login
7. [ ] Dashboard funciona correctamente

---

## 🚨 **Problemas Comunes y Soluciones**

### **❌ Frontend no carga:**
- Verificar que archivos estén en `/domains/anthonygt-scrappers.com.mx/public_html/`
- Revisar `.htaccess` para routing de Angular

### **❌ API no responde:**
- Verificar que FastAPI esté corriendo
- Revisar conexión a base de datos
- Verificar variables de entorno

### **❌ Scrapers fallan:**
- Verificar dependencias instaladas
- Revisar configuración de productos
- Verificar conexión a base de datos

### **❌ Telegram no funciona:**
- Verificar bot token
- Verificar chat ID
- Revisar rate limiting

---

## 📋 **Checklist Final**

- [ ] **Frontend**: http://anthonygt-scrappers.com.mx/ funciona
- [ ] **API**: Endpoints responden correctamente
- [ ] **Base de Datos**: Conexión y tablas funcionan
- [ ] **Scrapers**: Se ejecutan y guardan datos
- [ ] **IA**: Análisis funciona correctamente
- [ ] **Telegram**: Notificaciones se envían
- [ ] **GitHub Actions**: Workflows ejecutan automáticamente
- [ ] **Sistema Completo**: End-to-end funciona

## 🎉 **¡Sistema Listo para Producción!**

Una vez completadas todas las pruebas, el sistema estará completamente operativo y funcionando 24/7.

