# gasotrack
GasoTrack: Tu guía en la búsqueda de combustible (gasolina) en Venezuela.



# GasoTrack - Rama de Desarrollo (dev)

Esta es la rama de desarrollo de GasoTrack, donde se están implementando nuevas funcionalidades y mejoras.

## Estado Actual

* **Endpoints Básicos Implementados:**
    * `GET /estaciones`: Obtiene una lista de todas las estaciones de servicio.
    * `GET /estaciones/<estacion_id>`: Obtiene información detallada de una estación específica.
    * `POST /reportes`: Permite a los usuarios enviar reportes sobre la disponibilidad de combustible.
    * `GET /estadisticas`: Proporciona estadísticas generales sobre la disponibilidad de combustible.

* **Extracción de Datos desde OpenStreetMap:** Se está utilizando la API de Overpass para obtener datos de estaciones de servicio desde OpenStreetMap.

## Próximos Pasos

* **Mejorar la extracción de datos:** Manejar errores, automatizar la actualización de datos.
* **Agregar más funcionalidades a la API:** Endpoints para reportes más específicos, estadísticas avanzadas, autenticación de usuarios (opcional).
* **Desarrollar el frontend:** Crear una aplicación web o móvil con React Native para interactuar con la API.
* **Desplegar la aplicación:** Alojar el backend y el frontend en servidores o servicios en la nube.

## Cómo Contribuir

¡Tu contribución es bienvenida! Si deseas colaborar con el desarrollo de GasoTrack, puedes:

* **Ayudar a implementar nuevas funcionalidades.**
* **Corregir errores y mejorar el código existente.**
* **Probar la aplicación y reportar problemas.**

Consulta la sección de Contribuciones en este repositorio para obtener más detalles sobre cómo puedes participar.

## ¡Únete al Desarrollo de GasoTrack!

Si tienes habilidades en Python, Flask, React Native o cualquier otra área relacionada, ¡te invitamos a unirte al desarrollo de GasoTrack! Juntos podemos hacer una diferencia.