# Introducción a los contenedores

Un **contenedor** empaqueta una aplicación junto con sus dependencias para que se
ejecute igual en cualquier entorno. A diferencia de una máquina virtual, los
contenedores comparten el kernel del sistema operativo anfitrión, por lo que son
más ligeros y arrancan en segundos.

## Imágenes y contenedores

Una **imagen** es una plantilla inmutable construida por capas. Un contenedor es
una instancia en ejecución de una imagen. Las imágenes se describen en un
`Dockerfile` y se almacenan en un registro, como Docker Hub u OCI Registry.

## Redes y volúmenes

Cada contenedor recibe una interfaz de red virtual. Para comunicar contenedores se
crean redes definidas por el usuario. Los datos que deben sobrevivir al contenedor
se guardan en **volúmenes**, que viven fuera de su sistema de archivos efímero.

## Orquestación

Cuando hay decenas de contenedores se usa un orquestador como Kubernetes, que
programa los contenedores en un clúster, reinicia los que fallan y escala la
aplicación según la demanda.
