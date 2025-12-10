# Documento del Proyecto

**Proyecto:** SongHub  
**Curso:** 2024/2025  
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

## Resumen ejecutivo (≈800 palabras)
- Objetivo general del proyecto y problema que resuelve.
- Principales funcionalidades entregadas (top 5–7).
- Impacto para usuarios/negocio y métricas clave (rendimiento, estabilidad, seguridad).
- Hitos relevantes: fechas de releases, despliegues, integraciones, validaciones.
- Riesgos afrontados y cómo se mitigaron.
- Situación actual y próximo paso inmediato.

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
- **Stack técnico:** Python 3.12+, Flask, SQLAlchemy, Selenium, Locust, etc.
- **Requisitos previos:** versiones de Python, Docker/Compose, make/poetry/pip, etc.
- **Instalación y configuración:** pasos para clonar, instalar dependencias, configurar `.env`, inicializar DB/migraciones.
- **Entornos usados:** local, staging, producción; diferencias de configuración.
- **Herramientas por miembro (si difieren):** SO, IDE, extensiones, gestores de dependencias.
- **Ejecución y pruebas locales:** comandos para levantar servicios, correr tests unitarios, Selenium, linters.
- **Troubleshooting frecuente.**

## Ejercicio de propuesta de cambio
Ejemplo ilustrativo paso a paso (con comandos) de cómo abordar un cambio:
1. Crear issue y rama (`git checkout -b feature/…`).
2. Configurar entorno (variables, seeds de DB si aplican).
3. Desarrollo del cambio (archivo(s) afectados).
4. Formato y lint (`./.githooks/pre-commit` o `pre-commit run --all-files` equivalente).
5. Tests (`pytest`, Selenium, locust si procede).
6. Actualizar documentación/migraciones.
7. Push y PR; revisión y ajustes.
8. Merge y despliegue (workflow CI/CD correspondiente).
9. Verificación post-despliegue y monitoreo.

## Conclusiones y trabajo futuro
- Conclusiones clave del proyecto (qué se logró, valor entregado).
- Limitaciones actuales.
- Trabajo futuro propuesto (features, deuda técnica, mejoras de rendimiento/seguridad/UX).
- Plan de mantenimiento y monitoreo continuo.
