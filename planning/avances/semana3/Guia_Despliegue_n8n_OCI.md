Guía de despliegue: Flujo Agente Fauna Vet (n8n) en Oracle Cloud Infrastructure

Instructivo paso a paso para replicar el despliegue en una instancia de OCI, desde la descarga del flujo hasta su publicación con HTTPS.

Proyecto: Reto Tech Builder ONE + Alura

Requisitos previos
Una cuenta de Oracle Cloud Infrastructure (OCI). El nivel gratuito (Always Free) es suficiente.
Un dominio propio, con acceso a su panel de administración DNS (cPanel, Cloudflare o el proveedor que corresponda).
El archivo del flujo exportado (.json), descargado desde el repositorio de GitHub del proyecto.
Un cliente SSH (terminal de Linux/macOS o Windows con OpenSSH/PuTTY).
Cuentas y credenciales de los servicios que consume el flujo:
Cohere para el modelo de IA.
Un bot de Telegram creado con @BotFather.
Paso 1 — Crear la instancia de cómputo en OCI
Inicia sesión en Oracle Cloud Infrastructure y crea una instancia de Compute:

Menú → Compute → Instances → Create Instance.

Elige una imagen Ubuntu (se recomienda Ubuntu 24.04 LTS) y una forma (shape) del nivel gratuito, como VM.Standard.E2.1.Micro o una forma Ampere A1 elegible.
Al crear la instancia, genera o sube un par de llaves SSH. Guarda la llave privada (.key) en un lugar seguro: es necesaria para acceder al servidor.
Anota la IP pública asignada a la instancia. Se utilizará durante toda la configuración.
Paso 2 — Abrir los puertos necesarios en la red de OCI

Nota: En OCI, además de la lista de seguridad, una instancia puede tener asociado un Network Security Group (NSG) a su VNIC. Verifica siempre en Compute → Instancia → VNIC cuál de los dos está realmente conectado a tu instancia. Agregar reglas en el lugar equivocado es un error común y puede dificultar el diagnóstico.

Ve a Networking → Virtual Cloud Networks → tu VCN → Security → Default Security List.
Agrega una regla de entrada (Ingress) para el puerto 22 (SSH), si no existe. Normalmente ya viene configurada.
Agrega una regla de entrada para el puerto 80 (TCP), con origen 0.0.0.0/0. Es necesario para la validación de certificados SSL.
Agrega una regla de entrada para el puerto 443 (TCP), con origen 0.0.0.0/0. Es necesario para el tráfico HTTPS.
Paso 3 — Conectarse por SSH e instalar Docker

Conéctate a la instancia usando la llave privada y la IP pública:

bash
ssh -i /ruta/a/tu-clave.key ubuntu@<IP_PUBLICA_DE_TU_INSTANCIA>


Una vez dentro, instala Docker y Docker Compose:

bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER


Cierra la sesión y vuelve a conectarte por SSH para que el cambio de grupo tome efecto.

Paso 4 — Descargar el flujo desde GitHub
Clona o descarga el repositorio del proyecto desde GitHub. Debe incluir el archivo del flujo de n8n en formato .json.
Si solo necesitas el archivo del flujo, descárgalo directamente y súbelo a tu instancia con scp. Por ejemplo:
bash
scp -i /ruta/a/tu-clave.key Flujo_Agente_Fauna_Vet.json ubuntu@<IP_PUBLICA>:/home/ubuntu/

Paso 5 — Crear la configuración de n8n (docker-compose.yml)

Nota: Configura las variables de entorno correctas desde el inicio, usando el dominio definitivo que vas a utilizar (consulta el paso 6). Esto evita tener que recrear el contenedor más adelante.

Crea una carpeta de trabajo y abre el archivo docker-compose.yml:

bash
mkdir -p /home/ubuntu/n8n && cd /home/ubuntu/n8n
nano docker-compose.yml


Agrega el siguiente contenido:

yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.tudominio.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - N8N_SECURE_COOKIE=true
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.tudominio.com/
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:


Importante: reemplaza n8n.tudominio.com por tu subdominio real en las variables N8N_HOST y WEBHOOK_URL.

Levanta el contenedor:

bash
docker compose up -d

Paso 6 — Crear un subdominio propio para n8n

Telegram exige HTTPS válido (no autofirmado) para registrar un webhook, y los navegadores bloquean por seguridad las llamadas desde una página HTTPS hacia un servidor sin HTTPS.

Por eso, antes de continuar, crea un subdominio dedicado.

Entra al panel DNS de tu dominio (por ejemplo, cPanel → Zone Editor o el panel de tu proveedor).
Agrega un registro tipo A:
Nombre: n8n (o el que prefieras).
Valor: la IP pública de tu instancia OCI.
TTL: 3600.
Espera unos minutos y confirma la propagación desde la terminal de tu instancia:
bash
nslookup n8n.tudominio.com


Sustituye n8n.tudominio.com por el subdominio que hayas configurado.

Paso 7 — Instalar Nginx como proxy reverso

Instala Nginx y Certbot:

bash
sudo apt install -y nginx certbot python3-certbot-nginx


Crea el archivo de configuración /etc/nginx/sites-available/n8n:

bash
sudo nano /etc/nginx/sites-available/n8n


Agrega el siguiente contenido:

nginx
server {
  listen 80;
  server_name n8n.tudominio.com;

  location / {
    proxy_pass http://localhost:5678;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}


Reemplaza n8n.tudominio.com por tu subdominio real.

Activa la configuración y verifica la sintaxis:

bash
sudo ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx


Si nginx -t muestra errores, corrige la configuración antes de continuar.

Paso 8 — Generar el certificado SSL

Ejecuta Certbot para generar el certificado HTTPS:

bash
sudo certbot --nginx -d n8n.tudominio.com


Sigue las instrucciones en pantalla, incluyendo el correo de contacto y la aceptación de los términos.

Al finalizar, Certbot habilita automáticamente HTTPS y configura la renovación automática del certificado.

Nota: el dominio debe resolver a la IP pública de la instancia y el puerto 80 debe ser accesible para completar la validación HTTP.

Paso 9 — Importar el flujo y configurar credenciales
Entra a https://n8n.tudominio.com y crea la cuenta de propietario (correo, nombre y contraseña) la primera vez que accedas.
Ve a Workflows → Import from File y selecciona el archivo Flujo_Agente_Fauna_Vet.json descargado en el paso 4.
Abre cada nodo que use credenciales (modelo de IA, Telegram e integraciones externas) y configura tus propias claves y tokens.

Importante: por seguridad, las credenciales no viajan dentro del archivo .json exportado. Debes configurarlas en tu instancia.

Paso 10 — Activar el Telegram Trigger y publicar
Activa el nodo Telegram Trigger dentro del editor.
Haz clic en Publish. Si todo lo anterior está correctamente configurado (HTTPS válido y dominio propio), el webhook debería registrarse sin errores.
Prueba escribiéndole directamente a tu bot de Telegram para confirmar que responde.
Paso 11 — Conectar el widget de chat en tu página web (opcional)
Abre el nodo When chat message received dentro del flujo y copia su Chat URL (URL de producción del webhook).
Pega esa URL en el fragmento de integración del widget de chat de tu sitio web; por ejemplo, dentro de la propiedad webhookUrl del script embebido.
Prueba la burbuja de chat directamente en tu página web pública para confirmar que la integración funciona de principio a fin.
Checklist final

Antes de dar por terminado el despliegue, verifica los siguientes puntos:

El subdominio resuelve correctamente a la IP de la instancia (nslookup).
Los puertos 80 y 443 están abiertos en la Security List asociada a la subred de la instancia o en el NSG realmente conectado a su VNIC.
El comando docker exec -it <contenedor> env | grep -Ei 'N8N|WEBHOOK' muestra el dominio HTTPS correcto, no la IP ni HTTP.
El editor de n8n carga con el candado de sitio seguro en el navegador.
El Telegram Trigger se publica sin el error HTTPS URL must be provided for webhook.
El widget de chat de la web utiliza la misma URL de dominio HTTPS, no una URL temporal de pruebas.