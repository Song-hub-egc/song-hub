# Documento del Proyecto

**Proyecto:** SongHub  
**Curso:** 2025/2026  
**Equipo:** Grupo 1 
**Miembros:** 
- del Castillo Piñero, Daniel  
- Gómez Vela, Miguel Ángel 
- Manzanos Anento, Diego  
- Pérez Gaspar, Pablo  
- Petre, Rares Nicolae  
- Villalba Fernández, Jesús   
**Repositorio:** https://github.com/Song-hub-egc/song-hub.git
**Última edición:** 10/12/2025

## Indicadores del proyecto
Incluye enlaces a evidencias (gráficas de git, test, issues, CI, etc.).

| Miembro               | Horas | Commits | LoC | Test | Issues | Work Item principal       | Dificultad |
|-----------------------|------:|--------:|----:|-----:|-------:|---------------------------|-----------:|
| del Castillo Piñero, Daniel     |  HH   |   XX    | YY  |  ZZ  |  II    | Breve descripción         | H/M/L      |
| Gómez Vela, Miguel Ángel     |  HH   |   XX    | YY  |  ZZ  |  II    | Breve descripción         | H/M/L      |
| Manzanos Anento, Diego     |  HH   |   XX    | YY  |  ZZ  |  II    | Breve descripción         | H/M/L      |
| Pérez Gaspar, Pablo      |  HH   |   XX    | YY  |  ZZ  |  II    | Breve descripción         | H/M/L      |
| Petre, Rares Nicolae    |  HH   |   XX    | YY  |  ZZ  |  II    | Breve descripción         | H/M/L      |
| Villalba Fernández, Jesús     |  72   |   33    | 2436  |    |  18    | Breve descripción         | H |
| **TOTAL**             | tHH   |  tXX    | tYY | tZZ  | tII    | Resumen WI                | H(X)/M(Y)/L(Z) |

- **Horas:** esfuerzo estimado/registrado por persona. 
- **Commits:** realizados por el equipo durante el proyecto.  
- **LoC:** líneas netas aportadas por el equipo (sin terceros).  
- **Test:** pruebas nuevas añadidas.  
- **Issues:** issues gestionadas por el equipo.  
- **Work Item:** responsabilidad principal de cada miembro.  
- **Dificultad:** alta/media/baja; en totales indicar cuántas de cada tipo.

## Integración con otros equipos

    No ha habido integración con otros equipos.

## Resumen ejecutivo 

El presente documento describe el proceso de refactorización y mejora del sistema UVLHUB, transformándolo en Song-Hub. El objetivo principal ha sido potenciar su rendimiento, seguridad y facilidad de uso, evolucionando de un repositorio genérico de feature models a un entorno especializado en la gestión y distribución de datasets musicales.
Durante el desarrollo, se ha trabajado en la mejora de la estructura interna del sistema, la incorporación de nuevas funcionalidades y la adopción de metodologías más eficientes de trabajo colaborativo.

### Evolución y Cambios en el Proyecto

A lo largo del desarrollo de Song-Hub, se han aplicado múltiples mejoras tanto funcionales como técnicas que han transformado significativamente la plataforma original. Las principales novedades implementadas incluyen:

### Autenticación en Dos Factores (2FA)
Se añadió un sistema de doble verificación mediante el envío de códigos de seguridad por correo electrónico. Esta implementación refuerza sustancialmente la seguridad de las cuentas de usuario y reduce drásticamente los riesgos de acceso no autorizado.

### Datasets Populares
Se implementó un sistema completo de análisis y métricas que identifica y muestra los datasets más descargados y vistos.

### Sistema de Carrito de Descargas
Una innovación fundamental ha sido la implementación de un sistema de carrito que permite a los usuarios seleccionar múltiples datasets antes de proceder a la descarga. 


### Optimización de la Base de Datos y Scripts Automáticos
Se automatizó completamente la gestión del ciclo de vida de la base de datos mediante scripts especializados que facilitan tareas como la recreación de bases de datos, la ejecución de migraciones, el poblamiento con datos de prueba (seeders) y la inicialización de entornos de desarrollo. Estos scripts, ubicados en el directorio `scripts/`, incluyen herramientas para la gestión de contenedores Docker, renovación de certificados SSL y sincronización con repositorios Git, reduciendo significativamente el tiempo de configuración y minimizando errores humanos en el proceso de despliegue.

### Infraestructura y Despliegue
Se modernizó completamente la arquitectura de despliegue mediante la implementación de múltiples estrategias. Se configuraron entornos diferenciados (desarrollo, staging, producción) utilizando Render como plataforma PaaS, se dockerizó toda la aplicación con diferentes configuraciones (desarrollo, producción, SSL, webhooks), y se estableció un pipeline de CI/CD robusto mediante GitHub Actions que garantiza la calidad del código y automatiza los procesos de testing y despliegue.

### Refactorización Visual y Temática Musical
Más allá de la funcionalidad, se realizó una transformación completa de la identidad visual de la plataforma. Se diseñó e implementó una guía de estilo coherente que integra elementos visuales relacionados con el mundo de la música, desde la paleta de colores hasta la tipografía y la disposición de los elementos de interfaz. Esta refactorización no solo mejora la estética, sino que crea una experiencia de usuario más intuitiva y emocionalmente conectada con el dominio de aplicación.

Estas mejoras colectivas han transformado UVLHUB en una plataforma moderna, segura y orientada a la comunidad, específicamente diseñada para satisfacer las necesidades del ecosistema de investigación y creación musical.


### Personalización y Refactorización Visual

El primer nivel de intervención se centró en la experiencia de usuario (UX). El sistema original carecía de una identidad temática definida. Para Song-Hub, se ha implementado una nueva guía de estilo que alinea la paleta de colores, la tipografía y la disposición de los elementos (layout) con la estética del mundo musical. Esta transformación visual no es meramente decorativa, sino que busca crear una conexión emocional con investigadores, productores, compositores y aficionados a la música, facilitando una navegación intuitiva y coherente a lo largo de toda la plataforma.

### Sistema de Carrito de Datasets

Una de las innovaciones funcionales más destacadas respecto al proyecto base es la implementación del **Sistema de Carrito de Datasets**. Inspirado en los patrones de diseño del comercio electrónico (e-commerce), esta funcionalidad elimina la necesidad de realizar descargas unitarias y repetitivas. El sistema permite ahora la selección múltiple de recursos mediante el almacenamiento en sesión (session storage) de las referencias a los datasets seleccionados. El usuario puede navegar por distintas categorías musicales, añadir archivos a su "carrito" virtual y, finalmente, proceder a una gestión unificada de la descarga. Esta optimización del flujo de trabajo permite al investigador o aficionado obtener todo el material necesario en una única operación, reduciendo significativamente el tiempo de interacción y optimizando el uso del ancho de banda.

### Métricas de Popularidad e Interacción Comunitaria

Para transformar un repositorio estático en una comunidad dinámica y activa, se han integrado varios **Módulos de Interacción**. La característica central aquí es el sistema de comentarios, desarrollado como un sistema CRUD completo (Create, Read, Update, Delete) que permite a los usuarios registrados iniciar hilos de discusión en cada dataset. Esta funcionalidad añade una capa de valor cualitativo a los datos: los usuarios pueden advertir sobre erratas en los archivos, sugerir mejoras metodológicas, compartir análisis derivados o simplemente recomendar aplicaciones prácticas de los datos.

Paralelamente, se ha introducido un **motor de análisis de tendencias** que incorpora contadores internos para registrar eventos de visualización y descarga en tiempo real. Estos datos alimentan la sección de "Datasets de Moda" (Trending), un algoritmo de ordenamiento que destaca en la página principal aquellos recursos que están recibiendo mayor atención por parte de la comunidad. Esta funcionalidad no solo mejora la descubribilidad del contenido más relevante, sino que ofrece a los administradores una visión analítica clara sobre qué tipo de información musical es la más demandada, facilitando decisiones estratégicas sobre la curación de contenidos.

### Seguridad Avanzada: Doble Factor de Autenticación (2FA)

Dada la importancia crítica de proteger las cuentas de usuario y la integridad de los datos subidos, se ha elevado sustancialmente el nivel de seguridad mediante la integración de **Doble Factor de Autenticación (2FA)**. El flujo implementado requiere que, tras la validación tradicional de usuario y contraseña, el sistema genere un token único que se envía al correo electrónico del usuario. El acceso al sistema permanece bloqueado en una vista intermedia hasta que el usuario introduce correctamente el código recibido. Esta implementación de seguridad en capas asegura que, incluso si una contraseña es comprometida mediante phishing o fuerza bruta, el atacante no podrá acceder a la cuenta sin tener control simultáneo sobre el correo electrónico del propietario legítimo, elevando significativamente la barrera de protección.

### Infraestructura y Despliegue en la Nube

La arquitectura de despliegue ha sido modernizada utilizando **Render**, una plataforma en la nube (PaaS) que facilita el ciclo de vida completo del desarrollo de software. Se han establecido dos entornos completamente diferenciados: un **entorno de desarrollo** donde se despliegan las nuevas funcionalidades para su integración y revisión inicial, y un **entorno de pruebas (staging)** que actúa como espejo del entorno de producción para realizar validaciones finales, pruebas de carga y verificación de nuevas funcionalidades antes de su liberación. Esta separación de entornos, cada uno con su propia instancia de base de datos MariaDB, permite al equipo validar cambios, probar migraciones de esquema y ejecutar tests de regresión sin poner en riesgo la estabilidad del sistema ni la integridad de los datos visibles para los usuarios finales.

### Metodología y Buenas Prácticas

El equipo ha adoptado el modelo de ramas **EGC-flow**, basado en el concepto de feature-tasks, trabajando con ramas específicas para cada nueva funcionalidad y fusionándolas regularmente con la rama trunk. La integración continua se ha implementado mediante **GitHub Actions**, asegurando que cada cambio en el código se pruebe automáticamente antes de ser fusionado. Se han utilizado herramientas como Selenium para pruebas funcionales end-to-end y Locust para pruebas de carga, garantizando tanto la corrección funcional como el rendimiento adecuado bajo demanda.

### Conclusión

En resumen, Song-Hub representa una transformación exitosa de UVLHUB hacia una plataforma especializada en datasets musicales, incorporando funcionalidades avanzadas como el sistema de carrito, análisis de tendencias, comentarios comunitarios y autenticación de doble factor. El proyecto demuestra cómo una refactorización bien planificada puede convertir un sistema genérico en una solución especializada que aporta valor real a una comunidad específica, manteniendo altos estándares de calidad, seguridad y experiencia de usuario.



## Descripción del sistema (≈1.500 palabras)
- **Visión funcional:** roles, casos de uso principales, flujos críticos.
- **Arquitectura:** vista por capas/módulos (backend Flask + módulos `auth`, `dataset`, `featuremodel`, etc.), dependencias, puntos de integración externos (DB, servicios externos).
- **Datos y almacenamiento:** esquema principal (MariaDB/SQLAlchemy), migraciones relevantes.
- **APIs y endpoints clave:** autenticación, datasets, webhooks, etc.
- **Frontend/UX (si aplica):** vistas principales y recursos estáticos.
- **Infraestructura:** contenedores Docker, Nginx, variables de entorno, CI/CD.
- **Cambios desarrollados en el proyecto:** lista explícita de features/issues cerradas, migraciones, refactors, tests añadidos.
- **Calidad y seguridad:** linters (black/isort/flake8), tests (unitarios, Selenium, locust), controles de acceso y validaciones.

## Visión global del proceso de desarrollo (≈1.500 palabras)
- **Metodología y cadencia:** sprints, dailies, refinamientos.
- **Gestión de trabajo:** issues/boards, criterios de “definition of done”.
- **Flujo de cambios:** rama de feature → PR → CI → revisión → merge → despliegue.
- **Automatización:** pipelines de CI/CD (`.github/workflows/CD_dockerhub.yml`, `CD_webhook.yml`), calidad (hooks pre-commit).
- **Ejemplo de ciclo completo:** desde una issue concreta hasta producción (creación de rama, desarrollo, tests, code review, build, despliegue).
- **Gestión de riesgos y dependencias:** cómo se manejaron bloqueos y coordinaciones.
- **Lecciones aprendidas y mejoras al proceso.**

## Entorno de desarrollo (≈800 palabras)

### Visión general y sistemas operativos
El desarrollo de Song-Hub se ha realizado en Visual Studio principalmente con Python 3.12 y Flask, apoyado en SQLAlchemy para el acceso a datos y MariaDB como base de datos relacional. Para pruebas funcionales y de carga se emplean Selenium y Locust, y toda la aplicación se dockeriza para asegurar reproducibilidad. Los miembros del equipo han trabajado con macOS y Ubuntu 22.04.

### Requisitos previos
- Git (2.39+), Python 3.12.x (se recomienda `pyenv` o `asdf` para fijar versión), pip y virtualenv (o `venv`).
- Docker Engine 24+ y plugin `docker compose`; en Desktop activar integración con WSL donde aplique.
- Make (opcional pero cómodo en macOS/Linux) o, en su defecto, usar los comandos equivalentes indicados.
- Navegador Chrome/Chromium y ChromeDriver compatible para pruebas Selenium locales; en CI se usan contenedores con drivers preinstalados.
- Node no es requerido para la ejecución básica (los estáticos se sirven ya construidos), pero puede ser útil para tareas de linting front si se extiende la UI.

### Estructura de ramas y entornos
Se trabaja con trunk-based (rama `trunk`) y rama `main` para releases. Los entornos desplegados en Render son: `dev` (features en validación inicial) y `staging` (preproducción, espejo de prod). En local se replica la configuración mediante `docker/docker-compose.dev.yml`, que levanta app, base de datos MariaDB y Nginx. En producción se usan los `docker-compose.prod*.yml` con SSL y configuración de webhook cuando aplica.

### Configuración local paso a paso (entorno nativo)
1) Clonado del repositorio:
```
git clone https://github.com/Song-hub-egc/song-hub.git
cd song-hub
```
2) Creación de entorno virtual y dependencias Python:
```
python3.12 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```
3) Variables de entorno: crear un fichero `.env` (o usar `instance/config.py` según la configuración) con al menos:
```
FLASK_ENV=development
SECRET_KEY=changeme
DB_HOST=localhost
DB_PORT=3306
DB_USER=songhub
DB_PASSWORD=songhub
DB_NAME=songhub
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=user
MAIL_PASSWORD=pass
```
4) Base de datos local: levantar MariaDB con Docker si no se tiene instalada:
```
docker run -d --name songhub-db -p 3306:3306 -e MARIADB_ROOT_PASSWORD=root -e MARIADB_DATABASE=songhub -e MARIADB_USER=songhub -e MARIADB_PASSWORD=songhub mariadb:10.6
```
5) Migraciones de esquema:
```
flask db upgrade   # si la app expone el CLI
# o con alembic directamente
alembic upgrade head
```
6) Datos de prueba (opcional): usar los seeders incluidos en `core/resources/seeders` o scripts de `scripts/` si se requiere poblar con datasets iniciales.
7) Ejecutar la aplicación en local:
```
export FLASK_APP=wsgi.py
flask run --reload
# o bien
python wsgi.py
```

### Configuración local con Docker Compose (recomendada)
Para minimizar diferencias entre máquinas se usa el stack dockerizado.
```
docker compose -f docker/docker-compose.dev.yml up --build
```
Este archivo levanta la API Flask, MariaDB y Nginx con el mapeo de puertos por defecto (app en 5000 o 8000 según config, DB en 3306). Las variables de entorno se leen de `.env` o de los ficheros de entorno definidos en `docker/`. Para parar y limpiar:
```
docker compose -f docker/docker-compose.dev.yml down -v
```

### Diferencias entre miembros del equipo
- macOS y Linux: se trabajó principalmente con Docker Compose y `venv`. Makefiles facilitaron atajos (por ejemplo, `make up`, `make down`).
- Windows/WSL2: se recomendó clonar dentro de WSL para evitar problemas de rutas en los bind mounts de Docker y ejecutar los mismos comandos que en Linux.
- Algunos miembros ejecutaron la base de datos nativamente (MariaDB 10.6/10.11) y la app en `venv`, manteniendo la paridad de variables de entorno. Otros usaron el stack completo en contenedores.

### Ejecución de pruebas locales
- **Unitarias/integ:** `pytest` desde la raíz. Añadir `-q` o `-k` para filtrar.
- **Selenium (E2E):** requiere ChromeDriver accesible en PATH. Definir `SELENIUM_BASE_URL` apuntando al host de la app (por ejemplo, `http://localhost:5000`). En Docker, levantar el contenedor de tests o ejecutar con `docker compose -f docker/docker-compose.dev.yml run --rm app pytest -m selenium` si se han etiquetado.
- **Locust (carga):**
```
locust -f core/locust/common.py --host http://localhost:5000
```
- **Linters/format:** si se incluyen en el proyecto, ejecutar `flake8`, `isort`, `black` o el hook `pre-commit run --all-files` según configuración.

### Despliegue en Render y otros entornos
Los despliegues automáticos se orquestan con GitHub Actions, que construyen la imagen Docker, ejecutan tests y publican en Render. Para reproducir un build local equivalente:
```
docker build -t songhub:local -f docker/images/Dockerfile .
docker run --env-file .env -p 8000:8000 songhub:local
```
En `staging` y `producción` se usan ficheros `docker-compose.prod*.yml` con SSL y variables seguras. Las bases de datos están separadas por entorno para aislar datos y facilitar regresiones controladas.

### Troubleshooting frecuente
- **Puertos ocupados (5000/8000/3306):** parar servicios previos o ajustar puertos en `docker-compose.dev.yml`.
- **Migraciones fallidas:** revisar versión de MariaDB; ejecutar `alembic history` y `alembic downgrade` si es necesario; confirmar credenciales de conexión.
- **ChromeDriver no encontrado:** asegurar coincidencia de versiones entre navegador y driver; en CI usar imágenes con driver preinstalado.
- **Problemas de permisos en WSL:** ejecutar `git config core.fileMode false` si hay ruido por permisos; verificar que el repo está en el sistema de archivos de WSL, no en `C:`.
- **Variables de entorno ausentes:** comprobar `.env` y los ficheros de entorno cargados por Compose; sin `SECRET_KEY` la app no se inicia.
- **Volúmenes corruptos en Docker:** `docker compose -f docker/docker-compose.dev.yml down -v` y volver a levantar.

### Buenas prácticas adoptadas
- Reutilizar los ficheros de Compose de dev para alinear local con staging/prod.
- Mantener `.env` fuera del control de versiones y usar valores por entorno.
- Commits pequeños siguiendo Conventional Commits para facilitar el tracing en CI/CD.
- Ejecutar tests y linters antes de subir a `trunk`; los pipelines bloquean merges si fallan.
- Documentar scripts en `scripts/` (backup DB, renovación de certificados SSL, reinicios de contenedores) para reducir el bus factor.

Con este entorno de desarrollo unificado, cada miembro puede reproducir el sistema completo —aplicación, base de datos y proxy— en pocos comandos, minimizando discrepancias entre máquinas y asegurando que lo validado en local se comporta igual en los entornos de staging y producción.

## Ejercicio de propuesta de cambio

Se presentará un ejercicio con una propuesta concreta de cambio que ilustra todo el proceso de evolución y gestión de la configuración del proyecto de la siguiente manera.

### 1 Creación de la tarea en el tablero
El primer paso consiste en crear la tarea en el tablero de issues del proyecto. Para ello, se crea una issue que describa de manera clara y concisa el objetivo del cambio: ya sea implementar una nueva funcionalidad, corregir un error existente o realizar una mejora en el sistema. Una vez generada, la tarea se ubica inicialmente en la columna TO DO y se aigna a un miembro del grupo, donde se encuentran todos los elementos pendientes de abordar. Esta fase permite que el equipo mantenga una visión global del trabajo por realizar y que las tareas queden correctamente priorizadas antes de comenzar su desarrollo.

### 2 Creación de la rama correspondiente
Esta rama siempre debe originarse desde la rama trunk. El nombre de la rama dependerá del tipo de modificación que se vaya a realizar: “feature/nombre-de-la-tarea” para funcionalidades nuevas o ampliaciones, y “bugfix/descripción-del-cambio” para resolver errores. Para crear la rama se ejecutan los siguientes comandos: git checkout trunk y git checkout -b nombre-de-la-rama. Una vez creada la rama, se actualiza el tablero moviendo la issue al estado IN PROGRESS, indicando así al resto del equipo que se ha comenzado a trabajar en dicha tarea.

### 3 Desarrollo de la tarea y subida inicial de cambios
Durante esta fase, es recomendable realizar commits atómicos y periódicos, especialmente si se desea compartir los avances con otros miembros del equipo. Para subir los cambios se ejecutan los comandos git add ., git commit -m "mensaje-del-commit" y git push. Es importante respetar el formato de Conventional Commits, lo cual facilita la comprensión del historial y permite automatizar procesos como el versionado semántico. El mensaje del commit deberá seguir la estructura “feat(scope): descripción del cambio” para nuevas funcionalidades o “fix(scope): descripción del cambio” para correcciones.

### 4 Ejecución de pruebas
Una vez completada la implementación, se debe realizar un conjunto de pruebas que validen la calidad y el correcto funcionamiento de los cambios. Entre las pruebas contempladas se incluyen pruebas de interfaz utilizando Selenium, pruebas de carga con Locust y pruebas unitarias. Tras completar las pruebas, es necesario subir estos cambios a la rama siguiendo los comandos anteriores. Si el commit contiene únicamente pruebas, el prefijo adecuado será “test”, en caso contrario será el descrito en el paso anterior, manteniendo el estándar de Conventional Commits.

### 5 Integración de cambios en la rama trunk
Cuando la tarea ha sido desarrollada y validada con las pruebas correspondientes, llega el momento de incorporar los cambios en la rama trunk del proyecto. El procedimiento consiste en ejecutar git checkout trunk, git merge nombre-de-la-rama y git push. Esto actualiza la rama trunk con el nuevo código. Luego, la tarea se mueve a la columna REVIEW del tablero, indicando que está lista para ser revisada por el equipo. Si los miembros consideran que los cambios son correctos, la tarea pasa a DONE. Si se requieren correcciones, se vuelve al paso 3 para aplicar los cambios necesarios, subirlos de nuevo y repetir el proceso de revisión.

### 6 Integración en rama main
Por último, cuando el equipo de desarrollo considera oportuno generar una nueva release, se procede a integrar los cambios de la rama trunk en la rama main y a crear una nueva etiqueta de versión. Para ello, se ejecutan los siguientes comandos en este orden: git checkout main, git merge trunk, git push, git tag -a version, y finalmente git push origin version.

## Conclusiones y trabajo futuro

### Conclusiones
Song-Hub ha pasado de ser una evolución de UVLHUB a convertirse en una plataforma centrada en datasets musicales, con una arquitectura más sólida y funcionalidades que mejoran tanto la seguridad como la experiencia del usuario. Entre los principales avances destacan la incorporación de autenticación en dos factores (2FA), el carrito de descargas y las métricas de popularidad, que aportan una interacción más dinámica y útil para la comunidad.

El uso de integración y despliegue continuo (CI/CD) mediante GitHub Actions, junto con la dockerización, los scripts de automatización y el despliegue en Render, ha mejorado la robustez operativa del sistema y su mantenibilidad. Además, la adopción de buenas prácticas de ingeniería como linter, tests automatizados y despliegues en varios entornos ha dejado una base sólida y escalable para futuras mejoras.

En resumen, el proyecto consolida un entorno moderno, estable y bien estructurado, preparado para seguir creciendo con nuevas funcionalidades y una experiencia de usuario más completa.

### Trabajo futuro
- Internacionalización: permitir el uso de varios lenguajes para facilitar la expansión del proyecto fuera de España.
- Interacción social: añadir valoraciones, sistema de reputación y comentarios mejorados.
- Notificaciones y suscripciones: incluir avisos internos o por correo sobre nuevas versiones, respuestas o actividad en listas seguidas.
- Monitoreo y observabilidad: integrar métricas, logs centralizados y alertas para detectar incidencias en tiempo real.
- Automatización de QA: ampliar los tests unitarios, los tests con Selenium y de carga con Locust, mejorando la cobertura.
