# SendPulse WhatsApp Integration

Este módulo extiende el conector SendPulse para incl### 4. Configurar Variables
En cada template, configurar las variables:
- **Nombre:** Nombre de la variable en el template
- **Field Path:** Ruta del campo en el modelo (ej. name, partner_id.name)
- **Demo Value:** Valor para preview

### 5. Configurar Idioma
- **Language Code:** Código de idioma para el template (ej. en, es, fr)
- Este código se envía a la API de SendPulse junto con el template

## Funcionamiento Técnico

### Envío de Templates
El sistema utiliza el endpoint `/contacts/sendTemplateByPhone` de SendPulse con el siguiente formato:

```json
{
  "bot_id": "chatbot_bot_id",
  "phone": "380931112233",  // Teléfono sanitizado (solo números)
  "template": {
    "name": "template_name_from_odoo",
    "language": {
      "code": "en"  // Código de idioma del template
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Valor_Variable_1"
          },
          {
            "type": "text", 
            "text": "Valor_Variable_2"
          }
        ]
      }
    ]
  }
}
```

### Variables Dinámicas
- Las variables se ordenan por `sequence` en el template
- Los valores se toman de:
  1. Variables personalizadas del composer (prioridad alta)
  2. Campos del registro usando `field_path` (fallback)
- Los números de teléfono se sanitizan automáticamenteuncionalidades completas de WhatsApp, similares al módulo nativo de WhatsApp de Odoo.

## Características Principales

### 1. Gestión de Templates WhatsApp
- **Modelo:** `sendpulse.template`
- **Funcionalidad:** Crear y gestionar templates de WhatsApp para diferentes modelos
- **Ubicación:** SendPulse > WhatsApp > Templates

**Características:**
- Templates dinámicos con variables
- Configuración por modelo de datos
- Estados de aprobación (borrador, aprobado, rechazado)
- Preview de mensajes
- Configuración de campo de teléfono

### 2. Compositor de Mensajes
- **Modelo:** `sendpulse.composer`
- **Modelo auxiliar:** `sendpulse.composer.variable` (para variables dinámicas)
- **Funcionalidad:** Wizard para enviar mensajes WhatsApp usando templates
- **Acceso:** Botón "Send WhatsApp" en res.partner o desde menús contextuales

**Características:**
- Envío individual o masivo
- Preview del mensaje antes de enviar
- Variables dinámicas que se adaptan automáticamente al template seleccionado
- Posibilidad de personalizar valores de variables o usar datos del registro
- Validación de números de teléfono
- Interfaz intuitiva con explicaciones de variables

### 3. Historial de Mensajes
- **Modelo:** `sendpulse.message`
- **Funcionalidad:** Tracking de todos los mensajes enviados
- **Ubicación:** SendPulse > WhatsApp > Messages

**Características:**
- Estado de entrega (enviado, entregado, leído, fallido)
- Respuestas de la API de SendPulse
- Filtros por estado y template
- Vinculación con registros origen

### 4. Extensiones de res.partner
- Botón estadístico para ver mensajes enviados
- Botón de acción rápida "Send WhatsApp"
- Contador de mensajes SendPulse

### 5. Integración con mail.thread
- Capacidad de WhatsApp disponible en threads
- Método `_can_use_sendpulse_whatsapp()`
- Acción `action_send_sendpulse_whatsapp()`

### 6. Integración Automática con city.report
- Envío automático de notificaciones al cambiar estado del reporte
- Template "report_notification" para notificaciones de estado
- Integración tanto con el sistema legacy como con el nuevo sistema de templates

## Configuración

### 1. Configurar Autenticación SendPulse
```
SendPulse > Configuration > Auth
```
- Crear una nueva configuración de autenticación
- Configurar Client ID y Client Secret
- Obtener token de acceso

### 2. Configurar Chatbot SendPulse
```
SendPulse > Configuration > Chatbots
```
- Crear un nuevo chatbot
- Configurar Bot ID y Bot Type
- Asociar con la autenticación creada en el paso anterior

### 3. Crear Templates
```
SendPulse > WhatsApp > Templates
```
- Crear template para el modelo deseado (ej. res.partner)
- Seleccionar el chatbot configurado
- Configurar campo de teléfono (ej. mobile)
- Definir cuerpo del mensaje con variables: {{variable_name}}
- Aprobar el template

### 3. Configurar Variables
En cada template, configurar las variables:
- **Nombre:** Nombre de la variable en el template
- **Field Path:** Ruta del campo en el modelo (ej. name, partner_id.name)
- **Demo Value:** Valor para preview

## Uso

### Envío Manual desde Partner
1. Ir a un contacto (res.partner)
2. Hacer clic en "Send WhatsApp" 
3. Seleccionar template (se cargarán automáticamente las variables)
4. Personalizar variables si es necesario (dejar vacío usa datos del registro)
5. Revisar preview
6. Enviar mensaje

### Variables Dinámicas
- Las variables se crean automáticamente basadas en el template seleccionado
- Cada variable muestra:
  - **Nombre:** El placeholder en el template (ej. {{name}})
  - **Ejemplo:** Valor de demo configurado en el template
  - **Valor personalizado:** Campo editable para sobrescribir el valor
- Si se deja el valor personalizado vacío, se usa el valor del campo del registro

### Envío Masivo
1. Seleccionar múltiples registros en vista de lista
2. Acción > Send WhatsApp
3. Seleccionar template
4. Configurar variables
5. Enviar a todos

### Envío Automático (city.report)
Los reportes envían automáticamente notificaciones cuando:
- Se marca como completado
- Se marca como en progreso  
- Se cancela

## Templates de Demo Incluidos

### 1. Partner Welcome Message
- **Modelo:** res.partner
- **Uso:** Mensaje de bienvenida
- **Variables:** {{name}}

### 2. Report Status Notification  
- **Modelo:** city.report
- **Uso:** Notificación de cambio de estado
- **Variables:** {{partner_id.name}}, {{name}}, {{state}}, {{reference}}

## API y Métodos Principales

### sendpulse.template
```python
# Enviar template a registros
template.send_template(records, variables=None)

# Formatear contenido con variables
template._format_message_content(record, variables=None)
```

### mail.thread (cualquier modelo)
```python
# Verificar si puede usar WhatsApp
model._can_use_sendpulse_whatsapp()

# Enviar template específico
model.send_sendpulse_whatsapp_template(template_id, variables=None)

# Abrir compositor
model.action_send_sendpulse_whatsapp()
```

### res.partner
```python
# Ver mensajes del partner
partner.action_view_sendpulse_messages()

# Enviar WhatsApp al partner
partner.action_send_sendpulse_whatsapp()
```

## Menús del Sistema

```
SendPulse
├── WhatsApp
│   ├── Templates          # Gestión de templates
│   └── Messages           # Historial de mensajes
└── Configuration
    ├── Auth              # Configuración API
    └── Chatbots          # Configuración chatbots WhatsApp
```

## Permisos

- **Usuarios:** Solo lectura en templates y mensajes, acceso completo a composer
- **Administradores:** Acceso completo a todas las funcionalidades
- **Managers:** Creación y edición de templates y configuraciones

## Notas de Implementación

- Compatible con el sistema legacy existente
- Utiliza la API de SendPulse para envío real
- Templates similares al módulo whatsapp nativo de Odoo
- Validación de números de teléfono
- Manejo de errores y logging completo
- Datos de demo incluidos para testing
