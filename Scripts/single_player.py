import pickle
from functools import partial
from tkinter import *
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from .custom_menubar import SubMenu

from . import constants
from .console_window import *
get_console()
# Creates AppData folder if doesn't exist
if not os.path.exists(DEBUG):
    os.makedirs(DEBUG)
from .base_logger import init_logger
init_logger()
from .squares import PickleSquare, Square
from .grid import ButtonGrid, PickleButtonGrid
from .squares import PickleSquare, Square
from .functions import *
from .app import App
from .game import Game
logging.info('Loading Single Player...')


def more_info(
    num_mines,
    mines_found,
    squares_clicked_on,
    squares_not_clicked_on,
    start,
    session_start,
    total_squares
):
    messagebox.showinfo('Additional Information', f'''
Total Mines: {num_mines}
Mines found: {mines_found}
Squares clicked on: {len(squares_clicked_on)}
Squares not clicked on: {len(squares_not_clicked_on)}
Total squares: {total_squares}
Ratio of mines: {round((num_mines/total_squares) * 100, 2)}%
Started Game: {start.strftime(STRFTIME)}
Session Started: {session_start.strftime(STRFTIME)}
''')


def save_game(
    start,
    total_time,
    grid,
    zeros_checked,
    num_mines,
    chording,
):
    global difficulty
    logging.info(f'''Saving game with the following attributes:

start:               {start}
total_time:          {total_time}
grid:                {grid}
zeros_checked:       {zeros_checked}
num_mines:           {num_mines}
chording:            {chording}
grid.grid_size       {grid.grid_size}
''')
    data = {
        'start': start,
        'time played': total_time,
        'grid': PickleButtonGrid.from_grid(grid),
        'zeros checked': zeros_checked,
        'num mines': num_mines,
        'chording': chording,
        'difficulty': difficulty.get()
    }
    logging.info(f'Data to save: {data}')
    with filedialog.asksaveasfile('wb', filetypes=(('Pit Mopper Game Files', '*.min'), ('Any File', '*.*'))) as f:  # Pickling
        messagebox.showinfo('Save Game', 'You game is being saved right now, this may a few moments. Please wait until another popup comes before closing the game.')
        logging.info('Saving data...')
        pickle.dump(data, f)
        logging.info('Data successfully saved')
        messagebox.showinfo('Save Game', 'Your game has been saved, you can now close the game.')


def load_highscore() -> dict[str, float | int] | float:
    logging.info('Loading highscore...')
    if not os.path.exists(HIGHSCORE_TXT):
        logging.info(f'{HIGHSCORE_TXT} does not exist, looking in root directory')
        if not os.path.exists(os.path.join(os.getcwd(), 'highscore.txt')):
            logging.info('No highscore was found')
            return float('inf')
        else:
            with open(os.path.join(os.getcwd(), 'highscore.txt'), 'rb') as f:
                value = pickle.load(f)
            if isinstance(value, dict):
                logging.info(f'highscore.txt successfully read')
            else:
                logging.info(f'highscore.txt contains invalid data: {value}')
                messagebox.showerror('Highscore value invalide', 'The highscore file contains an invalid value, press OK to delete the content of it')
                logging.info('Removing file...')
                os.remove(HIGHSCORE_TXT)
                value = float('inf')
            messagebox.showerror('Highscore file in wrong place', 'The highscore file was found, but in the wrong spot, as soon as you click OK, Pit Mopper will attempt to move the file to a new location, you might have to delete the file yourself.')
            if not isinstance(value, float):
                with open(HIGHSCORE_TXT, 'wb') as f:
                    pickle.dump(value, f)
            try:
                os.remove(os.path.join(os.getcwd(), 'highscore.txt'))
            except:
                messagebox.showerror('File Delete', 'Unable to delete file, you will have to delete it yourself')
            return value
    else:
        logging.info(f'{HIGHSCORE_TXT} does exist, reading data from it')
        with open(HIGHSCORE_TXT, 'rb') as f:
            value = pickle.load(f)
        if isinstance(value, dict):
            logging.info(f'{HIGHSCORE_TXT} successfully read')
            return value
        else:
            logging.info(f'{HIGHSCORE_TXT} contains invalid data: {value}')
            messagebox.showerror('Highscore value invalide', 'The highscore file contains an invalid value, press OK to delete the content of it')
            logging.info('Removing file...')
            os.remove(HIGHSCORE_TXT)
            return float('inf')


class SinglePlayerApp(App):
    def draw_menubar(self):
        super().draw_menubar()
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Open File', command=self.load_game, accelerator='Ctrl+O')
        self.file_menu.add_command(label='Highscores', command=self.show_highscores, accelerator='Ctrl+H')
        self.settings.add_separator()
        self.settings.add_checkbutton(variable=self.chord_state, label='Enable Chording', accelerator='Ctrl+A')
    
    def set_variables(self):
        super().set_variables()
        self.chord_state = BooleanVar(self)
        self.mines = IntVar(self, -1)
        self.mines_counter = StringVar(self, f'Your game will have {self.mines.get()} mines')
        self.cols = IntVar(self)
        self.rows = IntVar(self)
        self.difficulty = Variable(self, (None, None))
        self.game_size = StringVar(self, f'You game size will be {self.difficulty.get()[0]} rows and {self.difficulty.get()[1]} columns')
    
    def draw_all(self):
        self.title('Game Loader')
        super().draw_all()
    
    def draw(self):
        super().draw()
        Label(text='Select Difficulty').pack(pady=(25, 0))
        # Variable to hold on to which radio button value is checked.

        Radiobutton(
            text="Easy", value=(10, 10), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Radiobutton(
            text="Medium", value=(20, 20), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Radiobutton(
            text='Hard', value=(30, 30), variable=self.difficulty, command=self.change_difficulty
        ).pack()

        Label(self, textvariable=self.game_size).pack()

        Spinbox(self, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=self.rows, width=4, command=partial(self.change_difficulty, True)).pack()
        Spinbox(self, from_=MIN_ROWS_AND_COLS, to=MAX_ROWS_AND_COLS, textvariable=self.cols, width=4, command=partial(self.change_difficulty, True)).pack()

        Label(self, textvariable=self.mines_counter).pack()
        Label(self, text='-1 means it will generate a random number/use default').pack(padx=20)

        Spinbox(self, textvariable=self.mines, width=4, from_= -1, to = 2000, command=self.change_mines).pack()

        Button(self, text='Play!', command=self.create_game).pack(pady=(0, 20))

        if self.dark_mode_state.get():
            self.dark_mode_state.set(True)
    
    def set_keyboard_shorcuts(self):
        super().set_keyboard_shorcuts()
        bindWidget(self, '<Control-o>', True, self.load_game)
        bindWidget(self, '<space>', True, self.create_game)
        bindWidget(self, '<Control-h>', True, self.show_highscores)
    
    def change_mines(self):
        self.mines_counter.set(f'Your game will have {self.mines.get()} mines')
        logging.info(f'Setting custom mine count: {self.mines.get()}')

    def change_difficulty(self, from_spinbox:bool = False):
        if not from_spinbox:
            logging.info(f'Setting game size to: {tuple(int(i) for i in self.difficulty.get().split(" "))}')
            self.difficulty.set(tuple(int(i) for i in self.difficulty.get().split(' ')))
        else:
            logging.info(f'Setting custom game size: {(self.rows.get(), self.cols.get())}')
            self.difficulty.set((self.rows.get(), self.cols.get()))
        self.game_size.set(f'Your game size will be {self.difficulty.get()[0]} rows and {self.difficulty.get()[1]} columns')
    
    def create_game(
        self,
        _ = None,
        start: datetime = None,
        grid: ButtonGrid = None,
        zeros_checked: list[Square] = None,
        num_mines: int = 0,
        chording: bool = None,
        mines_found: int = 0,
        additional_time: float = 0.0
    ):
        if zeros_checked is None:
            zeros_checked = []
        if self.difficulty.get() == (None, None) or self.difficulty.get() == ('None', 'None'):
            logging.error('Game size not chosen')
            messagebox.showerror(title='Game Size not chosen', message='You have not chosen a game size!')
            return
        elif self.difficulty.get() >= (60, 60):
            logging.warning(f'Size too big {self.difficulty.get()}')
            messagebox.showwarning(title='Size too big', message='Warning: When the game is a size of 60x60 or above, the expierence might be so laggy it is unplayable.')
        elif self.mines.get() > (self.difficulty.get()[0] * self.difficulty.get()[1]) - 10:
            logging.error(f'Mines too high, game size {self.difficulty.get()}, mines: {self.mines.get()}')
            messagebox.showerror(title='Mines too high', message='You have chosen too many mines.')
            return
        elif self.mines.get() == 0 or self.mines.get() < -1:
            logging.error(f'Mines too low ({self.mines.get()})')
            messagebox.showerror('Mines too low', 'You cannot have a mine count below 0 with -1 being a special number')
            return
        elif self.mines.get() > ((self.difficulty.get()[0] * self.difficulty.get()[1])/2):
            logging.warning(f'Number of mines high, game size {self.difficulty.get()}, mines: {self.mines.get()}')
            messagebox.showwarning(title='Number of mines high', message='You have chosen a high amount of mines, so it might take a long time to place them all')

        self.clear()
        self.set_keyboard_shorcuts()
        self.title('Pit Mopper')
        self.grid_columnconfigure(1, weight=1)
        session_start: datetime = datetime.now()
        total_time = StringVar(self)
        if self.dark_mode_state.get():
            dark_title_bar(self)
        Label(self, textvariable=total_time, bg=constants.CURRENT_BG, fg=constants.CURRENT_FG).grid(
            row=1, column=1, sticky=N+S+E+W, pady=(5, 0))
        self.config(bg=constants.CURRENT_BG)

        if grid is None:
            logging.info('Creating grid of buttons...')
            grid = ButtonGrid(self.difficulty.get(), self, dark_mode=self.dark_mode_state.get(), num_mines=self.mines.get())
            if constants.APP_CLOSED:
                try:
                    self.destroy()
                except TclError:
                    return
            for row in grid.grid:
                for square in row:
                    if square.category == 'mine':
                        num_mines += 1
        if chording is None:
            chording = self.chord_state.get()

        if start is None:
            start = datetime.now()

        logging.info(f'''Creating game with following attributes:

    start:                 {start}
    grid:                  {grid}
    zeros_checked:         {zeros_checked}
    num_mines:             {num_mines}
    chording:              {chording}
    mines_found:           {mines_found}
    additional_time:       {additional_time}
    ''')

        squares_clicked_on = [
            square
            for row in grid.grid
            for square in row
            if square.clicked_on
        ]

        squares_not_clicked_on = [
            square
            for row in grid.grid
            for square in row
            if square.clicked_on == False
        ]

        if additional_time != 0.0:
            total_time.set(f'Time: {format_second(int(additional_time))} 🚩0/{num_mines}💣')

        highscore_data = load_highscore()
        game_size_str = f'{self.difficulty.get()[0]}x{self.difficulty.get()[1]}'
        self.title(f'{game_size_str} Pit Mopper Game')
        logging.info(f'{game_size_str} Pit Mopper Game starting...')
        if not isinstance(highscore_data, float):
            try:
                highscore = highscore_data[game_size_str]
            except KeyError:
                highscore = float('inf')
        else:
            highscore = float('inf')
        seconds = additional_time
        self.draw_menubar()
        game_menu = SubMenu()
        bindWidget(self, '<Control-s>', func=lambda _: save_game(start, seconds, grid, zeros_checked, num_mines, chording))
        bindWidget(self, '<Alt-q>', func=lambda _:  [self.clear(), setattr(self.game, 'quit', True), self.draw_all()])
        bindWidget(self, '<Alt-i>', func=lambda _: more_info(
            num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start,  grid.grid_size[0] * grid.grid_size[1]))

        game_menu.add_command(label='Save As', accelerator='Ctrl+S', command=partial(save_game, start, seconds, grid, [
                            PickleSquare.from_square(square) for square in zeros_checked], num_mines, chording))
        game_menu.add_command(label='More Info', command=lambda: more_info(
            num_mines, mines_found, squares_clicked_on, squares_not_clicked_on, start, session_start, grid.grid_size[0] * grid.grid_size[1]),
            accelerator='Alt+I')
        game_menu.add_command(label='Exit', command=lambda: [self.clear(), setattr(self.game, 'quit', True), self.draw_all()], accelerator='Alt+Q')

        self.menubar.add_menu(menu=game_menu, title='Game')

        logging.info('Entering while loop...')
        if self.dark_mode_state.get():
            self.dark_mode_state.set(True)

        result = self._game(
            grid,
            session_start,
            total_time,
            zeros_checked,
            num_mines,
            chording,
            mines_found,
            additional_time
        )
        if not result:
            return
        win = self.game.result['win']
        seconds = self.game.result['seconds']
        mines_found = self.game.mines_found
        if win:
            messagebox.showinfo(
                'Game Over', f'Game Over.\nYou won!\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
        else:
            messagebox.showinfo(
                'Game Over', f'Game Over.\nYou lost.\nYou found {mines_found} out of {num_mines} mines.\nTime: {format_second(seconds)}\nHighscore: {format_second(highscore)}')
        if win and seconds < highscore:
            logging.info('Highscore has been beaten, writing new highscore data')
            with open(HIGHSCORE_TXT, 'wb') as f:
                if isinstance(highscore_data, dict):
                    new_highscore_data = highscore_data.copy()
                else:
                    new_highscore_data = {}
                new_highscore_data[game_size_str] = seconds
                pickle.dump(new_highscore_data, f)
        logging.info('Destroying window')
        self.clear()
        self.draw_all()
        delattr(self, 'game')
    
    def show_highscores(self):
        logging.info('User requested highscores')
        highscore_data = load_highscore()

        if isinstance(highscore_data, dict):
            logging.info(f'Highscore data detected: {highscore_data}')
            data = [['Game Size', 'Seconds']]
            for key, value in highscore_data.items():
                data.append([key, str(round(value, 1))])
            self.clear()
            self.title('Highscores')
            self.iconbitmap(LOGO)
            self.config(padx=50, pady=20)
            frame = Frame(self, bg='black')
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            frame.grid(row=0, column=0)

            if self.dark_mode_state.get():
                self.config(bg=DARK_MODE_BG)
                dark_title_bar(self)
                bg_of_labels = DARK_MODE_BG
                fg_of_labels = DARK_MODE_FG
            else:
                bg_of_labels = DEFAULT_BG
                fg_of_labels = DEFAULT_FG

            for y, row in enumerate(data):
                Grid.rowconfigure(frame, y, weight=1)
                for x, item in enumerate(row):
                    Grid.columnconfigure(frame, x, weight=1)
                    Label(frame, text=str(item), bg=bg_of_labels, fg=fg_of_labels).grid(row=y, column=x, padx=1, pady=1, sticky='nsew')
            Button(self,
                    text='Exit', 
                    bg=constants.CURRENT_BG, 
                    fg=constants.CURRENT_FG,
                    command=lambda: [self.config(padx=0, pady=0), self.clear(), self.draw_all()][0]
                ).grid(row=1, column=0)
            self.update()
        else:
            logging.info('No highscores found')
            messagebox.showinfo('Highscores', 'No highscores were found, play a game and win it to get some')
    
    def load_game(self, _=None):
        logging.info('Opening game...')
        file = filedialog.askopenfile('rb', filetypes=(('Pit Mopper Game Files', '*.min'), ('Any File', '*.*')))
        if file == None:
            return
        else:
            logging.info(f'Reading {file}...')
            with file as f:  # Un Pickling
                data = pickle.load(f)
                data: dict[str]
        logging.info(f'{file} successfully read, setting up game...')

        grid = data['grid'].grid
        button_grid = ButtonGrid(data['grid'].grid_size, self, grid, window.dark_mode_state.get())

        start: datetime = data['start']
        time = data['time played']
        num_mines: int = data['num mines']
        zeros_checked = data['zeros checked']
        chording = data['chording']
        self.grid_columnconfigure(1, weight=1)

        mines_found = 0
        for row in button_grid.grid:
            for square in row:
                if square.category == 'mine' and square.cget('text') == '🚩':
                    mines_found += 1

        self.create_game(
            None,
            start,
            button_grid,
            zeros_checked,
            num_mines,
            chording,
            mines_found,
            additional_time=time,
        )
    
    def _game(
        self,
        grid: ButtonGrid,
        session_start: datetime,
        total_time: StringVar,
        zeros_checked: list[Square] = None,
        num_mines: int = 0,
        chording: bool = None,
        mines_found: int = 0,
        additional_time: float = 0.0,
    ):
        if zeros_checked == None:
            zeros_checked = []
        self.game = Game(
            grid,
            session_start,
            total_time,
            zeros_checked,
            num_mines,
            chording,
            mines_found,
            additional_time,
        )
        self.after(50, self._update_game())
        while True:
            self.after(50, self._update_game())
            if self.game.quit:
                return True


logging.info('Functions successfully defined, creating GUI')

window = SinglePlayerApp('Game Loader')

logging.info('GUI successfully created')
window.mainloop()
