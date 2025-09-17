import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def getmap(f):
    d = {}
    lines = open(f, encoding="utf-8").readlines()
    for line in lines:
        if " - " in line and not line.strip().startswith("#"):
            a,b = line.strip().split(" - ",1)
            d[a.strip()] = b.strip()
    return d

def dofile(fp, m, log=None):
    try:
        t = open(fp, encoding="utf-8").read()
    except Exception as e:
        if log: log(f"couldnt read {fp} ({e})\n")
        return False
    orig = t
    def sub(match):
        prefix = match.group(1)
        n = match.group(2)
        if n in m:
            if log: log(f"   {fp} {prefix} {n} replaced with {m[n]}\n")
            return f"{prefix} = {m[n]};"
        else:
            if log: log(f"   {fp} {prefix} {n} not in map\n")
            return match.group(0)
    t = re.sub(r"(target[Rr]ooms?)\s*=\s*(\d+)\s*;", sub, t)
    if t != orig:
        try:
            shutil.copyfile(fp, fp+".bak")
        except:
            pass
        open(fp,"w",encoding="utf-8").write(t)
        if log: log(f"   wrote {fp}\n")
        return True
    return False

def find_folders(project):
    folders = []
    for root, dirs, files in os.walk(project):
        for d in dirs:
            if d.lower() in ("objects", "scripts"):
                folders.append(os.path.join(root, d))
    return folders

def proc(proj, mapping, log):
    ch = 0
    folders = find_folders(proj)
    if not folders:
        log("No /objects or /scripts folders found in project.\n")
        return 0
    for folder in folders:
        log(f"Looking in: {folder}\n")
        for root, dirs, files in os.walk(folder):
            for f in files:
                fpath = os.path.join(root, f)
                # Only .gml and .yy in objects, only .gml in scripts
                if "/objects" in root.replace("\\", "/"):
                    if f.endswith(".gml") or f.endswith(".yy"):
                        log(f" Checking file: {fpath}\n")
                        if dofile(fpath, mapping, log):
                            ch += 1
                elif "/scripts" in root.replace("\\", "/"):
                    if f.endswith(".gml"):
                        log(f" Checking file: {fpath}\n")
                        if dofile(fpath, mapping, log):
                            ch += 1
    return ch

def dark(w):
    c1 = "#23272e"
    c2 = "#e6e6e6"
    c3 = "#007fff"
    w.tk_setPalette(background=c1, foreground=c2, activeBackground=c3, activeForeground=c2)
    w.option_add("*TButton*background", "#2d333b")
    w.option_add("*TButton*foreground", c2)
    w.option_add("*Entry.Background", "#2d333b")
    w.option_add("*Entry.Foreground", c2)
    w.option_add("*Label.Background", c1)
    w.option_add("*Label.Foreground", c2)
    w.option_add("*Button.Background", "#2d333b")
    w.option_add("*Button.Foreground", c2)
    w.option_add("*Text.Background", c1)
    w.option_add("*Text.Foreground", c2)
    w.option_add("*ScrolledText.Background", c1)
    w.option_add("*ScrolledText.Foreground", c2)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GM2 Room Index Tool")
        try:
            root.iconbitmap("gamemaker.ico")
        except: pass
        dark(self.root)
        self.p = tk.StringVar()
        self.m = tk.StringVar()
        f = tk.Frame(root, bg="#23272e")
        f.pack(padx=10, pady=10)
        tk.Label(f,text="Project Folder:").grid(row=0,column=0,sticky="e")
        tk.Entry(f,textvariable=self.p,width=40,bg="#2d333b",fg="#e6e6e6",insertbackground="#e6e6e6").grid(row=0,column=1)
        tk.Button(f,text="...",command=self.pickp).grid(row=0,column=2,padx=5)
        tk.Label(f,text="Mapper File:").grid(row=1,column=0,sticky="e")
        tk.Entry(f,textvariable=self.m,width=40,bg="#2d333b",fg="#e6e6e6",insertbackground="#e6e6e6").grid(row=1,column=1)
        tk.Button(f,text="...",command=self.pickm).grid(row=1,column=2,padx=5)
        tk.Button(f,text="GO",command=self.run,bg="#007fff",fg="#e6e6e6",activebackground="#0059b3").grid(row=2,columnspan=3,pady=(10,0))
        self.log = scrolledtext.ScrolledText(root,width=80,height=25,state='disabled',bg="#23272e",fg="#e6e6e6",insertbackground="#e6e6e6")
        self.log.pack(padx=10,pady=(0,10))
    def logmsg(self, msg):
        self.log.config(state='normal')
        self.log.insert(tk.END, msg)
        self.log.see(tk.END)
        self.log.config(state='disabled')
        self.root.update()
    def pickp(self):
        path = filedialog.askdirectory(title="proj folder")
        if path: self.p.set(path)
    def pickm(self):
        path = filedialog.askopenfilename(title="map file",filetypes=[("txt","*.txt"),("all","*.*")])
        if path: self.m.set(path)
    def run(self):
        proj = self.p.get()
        mapf = self.m.get()
        if not os.path.isdir(proj):
            messagebox.showerror("err","bad proj folder")
            return
        if not os.path.isfile(mapf):
            messagebox.showerror("err","bad map file")
            return
        try:
            mapping = getmap(mapf)
        except Exception as e:
            messagebox.showerror("err",f"couldnt read map file: {e}")
            return
        self.log.config(state='normal')
        self.log.delete('1.0',tk.END)
        self.log.config(state='disabled')
        self.logmsg("Looking for targetRoom/targetRooms assignments in /objects (.gml/.yy) and /scripts (.gml)...\n")
        c = proc(proj, mapping, self.logmsg)
        self.logmsg(f"\nDone! {c} files changed.\n")

if __name__ == "__main__":
    r = tk.Tk()
    App(r)
    r.mainloop()