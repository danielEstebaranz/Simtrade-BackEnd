# Migracion a Firebase Authentication

Este documento resume el estado final de la migracion.

## Antes

El proyecto hacia autenticacion casera:

- guardaba password en Firestore en formato hash
- iniciaba sesion comparando hash en backend
- identificaba usuarios por `username`

## Ahora

El proyecto usa Firebase Authentication para identidad:

- registro en Firebase Authentication
- login en Firebase Authentication
- `ID token` y `refreshToken` emitidos por Firebase
- consola y API alineadas con el mismo sistema de autenticacion
- Firestore reservado para perfil, cartera, saldo e historial

## Guardado final

### En Firebase Authentication

Se guarda:

- email
- password
- `uid`
- `displayName`

### En Firestore

Se guarda:

- `usuarios/{uid}`
- datos de negocio del usuario
- sin password

## Compatibilidad resuelta

El frontend tenia un formulario con un solo campo llamado `username`. Para no bloquear el trabajo:

- si el contenido tiene formato de email, el backend lo usa como email real
- el login sigue funcionando con ese campo
- visualmente el frontend ya se ha ajustado para indicar que ese campo es `Email`

En consola ocurria algo parecido pero con un problema distinto:

- la interfaz seguia pidiendo `Usuario`
- el sistema real ya necesitaba un email para Firebase Authentication

Por eso se mantuvo el texto sencillo en consola, pero internamente se obliga a que el valor tenga formato de email y se usa ese email para autenticar.

## Limpieza aplicada

Se han eliminado los documentos incompatibles legacy de Firestore:

- `dani`
- `usuario_demo`

Tambien se ha limpiado el perfil valido para quitar el campo `password` que solo existia como compatibilidad temporal.

## Estado final de seguridad

- el backend ya no autentica contra Firestore
- la consola ya no autentica contra Firestore
- el password ya no vive en Firestore
- la identidad real esta en Firebase Authentication
- Firestore queda desacoplado de la autenticacion

## Siguiente paso ideal

Aunque la migracion backend ya esta cerrada, lo mas limpio a medio plazo seria que el frontend consuma y use siempre el `idToken` devuelto por login para todas las rutas protegidas del backend.
