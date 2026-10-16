# Guía de arquitectura cloud para equipos de desarrollo

Esta guía resume los conceptos fundamentales para diseñar, desplegar y operar aplicaciones en la nube. Está pensada para equipos que pasan de un servidor tradicional a una plataforma gestionada y necesitan un vocabulario común antes de tomar decisiones de arquitectura.

## Contenedores y aislamiento

Un contenedor empaqueta una aplicación junto con sus librerías y su configuración, de modo que se ejecuta igual en el portátil de un desarrollador y en producción. A diferencia de una máquina virtual, el contenedor comparte el kernel del sistema operativo anfitrión, por lo que arranca en segundos y consume menos memoria. Las imágenes se construyen por capas a partir de un Dockerfile y se publican en un registro. Cada vez que cambia el código se reconstruye únicamente la capa afectada, lo que acelera los ciclos de entrega y reduce el tamaño de las descargas.

## Redes y balanceo de carga

Los servicios de una aplicación distribuida se comunican mediante redes virtuales. Cada subred define un rango de direcciones IP y reglas de enrutamiento. Un balanceador de carga reparte las peticiones entre varias instancias del mismo servicio para evitar que una sola se sature y para tolerar fallos: si una instancia deja de responder, el balanceador deja de enviarle tráfico. Los grupos de seguridad actúan como cortafuegos virtuales y permiten abrir solo los puertos necesarios, por ejemplo el 443 para tráfico cifrado hacia el exterior.

## Almacenamiento de objetos y bases de datos

El almacenamiento de objetos guarda archivos de cualquier tamaño dentro de cubos o buckets, identificados por un nombre único y accesibles mediante una API HTTP. Es barato, duradero y adecuado para copias de seguridad, imágenes y documentos. Las bases de datos relacionales ofrecen transacciones y consultas SQL, mientras que las bases documentales escalan mejor con datos poco estructurados. Elegir una u otra depende del patrón de acceso: lecturas frecuentes con relaciones complejas favorecen el modelo relacional.

## Seguridad e identidad

La seguridad en la nube sigue el principio de mínimo privilegio: cada persona y cada servicio recibe únicamente los permisos que necesita. Las credenciales nunca se escriben en el código ni en el repositorio; se guardan en un gestor de secretos y se rotan periódicamente. La autenticación multifactor reduce el riesgo de accesos no autorizados. Además, los datos se cifran tanto en tránsito, con TLS, como en reposo, con claves administradas por el proveedor o por el propio equipo.

## Observabilidad y operación

Operar un sistema distribuido exige ver lo que ocurre dentro de él. La observabilidad se apoya en tres señales: registros de eventos, métricas numéricas como la latencia o la tasa de errores, y trazas que siguen una petición a través de varios servicios. Con alertas bien definidas el equipo detecta incidentes antes que los usuarios. Tras cada incidente conviene redactar un análisis posterior sin culpables que identifique las causas y las acciones de mejora.

## Entrega continua y automatización

La entrega continua automatiza la compilación, las pruebas y el despliegue de cada cambio. Un pipeline típico ejecuta el análisis estático, las pruebas unitarias y de integración, construye la imagen y la despliega primero en un entorno de pruebas. Los despliegues graduales, como el canario, exponen la nueva versión a un pequeño porcentaje de usuarios y permiten volver atrás con rapidez si aparecen errores. La infraestructura como código describe los recursos en archivos versionados, lo que hace los entornos reproducibles.

## Costos y elasticidad

La nube permite pagar únicamente por lo que se usa, pero eso exige disciplina. El escalado automático añade instancias cuando sube la demanda y las retira cuando baja, lo que evita sobredimensionar la infraestructura. Etiquetar los recursos por equipo y por proyecto facilita atribuir gastos, y los presupuestos con alertas avisan antes de superar el límite mensual. Apagar los entornos de pruebas fuera del horario laboral es una de las medidas de ahorro más sencillas.
