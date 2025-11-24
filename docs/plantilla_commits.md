# Plantilla para Commits

A continuación, se presenta cómo los integrantes del equipo tienen que realizar los commits de acuerdo con el estándar **Conventional Commits**:

## Estructura del Commit

Cada commit debe seguir la siguiente estructura:

- no usar emojis

- <type>(<scope>): <breve resumen>

- <body (opcional, descripción más detallada)>


**Tipos permitidos (type):**
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: cambios en la documentación
- `style`: formato, lint, espacios, sin cambios en lógica
- `refactor`: refactorización de código que no añade ni corrige funcionalidades
- `perf`: mejora de rendimiento
- `test`: añadir o corregir tests
- `chore`: tareas de mantenimiento (build, herramientas, dependencias)
- `ci`: cambios en la integración continua
- `build`: cambios en el sistema de build
- `revert`: revertir un commit previo

**Scope (opcional):** nombre corto del área afectada (por ejemplo `auth`, `dataset`, `fakenodo`).


- Crear la rama desde la rama trunk

git checkout -b feature/mi-nueva-funcionalidad

- Antes de subir los cambios, asegurarase de que todos los tests pasen correctamente. 

rosemary test

- Después de esto se añaden y se commitean los cambios siguiendo Conventional Commits.

git add <archivos>
git commit
git push origin feature/mi-nueva-funcionalidad
git checkout trunk
git pull origin trunk
git merge feature/mi-nueva-funcionalidad
git push origin trunk
