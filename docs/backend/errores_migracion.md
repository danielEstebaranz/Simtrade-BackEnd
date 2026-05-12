# Errores Encontrados Durante La Migracion

Este documento resume los errores reales que fueron apareciendo mientras se hacia la migracion a Firebase Authentication y como se resolvieron.

## 1. El usuario aparecia en Firestore pero no en Authentication

### Causa

Existian mezclas entre el flujo antiguo y el nuevo:

- algunos registros se estaban guardando en Firestore
- pero no todos estaban entrando en Firebase Authentication

### Solucion

- se reviso el registro del backend
- se hizo que el alta se cree primero en Firebase Authentication
- despues se cree el perfil en Firestore

## 2. El frontend no podia registrarse

### Causa

El frontend seguia enviando:

```json
{
  "username": "...",
  "password": "..."
}
```

pero el backend migrado esperaba `email`, `username` y `password`.

### Solucion

Se anadio compatibilidad temporal en backend para interpretar `username` como email cuando tiene formato de correo.

## 3. El login devolvia solo un mensaje guia y no iniciaba sesion

### Causa

En una fase intermedia, `/auth/login` se dejo como endpoint informativo para una futura migracion completa con token.

### Solucion

Se reemplazo por login real contra Firebase Authentication usando `signInWithPassword`.

## 4. El frontend permitia contrasenas demasiado cortas

### Causa

El formulario Angular validaba a partir de 4 caracteres, pero Firebase Authentication exige al menos 6.

### Solucion

Se actualizo el frontend para exigir 6 caracteres y mostrar un mensaje correcto al usuario.

## 5. No existia configuracion web de Firebase

### Causa

El proyecto Firebase no tenia ninguna Web App creada, por lo que no existia `apiKey` ni configuracion web para autenticacion moderna.

### Solucion

Se creo una Web App de Firebase para SimTrade y se obtuvo su configuracion.

## 6. Seguian existiendo usuarios legacy incompatibles

### Causa

Habia documentos antiguos en Firestore con ids y estructura del sistema anterior:

- `dani`
- `usuario_demo`

### Solucion

Se eliminaron esos documentos y se limpio el perfil valido restante para quitar el campo `password`.

## 7. El backend perdio el endpoint de tendencia usado por el frontend

### Causa

Durante la refactorizacion de la API se simplifico `api_server.py` y desaparecio la ruta `/market/{ticker}/trend`.

### Solucion

Se restauro el endpoint usando `ApiHandler.obtener_tendencia(...)` para que el dashboard siga funcionando.

## 8. La consola no podia iniciar sesion y mostraba "El usuario no existe"

### Causa

Tras limpiar los usuarios legacy e implantar Firebase Authentication en la web, `main.py` seguia usando el flujo antiguo:

- buscaba el usuario por `username` en Firestore
- comparaba un `password` local

Ese modelo ya no era valido porque los perfiles nuevos se guardan por `uid` y ya no almacenan contrasena en Firestore.

### Solucion

Se migro tambien la consola:

- login contra Firebase Authentication con `signInWithPassword`
- registro creando primero el usuario en Authentication
- lectura posterior del perfil en Firestore usando el `uid`

## 9. GitHub detecto una Google API Key en el repositorio

### Causa

Durante la migracion se dejo `FIREBASE_WEB_API_KEY` como valor por defecto hardcodeado en:

- `main.py`
- `api_server.py`

Aunque esa clave se usaba para simplificar la configuracion local, GitHub la detecto correctamente como secreto expuesto.

### Solucion

Se elimino el valor hardcodeado del codigo y se dejo el backend preparado para leer la clave solo desde entorno:

- `FIREBASE_WEB_API_KEY` en `.env`
- o en el sistema de secretos del despliegue
