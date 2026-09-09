# Farmax POS – Ticket Gana Max (58 mm)

Módulo de Odoo 17 que, al **facturar una venta en el Punto de Venta**, genera
automáticamente un PDF con tickets de **58 × 58 mm** para la promoción
**«CON FARMAX GANA MAX»**.

---

## 1. Funcionamiento

### Regla de emisión

El número de tickets depende del **total de la factura** (`account.move.amount_total`,
en la moneda de la compañía):

| Total de la factura | Tickets |
|---------------------|---------|
| menor a 10          | 0       |
| 10 – 19,99          | 1       |
| 20 – 29,99          | 2       |
| …                   | …       |
| `N`                 | `floor(N / 10)` |

Fórmula: `tickets = floor(total / 10)`, con un **tope de seguridad** (por defecto
100) para no bloquear el servidor con facturas muy grandes.

Cada ticket es **una página cuadrada de 58 × 58 mm** del PDF.

### Contenido de cada ticket

```
        CON FARMAX GANA MAX
NOMBRE                       <nombre del cliente>
APELLIDO                     <apellido del cliente>
CEDULA                       <res.partner.vat>
TELEFONO                     <res.partner.phone / mobile>
FACTURA                      <número REAL del asiento, p. ej. INV/2026/00007>
        Ticket 1 de N
```

- **NOMBRE / APELLIDO**: si está instalado `partner_firstname` (OCA) se usan los
  campos `firstname` / `lastname`; si no, se divide `res.partner.name`
  (primera palabra = nombre, resto = apellido).
- **CEDULA**: campo `vat` del contacto.
- **TELEFONO**: `phone`, y si está vacío, `mobile`.
- **FACTURA**: `account.move.name` — el número real del asiento contable, para
  poder rastrear la compra del cliente.

### Cuándo se genera

1. **Al validar la venta en el TPV** (orden marcada como *Factura*):
   - El servidor renderiza el PDF y lo **adjunta a la factura** (`ir.attachment`).
   - Se deja una nota en el *chatter* de la factura.
   - El navegador **abre el PDF automáticamente** (patch de frontend sobre
     `PaymentScreen.afterOrderValidation`) para que el cajero lo imprima.
2. **Manualmente**, desde la factura: menú **Imprimir → «Ticket Gana Max (58mm)»**.

Si el total es menor a 10, no se genera nada. Si algo falla, la venta del TPV
**no se bloquea** (los errores se registran en el log).

---

## 2. Estructura del módulo

```
farmax_pos_ticket/
├── __manifest__.py                     # Declaración del módulo (depends, data, assets)
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── account_move.py                 # Lógica de cálculo y datos del cliente
│   └── pos_order.py                    # Hook de facturación del TPV + adjunto/chatter
├── report/
│   ├── paperformat.xml                 # Formato de papel 58 × 58 mm (dpi 90)
│   ├── farmax_ticket_report.xml        # ir.actions.report (qweb-pdf) + binding en la factura
│   └── farmax_ticket_templates.xml     # Plantilla QWeb del ticket (1 página por ticket)
├── static/src/js/
│   └── payment_screen_ticket.js        # Abre el PDF al validar la venta en el TPV
├── LICENSE
├── .gitignore
└── README.md
```

### Puntos técnicos

| Elemento | Descripción |
|----------|-------------|
| `account.move.farmax_ticket_count()` | Devuelve el nº de tickets (con tope). |
| `account.move.farmax_ticket_range()` | Iterable `1..N` para el `t-foreach` del QWeb. |
| `account.move.farmax_partner_data()` | Diccionario con nombre, apellido, cédula, teléfono y nº de factura. |
| `pos.order._generate_pos_order_invoice()` | *Override*: tras crear la factura llama a `_farmax_generate_ticket_pdf()`. Evita duplicar el adjunto si ya existe. |
| `paperformat_farmax_ticket_58mm` | 58 × 58 mm, márgenes 1–2 mm, **dpi 90** (imprescindible: con dpi altos wkhtmltopdf distorsiona las medidas en mm). |
| `action_report_farmax_ganamax_ticket` | Reporte `qweb-pdf` sobre `account.move`, con *binding* para que aparezca en el menú **Imprimir**. |
| Plantilla QWeb | Resetea el `.container` de Bootstrap que Odoo añade al `<body>` para que el contenido ocupe todo el ancho; dibuja un recuadro (`.farmax-box`) y salta de página entre tickets con `page-break-before`. |

---

## 3. Instalación

Requisitos: **Odoo 17.0**, módulos `point_of_sale` y `account`.

```bash
# copiar el módulo en un addons_path y luego:
odoo-bin -c odoo.conf -d <BASE_DE_DATOS> -i farmax_pos_ticket --stop-after-init
```

Actualización tras cambios:

```bash
odoo-bin -c odoo.conf -d <BASE_DE_DATOS> -u farmax_pos_ticket --stop-after-init
```

Después de instalar/actualizar, **recarga el TPV** (Ctrl+F5) para que se cargue
el asset JavaScript.

---

## 4. Configuración

**Ajustes → Técnico → Parámetros → Parámetros del sistema**

| Clave | Valor por defecto | Descripción |
|-------|-------------------|-------------|
| `farmax_pos_ticket.max_tickets` | `100` | Máximo de tickets (páginas) por factura. |

El importe por ticket (10) es una constante del módulo (`FARMAX_TICKET_STEP` en
`models/account_move.py`).

---

## 5. Prueba manual

1. Activa **Facturación** en la configuración del TPV.
2. Crea/edita un contacto con **NIF (cédula)** y **teléfono**.
3. Abre una sesión de TPV, añade productos por un total ≥ 10 (p. ej. 25 → 2 tickets).
4. Botón **Cliente** → selecciona el contacto.
5. **Pagar** → marca **Factura** → **Validar**.
6. Se abre el PDF con `N` tickets de 58 × 58 mm. La misma factura queda con el
   PDF adjunto y una nota en el chatter.
7. Casos límite: total `9.99` → 0 tickets; `10` → 1; `55` → 5.

---

## 6. Limitaciones conocidas

- El renderizado usa **wkhtmltopdf**; si un cliente tiene un nombre muy largo que
  ocupe dos líneas, ese ticket podría desbordar a una segunda página. Ajustar el
  `padding` de `.farmax-box` o el `page_height` del *paperformat* si ocurre.
- La apertura automática del PDF en el TPV depende de que el navegador **permita
  ventanas emergentes / descargas** para el dominio de Odoo.
- El cálculo usa el total en la **moneda de la compañía**; no hace conversión.

---

## 7. Licencia

LGPL-3.0. Ver el archivo [`LICENSE`](LICENSE).
