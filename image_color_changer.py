import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import numpy as np
from colorthief import ColorThief
import customtkinter as ctk

class ImageColorChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Color Changer")
        self.root.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.original_image = None
        self.modified_image = None
        self.image_path = None
        self.dominant_color = None
        self.selected_images = []
        self.pick_color_mode = False
        self.selected_source_color = None
        self.display_scale = 1.0
        self.display_offset = (0, 0)
        self.history = []
        self.history_index = -1
        
        self.setup_ui()
        
    def load_single_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Single Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path).convert("RGBA")
                self.modified_image = self.original_image.copy()
                self.history = [self.modified_image.copy()]
                self.history_index = 0
                self.dominant_color = self.get_dominant_color(file_path)
                self.selected_images = [file_path]
                self.display_image()
                self.info_label.configure(text=f"Loaded single image: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error while loading image: {str(e)}")
                
    def load_multiple_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_paths:
            try:
                self.selected_images = list(file_paths)
                self.image_path = file_paths[0]
                self.original_image = Image.open(file_paths[0]).convert("RGBA")
                self.modified_image = self.original_image.copy()
                self.history = [self.modified_image.copy()]
                self.history_index = 0
                self.dominant_color = self.get_dominant_color(file_paths[0])
                self.display_image()
                self.info_label.configure(text=f"{len(file_paths)} images selected. First image loaded: {os.path.basename(file_paths[0])}")
            except Exception as e:
                messagebox.showerror("Error", f"Error while loading images: {str(e)}")
        
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root, corner_radius=12)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)

        left_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(left_frame, text="Preview", font=("Segoe UI Semibold", 16))
        header.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 0))

        self.setup_image_display(left_frame)

        right_frame = ctk.CTkScrollableFrame(main_frame, width=380, corner_radius=12)
        right_frame.grid(row=0, column=1, sticky="ns")
        right_frame.grid_columnconfigure(0, weight=1)

        self.setup_controls(right_frame)
        
    def setup_image_display(self, parent):
        image_frame = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        image_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(image_frame, bg="#0f0f12", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.scrollbar_v = ctk.CTkScrollbar(image_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.scrollbar_h = ctk.CTkScrollbar(image_frame, orientation="horizontal", command=self.canvas.xview)
        self.scrollbar_h.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        self.draw_placeholder()
        
    def setup_controls(self, parent):
        section_files = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_files.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        section_files.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(section_files, text="Files", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        ctk.CTkButton(section_files, text="Select Single Image", command=self.load_single_image).grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(section_files, text="Select Multiple Images", command=self.load_multiple_images).grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        section_color = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_color.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        section_color.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(section_color, text="Color", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6), columnspan=2)
        ctk.CTkLabel(section_color, text="Target Color").grid(row=1, column=0, sticky="w", padx=12)
        self.color_var = tk.StringVar(value="#FF0000")
        self.color_entry = ctk.CTkEntry(section_color, textvariable=self.color_var)
        self.color_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=6)
        self.color_button = ctk.CTkButton(section_color, text="", width=36, command=self.choose_color, fg_color="#FF0000")
        self.color_button.grid(row=1, column=2, sticky="e", padx=12)
        self.color_var.trace_add('write', lambda *_: self.on_color_var_change())
        ctk.CTkButton(section_color, text="Color Palette", command=self.show_color_palette).grid(row=2, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 12))

        ctk.CTkLabel(section_color, text="Source Color").grid(row=3, column=0, sticky="w", padx=12)
        self.source_color_var = tk.StringVar(value="")
        self.source_color_entry = ctk.CTkEntry(section_color, textvariable=self.source_color_var)
        self.source_color_entry.grid(row=3, column=1, sticky="ew", padx=(0, 12), pady=6)
        self.source_color_button = ctk.CTkButton(section_color, text="", width=36, fg_color="#333333", state="disabled")
        self.source_color_button.grid(row=3, column=2, sticky="e", padx=12)
        self.pick_color_btn = ctk.CTkButton(section_color, text="Pick Color From Image", command=self.toggle_pick_color)
        self.pick_color_btn.grid(row=4, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 12))

        section_settings = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_settings.grid(row=2, column=0, sticky="ew", padx=12, pady=6)
        section_settings.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(section_settings, text="Settings", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        ctk.CTkLabel(section_settings, text="Color Change Strength").grid(row=1, column=0, sticky="w", padx=12)
        self.intensity_var = tk.DoubleVar(value=0.5)
        self.intensity_slider = ctk.CTkSlider(section_settings, from_=0.0, to=1.0, number_of_steps=100, command=lambda v: self.intensity_var.set(v))
        self.intensity_slider.set(self.intensity_var.get())
        self.intensity_slider.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        ctk.CTkLabel(section_settings, text="Color Match Sensitivity").grid(row=3, column=0, sticky="w", padx=12)
        self.sensitivity_var = tk.DoubleVar(value=0.3)
        self.sensitivity_slider = ctk.CTkSlider(section_settings, from_=0.1, to=1.0, number_of_steps=90, command=lambda v: self.sensitivity_var.set(v))
        self.sensitivity_slider.set(self.sensitivity_var.get())
        self.sensitivity_slider.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))

        section_history = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_history.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        section_history.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(section_history, text="History", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        ctk.CTkButton(section_history, text="Undo", command=self.undo).grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(section_history, text="Redo", command=self.redo).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        section_actions = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_actions.grid(row=4, column=0, sticky="ew", padx=12, pady=6)
        section_actions.grid_columnconfigure(0, weight=1)
        section_actions.grid_columnconfigure(1, weight=1)
        section_actions.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(section_actions, text="Actions", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))
        ctk.CTkButton(section_actions, text="Apply Color", command=self.change_color).grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(section_actions, text="Reset", command=self.reset_image).grid(row=2, column=0, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(section_actions, text="Save", command=self.save_image).grid(row=2, column=1, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(section_actions, text="Batch Save", command=self.save_all_images).grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12))

        section_info = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="#2A2D2E")
        section_info.grid(row=5, column=0, sticky="ew", padx=12, pady=(6, 12))
        section_info.grid_columnconfigure(0, weight=1)
        self.info_label = ctk.CTkLabel(section_info, text="Select an image and start changing colors", wraplength=300, justify="left")
        self.info_label.grid(row=0, column=0, sticky="w", padx=12, pady=12)
        
        powered_label = ctk.CTkLabel(section_info, text="Powered by Eneswunbeaten", font=("Segoe UI", 10), text_color="#6b7280")
        powered_label.grid(row=1, column=0, sticky="e", padx=12, pady=(0, 12))

    def draw_placeholder(self):
        try:
            self.canvas.delete("all")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            if w < 2 or h < 2:
                return
            text = "Preview area\nSelect an image from the right"
            self.canvas.create_text(
                w // 2,
                h // 2,
                text=text,
                fill="#6b7280",
                font=("Segoe UI", 14),
                justify="center",
                anchor="center",
                tags=("__placeholder__",),
            )
            self.canvas.configure(scrollregion=(0, 0, w, h))
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        except Exception:
            pass

    def push_history(self):
        try:
            if self.modified_image is None:
                return
            if self.history_index < len(self.history) - 1:
                self.history = self.history[: self.history_index + 1]
            self.history.append(self.modified_image.copy())
            self.history_index += 1
        except Exception:
            pass

    def undo(self):
        if self.history_index <= 0:
            return
        self.history_index -= 1
        self.modified_image = self.history[self.history_index].copy()
        self.display_image()
        self.info_label.configure(text="Geri alındı")

    def redo(self):
        if self.history_index >= len(self.history) - 1:
            return
        self.history_index += 1
        self.modified_image = self.history[self.history_index].copy()
        self.display_image()
        self.info_label.configure(text="İleri alındı")

                
    def get_dominant_color(self, image_path):
        try:
            color_thief = ColorThief(image_path)
            dominant_color = color_thief.get_color(quality=1)
            return dominant_color
        except:
            return (128, 128, 128)
            
    def display_image(self):
        if self.modified_image:
            self.canvas.delete("all")
            
            display_image = self.modified_image.copy()
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_width, img_height = display_image.size
                
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y, 1.0)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                self.photo = ImageTk.PhotoImage(display_image)
                
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.display_scale = scale
                self.display_offset = (x, y)
                
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color", color=self.color_var.get())
        if color[1]:
            hex_val = color[1].upper()
            self.color_var.set(hex_val)
            self.color_button.configure(bg=hex_val)
            
    def show_color_palette(self):
        palette_window = tk.Toplevel(self.root)
        palette_window.title("Color Palette")
        palette_window.geometry("400x300")
        
        colors = [
            "#FF0000", "#FF4500", "#FF8C00", "#FFD700", "#FFFF00",
            "#ADFF2F", "#00FF00", "#00FA9A", "#00FFFF", "#00BFFF",
            "#0000FF", "#8A2BE2", "#FF00FF", "#FF1493", "#FF69B4",
            "#F5F5DC", "#A0522D", "#808080", "#000000", "#FFFFFF"
        ]
        
        for i, color in enumerate(colors):
            row = i // 5
            col = i % 5
            btn = tk.Button(palette_window, bg=color, width=8, height=3,
                          command=lambda c=color: self.select_palette_color(c, palette_window))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
    def select_palette_color(self, color, window):
        self.color_var.set(color)
        self.color_button.configure(bg=color)
        window.destroy()
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def on_color_var_change(self):
        try:
            rgb = self.parse_color_input(self.color_var.get())
            hex_val = self.rgb_to_hex(rgb).upper()
            self.color_button.configure(bg=hex_val)
        except Exception:
            pass

    def toggle_pick_color(self):
        if self.modified_image is None:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        self.pick_color_mode = not self.pick_color_mode
        self.pick_color_btn.configure(text="Renk Seçimi Açık" if self.pick_color_mode else "Görselden Renk Seç")

    def on_canvas_click(self, event):
        if not self.pick_color_mode or self.modified_image is None:
            return
        x = int((event.x - self.display_offset[0]) / max(self.display_scale, 1e-6))
        y = int((event.y - self.display_offset[1]) / max(self.display_scale, 1e-6))
        w, h = self.modified_image.size
        if 0 <= x < w and 0 <= y < h:
            rgba = self.modified_image.getpixel((x, y))
            rgb = rgba[:3]
            self.selected_source_color = rgb
            hex_val = self.rgb_to_hex(rgb).upper()
            self.source_color_var.set(hex_val)
            self.source_color_button.configure(fg_color=hex_val)
            self.pick_color_mode = False
            self.pick_color_btn.configure(text="Görselden Renk Seç")

    def parse_color_input(self, color_text):
        text = color_text.strip()
        if text.startswith('#'):
            text = text.upper()
            if len(text) == 7:
                return self.hex_to_rgb(text)
            if len(text) == 4:
                r = text[1]*2
                g = text[2]*2
                b = text[3]*2
                return self.hex_to_rgb('#' + r + g + b)
        if len(text) in (3, 6) and all(c in '0123456789ABCDEFabcdef' for c in text):
            return self.hex_to_rgb('#' + text.upper())
        if ',' in text or ' ' in text:
            sep = ',' if ',' in text else ' '
            parts = [p for p in text.split(sep) if p]
            if len(parts) == 3:
                r, g, b = [int(float(p)) for p in parts]
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                return (r, g, b)
        raise ValueError("Geçersiz renk kodu")

    def rgb_to_hex(self, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)
        
    def change_color(self):
        if self.modified_image is None:
            messagebox.showwarning("Uyarı", "Önce bir görsel seçin")
            return
            
        try:
            target_color = self.parse_color_input(self.color_var.get())
            intensity = self.intensity_var.get()
            sensitivity = self.sensitivity_var.get()
            src_dom = None
            if self.selected_source_color is not None and self.color_var.get().strip() != "":
                src_dom = self.selected_source_color
            
            self.push_history()
            self.modified_image = self.apply_color_change(
                self.original_image.copy(),
                target_color,
                intensity,
                sensitivity,
                src_dom if src_dom is not None else self.dominant_color
            )
            
            self.display_image()
            self.info_label.configure(text="Color applied")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error while applying color: {str(e)}")
            
    def apply_color_change(self, image, target_color, intensity, sensitivity, source_dominant_color=None):
        img_array = np.array(image)
        if len(img_array.shape) != 3 or img_array.shape[2] != 4:
            return image
        rgb_array = img_array[:, :, :3].astype(np.float32)
        alpha_array = img_array[:, :, 3].astype(np.float32)
        target_rgb = np.array(target_color, dtype=np.float32)
        dominant = np.array(source_dominant_color if source_dominant_color is not None else self.dominant_color, dtype=np.float32)
        if dominant is None:
            return image
        diff = rgb_array - dominant
        dist = np.sqrt(np.sum(np.square(diff), axis=2))
        thresh = sensitivity * 255.0
        mask = (alpha_array > 0) & (dist < thresh)
        with np.errstate(divide='ignore', invalid='ignore'):
            factor = intensity * (1.0 - (dist / thresh))
        factor = np.clip(factor, 0.0, 1.0)
        factor3 = np.repeat(factor[:, :, np.newaxis], 3, axis=2)
        blend = rgb_array * (1.0 - factor3) + target_rgb * factor3
        rgb_array[mask] = blend[mask]
        rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)
        result_array = np.dstack((rgb_array, alpha_array.astype(np.uint8)))
        return Image.fromarray(result_array)
        
    def reset_image(self):
        if self.original_image:
            self.push_history()
            self.modified_image = self.original_image.copy()
            self.display_image()
            self.info_label.configure(text="Görsel sıfırlandı")
            
    def save_image(self):
        if self.modified_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return
            
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
            
        try:
            from datetime import datetime
            import os
            
            original_dir = os.path.dirname(self.image_path)
            original_filename = os.path.splitext(os.path.basename(self.image_path))[0]
            color_code = self.rgb_to_hex(self.parse_color_input(self.color_var.get())).replace("#", "").upper()
            current_date = datetime.now().strftime("%Y-%m-%d")
            folder_name = f"{color_code} - {current_date}"
            save_dir = os.path.join(original_dir, folder_name)
            
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            new_filename = f"{original_filename}_renkli.png"
            save_path = os.path.join(save_dir, new_filename)
            
            self.push_history()
            self.modified_image.save(save_path, "PNG")
            messagebox.showinfo("Success", f"Image saved successfully:\n{save_path}")
            self.info_label.configure(text=f"Saved: {save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving image: {str(e)}")
            
    def save_all_images(self):
        if not self.selected_images:
            messagebox.showwarning("Warning", "No images to save")
            return
            
        try:
            from datetime import datetime
            import os
            
            color_code = self.rgb_to_hex(self.parse_color_input(self.color_var.get())).replace("#", "").upper()
            current_date = datetime.now().strftime("%Y-%m-%d")
            folder_name = f"{color_code} - {current_date}"
            
            saved_count = 0
            error_count = 0
            
            for image_path in self.selected_images:
                try:
                    original_dir = os.path.dirname(image_path)
                    original_filename = os.path.splitext(os.path.basename(image_path))[0]
                    
                    save_dir = os.path.join(original_dir, folder_name)
                    
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    
                    original_img = Image.open(image_path).convert("RGBA")
                    dom = self.selected_source_color if (self.selected_source_color is not None and self.color_var.get().strip() != "") else self.get_dominant_color(image_path)
                    modified_img = self.apply_color_change(
                        original_img.copy(),
                        self.parse_color_input(self.color_var.get()),
                        self.intensity_var.get(),
                        self.sensitivity_var.get(),
                        dom
                    )
                    
                    new_filename = f"{original_filename}_renkli.png"
                    save_path = os.path.join(save_dir, new_filename)
                    
                    modified_img.save(save_path, "PNG")
                    saved_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error: {image_path} - {str(e)}")
            
            if error_count == 0:
                messagebox.showinfo("Success", f"{saved_count} images saved successfully:\n{save_dir}")
            else:
                messagebox.showwarning("Partial Success", f"{saved_count} images saved, {error_count} errors")
            self.info_label.configure(text=f"Batch save done: {saved_count} OK, {error_count} Errors")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error during batch save: {str(e)}")
                
    def on_canvas_configure(self, event):
        if self.modified_image is None:
            self.draw_placeholder()
        else:
            self.display_image()

def main():
    root = tk.Tk()
    app = ImageColorChanger(root)
    
    root.bind("<Configure>", lambda e: app.on_canvas_configure(e))
    
    root.mainloop()

if __name__ == "__main__":
    main() 