import tkinter as tk
from tkinter import ttk, messagebox
import re, smtplib, threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── Gmail SMTP config — fill these in ─────────────────────────────────────────
GMAIL_SENDER   = "@gmail.com"   # ← your Gmail address
GMAIL_APP_PASS = "qweytwytqwy"    # ← your 16-char App Password
STORE_NAME     = "Computer Parts & Accesorries Store"

# ── Sample Product Data ────────────────────────────────────────────────────────
PRODUCTS = [
    {"code": "PRD-001", "item": "Wireless Mouse",        "quantity": 50,  "cost": 899.00,  "tax": 12},
    {"code": "PRD-002", "item": "Mechanical Keyboard",   "quantity": 30,  "cost": 2499.00, "tax": 12},
    {"code": "PRD-003", "item": "USB-C Hub",             "quantity": 75,  "cost": 1299.00, "tax": 12},
    {"code": "PRD-004", "item": "Monitor Stand",         "quantity": 20,  "cost": 799.00,  "tax": 12},
    {"code": "PRD-005", "item": "Laptop Sleeve 15\"",    "quantity": 45,  "cost": 549.00,  "tax": 0},
    {"code": "PRD-006", "item": "Webcam HD 1080p",       "quantity": 18,  "cost": 1899.00, "tax": 12},
    {"code": "PRD-007", "item": "Noise-Cancel Headset",  "quantity": 12,  "cost": 3299.00, "tax": 12},
    {"code": "PRD-008", "item": "Desk LED Lamp",         "quantity": 60,  "cost": 649.00,  "tax": 12},
    {"code": "PRD-009", "item": "Screen Cleaning Kit",   "quantity": 100, "cost": 199.00,  "tax": 0},
    {"code": "PRD-010", "item": "Portable SSD 1TB",      "quantity": 25,  "cost": 3799.00, "tax": 12},
]

# ── Theme ──────────────────────────────────────────────────────────────────────
BG        = "#0F172A"
PANEL     = "#1E293B"
CARD      = "#263348"
BORDER    = "#334155"
ACCENT    = "#38BDF8"
ACCENT2   = "#0EA5E9"
SUCCESS   = "#22C55E"
SUCCESS_D = "#16A34A"
DANGER    = "#EF4444"
PURPLE    = "#A855F7"
PURPLE_D  = "#9333EA"
TEXT      = "#F1F5F9"
MUTED     = "#94A3B8"
HIGHLIGHT = "#1D4ED8"
EMAIL_OK  = "#22C55E"
EMAIL_ERR = "#EF4444"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ── Email builder ──────────────────────────────────────────────────────────────
def build_html_receipt(txn, now, cart, sub, taxes, grand):
    rows = ""
    for item in cart:
        tax_amt  = item["cost"] * item["qty"] * item["tax"] / 100
        line_tot = item["cost"] * item["qty"] + tax_amt
        tax_note = f'<br><small style="color:#94A3B8">incl. {item["tax"]}% VAT ₱{tax_amt:,.2f}</small>' if item["tax"] else ""
        rows += f"""
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #334155">{item['item']}{tax_note}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #334155;text-align:center">{item['qty']}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #334155;text-align:right">₱{item['cost']:,.2f}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #334155;text-align:right">₱{line_tot:,.2f}</td>
        </tr>"""

    return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0F172A;font-family:'Segoe UI',Arial,sans-serif;color:#F1F5F9">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;padding:30px 0">
    <tr><td align="center">
      <table width="580" cellpadding="0" cellspacing="0" style="background:#1E293B;border-radius:12px;overflow:hidden">

        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#A855F7,#6366F1);padding:28px 32px">
          <div style="font-size:22px;font-weight:900;color:#fff">⚡ {STORE_NAME}</div>
          <div style="font-size:13px;color:#E9D5FF;margin-top:4px">Official Digital Receipt</div>
        </td></tr>

        <!-- Ref & Date -->
        <tr><td style="padding:20px 32px;background:#263348">
          <table width="100%"><tr>
            <td><span style="color:#94A3B8;font-size:12px">REFERENCE NO.</span><br>
                <span style="color:#38BDF8;font-weight:700;font-size:15px">{txn}</span></td>
            <td align="right"><span style="color:#94A3B8;font-size:12px">DATE &amp; TIME</span><br>
                <span style="font-size:13px">{now.strftime('%B %d, %Y  %I:%M %p')}</span></td>
          </tr></table>
        </td></tr>

        <!-- Items table -->
        <tr><td style="padding:0 32px 0 32px">
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px">
            <tr style="background:#334155;font-size:12px;color:#94A3B8;text-transform:uppercase">
              <th style="padding:10px 8px;text-align:left">Item</th>
              <th style="padding:10px 8px;text-align:center">Qty</th>
              <th style="padding:10px 8px;text-align:right">Unit Price</th>
              <th style="padding:10px 8px;text-align:right">Total</th>
            </tr>
            {rows}
          </table>
        </td></tr>

        <!-- Totals -->
        <tr><td style="padding:16px 32px">
          <table width="100%" style="background:#0F172A;border-radius:8px;padding:16px">
            <tr>
              <td style="color:#94A3B8;padding:5px 12px">Subtotal</td>
              <td align="right" style="padding:5px 12px">₱{sub:,.2f}</td>
            </tr>
            <tr>
              <td style="color:#94A3B8;padding:5px 12px">Total VAT</td>
              <td align="right" style="padding:5px 12px">₱{taxes:,.2f}</td>
            </tr>
            <tr>
              <td style="font-size:16px;font-weight:700;color:#22C55E;padding:10px 12px">AMOUNT DUE</td>
              <td align="right" style="font-size:18px;font-weight:900;color:#22C55E;padding:10px 12px">₱{grand:,.2f}</td>
            </tr>
          </table>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:20px 32px;text-align:center;color:#94A3B8;font-size:12px;border-top:1px solid #334155">
          Thank you for your purchase! 🎉<br>
          <span style="color:#475569">{STORE_NAME} · {now.strftime('%Y')}</span>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_receipt_email(to_email, txn, now, cart, sub, taxes, grand):
    """Sends HTML receipt via Gmail SMTP. Raises on failure."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your Receipt from {STORE_NAME} — {txn}"
    msg["From"]    = f"{STORE_NAME} <{GMAIL_SENDER}>"
    msg["To"]      = to_email

    # Plain-text fallback
    plain = (f"Receipt from {STORE_NAME}\n"
             f"Ref: {txn}\nDate: {now.strftime('%B %d, %Y %I:%M %p')}\n\n"
             + "\n".join(f"  {i['item']} x{i['qty']}  ₱{i['cost']*i['qty']:,.2f}"
                         for i in cart)
             + f"\n\nSubtotal: ₱{sub:,.2f}\nVAT: ₱{taxes:,.2f}\nTOTAL: ₱{grand:,.2f}\n\n"
               "Thank you for your purchase!")

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(build_html_receipt(txn, now, cart, sub, taxes, grand), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_SENDER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())


# ──────────────────────────────────────────────────────────────────────────────

class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NovaPOS  —  Point of Sale")
        self.geometry("1300x800")
        self.minsize(1100, 720)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.cart      = []
        self.hint_win  = None
        self._email_ph = True

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Treeview",
            background=CARD, foreground=TEXT, fieldbackground=CARD,
            rowheight=34, borderwidth=0, relief="flat", font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
            background=PANEL, foreground=ACCENT, relief="flat",
            borderwidth=0, font=("Segoe UI Semibold", 10))
        style.map("Treeview",
            background=[("selected", HIGHLIGHT)],
            foreground=[("selected", TEXT)])
        style.configure("TScrollbar",
            background=BORDER, troughcolor=PANEL, borderwidth=0, arrowcolor=MUTED)

    def _build_ui(self):
        hdr = tk.Frame(self, bg=PANEL, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  ⚡ NovaPOS", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI Black", 16)).pack(side="left", padx=20, pady=12)
        self.clock_lbl = tk.Label(hdr, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 10))
        self.clock_lbl.pack(side="right", padx=20)
        self._tick()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self._build_left(body)
        self._build_right(body)

    # ── LEFT ───────────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        tk.Label(left, text="Product Search", bg=BG, fg=TEXT,
                 font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(left, text="Type a product name or code",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        ef = tk.Frame(left, bg=BORDER)
        ef.pack(fill="x", pady=(6, 0))
        tk.Label(ef, text="🔍", bg=BORDER, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="left", padx=(10, 0))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(ef, textvariable=self.search_var,
                                     bg=BORDER, fg=TEXT, insertbackground=ACCENT,
                                     relief="flat", bd=0, font=("Segoe UI", 12),
                                     highlightthickness=0)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=8)
        clr = tk.Label(ef, text="✕", bg=BORDER, fg=MUTED, font=("Segoe UI", 11), cursor="hand2")
        clr.pack(side="right", padx=10)
        clr.bind("<Button-1>", lambda e: (self.search_var.set(""), self.search_entry.focus()))

        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry.bind("<FocusOut>", self._hide_hint)
        self.search_entry.bind("<Escape>", lambda e: self._hide_hint())
        self.search_entry.bind("<Down>", self._hint_down)

        tf = tk.Frame(left, bg=BG)
        tf.pack(fill="both", expand=True, pady=(14, 0))
        cols = ("code", "item", "qty", "cost", "tax")
        self.catalogue = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for cid, label, width in [
            ("code", "Code", 100), ("item", "Item", 220),
            ("qty", "Stock", 70), ("cost", "Price (₱)", 110), ("tax", "Tax %", 70)]:
            self.catalogue.heading(cid, text=label)
            self.catalogue.column(cid, width=width,
                anchor="center" if cid != "item" else "w", minwidth=50)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.catalogue.yview)
        self.catalogue.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.catalogue.pack(fill="both", expand=True)
        self.catalogue.tag_configure("even", background=CARD)
        self.catalogue.tag_configure("odd", background="#1A2840")
        self._load_catalogue(PRODUCTS)

        ar = tk.Frame(left, bg=BG)
        ar.pack(fill="x", pady=(12, 0))
        tk.Label(ar, text="Qty:", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(ar, textvariable=self.qty_var, width=5, bg=CARD, fg=TEXT,
                 insertbackground=ACCENT, relief="flat", bd=0, font=("Segoe UI", 11),
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT, justify="center"
                 ).pack(side="left", padx=(6, 14), ipady=6)
        add_btn = tk.Button(ar, text="＋ Add to Cart", bg=ACCENT2, fg="white",
                            relief="flat", bd=0, font=("Segoe UI Semibold", 11),
                            cursor="hand2", padx=18, pady=7, command=self._add_to_cart)
        add_btn.pack(side="left")
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=ACCENT))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=ACCENT2))
        self.catalogue.bind("<Double-1>", lambda e: self._add_to_cart())

    # ── RIGHT ──────────────────────────────────────────────────────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=PANEL, width=420)
        right.pack(side="right", fill="y", padx=(0, 16), pady=16)
        right.pack_propagate(False)

        # ── Bottom action bar — pinned OUTSIDE the scroll area, packed FIRST
        #    with side="bottom" so it always keeps its space, no matter how
        #    tall the content above it gets or how short the screen is.
        tk.Frame(right, bg=BORDER, height=1).pack(side="bottom", fill="x", padx=14, pady=(8, 10))
        br = tk.Frame(right, bg=PANEL)
        br.pack(side="bottom", fill="x", padx=14, pady=(0, 18))

        tk.Button(br, text="Clear All", bg=CARD, fg=MUTED, relief="flat", bd=0,
                  font=("Segoe UI", 10), cursor="hand2",
                  padx=14, pady=10, command=self._clear_cart).pack(side="left", padx=(0, 8))

        self.purchase_btn = tk.Button(br, text="💳  Purchase", bg=PURPLE, fg="white",
                                      relief="flat", bd=0, font=("Segoe UI Semibold", 12),
                                      cursor="hand2", padx=22, pady=10, command=self._purchase)
        self.purchase_btn.pack(side="right")
        self.purchase_btn.bind("<Enter>", lambda e: self.purchase_btn.config(bg=PURPLE_D))
        self.purchase_btn.bind("<Leave>", lambda e: self.purchase_btn.config(bg=PURPLE))

        # ── Scrollable content area ─────────────────────────────────────────────
        # Cart list, totals, and the email field all live inside this canvas.
        # If the window/screen is too short to show everything at once, the
        # user scrolls — nothing ever silently disappears.
        scroll_outer = tk.Frame(right, bg=PANEL)
        scroll_outer.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(scroll_outer, bg=PANEL, highlightthickness=0, bd=0)
        vbar = ttk.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, bg=PANEL)
        content_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def _sync_scrollregion(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content.bind("<Configure>", _sync_scrollregion)

        def _sync_width(event):
            canvas.itemconfig(content_id, width=event.width)
        canvas.bind("<Configure>", _sync_width)

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _wheel_up(_):
            canvas.yview_scroll(-3, "units")
        def _wheel_down(_):
            canvas.yview_scroll(3, "units")
        def _bind_wheel(_):
            canvas.bind_all("<MouseWheel>", _wheel)
            canvas.bind_all("<Button-4>", _wheel_up)
            canvas.bind_all("<Button-5>", _wheel_down)
        def _unbind_wheel(_):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        # Only hijack the scroll wheel while the cursor is actually over this
        # panel, so it doesn't fight with the product catalogue's own scrolling.
        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        tk.Label(content, text="🛒  Cart", bg=PANEL, fg=TEXT,
                 font=("Segoe UI Black", 14)).pack(anchor="w", padx=18, pady=(18, 6))

        cf = tk.Frame(content, bg=PANEL)
        cf.pack(fill="x", padx=12)
        ccols = ("item", "qty", "price", "tax_amt", "total")
        self.cart_tree = ttk.Treeview(cf, columns=ccols, show="headings",
                                       selectmode="browse", height=8)
        for cid, label, width in [
            ("item", "Item", 130), ("qty", "Qty", 45),
            ("price", "Price", 80), ("tax_amt", "Tax", 70), ("total", "Total", 80)]:
            self.cart_tree.heading(cid, text=label)
            self.cart_tree.column(cid, width=width,
                anchor="center" if cid != "item" else "w", minwidth=40)
        csb = ttk.Scrollbar(cf, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=csb.set)
        csb.pack(side="right", fill="y")
        self.cart_tree.pack(side="left", fill="both", expand=True)
        self.cart_tree.tag_configure("cart_row", background=CARD)

        tk.Button(content, text="🗑  Remove Selected", bg="#2D1B1B", fg=DANGER,
                  relief="flat", bd=0, font=("Segoe UI", 10), cursor="hand2",
                  padx=12, pady=5, command=self._remove_item
                  ).pack(anchor="e", padx=14, pady=(6, 2))

        tk.Frame(content, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)

        totals = tk.Frame(content, bg=PANEL)
        totals.pack(fill="x", padx=18)
        self.subtotal_var = tk.StringVar(value="₱ 0.00")
        self.tax_var      = tk.StringVar(value="₱ 0.00")
        self.total_var    = tk.StringVar(value="₱ 0.00")
        for label, var, big, color in [
            ("Subtotal", self.subtotal_var, False, TEXT),
            ("Tax",      self.tax_var,      False, TEXT),
            ("TOTAL",    self.total_var,    True,  SUCCESS)]:
            r = tk.Frame(totals, bg=PANEL)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 10 if not big else 12)).pack(side="left")
            tk.Label(r, textvariable=var, bg=PANEL, fg=color,
                     font=("Segoe UI Semibold", 10 if not big else 14)).pack(side="right")

        # ── Email section ──────────────────────────────────────────────────────
        tk.Frame(content, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(12, 0))

        eh = tk.Frame(content, bg=PANEL)
        eh.pack(fill="x", padx=18, pady=(10, 4))
        tk.Label(eh, text="✉  Customer Email", bg=PANEL, fg=TEXT,
                 font=("Segoe UI Semibold", 11)).pack(side="left")
        self.email_status = tk.Label(eh, text="", bg=PANEL, font=("Segoe UI", 9))
        self.email_status.pack(side="right")

        ew = tk.Frame(content, bg=BORDER)
        ew.pack(fill="x", padx=14, pady=(0, 4))
        tk.Label(ew, text="@", bg=BORDER, fg=MUTED,
                 font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(ew, textvariable=self.email_var,
                                    bg=BORDER, fg=MUTED, insertbackground=ACCENT,
                                    relief="flat", bd=0, font=("Segoe UI", 11),
                                    highlightthickness=0)
        self.email_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=8)
        self.email_dot = tk.Label(ew, text="●", bg=BORDER, fg=BORDER, font=("Segoe UI", 12))
        self.email_dot.pack(side="right", padx=8)

        self._email_ph = True
        self.email_var.set("e.g. juan@example.com")

        def _ein(e):
            if self._email_ph:
                self._email_ph = False
                self.email_var.set("")
                self.email_entry.config(fg=TEXT)
        def _eout(e):
            if not self.email_var.get().strip():
                self._email_ph = True
                self.email_var.set("e.g. juan@example.com")
                self.email_entry.config(fg=MUTED)
                self._set_email_state("idle")
            else:
                self._validate_email_live()

        self.email_entry.bind("<FocusIn>", _ein)
        self.email_entry.bind("<FocusOut>", _eout)
        self.email_var.trace_add("write", self._validate_email_live)

        self.email_hint = tk.Label(content, text="", bg=PANEL, font=("Segoe UI", 8), anchor="w")
        self.email_hint.pack(fill="x", padx=18, pady=(0, 4))
        self._set_email_state("idle")

        # ── Sending status bar ─────────────────────────────────────────────────
        self.send_status = tk.Label(content, text="", bg=PANEL,
                                    font=("Segoe UI", 9), anchor="w")
        self.send_status.pack(fill="x", padx=18, pady=(0, 14))

    # ── Email validation ───────────────────────────────────────────────────────
    def _validate_email_live(self, *_):
        if self._email_ph:
            return
        val = self.email_var.get().strip()
        if not val:
            self._set_email_state("idle")
        elif EMAIL_RE.match(val):
            self._set_email_state("ok")
        else:
            self._set_email_state("error")

    def _set_email_state(self, state):
        if state == "ok":
            self.email_dot.config(fg=EMAIL_OK)
            self.email_status.config(text="✓ Valid", fg=EMAIL_OK)
            self.email_hint.config(text="Receipt will be emailed after purchase.", fg=MUTED)
        elif state == "error":
            self.email_dot.config(fg=EMAIL_ERR)
            self.email_status.config(text="✗ Invalid", fg=EMAIL_ERR)
            self.email_hint.config(text="Please enter a valid email address.", fg=EMAIL_ERR)
        else:
            self.email_dot.config(fg=BORDER)
            self.email_status.config(text="", fg=MUTED)
            self.email_hint.config(text="Optional — leave blank to skip receipt.", fg=MUTED)

    def _get_email(self):
        if self._email_ph:
            return ""
        return self.email_var.get().strip()

    # ── Catalogue helpers ──────────────────────────────────────────────────────
    def _load_catalogue(self, products):
        for row in self.catalogue.get_children():
            self.catalogue.delete(row)
        for i, p in enumerate(products):
            self.catalogue.insert("", "end", iid=p["code"],
                tags=("even" if i % 2 == 0 else "odd",),
                values=(p["code"], p["item"], p["quantity"],
                        f"₱{p['cost']:,.2f}", f"{p['tax']}%"))

    # ── Autocomplete ───────────────────────────────────────────────────────────
    def _on_search_change(self, *_):
        q = self.search_var.get().strip().lower()
        if not q:
            self._hide_hint()
            self._load_catalogue(PRODUCTS)
            return
        matches = [p for p in PRODUCTS
                   if q in p["item"].lower() or q in p["code"].lower()]
        self._load_catalogue(matches)
        self._show_hint(matches)

    def _show_hint(self, matches):
        self._hide_hint()
        if not matches:
            return
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 2
        w = self.search_entry.winfo_width() + 60
        self.hint_win = tk.Toplevel(self)
        self.hint_win.wm_overrideredirect(True)
        self.hint_win.geometry(f"{w}x{min(len(matches)*36, 216)}+{x}+{y}")
        self.hint_win.configure(bg=BORDER)
        self.hint_win.attributes("-topmost", True)
        for p in matches[:6]:
            row = tk.Frame(self.hint_win, bg=CARD, cursor="hand2")
            row.pack(fill="x", pady=1)
            code_l  = tk.Label(row, text=f"  {p['code']}", bg=CARD, fg=ACCENT,
                               font=("Segoe UI", 9), width=10, anchor="w")
            code_l.pack(side="left")
            name_l  = tk.Label(row, text=p["item"], bg=CARD, fg=TEXT,
                               font=("Segoe UI", 10), anchor="w")
            name_l.pack(side="left", fill="x", expand=True, padx=4)
            price_l = tk.Label(row, text=f"₱{p['cost']:,.0f}  ", bg=CARD, fg=MUTED,
                               font=("Segoe UI", 9), anchor="e")
            price_l.pack(side="right")
            def _sel(prod=p):
                self.search_var.set(prod["item"])
                self._hide_hint()
                self.catalogue.selection_set(prod["code"])
                self.catalogue.focus(prod["code"])
                self.catalogue.see(prod["code"])
            for w2 in (row, code_l, name_l, price_l):
                w2.bind("<Button-1>", lambda e, fn=_sel: fn())
                w2.bind("<Enter>", lambda e, r=row: r.config(bg=HIGHLIGHT))
                w2.bind("<Leave>", lambda e, r=row: r.config(bg=CARD))

    def _hide_hint(self, *_):
        if self.hint_win:
            try: self.hint_win.destroy()
            except Exception: pass
            self.hint_win = None

    def _hint_down(self, _=None): pass

    # ── Cart operations ────────────────────────────────────────────────────────
    def _add_to_cart(self):
        sel = self.catalogue.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a product first.")
            return
        code = sel[0]
        product = next((p for p in PRODUCTS if p["code"] == code), None)
        if not product: return
        try:
            qty = int(self.qty_var.get())
            if qty < 1: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Qty", "Enter a valid quantity (≥ 1).")
            return
        if qty > product["quantity"]:
            messagebox.showerror("Insufficient Stock",
                                 f"Only {product['quantity']} units available.")
            return
        for item in self.cart:
            if item["code"] == code:
                item["qty"] = min(item["qty"] + qty, product["quantity"])
                self._refresh_cart()
                return
        self.cart.append({"code": code, "item": product["item"],
                          "qty": qty, "cost": product["cost"], "tax": product["tax"]})
        self._refresh_cart()

    def _refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        subtotal = total_tax = 0.0
        for item in self.cart:
            tax_amt  = item["cost"] * item["qty"] * item["tax"] / 100
            line_tot = item["cost"] * item["qty"] + tax_amt
            subtotal  += item["cost"] * item["qty"]
            total_tax += tax_amt
            self.cart_tree.insert("", "end", tags=("cart_row",),
                values=(item["item"], item["qty"],
                        f"₱{item['cost']:,.2f}",
                        f"₱{tax_amt:,.2f}",
                        f"₱{line_tot:,.2f}"))
        grand = subtotal + total_tax
        self.subtotal_var.set(f"₱ {subtotal:,.2f}")
        self.tax_var.set(f"₱ {total_tax:,.2f}")
        self.total_var.set(f"₱ {grand:,.2f}")

    def _remove_item(self):
        sel = self.cart_tree.selection()
        if not sel: return
        del self.cart[self.cart_tree.index(sel[0])]
        self._refresh_cart()

    def _clear_cart(self):
        if not self.cart: return
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            self.cart.clear()
            self._refresh_cart()

    # ── Purchase ───────────────────────────────────────────────────────────────
    def _purchase(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items before purchasing.")
            return

        email = self._get_email()
        if email and not EMAIL_RE.match(email):
            if not messagebox.askyesno("Invalid Email",
                    "The email address doesn't look right.\nContinue without sending a receipt?"):
                self.email_entry.focus()
                return
            email = ""

        sub   = sum(i["cost"] * i["qty"] for i in self.cart)
        taxes = sum(i["cost"] * i["qty"] * i["tax"] / 100 for i in self.cart)
        grand = sub + taxes

        summary    = "\n".join(f"  • {i['item']} × {i['qty']}  →  ₱{i['cost']*i['qty']:,.2f}"
                               for i in self.cart)
        email_line = f"\n\n  📧 Receipt → {email}" if email else "\n\n  (No receipt email)"

        if not messagebox.askyesno("Confirm Purchase",
                f"Items:\n{summary}\n\n"
                f"  Subtotal : ₱{sub:,.2f}\n"
                f"  Tax      : ₱{taxes:,.2f}\n"
                f"  TOTAL    : ₱{grand:,.2f}"
                f"{email_line}\n\nProceed?", icon="question"):
            return

        now = datetime.now()
        txn = f"TXN-{now.strftime('%Y%m%d%H%M%S')}"

        # Snapshot cart before clearing
        cart_snap = list(self.cart)
        self.cart.clear()
        self._refresh_cart()
        self._reset_email()

        self._show_receipt(email, txn, now, cart_snap, sub, taxes, grand)

        # Send email in background thread so UI doesn't freeze
        if email:
            self._send_email_async(email, txn, now, cart_snap, sub, taxes, grand)

    def _send_email_async(self, email, txn, now, cart_snap, sub, taxes, grand):
        self.send_status.config(text="⏳ Sending receipt email...", fg=ACCENT)
        self.purchase_btn.config(state="disabled")

        def worker():
            try:
                send_receipt_email(email, txn, now, cart_snap, sub, taxes, grand)
                self.after(0, lambda: self.send_status.config(
                    text=f"✅ Receipt sent to {email}", fg=EMAIL_OK))
            except Exception as ex:
                self.after(0, lambda: self.send_status.config(
                    text=f"❌ Email failed: {ex}", fg=EMAIL_ERR))
            finally:
                self.after(0, lambda: self.purchase_btn.config(state="normal"))
                self.after(8000, lambda: self.send_status.config(text=""))

        threading.Thread(target=worker, daemon=True).start()

    def _reset_email(self):
        self._email_ph = True
        self.email_var.set("e.g. juan@example.com")
        self.email_entry.config(fg=MUTED)
        self._set_email_state("idle")

    # ── Receipt window ─────────────────────────────────────────────────────────
    def _show_receipt(self, email, txn, now, cart_snap, sub, taxes, grand):
        lines = [
            "=" * 46,
            "       ⚡ NovaPOS — Official Receipt",
            "=" * 46,
            f"  Date    : {now.strftime('%B %d, %Y')}",
            f"  Time    : {now.strftime('%I:%M:%S %p')}",
            f"  Ref No. : {txn}",
            "",
            f"  {'ITEM':<26} {'QTY':>4} {'PRICE':>9} {'TOTAL':>10}",
            "  " + "-" * 52,
        ]
        for item in cart_snap:
            tax_amt  = item["cost"] * item["qty"] * item["tax"] / 100
            line_tot = item["cost"] * item["qty"] + tax_amt
            lines.append(f"  {item['item'][:24]:<26} {item['qty']:>4} "
                         f"₱{item['cost']:>8,.2f} ₱{line_tot:>9,.2f}")
            if item["tax"]:
                lines.append(f"    (incl. {item['tax']}% VAT: ₱{tax_amt:.2f})")
        lines += [
            "  " + "-" * 52,
            f"  {'Subtotal':<34} ₱{sub:>9,.2f}",
            f"  {'Total VAT':<34} ₱{taxes:>9,.2f}",
            f"  {'AMOUNT DUE':<34} ₱{grand:>9,.2f}",
            "=" * 46,
        ]
        if email:
            lines += [f"  ✉  Receipt emailed to: {email}", "=" * 46]
        lines += ["", "    Thank you for your purchase!  ⚡", ""]

        win = tk.Toplevel(self)
        win.title("Receipt")
        win.configure(bg=PANEL)
        win.geometry("520x580")
        win.resizable(False, False)

        hf = tk.Frame(win, bg=PURPLE, height=50)
        hf.pack(fill="x")
        hf.pack_propagate(False)
        tk.Label(hf, text="✅  Purchase Complete", bg=PURPLE, fg="white",
                 font=("Segoe UI Black", 13)).pack(side="left", padx=20, pady=12)
        tk.Label(hf, text=txn, bg=PURPLE, fg="#E9D5FF",
                 font=("Segoe UI", 9)).pack(side="right", padx=20)

        if email:
            badge = tk.Frame(win, bg="#1A2840")
            badge.pack(fill="x", padx=14, pady=(10, 0))
            tk.Label(badge, text=f"  ✉  Receipt emailed to: {email}",
                     bg="#1A2840", fg=EMAIL_OK, font=("Segoe UI", 10)
                     ).pack(anchor="w", pady=8, padx=6)

        txt = tk.Text(win, bg=CARD, fg=TEXT, relief="flat",
                      font=("Courier New", 10), bd=0, wrap="none",
                      highlightthickness=0, padx=12, pady=10)
        txt.pack(fill="both", expand=True, padx=14, pady=(10, 0))
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

        tk.Button(win, text="Close", bg=PURPLE, fg="white",
                  relief="flat", bd=0, font=("Segoe UI Semibold", 11),
                  padx=24, pady=9, cursor="hand2",
                  command=win.destroy).pack(pady=14)

    # ── Clock ──────────────────────────────────────────────────────────────────
    def _tick(self):
        self.clock_lbl.config(text=datetime.now().strftime("%a, %d %b %Y  %H:%M:%S"))
        self.after(1000, self._tick)


if __name__ == "__main__":
    app = POSApp()
    app.mainloop()