import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from styles import get_colors
from logic import (
    load_categories_from_db,
    load_services_by_category,
    load_stylists_for_service,
    get_available_times,
    get_or_create_client,
    create_appointment,
    get_bookings_by_phone,
    submit_review_by_phone
)


class SalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neutral Elegance Salon")
        self.root.geometry("1480x980")
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
        colors = get_colors()
        for key, value in colors.items():
            setattr(self, key, value)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "CustomNotebook.TNotebook",
            background=self.bg_main,
            borderwidth=0
        )

        style.configure(
            "CustomNotebook.TNotebook.Tab",
            background=self.bg_soft,
            foreground=self.text_dark,
            padding=(28, 14),
            font=("helvetica", 11, "bold")
        )

        style.map(
            "CustomNotebook.TNotebook.Tab",
            background=[("selected", self.bg_dark)],
            foreground=[("selected", "white")]
        )

        style.configure(
            "Treeview",
            background=self.white,
            foreground=self.text_dark,
            fieldbackground=self.white,
            rowheight=38,
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
            "TCombobox",
            fieldbackground=self.white,
            background=self.white,
            foreground=self.text_dark,
            padding=8
        )

    def build_layout(self):
        self.build_header()

        body = tk.Frame(self.root, bg=self.bg_main)
        body.pack(fill="both", expand=True, padx=20, pady=18)

        self.left_panel = tk.Frame(
            body,
            bg=self.bg_card,
            width=340,
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
        header = tk.Frame(self.root, bg=self.bg_header, height=130)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=self.bg_header)
        inner.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(
            inner,
            text="Neutral Elegance",
            font=("helvetica", 34, "bold"),
            bg=self.bg_header,
            fg=self.text_dark
        ).pack(anchor="w")

        tk.Label(
            inner,
            text="modern salon booking • services, stylists, appointments, and reviews",
            font=("helvetica", 12),
            bg=self.bg_header,
            fg=self.text_muted
        ).pack(anchor="w", pady=(6, 0))

    def build_left_panel(self):
        tk.Label(
            self.left_panel,
            text="discover services",
            font=("helvetica", 18, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", padx=20, pady=(22, 6))

        tk.Label(
            self.left_panel,
            text="choose a category and browse available services",
            font=("helvetica", 10),
            bg=self.bg_card,
            fg=self.text_muted
        ).pack(anchor="w", padx=20, pady=(0, 20))

        tk.Label(
            self.left_panel,
            text="service category",
            font=("helvetica", 10, "bold"),
            bg=self.bg_card,
            fg=self.text_dark
        ).pack(anchor="w", padx=20)

        self.category_box = ttk.Combobox(self.left_panel, state="readonly")
        self.category_box.pack(fill="x", padx=20, pady=(8, 18))
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
            bg=self.white,
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
            text="Refresh Categories",
            command=self.load_categories,
            bg="#3a2a1f",
            fg="#ffffff",
            activebackground="#5a4030",
            activeforeground="#000000",
            relief="flat",
            font=("helvetica", 10, "bold"),
            padx=10,
            pady=12,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground="#d6c5b4"
        ).pack(fill="x", padx=20, pady=(0, 20))

    def build_right_panel(self):
        notebook = ttk.Notebook(self.right_panel, style="CustomNotebook.TNotebook")
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
        hero = tk.Frame(self.book_tab, bg=self.bg_dark, height=150)
        hero.pack(fill="x", padx=18, pady=18)
        hero.pack_propagate(False)

        tk.Label(
            hero,
            text="book your next beauty appointment",
            font=("helvetica", 24, "bold"),
            bg=self.bg_dark,
            fg="white"
        ).pack(anchor="w", padx=24, pady=(24, 8))

        tk.Label(
            hero,
            text="choose a service, select a stylist, then complete your booking details below.",
            font=("helvetica", 11),
            bg=self.bg_dark,
            fg="#f3ebe2"
        ).pack(anchor="w", padx=24)

        content = tk.Frame(self.book_tab, bg=self.bg_card)
        content.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        cards_row = tk.Frame(content, bg=self.bg_card)
        cards_row.pack(fill="x", pady=(0, 16))

        self.selection_card = self.make_info_card(cards_row, "selected service", "none yet")
        self.selection_card.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.stylist_card = self.make_info_card(cards_row, "selected stylist", "none yet")
        self.stylist_card.pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.selection_status = tk.Label(
            content,
            text="step 1: choose a service from the left, then click a stylist row below",
            font=("helvetica", 10),
            bg=self.bg_card,
            fg=self.text_muted
        )
        self.selection_status.pack(anchor="w", pady=(0, 12))

        main_row = tk.Frame(content, bg=self.bg_card)
        main_row.pack(fill="both", expand=True, pady=(0, 8))

        # left side stylists
        stylists_box = tk.Frame(
            main_row,
            bg=self.white,
            highlightbackground=self.line,
            highlightthickness=1
        )
        stylists_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            stylists_box,
            text="available stylists",
            font=("helvetica", 15, "bold"),
            bg=self.white,
            fg=self.text_dark
        ).pack(anchor="w", padx=18, pady=(18, 10))

        self.stylist_tree = ttk.Treeview(
            stylists_box,
            columns=("stylist_id", "service_id", "name", "specialty", "service", "price", "duration", "rating"),
            show="headings",
            height=12
        )
        self.stylist_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

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
        self.stylist_tree.column("name", width=150, anchor="center")
        self.stylist_tree.column("specialty", width=110, anchor="center")
        self.stylist_tree.column("service", width=150, anchor="center")
        self.stylist_tree.column("price", width=80, anchor="center")
        self.stylist_tree.column("duration", width=90, anchor="center")
        self.stylist_tree.column("rating", width=70, anchor="center")

        self.stylist_tree.bind("<<TreeviewSelect>>", self.select_stylist)

        # right side form — scrollable so nothing gets clipped
        form_outer = tk.Frame(
            main_row,
            bg=self.white,
            width=490,
            highlightbackground=self.line,
            highlightthickness=1
        )
        form_outer.pack(side="right", fill="both")
        form_outer.pack_propagate(False)

        form_canvas = tk.Canvas(form_outer, bg=self.white, highlightthickness=0, width=470)
        form_scrollbar = ttk.Scrollbar(form_outer, orient="vertical", command=form_canvas.yview)
        form_canvas.configure(yscrollcommand=form_scrollbar.set)

        form_scrollbar.pack(side="right", fill="y")
        form_canvas.pack(side="left", fill="both", expand=True)

        form_card = tk.Frame(form_canvas, bg=self.white)
        form_card_window = form_canvas.create_window((0, 0), window=form_card, anchor="nw")

        def _on_form_configure(event):
            form_canvas.configure(scrollregion=form_canvas.bbox("all"))

        def _on_canvas_resize(event):
            form_canvas.itemconfig(form_card_window, width=event.width)

        form_card.bind("<Configure>", _on_form_configure)
        form_canvas.bind("<Configure>", _on_canvas_resize)

        def _on_mousewheel(event):
            form_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        form_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(
            form_card,
            text="appointment details",
            font=("helvetica", 15, "bold"),
            bg=self.white,
            fg=self.text_dark
        ).pack(anchor="w", padx=18, pady=(18, 14))

        self.booking_entries = {}

        field_frame = tk.Frame(form_card, bg=self.white)
        field_frame.pack(fill="x", padx=18)

        fields = [
            "first name",
            "last name",
            "phone",
            "email"
        ]

        for field in fields:
            tk.Label(
                field_frame,
                text=field,
                font=("helvetica", 10, "bold"),
                bg=self.white,
                fg=self.text_dark
            ).pack(anchor="w", pady=(6, 4))

            entry = tk.Entry(
                field_frame,
                font=("helvetica", 11),
                bg=self.input_bg,
                fg=self.text_dark,
                relief="flat",
                highlightthickness=1,
                highlightbackground=self.line
            )
            entry.pack(fill="x", ipady=8)
            self.booking_entries[field] = entry

        tk.Label(
            field_frame,
            text="appointment date",
            font=("helvetica", 10, "bold"),
            bg=self.white,
            fg=self.text_dark
        ).pack(anchor="w", pady=(14, 4))

        self.date_picker = DateEntry(
            field_frame,
            width=26,
            background=self.bg_dark,
            foreground="white",
            borderwidth=1,
            date_pattern="yyyy-mm-dd",
            year=2026,
            month=4,
            day=1,
            mindate=date(2026, 4, 1)
        )
        self.date_picker.pack(fill="x", ipady=4)
        self.date_picker.bind("<<DateEntrySelected>>", self.update_time_options)

        tk.Label(
            field_frame,
            text="available time",
            font=("helvetica", 10, "bold"),
            bg=self.white,
            fg=self.text_dark
        ).pack(anchor="w", pady=(14, 4))

        self.time_dropdown = ttk.Combobox(field_frame, state="readonly")
        self.time_dropdown.pack(fill="x")

        self.form_hint = tk.Label(
            field_frame,
            text="step 2: select a stylist first to load available times",
            font=("helvetica", 10),
            bg=self.white,
            fg=self.text_muted,
            wraplength=400,
            justify="left"
        )
        self.form_hint.pack(anchor="w", pady=(16, 12))

        button_row = tk.Frame(form_card, bg=self.white)
        button_row.pack(fill="x", padx=18, pady=(6, 24))

        tk.Button(
            button_row,
            text="✓  book appointment",
            command=self.book_appointment,
            bg=self.bg_tan,
            fg="white",
            relief="flat",
            font=("helvetica", 11, "bold"),
            padx=16,
            pady=14,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            button_row,
            text="clear",
            command=self.clear_booking_fields,
            bg=self.bg_soft,
            fg=self.text_dark,
            relief="flat",
            font=("helvetica", 11, "bold"),
            padx=16,
            pady=14,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

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

        search_bar = tk.Frame(wrap, bg=self.white, highlightbackground=self.line, highlightthickness=1)
        search_bar.pack(fill="x", pady=(0, 18))

        self.lookup_phone = tk.Entry(
            search_bar,
            font=("helvetica", 12),
            bg=self.white,
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
            bg=self.white,
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

        form = tk.Frame(wrap, bg=self.white, highlightbackground=self.line, highlightthickness=1)
        form.pack(fill="x")

        self.review_entries = {}

        fields = ["phone", "stylist id", "rating (1-5)"]

        for i, field in enumerate(fields):
            tk.Label(
                form,
                text=field,
                font=("helvetica", 10, "bold"),
                bg=self.white,
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
            bg=self.white,
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
            bg=self.white,
            highlightbackground=self.line,
            highlightthickness=1,
            height=78
        )
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            font=("helvetica", 10, "bold"),
            bg=self.white,
            fg=self.text_muted
        ).pack(anchor="w", padx=16, pady=(14, 4))

        value_label = tk.Label(
            card,
            text=value,
            font=("helvetica", 12, "bold"),
            bg=self.white,
            fg=self.text_dark
        )
        value_label.pack(anchor="w", padx=16)

        card.value_label = value_label
        return card

    def clear_stylist_tree(self):
        for item in self.stylist_tree.get_children():
            self.stylist_tree.delete(item)

    def load_categories(self):
        try:
            categories = load_categories_from_db()
            self.category_box["values"] = categories
            self.service_list.delete(0, tk.END)
            self.clear_stylist_tree()
            self.selection_status.config(text="step 1: choose a service from the left, then click a stylist row below")
        except Exception as err:
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
        self.selection_status.config(text="step 1: choose a service from the list")
        self.form_hint.config(text="step 2: select a stylist first to load available times")
        self.time_dropdown["values"] = []
        self.time_dropdown.set("")

        try:
            services = load_services_by_category(category)
            for service in services:
                self.service_list.insert(tk.END, service)
        except Exception as err:
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
        self.selection_status.config(text="step 2: click a stylist row below")
        self.form_hint.config(text="step 3: after selecting a stylist, choose date and time, then click book")
        self.time_dropdown["values"] = []
        self.time_dropdown.set("")
        self.load_stylists_for_service()

    def load_stylists_for_service(self):
        self.clear_stylist_tree()

        try:
            rows = load_stylists_for_service(self.selected_service_name)

            if not rows:
                self.selection_status.config(text="no stylists found for this service")
            else:
                self.selection_status.config(text="step 2: click a stylist row below")

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
        except Exception as err:
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
            text=f"selected: {self.selected_stylist_name}"
        )
        self.form_hint.config(
            text=f"great — {self.selected_stylist_name} selected. now choose a date, pick a time, fill in your info, and click book appointment."
        )
        self.update_time_options()

    def update_time_options(self, event=None):
        if not self.selected_stylist_id:
            self.time_dropdown["values"] = []
            self.time_dropdown.set("")
            return

        try:
            selected_date = self.date_picker.get_date().strftime("%Y-%m-%d")
            times = get_available_times(self.selected_stylist_id, selected_date)
            self.time_dropdown["values"] = times

            if times:
                self.time_dropdown.set(times[0])
            else:
                self.time_dropdown.set("")
        except Exception as err:
            messagebox.showerror("database error", str(err))

    def book_appointment(self):
        if not self.selected_service_id or not self.selected_stylist_id:
            messagebox.showwarning(
                "missing selection",
                "please choose a service and click a stylist first."
            )
            return

        first_name = self.booking_entries["first name"].get().strip()
        last_name = self.booking_entries["last name"].get().strip()
        phone = self.booking_entries["phone"].get().strip()
        email = self.booking_entries["email"].get().strip()
        appointment_date = self.date_picker.get_date().strftime("%Y-%m-%d")
        appointment_time = self.time_dropdown.get().strip()

        if not all([first_name, last_name, phone, email, appointment_time]):
            messagebox.showwarning(
                "missing fields",
                "please fill in first name, last name, phone, email, date, and time."
            )
            return

        try:
            client_id = get_or_create_client(first_name, last_name, phone, email)
            appointment_id = create_appointment(
                client_id,
                self.selected_stylist_id,
                self.selected_service_id,
                appointment_date,
                appointment_time
            )

            if appointment_id is None:
                messagebox.showerror("time unavailable", "that time is already booked for this stylist.")
                self.update_time_options()
                return

            messagebox.showinfo(
                "appointment booked",
                f"appointment #{appointment_id} booked with {self.selected_stylist_name} for {self.selected_service_name} on {appointment_date} at {appointment_time}."
            )
            self.clear_booking_fields()
            self.update_time_options()

        except Exception as err:
            messagebox.showerror("database error", str(err))

    def clear_booking_fields(self):
        for entry in self.booking_entries.values():
            entry.delete(0, tk.END)
        self.time_dropdown.set("")

    def view_bookings(self):
        phone = self.lookup_phone.get().strip()
        self.bookings_text.delete("1.0", tk.END)

        if not phone:
            messagebox.showwarning("missing phone", "please enter your phone number.")
            return

        try:
            rows = get_bookings_by_phone(phone)

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
        except Exception as err:
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
            result = submit_review_by_phone(phone, stylist_id, rating, review_text)

            if result == "no_client":
                messagebox.showerror("not found", "no client found with that phone number.")
            elif result == "not_completed":
                messagebox.showerror("not allowed", "you can only review after a completed appointment.")
            else:
                messagebox.showinfo("success", "review submitted successfully.")
                self.review_entries["phone"].delete(0, tk.END)
                self.review_entries["stylist id"].delete(0, tk.END)
                self.review_entries["rating (1-5)"].delete(0, tk.END)
                self.review_entries["review text"].delete("1.0", tk.END)

        except Exception as err:
            messagebox.showerror("database error", str(err))