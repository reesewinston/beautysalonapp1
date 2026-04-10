import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector


def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="appuser",
        password="AppPass123!",
        database="beauty_booking_system"
    )


class salon_app:
    def __init__(self, root):
        self.root = root
        self.root.title("neutral elegance salon")
        self.root.geometry("1380x860")
        self.root.configure(bg="#f6f1eb")

        self.selected_service_name = None
        self.selected_service_id = None
        self.selected_stylist_id = None
        self.selected_stylist_name = None

        self.setup_colors()
        self.setup_styles()
        self.build_layout()
        self.load_categories()

    def setup_colors(self):
        self.bg_main = "#f6f1eb"
        self.bg_header = "#f2efec"
        self.bg_card = "#fffaf5"
        self.bg_soft = "#ebe2d7"
        self.bg_mid = "#ccbeb1"
        self.bg_tan = "#997e67"
        self.bg_dark = "#664930"
        self.text_dark = "#2d2219"
        self.text_muted = "#6d5a49"
        self.line = "#ddd1c5"
        self.input_bg = "#fbf7f3"

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#fffaf5",
            foreground=self.text_dark,
            fieldbackground="#fffaf5",
            rowheight=34,
            borderwidth=0,
            font=("helvetica", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=self.bg_soft,
            foreground=self.text_dark,
            relief="flat",
            font=("helvetica", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", self.bg_mid)],
            foreground=[("selected", self.text_dark)]
        )

        style.configure(
            "TNotebook",
            background=self.bg_main,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=self.bg_soft,
            foreground=self.text_dark,
            padding=(18, 10),
            font=("helvetica", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", self.bg_dark)],
            foreground=[("selected", "white")]
        )

        style.configure(
            "TCombobox",
            fieldbackground="white",
            background="white",
            foreground=self.text_dark,
            padding=6
        )

    def build_layout(self):
        self.build_header()

        body = tk.Frame(self.root, bg=self.bg_main)
        body.pack(fill="both", expand=True, padx=22, pady=18)

        self.left_panel = tk.Frame(
            body,
            bg=self.bg_card,
            width=360,
            highlightbackground=self.line,
            highlightthickness=1
        )
        self.left_panel.pack(side="left", fill="y", padx=(0, 16))
        self.left_panel.pack_propagate(False)

        self.right_panel = tk.Frame(
            body,
            bg=self.bg_card,
            highlightbackground=self.line,
            highlightthickness=1
        )
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.build_left_panel()
        self.build_right_panel()

    def build_header(self):
        header = tk.Frame(self.root, bg=self.bg_header, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=self.bg_header)
        inner.pack(fill="both", expand=True, padx=28, pady=20)

        tk.Label(
            inner,
            text="Neutral Elegance",
            font=("helvetica", 36, "bold"),
            bg=self.bg_header,
            fg=self.text_dark
        ).pack(anchor="w")

        tk.Label(
            inner,
            text="modern salon booking • services, stylists, appointments, and reviews",
            font=("helvetica", 12),
            bg=self.bg_header,
            fg=self.text_muted
        ).pack(anchor="w", pady=(4, 0))

    def build_left_panel(self):
        tk.Label(
            self.left_panel,
            text="discover services",
            font=("helvetica", 18, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", padx=20, pady=(22, 4))

        tk.Label(
            self.left_panel,
            text="choose a category and browse available services",
            font=("helvetica", 10),
            bg=self.bg_card,
            fg=self.text_muted
        ).pack(anchor="w", padx=20, pady=(0, 18))

        tk.Label(
            self.left_panel,
            text="service category",
            font=("helvetica", 10, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", padx=20)

        self.category_box = ttk.Combobox(self.left_panel, state="readonly", width=30)
        self.category_box.pack(padx=20, pady=(8, 18), fill="x")
        self.category_box.bind("<<ComboboxSelected>>", self.show_services_by_category)

        tk.Label(
            self.left_panel,
            text="services",
            font=("helvetica", 10, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", padx=20)

        self.service_list = tk.Listbox(
            self.left_panel,
            height=22,
            bg="white",
            fg=self.text_dark,
            font=("helvetica", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.line,
            selectbackground=self.bg_mid,
            selectforeground=self.text_dark,
            activestyle="none"
        )
        self.service_list.pack(fill="both", expand=True, padx=20, pady=(8, 18))
        self.service_list.bind("<<ListboxSelect>>", self.select_service)

        tk.Button(
            self.left_panel,
            text="refresh categories",
            command=self.load_categories,
            bg=self.bg_dark,
            fg="white",
            relief="flat",
            font=("helvetica", 10, "bold"),
            padx=10,
            pady=10,
            cursor="hand2"
        ).pack(fill="x", padx=20, pady=(0, 20))

    def build_right_panel(self):
        notebook = ttk.Notebook(self.right_panel)
        notebook.pack(fill="both", expand=True, padx=18, pady=18)

        self.book_tab = tk.Frame(notebook, bg=self.bg_card)
        self.lookup_tab = tk.Frame(notebook, bg=self.bg_card)
        self.review_tab = tk.Frame(notebook, bg=self.bg_card)

        notebook.add(self.book_tab, text="book")
        notebook.add(self.lookup_tab, text="my bookings")
        notebook.add(self.review_tab, text="reviews")

        self.build_book_tab()
        self.build_lookup_tab()
        self.build_review_tab()

    def build_book_tab(self):
        hero = tk.Frame(self.book_tab, bg=self.bg_dark, height=170)
        hero.pack(fill="x", padx=18, pady=18)
        hero.pack_propagate(False)

        tk.Label(
            hero,
            text="book your next beauty appointment",
            font=("helvetica", 24, "bold"),
            bg=self.bg_dark,
            fg="white"
        ).pack(anchor="w", padx=24, pady=(28, 6))

        tk.Label(
            hero,
            text="select a service, select a stylist, then enter your date and time.",
            font=("helvetica", 11),
            bg=self.bg_dark,
            fg="#f3ebe2"
        ).pack(anchor="w", padx=24)

        content = tk.Frame(self.book_tab, bg=self.bg_card)
        content.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        top_cards = tk.Frame(content, bg=self.bg_card)
        top_cards.pack(fill="x", pady=(0, 16))

        self.selection_card = self.make_info_card(top_cards, "selected service", "none yet")
        self.selection_card.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.stylist_card = self.make_info_card(top_cards, "selected stylist", "none yet")
        self.stylist_card.pack(side="left", fill="x", expand=True, padx=(10, 0))

        table_wrap = tk.Frame(content, bg=self.bg_card)
        table_wrap.pack(fill="both", expand=True)

        tk.Label(
            table_wrap,
            text="available stylists",
            font=("helvetica", 15, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", pady=(0, 10))

        self.stylist_tree = ttk.Treeview(
            table_wrap,
            columns=("stylist_id", "service_id", "name", "specialty", "service", "price", "duration", "rating"),
            show="headings",
            height=9
        )
        self.stylist_tree.pack(fill="x")

        self.stylist_tree.heading("stylist_id", text="stylist_id")
        self.stylist_tree.heading("service_id", text="service_id")
        self.stylist_tree.heading("name", text="Name")
        self.stylist_tree.heading("specialty", text="Specialty")
        self.stylist_tree.heading("service", text="Service")
        self.stylist_tree.heading("price", text="Price")
        self.stylist_tree.heading("duration", text="Duration")
        self.stylist_tree.heading("rating", text="Rating")

        self.stylist_tree.column("stylist_id", width=0, stretch=False)
        self.stylist_tree.column("service_id", width=0, stretch=False)
        self.stylist_tree.column("name", width=170, anchor="center")
        self.stylist_tree.column("specialty", width=120, anchor="center")
        self.stylist_tree.column("service", width=170, anchor="center")
        self.stylist_tree.column("price", width=90, anchor="center")
        self.stylist_tree.column("duration", width=100, anchor="center")
        self.stylist_tree.column("rating", width=100, anchor="center")

        self.stylist_tree.bind("<<TreeviewSelect>>", self.select_stylist)
        self.stylist_tree.bind("<Double-1>", self.select_stylist)

        self.selection_status = tk.Label(
            table_wrap,
            text="click a stylist row to select it",
            font=("helvetica", 10),
            bg=self.bg_card,
            fg=self.text_muted
        )
        self.selection_status.pack(anchor="w", pady=(8, 0))

        form_card = tk.Frame(content, bg="#ffffff", highlightbackground=self.line, highlightthickness=1)
        form_card.pack(fill="x", pady=(18, 0))

        tk.Label(
            form_card,
            text="appointment details",
            font=("helvetica", 15, "bold"),
            bg="#ffffff",
            fg=self.text_dark
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(18, 12))

        fields = [
            "first name",
            "last name",
            "phone",
            "email",
            "date (yyyy-mm-dd)",
            "time (hh:mm:ss)"
        ]

        self.booking_entries = {}

        for i, field in enumerate(fields):
            row = (i // 2) + 1
            col = (i % 2) * 2

            tk.Label(
                form_card,
                text=field,
                font=("helvetica", 10, "bold"),
                bg="#ffffff",
                fg=self.text_dark
            ).grid(row=row, column=col, sticky="w", padx=18, pady=8)

            entry = tk.Entry(
                form_card,
                font=("helvetica", 11),
                bg=self.input_bg,
                fg=self.text_dark,
                relief="flat",
                highlightthickness=1,
                highlightbackground=self.line,
                width=26
            )
            entry.grid(row=row, column=col + 1, sticky="w", padx=18, pady=8, ipady=8)
            self.booking_entries[field] = entry

        button_row = tk.Frame(form_card, bg="#ffffff")
        button_row.grid(row=5, column=0, columnspan=4, sticky="w", padx=18, pady=18)

        tk.Button(
            button_row,
            text="book appointment",
            command=self.book_appointment,
            bg=self.bg_tan,
            fg="white",
            relief="flat",
            font=("helvetica", 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            button_row,
            text="clear",
            command=self.clear_booking_fields,
            bg=self.bg_soft,
            fg=self.text_dark,
            relief="flat",
            font=("helvetica", 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="left")

    def build_lookup_tab(self):
        wrap = tk.Frame(self.lookup_tab, bg=self.bg_card)
        wrap.pack(fill="both", expand=True, padx=22, pady=22)

        tk.Label(
            wrap,
            text="find your bookings",
            font=("helvetica", 22, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w")

        tk.Label(
            wrap,
            text="enter your phone number to see scheduled and completed appointments",
            font=("helvetica", 11),
            bg=self.bg_card,
            fg=self.text_muted
        ).pack(anchor="w", pady=(4, 18))

        search_bar = tk.Frame(wrap, bg="#ffffff", highlightbackground=self.line, highlightthickness=1)
        search_bar.pack(fill="x", pady=(0, 18))

        self.lookup_phone = tk.Entry(
            search_bar,
            font=("helvetica", 12),
            bg="#ffffff",
            fg=self.text_dark,
            relief="flat",
            width=28
        )
        self.lookup_phone.pack(side="left", padx=16, pady=14)

        tk.Button(
            search_bar,
            text="view bookings",
            command=self.view_bookings,
            bg=self.bg_dark,
            fg="white",
            relief="flat",
            font=("helvetica", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2"
        ).pack(side="right", padx=16)

        self.bookings_text = tk.Text(
            wrap,
            bg="#ffffff",
            fg=self.text_dark,
            font=("helvetica", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.line,
            wrap="word"
        )
        self.bookings_text.pack(fill="both", expand=True)

    def build_review_tab(self):
        wrap = tk.Frame(self.review_tab, bg=self.bg_card)
        wrap.pack(fill="both", expand=True, padx=22, pady=22)

        tk.Label(
            wrap,
            text="leave feedback",
            font=("helvetica", 22, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w")

        tk.Label(
            wrap,
            text="reviews are only allowed after a completed appointment",
            font=("helvetica", 11),
            bg=self.bg_card,
            fg=self.text_muted
        ).pack(anchor="w", pady=(4, 18))

        form = tk.Frame(wrap, bg="#ffffff", highlightbackground=self.line, highlightthickness=1)
        form.pack(fill="x")

        self.review_entries = {}

        fields = ["phone", "stylist id", "rating (1-5)"]

        for i, field in enumerate(fields):
            tk.Label(
                form,
                text=field,
                font=("helvetica", 10, "bold"),
                bg="#ffffff",
                fg=self.text_dark
            ).grid(row=i, column=0, sticky="w", padx=18, pady=12)

            entry = tk.Entry(
                form,
                font=("helvetica", 11),
                bg=self.input_bg,
                fg=self.text_dark,
                relief="flat",
                highlightthickness=1,
                highlightbackground=self.line,
                width=32
            )
            entry.grid(row=i, column=1, sticky="w", padx=18, pady=12, ipady=8)
            self.review_entries[field] = entry

        tk.Label(
            form,
            text="review text",
            font=("helvetica", 10, "bold"),
            bg="#ffffff",
            fg=self.text_dark
        ).grid(row=3, column=0, sticky="nw", padx=18, pady=12)

        self.review_entries["review text"] = tk.Text(
            form,
            width=50,
            height=8,
            font=("helvetica", 11),
            bg=self.input_bg,
            fg=self.text_dark,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.line
        )
        self.review_entries["review text"].grid(row=3, column=1, sticky="w", padx=18, pady=12)

        tk.Button(
            form,
            text="submit review",
            command=self.submit_review,
            bg=self.bg_tan,
            fg="white",
            relief="flat",
            font=("helvetica", 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).grid(row=4, column=1, sticky="w", padx=18, pady=18)

    def make_info_card(self, parent, title, value):
        card = tk.Frame(
            parent,
            bg="#ffffff",
            highlightbackground=self.line,
            highlightthickness=1,
            height=78
        )
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            font=("helvetica", 10, "bold"),
            bg="#ffffff",
            fg=self.text_muted
        ).pack(anchor="w", padx=16, pady=(14, 4))

        value_label = tk.Label(
            card,
            text=value,
            font=("helvetica", 12, "bold"),
            bg="#ffffff",
            fg=self.text_dark
        )
        value_label.pack(anchor="w", padx=16)

        card.value_label = value_label
        return card

    def load_categories(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                select distinct specialty
                from stylists
                where specialty is not null
                order by specialty
            """)
            categories = [row[0] for row in cursor.fetchall()]
            self.category_box["values"] = categories
            self.service_list.delete(0, tk.END)
            self.clear_stylist_tree()
            self.selection_status.config(text="click a stylist row to select it")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))

    def show_services_by_category(self, event=None):
        category = self.category_box.get()
        self.service_list.delete(0, tk.END)
        self.clear_stylist_tree()

        self.selected_service_name = None
        self.selected_service_id = None
        self.selected_stylist_id = None
        self.selected_stylist_name = None

        self.selection_card.value_label.config(text="none yet")
        self.stylist_card.value_label.config(text="none yet")
        self.selection_status.config(text="choose a service first")

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                select distinct s.service_name
                from services s
                join stylists st on s.stylist_id = st.stylist_id
                where st.specialty = %s
                order by s.service_name
            """, (category,))

            for row in cursor.fetchall():
                self.service_list.insert(tk.END, row[0])

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))

    def select_service(self, event=None):
        selection = self.service_list.curselection()
        if not selection:
            return

        self.selected_service_name = self.service_list.get(selection[0])
        self.selection_card.value_label.config(text=self.selected_service_name)
        self.stylist_card.value_label.config(text="none yet")
        self.selected_service_id = None
        self.selected_stylist_id = None
        self.selected_stylist_name = None
        self.selection_status.config(text="now click a stylist row below")
        self.load_stylists_for_service()

    def clear_stylist_tree(self):
        for item in self.stylist_tree.get_children():
            self.stylist_tree.delete(item)

    def load_stylists_for_service(self):
        self.clear_stylist_tree()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                select
                    st.stylist_id,
                    concat(st.first_name, ' ', st.last_name) as stylist_name,
                    st.specialty,
                    s.service_id,
                    s.service_name,
                    s.price,
                    s.duration,
                    round(avg(r.rating), 1) as avg_rating
                from services s
                join stylists st on s.stylist_id = st.stylist_id
                left join reviews r on st.stylist_id = r.stylist_id
                where s.service_name = %s
                group by st.stylist_id, stylist_name, st.specialty, s.service_id, s.service_name, s.price, s.duration
                order by avg_rating desc, s.price asc
            """, (self.selected_service_name,))

            rows = cursor.fetchall()

            if not rows:
                self.selection_status.config(text="no stylists found for this service")
            else:
                self.selection_status.config(text="click a stylist row to select it")

            for row in rows:
                stylist_id, stylist_name, specialty, service_id, service_name, price, duration, avg_rating = row
                rating_display = avg_rating if avg_rating is not None else "new"

                self.stylist_tree.insert(
                    "",
                    tk.END,
                    values=(
                        stylist_id,
                        service_id,
                        stylist_name,
                        specialty.title(),
                        service_name,
                        f"${price}",
                        f"{duration} min",
                        rating_display
                    )
                )

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))

    def select_stylist(self, event=None):
        selected = self.stylist_tree.selection()
        if not selected:
            return

        item = self.stylist_tree.item(selected[0])
        values = item.get("values", [])

        if not values:
            return

        self.selected_stylist_id = int(values[0])
        self.selected_service_id = int(values[1])
        self.selected_stylist_name = values[2]

        self.stylist_card.value_label.config(text=self.selected_stylist_name)
        self.selection_status.config(
            text=f"selected: {self.selected_stylist_name} • fill in the form below and click book appointment"
        )

    def get_or_create_client(self, first_name, last_name, phone, email):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            select client_id
            from clients
            where phone = %s
            limit 1
        """, (phone,))
        existing = cursor.fetchone()

        if existing:
            client_id = existing[0]
        else:
            cursor.execute("""
                insert into clients (first_name, last_name, phone, email)
                values (%s, %s, %s, %s)
            """, (first_name, last_name, phone, email))
            conn.commit()
            client_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return client_id

    def book_appointment(self):
        if not self.selected_service_id or not self.selected_stylist_id:
            messagebox.showwarning(
                "missing selection",
                "please click a stylist row first, then fill in the form and click book appointment."
            )
            return

        first_name = self.booking_entries["first name"].get().strip()
        last_name = self.booking_entries["last name"].get().strip()
        phone = self.booking_entries["phone"].get().strip()
        email = self.booking_entries["email"].get().strip()
        appointment_date = self.booking_entries["date (yyyy-mm-dd)"].get().strip()
        appointment_time = self.booking_entries["time (hh:mm:ss)"].get().strip()

        if not all([first_name, last_name, phone, email, appointment_date, appointment_time]):
            messagebox.showwarning("missing fields", "please fill in all booking details.")
            return

        try:
            client_id = self.get_or_create_client(first_name, last_name, phone, email)

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                select appointment_id
                from appointments
                where stylist_id = %s
                  and appointment_date = %s
                  and appointment_time = %s
                  and appointment_status in ('scheduled', 'completed')
            """, (self.selected_stylist_id, appointment_date, appointment_time))

            taken = cursor.fetchone()
            if taken:
                cursor.close()
                conn.close()
                messagebox.showerror("time unavailable", "that time is already booked for this stylist.")
                return

            cursor.execute("""
                insert into appointments (
                    client_id, stylist_id, service_id, appointment_date, appointment_time, appointment_status
                )
                values (%s, %s, %s, %s, %s, 'scheduled')
            """, (
                client_id,
                self.selected_stylist_id,
                self.selected_service_id,
                appointment_date,
                appointment_time
            ))

            conn.commit()
            appointment_id = cursor.lastrowid
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "appointment booked",
                f"appointment #{appointment_id} booked with {self.selected_stylist_name} for {self.selected_service_name}."
            )
            self.clear_booking_fields()

        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))

    def clear_booking_fields(self):
        for entry in self.booking_entries.values():
            entry.delete(0, tk.END)

    def view_bookings(self):
        phone = self.lookup_phone.get().strip()
        self.bookings_text.delete("1.0", tk.END)

        if not phone:
            messagebox.showwarning("missing phone", "please enter your phone number.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                select
                    a.appointment_id,
                    concat(c.first_name, ' ', c.last_name),
                    concat(st.first_name, ' ', st.last_name),
                    s.service_name,
                    a.appointment_date,
                    a.appointment_time,
                    a.appointment_status
                from appointments a
                join clients c on a.client_id = c.client_id
                join stylists st on a.stylist_id = st.stylist_id
                join services s on a.service_id = s.service_id
                where c.phone = %s
                order by a.appointment_date desc, a.appointment_time desc
            """, (phone,))

            rows = cursor.fetchall()

            if not rows:
                self.bookings_text.insert(tk.END, "no bookings found for that phone number.")
            else:
                for row in rows:
                    self.bookings_text.insert(
                        tk.END,
                        f"appointment #{row[0]}\n"
                        f"client: {row[1]}\n"
                        f"stylist: {row[2]}\n"
                        f"service: {row[3]}\n"
                        f"date: {row[4]}\n"
                        f"time: {row[5]}\n"
                        f"status: {row[6]}\n"
                        f"{'-' * 55}\n"
                    )

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))

    def submit_review(self):
        phone = self.review_entries["phone"].get().strip()
        stylist_id = self.review_entries["stylist id"].get().strip()
        rating = self.review_entries["rating (1-5)"].get().strip()
        review_text = self.review_entries["review text"].get("1.0", tk.END).strip()

        if not phone or not stylist_id or not rating:
            messagebox.showwarning("missing fields", "please enter phone, stylist id, and rating.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                select client_id
                from clients
                where phone = %s
                limit 1
            """, (phone,))
            client = cursor.fetchone()

            if not client:
                cursor.close()
                conn.close()
                messagebox.showerror("not found", "no client found with that phone number.")
                return

            client_id = client[0]

            cursor.execute("""
                select appointment_id
                from appointments
                where client_id = %s
                  and stylist_id = %s
                  and appointment_status = 'completed'
                limit 1
            """, (client_id, stylist_id))
            completed = cursor.fetchone()

            if not completed:
                cursor.close()
                conn.close()
                messagebox.showerror("not allowed", "you can only review after a completed appointment.")
                return

            cursor.execute("""
                insert into reviews (client_id, stylist_id, rating, client_review, review_date)
                values (%s, %s, %s, %s, %s)
            """, (
                client_id,
                stylist_id,
                rating,
                review_text,
                date.today()
            ))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("success", "review submitted successfully.")

            self.review_entries["phone"].delete(0, tk.END)
            self.review_entries["stylist id"].delete(0, tk.END)
            self.review_entries["rating (1-5)"].delete(0, tk.END)
            self.review_entries["review text"].delete("1.0", tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("database error", str(err))


root = tk.Tk()
app = salon_app(root)
root.mainloop()