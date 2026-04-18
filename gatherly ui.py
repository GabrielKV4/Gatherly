import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import json, os, uuid

FILE = 'study_groups.json'
BG = '#cfe0ee'
CARD = '#d9e7f2'
BTN = '#f2f2f2'

class App:
    def __init__(self, root):
        self.root = root
        root.title('Study Groups')
        root.geometry('980x620')
        root.configure(bg=BG)
        self.groups = []
        self.joined_ids = set()
        self.load()
        self.main = tk.Frame(root, bg=BG)
        self.create = tk.Frame(root, bg=BG)
        self.build_main()
        self.build_create()
        self.show_main()

    def load(self):
        if os.path.exists(FILE):
            with open(FILE, 'r') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.groups = data.get('groups', [])
                        self.joined_ids = set(data.get('joined_ids', []))
                    else:
                        self.groups = data
                except json.JSONDecodeError:
                    self.groups = []

    def save(self):
        with open(FILE, 'w') as f:
            json.dump({'groups': self.groups, 'joined_ids': list(self.joined_ids)}, f, indent=2)

    def clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def build_main(self):
        self.clear(self.main)
        top = tk.Frame(self.main, bg=BG)
        top.pack(fill='x', padx=20, pady=20)
        tk.Button(top, text='Create', bg=BTN, font=('Arial', 18), width=10, command=self.show_create).pack(side='left')
        
        self.search = tk.Entry(top, font=('Arial', 16), width=24)
        self.search.pack(side='right')
        self.search.bind('<KeyRelease>', lambda e: self.render_cards())
        
        self.cards = tk.Frame(self.main, bg=BG)
        self.cards.pack(fill='both', expand=True, padx=20)
        self.render_cards()

    def render_cards(self):
        self.clear(self.cards)
        q = self.search.get().lower() if hasattr(self, 'search') else ''
        shown = [g for g in self.groups if q in g['name'].lower() or q in g['topic'].lower()]
        
        for g in shown:
            card = tk.Frame(self.cards, bg=CARD, bd=1, relief='solid')
            card.pack(fill='x', pady=12, ipady=10)
            
            name_lbl = tk.Label(card, text=g['name'], bg=CARD, font=('Arial', 16, 'bold'), cursor='hand2')
            name_lbl.grid(row=0, column=0, sticky='w', padx=18, pady=(8, 0))
            name_lbl.bind('<Button-1>', lambda e, x=g: self.open_chat(x))
            
            tk.Label(card, text=g['date'], bg='white', width=20, font=('Arial', 12)).grid(row=0, column=1, padx=10)
            tk.Label(card, text=f"{g['people']} people", bg=CARD, font=('Arial', 12)).grid(row=0, column=2, padx=20)
            tk.Label(card, text=g['topic'], bg='white', font=('Arial', 11), width=15).grid(row=1, column=0, sticky='w', padx=25, pady=8)
            
            is_joined = g['id'] in self.joined_ids
            join_txt = 'Joined' if is_joined else '+1 Join'
            btn_state = 'disabled' if is_joined else 'normal'
            
            tk.Button(card, text=join_txt, state=btn_state, command=lambda x=g: self.join_group(x)).grid(row=1, column=2)
            card.grid_columnconfigure(1, weight=1)

    def join_group(self, g):
        if g['id'] in self.joined_ids:
            return
        g['people'] += 1
        self.joined_ids.add(g['id'])
        if 'messages' not in g:
            g['messages'] = []
        self.save()
        self.render_cards()

    def build_create(self):
        self.clear(self.create)
        tk.Label(self.create, text='Name your study group', bg=BG, font=('Arial', 24)).pack(anchor='w', padx=60, pady=(40, 10))
        self.name_e = tk.Entry(self.create, font=('Arial', 18), width=40)
        self.name_e.pack(padx=60)
        
        tk.Label(self.create, text='What is the topic?', bg=BG, font=('Arial', 24)).pack(anchor='w', padx=60, pady=(30, 10))
        self.topic_e = tk.Entry(self.create, font=('Arial', 18), width=40)
        self.topic_e.pack(padx=60)
        
        tk.Label(self.create, text='Date (e.g. June 5th)', bg=BG, font=('Arial', 18)).pack(anchor='w', padx=60, pady=(30, 10))
        self.date_e = tk.Entry(self.create, font=('Arial', 16), width=30)
        self.date_e.pack(padx=60)
        
        tk.Button(self.create, text='Create Group', font=('Arial', 20), bg=BTN, width=12, command=self.add_group).pack(pady=40)
        tk.Button(self.create, text='Back', command=self.show_main).pack()

    def add_group(self):
        n = self.name_e.get().strip()
        t = self.topic_e.get().strip()
        d = self.date_e.get().strip()
        if not n or not t or not d:
            messagebox.showerror('Missing info', 'Fill every box.')
            return
        
        new_id = str(uuid.uuid4())
        self.groups.append({
            'id': new_id,
            'name': n,
            'topic': t,
            'date': d,
            'people': 1,
            'owner': 'You',
            'messages': []
        })
        self.joined_ids.add(new_id) # Owner automatically joins
        self.save()
        self.name_e.delete(0, 'end'); self.topic_e.delete(0, 'end'); self.date_e.delete(0, 'end')
        self.render_cards()
        self.show_main()

    def open_chat(self, g):
        if g['id'] not in self.joined_ids:
            messagebox.showinfo('Join first', 'You need to join this study group first.')
            return
        
        win = tk.Toplevel(self.root)
        win.title(g['name'])
        win.geometry('600x550')
        win.configure(bg=BG)

        tk.Label(win, text=g['name'], bg=BG, font=('Arial', 22, 'bold')).pack(pady=10)

        txt = tk.Text(win, height=15, width=65)
        txt.pack(padx=10, pady=10)
        txt.insert('end', '\n'.join(g.get('messages', [])))
        txt.config(state='disabled')

        entry_frame = tk.Frame(win, bg=BG)
        entry_frame.pack(fill='x', padx=10)

        entry = tk.Entry(entry_frame, font=('Arial', 14), width=40)
        entry.pack(side='left', padx=5, pady=10)

        def send():
            m = entry.get().strip()
            if not m: return
            g.setdefault('messages', []).append('You: ' + m)
            txt.config(state='normal')
            txt.delete('1.0', 'end')
            txt.insert('end', '\n'.join(g['messages']))
            txt.config(state='disabled')
            txt.see('end')
            entry.delete(0, 'end')
            self.save()

        tk.Button(entry_frame, text='Send', command=send, bg=BTN).pack(side='left', padx=5)

        if g.get('owner') == 'You':
            admin = tk.Frame(win, bg=BG)
            admin.pack(fill='x', pady=20)
            tk.Label(admin, text='Admin:', bg=BG, font=('Arial', 12, 'bold')).pack(side='left', padx=10)
            tk.Button(admin, text='Delete Group', fg='red', command=lambda: self.delete_group(g, win)).pack(side='left', padx=5)
            tk.Button(admin, text='Clear Chat', command=lambda: self.clear_chat(g, txt)).pack(side='left', padx=5)

    def delete_group(self, g, win):
        if messagebox.askyesno("Confirm", "Delete this group?"):
            self.groups = [x for x in self.groups if x['id'] != g['id']]
            self.joined_ids.discard(g['id'])
            self.save()
            win.destroy()
            self.render_cards()

    def clear_chat(self, g, txt):
        g['messages'] = []
        txt.config(state='normal')
        txt.delete('1.0', 'end')
        txt.config(state='disabled')
        self.save()

    def show_main(self):
        self.create.pack_forget()
        self.main.pack(fill='both', expand=True)

    def show_create(self):
        self.main.pack_forget()
        self.create.pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
