#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from spotify_auth import get_spotify_client, load_config, save_config, save_credentials
import sys

class SpotifyPlaylistAdder:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("320x260")
        self.root.attributes('-topmost', True)  # Always on top
        self.root.resizable(False, False)

        # Colors - Jony Ive minimalist palette
        self.bg_color = '#0a0a0a'
        self.fg_color = '#ffffff'
        self.accent_color = '#1db954'  # Spotify green
        self.secondary_fg = '#b3b3b3'
        self.hover_color = '#1a1a1a'

        # Semi-transparent background
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg=self.bg_color)

        # Remove window decorations for sleek look
        self.root.overrideredirect(True)

        # Additional macOS-specific styling to remove all chrome
        try:
            # Try to remove macOS title bar if overrideredirect didn't work
            self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'plain', 'none')
        except:
            pass

        # Make window draggable
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)
        self.offset_x = 0
        self.offset_y = 0

        self.sp = None
        self.current_track = None
        self.current_track_id = None
        self.playlists = []
        self.running = True
        self.last_added_track = None
        self.track_in_playlist = False

        # Create UI first
        self.create_widgets()

        # Initialize Spotify client (after UI is created)
        self.init_spotify()

        # Start background thread for track monitoring
        self.monitor_thread = threading.Thread(target=self.monitor_current_track, daemon=True)
        self.monitor_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_move(self, event):
        """Start dragging the window."""
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        """Drag the window."""
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f'+{x}+{y}')

    def init_spotify(self):
        """Initialize Spotify client with credentials."""
        config = load_config()

        if not config.get('client_id') or not config.get('client_secret'):
            messagebox.showerror("Setup Required",
                               "Please run setup_auth.py first to configure Spotify authentication.\n\n"
                               "In terminal:\n"
                               "  python setup_auth.py")
            sys.exit(1)

        try:
            self.sp = get_spotify_client()
            self.load_playlists()
        except Exception as e:
            messagebox.showerror("Authentication Error",
                               f"Failed to authenticate with Spotify:\n{str(e)}\n\n"
                               "Try running: python setup_auth.py")
            sys.exit(1)


    def create_widgets(self):
        """Create the UI components with minimalist black design."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=18)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Close button (minimal, top right)
        close_btn = tk.Label(main_frame, text="✕", font=('SF Pro Display', 11),
                            fg=self.secondary_fg, bg=self.bg_color, cursor='hand2')
        close_btn.place(x=280, y=0)
        close_btn.bind('<Button-1>', lambda e: self.on_close())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=self.fg_color))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=self.secondary_fg))

        # Track info (large, prominent)
        self.track_label = tk.Label(main_frame, text="No track playing",
                                    font=('SF Pro Display', 11), fg=self.fg_color,
                                    bg=self.bg_color, wraplength=280, justify=tk.LEFT,
                                    anchor='w')
        self.track_label.pack(fill=tk.X, pady=(15, 10))

        # Playback controls (back, play/pause, next) - centered
        controls_container = tk.Frame(main_frame, bg=self.bg_color)
        controls_container.pack(fill=tk.X, pady=(0, 15))

        controls_frame = tk.Frame(controls_container, bg=self.bg_color)
        controls_frame.pack(anchor='center')

        # Previous button
        prev_btn = tk.Label(controls_frame, text="⏮",
                           font=('SF Pro Display', 16),
                           fg=self.secondary_fg, bg=self.bg_color,
                           cursor='hand2')
        prev_btn.pack(side=tk.LEFT, padx=8)
        prev_btn.bind('<Button-1>', lambda e: self.previous_track())
        prev_btn.bind('<Enter>', lambda e: prev_btn.config(fg=self.fg_color))
        prev_btn.bind('<Leave>', lambda e: prev_btn.config(fg=self.secondary_fg))

        # Play/Pause button
        self.play_pause_btn = tk.Label(controls_frame, text="⏸",
                                       font=('SF Pro Display', 18),
                                       fg=self.fg_color, bg=self.bg_color,
                                       cursor='hand2')
        self.play_pause_btn.pack(side=tk.LEFT, padx=20)
        self.play_pause_btn.bind('<Button-1>', lambda e: self.toggle_play_pause())
        self.play_pause_btn.bind('<Enter>', lambda e: self.play_pause_btn.config(fg=self.accent_color))
        self.play_pause_btn.bind('<Leave>', lambda e: self.play_pause_btn.config(fg=self.fg_color))

        # Next button
        next_btn = tk.Label(controls_frame, text="⏭",
                           font=('SF Pro Display', 16),
                           fg=self.secondary_fg, bg=self.bg_color,
                           cursor='hand2')
        next_btn.pack(side=tk.LEFT, padx=8)
        next_btn.bind('<Button-1>', lambda e: self.next_track())
        next_btn.bind('<Enter>', lambda e: next_btn.config(fg=self.fg_color))
        next_btn.bind('<Leave>', lambda e: next_btn.config(fg=self.secondary_fg))

        # Playlist dropdown - custom implementation for better control
        self.playlist_var = tk.StringVar()

        # Dropdown button that triggers menu (with border)
        dropdown_container = tk.Frame(main_frame, bg=self.secondary_fg, height=38)
        dropdown_container.pack(fill=tk.X, pady=(0, 12))
        dropdown_container.pack_propagate(False)

        # Inner frame for actual content (creates border effect)
        inner_dropdown = tk.Frame(dropdown_container, bg=self.hover_color)
        inner_dropdown.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.playlist_button = tk.Label(inner_dropdown,
                                       textvariable=self.playlist_var,
                                       font=('SF Pro Display', 10),
                                       fg=self.fg_color,
                                       bg=self.hover_color,
                                       anchor='w',
                                       padx=12,
                                       cursor='hand2')
        self.playlist_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dropdown arrow
        arrow_label = tk.Label(inner_dropdown, text="▾",
                              font=('SF Pro Display', 10),
                              fg=self.secondary_fg,
                              bg=self.hover_color,
                              padx=12,
                              cursor='hand2')
        arrow_label.pack(side=tk.RIGHT)

        # Create menu for playlist selection
        self.playlist_menu = tk.Menu(self.root, tearoff=0,
                                    bg='#1a1a1a',
                                    fg=self.fg_color,
                                    activebackground=self.accent_color,
                                    activeforeground='#ffffff',
                                    bd=0,
                                    relief='flat',
                                    font=('SF Pro Display', 10))

        # Bind click to show menu
        self.playlist_button.bind('<Button-1>', self.show_playlist_menu)
        arrow_label.bind('<Button-1>', self.show_playlist_menu)

        # Add button (prominent, Spotify green) - using Label for full color control
        button_container = tk.Frame(main_frame, bg=self.accent_color, height=44)
        button_container.pack(fill=tk.X, pady=(0, 8))
        button_container.pack_propagate(False)

        self.add_button = tk.Label(button_container, text="Add to Playlist",
                                   font=('SF Pro Display', 11, 'bold'),
                                   fg='#ffffff',
                                   bg=self.accent_color,
                                   cursor='hand2')
        self.add_button.pack(fill=tk.BOTH, expand=True)

        # Bind click and hover events
        self.add_button.bind('<Button-1>', lambda e: self.add_to_playlist())
        self.add_button.bind('<Enter>', lambda e: self.add_button.config(bg='#1ed760'))
        self.add_button.bind('<Leave>', lambda e: self.add_button.config(bg=self.accent_color))

        # Also bind to container for full clickable area
        button_container.bind('<Button-1>', lambda e: self.add_to_playlist())
        button_container.bind('<Enter>', lambda e: [self.add_button.config(bg='#1ed760'), button_container.config(bg='#1ed760')])
        button_container.bind('<Leave>', lambda e: [self.add_button.config(bg=self.accent_color), button_container.config(bg=self.accent_color)])

        # Refresh button (minimal, bottom right)
        refresh_btn = tk.Label(main_frame, text="↻", font=('SF Pro Display', 14),
                              fg=self.secondary_fg, bg=self.bg_color, cursor='hand2')
        refresh_btn.place(x=280, y=175)
        refresh_btn.bind('<Button-1>', lambda e: self.load_playlists())
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(fg=self.fg_color))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(fg=self.secondary_fg))

    def show_playlist_menu(self, event):
        """Show the playlist selection menu."""
        try:
            self.playlist_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.playlist_menu.grab_release()

    def select_playlist(self, playlist_name):
        """Handle playlist selection from menu."""
        self.playlist_var.set(playlist_name)
        config = load_config()
        config['selected_playlist'] = playlist_name
        save_config(config)
        # Check if current track is in the newly selected playlist
        threading.Thread(target=self.check_track_in_playlist, daemon=True).start()

    def load_playlists(self):
        """Load user's playlists from Spotify."""
        try:
            # Fetch all playlists (paginate through results)
            self.playlists = []
            results = self.sp.current_user_playlists(limit=50)
            self.playlists.extend([(p['name'], p['id']) for p in results['items']])

            # Continue fetching if there are more playlists
            while results['next']:
                results = self.sp.next(results)
                self.playlists.extend([(p['name'], p['id']) for p in results['items']])

            # Clear and rebuild menu
            self.playlist_menu.delete(0, tk.END)

            playlist_names = [name for name, _ in self.playlists]

            # Add playlists to menu
            for name in playlist_names:
                self.playlist_menu.add_command(
                    label=name,
                    command=lambda n=name: self.select_playlist(n)
                )

            # Load saved playlist selection
            config = load_config()
            saved_playlist = config.get('selected_playlist')

            if saved_playlist and saved_playlist in playlist_names:
                self.playlist_var.set(saved_playlist)
            elif playlist_names:
                self.playlist_var.set(playlist_names[0])
            else:
                self.playlist_var.set("No playlists found")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlists:\n{str(e)}")

    def monitor_current_track(self):
        """Background thread to monitor currently playing track and playback state."""
        while self.running:
            try:
                current = self.sp.current_playback()

                if current and current['item']:
                    track = current['item']
                    track_id = track['id']
                    track_name = track['name']
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    is_playing = current['is_playing']

                    if track_id != self.current_track_id:
                        self.current_track_id = track_id
                        self.current_track = f"{track_name} - {artists}"
                        self.root.after(0, self.update_track_label)
                        # Check if new track is in playlist
                        threading.Thread(target=self.check_track_in_playlist, daemon=True).start()

                    # Update play/pause button icon
                    expected_icon = "⏸" if is_playing else "▶"
                    if self.play_pause_btn['text'] != expected_icon:
                        self.root.after(0, lambda: self.play_pause_btn.config(text=expected_icon))
                else:
                    if self.current_track_id is not None:
                        self.current_track_id = None
                        self.current_track = None
                        self.root.after(0, self.update_track_label)

            except Exception as e:
                print(f"Error monitoring track: {e}")

            time.sleep(2)  # Poll every 2 seconds

    def update_track_label(self):
        """Update the track label in the UI."""
        if self.current_track:
            self.track_label.config(text=self.current_track)
        else:
            self.track_label.config(text="No track playing")

    def add_to_playlist(self):
        """Add or remove current track from selected playlist."""
        if not self.current_track_id:
            # Show inline feedback instead of popup
            self.add_button.config(text="No track playing", bg='#8b0000')
            self.root.after(1500, self.update_button_state)
            return

        playlist_name = self.playlist_var.get()
        if not playlist_name or playlist_name == "No playlists found":
            # Show inline feedback instead of popup
            self.add_button.config(text="Select playlist first", bg='#8b0000')
            self.root.after(1500, self.update_button_state)
            return

        # Find playlist ID
        playlist_id = None
        for name, pid in self.playlists:
            if name == playlist_name:
                playlist_id = pid
                break

        if not playlist_id:
            self.add_button.config(text="Playlist not found", bg='#8b0000')
            self.root.after(1500, self.update_button_state)
            return

        try:
            if self.track_in_playlist:
                # Remove from playlist
                self.sp.playlist_remove_all_occurrences_of_items(playlist_id, [self.current_track_id])
                self.track_in_playlist = False
                self.add_button.config(text="✓ Removed", bg='#ff6b6b')
                self.root.after(1200, self.update_button_state)
            else:
                # Add to playlist
                self.sp.playlist_add_items(playlist_id, [self.current_track_id])
                self.track_in_playlist = True
                self.add_button.config(text="✓ Added", bg='#1ed760')
                self.root.after(1200, self.update_button_state)

        except Exception as e:
            print(f"Error modifying playlist: {e}")
            self.add_button.config(text="Error", bg='#8b0000')
            self.root.after(1500, self.update_button_state)

    def update_button_state(self):
        """Update the add/remove button based on current track status in playlist."""
        if self.track_in_playlist:
            self.add_button.config(text="Remove from Playlist", bg='#ff6b6b')
        else:
            self.add_button.config(text="Add to Playlist", bg=self.accent_color)

    def check_track_in_playlist(self):
        """Check if current track is in the selected playlist."""
        if not self.current_track_id:
            return

        playlist_name = self.playlist_var.get()
        if not playlist_name or playlist_name == "No playlists found":
            return

        # Find playlist ID
        playlist_id = None
        for name, pid in self.playlists:
            if name == playlist_name:
                playlist_id = pid
                break

        if not playlist_id:
            return

        try:
            # Check if track is in playlist
            results = self.sp.playlist_items(playlist_id, fields='items.track.id', limit=100)
            track_ids = [item['track']['id'] for item in results['items'] if item['track']]

            # Handle pagination if playlist has more than 100 tracks
            while results['next']:
                results = self.sp.next(results)
                track_ids.extend([item['track']['id'] for item in results['items'] if item['track']])

            self.track_in_playlist = self.current_track_id in track_ids
            self.update_button_state()

        except Exception as e:
            print(f"Error checking track in playlist: {e}")

    def toggle_play_pause(self):
        """Toggle play/pause on Spotify."""
        try:
            playback = self.sp.current_playback()
            if playback and playback['is_playing']:
                self.sp.pause_playback()
                self.play_pause_btn.config(text="▶")
            else:
                self.sp.start_playback()
                self.play_pause_btn.config(text="⏸")
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def previous_track(self):
        """Skip to previous track."""
        try:
            self.sp.previous_track()
        except Exception as e:
            print(f"Error going to previous track: {e}")

    def next_track(self):
        """Skip to next track."""
        try:
            self.sp.next_track()
        except Exception as e:
            print(f"Error going to next track: {e}")

    def on_close(self):
        """Handle window close event."""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = SpotifyPlaylistAdder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
