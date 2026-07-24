# Guía de la Aplicación Móvil (Envoltura Híbrida)

Esta carpeta contiene la configuración para compilar y ejecutar el **Sistema de Reportes de Acapulco** como una aplicación móvil nativa para Android y iOS utilizando **Capacitor**.

La aplicación funciona como un WebView nativo de alto rendimiento que carga el sitio web directamente de tu servidor Django. Esto significa que cualquier cambio visual, de plantilla o de base de datos que realices en el servidor web Django se reflejará inmediatamente en la app móvil sin necesidad de subir actualizaciones a las tiendas.

---

## Estructura del Proyecto

- `capacitor.config.json`: Archivo de configuración donde se define el identificador de la app, el nombre y la dirección del servidor Django.
- `android/`: Proyecto nativo para **Android Studio**.
- `www/`: Carpeta con un archivo HTML temporal que se carga como splash screen mientras se conecta al servidor.

---

## Configuración de la Dirección del Servidor

En el archivo `capacitor.config.json` encontrarás la clave `server.url`:

```json
  "server": {
    "url": "https://renesalas.com",
    "cleartext": true
  }
```

### 1. Producción (Google Play / App Store)
Por defecto, la aplicación móvil está configurada para conectarse a tu dominio de producción: **`https://renesalas.com`**.
Esto significa que si compilas y descargas la app en tu teléfono, cargará de forma automática e inmediata la versión en vivo de tu plataforma.

### 2. Pruebas Locales (Emulador de Android)
Si estás corriendo el servidor de Django localmente con `python manage.py runserver` y quieres que la aplicación en el emulador de Android apunte a tu servidor local de pruebas en lugar del servidor en producción:
1. Cambia `"url"` en `capacitor.config.json` por `"http://10.0.2.2:8000"`.
2. Sincroniza el proyecto ejecutando: `npx cap sync`.

### 3. Pruebas Locales (Celular Físico)
Si quieres probar la app en tu propio celular físico apuntando a tu servidor local de pruebas (ambos dispositivos conectados al mismo Wi-Fi):
1. Averigua la dirección IP local de tu computadora (por ejemplo, `192.168.1.15`).
2. Cambia `"url"` en `capacitor.config.json` a `http://192.168.1.15:8000`.
3. Sincroniza el proyecto ejecutando:
   ```bash
   npx cap sync
   ```


---

## Cómo abrir y compilar en Android Studio

### Requisitos previos
- Tener instalado [Android Studio](https://developer.android.com/studio).
- Tener instalado el SDK de Android (se descarga automáticamente al iniciar Android Studio).

### Pasos para ejecutar la App:

1. **Abrir el proyecto en Android Studio**:
   Puedes abrir Android Studio y seleccionar la carpeta `reportes_movil/android`.
   O también puedes abrirlo automáticamente desde la consola ejecutando el siguiente comando dentro de esta carpeta:
   ```bash
   npx cap open android
   ```

2. **Compilar y Descargar en un Dispositivo**:
   - En Android Studio, espera a que termine la sincronización de Gradle (barra de carga al fondo).
   - Conecta tu celular físico con la "Depuración USB" activada, o bien crea un Emulador Virtual (AVD).
   - Haz clic en el botón verde de **Run (Ejecutar)** `▶` en la barra superior.
   - ¡La aplicación se instalará y se abrirá en tu teléfono automáticamente!

---

## Cómo abrir y compilar en iOS (iPhone)

### Requisitos previos
- **Sistema operativo macOS**: La compilación de aplicaciones iOS requiere obligatoriamente una computadora Mac (Xcode es exclusivo de macOS).
- Tener instalado **Xcode** (disponible de forma gratuita en la Mac App Store).
- Disponer de un **Apple ID** (incluso una cuenta gratuita sirve para hacer pruebas de desarrollo personal).
- Tener instalado [CocoaPods](https://cocoapods.org/) en la Mac (`sudo gem install cocoapods`).

### Pasos para ejecutar en tu iPhone:

1. **Sincronizar el proyecto**:
   Ejecuta en la consola para asegurar que Xcode tenga todos los archivos más recientes:
   ```bash
   npx cap sync ios
   ```

2. **Abrir el proyecto en Xcode**:
   Ejecuta desde la terminal de tu Mac dentro de la carpeta `reportes_movil` para abrir el espacio de trabajo en Xcode automáticamente:
   ```bash
   npx cap open ios
   ```

3. **Configurar Firma del Desarrollador (Signing)**:
   - En la barra lateral izquierda de Xcode, haz clic sobre el proyecto raíz (`App`).
   - Ve a la pestaña **Signing & Capabilities**.
   - Activa la casilla **Automatically manage signing**.
   - En **Team**, selecciona tu Apple ID (si no está, ve a *Xcode > Settings > Accounts* en el menú superior de la Mac y agrégala).
   - Xcode configurará automáticamente el perfil de aprovisionamiento de desarrollo personal.

4. **Conectar tu iPhone y Ejecutar**:
   - Conecta tu iPhone mediante cable USB a tu Mac.
   - En tu iPhone, si es la primera vez, asegúrate de activar el **Modo Desarrollador** en: *Ajustes > Privacidad y seguridad > Modo de desarrollador* (reinicia el teléfono si te lo solicita).
   - En la parte superior de Xcode, junto al botón de Play `▶`, selecciona tu iPhone físico de la lista de dispositivos.
   - Presiona el botón **Play (Build and Run)** `▶`.
   - La aplicación se compilará y se instalará en tu iPhone.

---

## Comandos Útiles

Si realizas cambios en el archivo de configuración `capacitor.config.json` o agregas plugins nuevos:
```bash
npx cap sync
```
Este comando copia los activos web y sincroniza de forma global tanto la carpeta de Android como la de iOS automáticamente.
