import multiprocessing

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import data_caching, prompts, puzzleboard, score, strings, used_letters, values
from fullscreen import Fullscreenable

Builder.load_file(strings.file_kv_manager)

def bind_keyboard(widget):
    """Provide keyboard focus to a widget"""
    
    widget._keyboard = Window.request_keyboard(
        widget._keyboard_closed, widget)
    widget._keyboard.bind(on_key_down=widget._on_keyboard_down)

puzzleboard.bind_keyboard = bind_keyboard

class SquareButton(Button):
    """
    A button with its width set to equal its height
    """
    
    pass

class SettingsButton(ButtonBehavior, Label):
    """
    A square button with a settings icon
    """
    
    pass

class CommQueue:
    """
    Contains two Queues named `a` and `b`.
    This way, a parent process can write to `a`
    and read from `b`, and the child process
    can do the opposite.
    """
    def __init__(self):
        self.a = multiprocessing.Queue()
        self.b = multiprocessing.Queue()

class PlayerButton(ButtonBehavior, score.ScoreLayout):
    def __init__(self, bg_color=(0, 0, 0, 1), **kwargs):
        super(PlayerButton, self).__init__(**kwargs)
        self.bg_color = bg_color

class TossupOneButton(BoxLayout):
    """
    A layout containing one button to start a tossup.
    """
    
    def __init__(self, manager_layout=None, **kwargs):
        super(TossupOneButton, self).__init__(**kwargs)
        self.manager_layout = manager_layout

class TossupThreeButtons(BoxLayout):
    """
    A layout containing three buttons,
    one for each player to ring in during a tossup.
    """
    
    def __init__(self, manager_layout=None, **kwargs):
        super(TossupThreeButtons, self).__init__(**kwargs)
        self.manager_layout = manager_layout

class ManagerLayout(BoxLayout, Fullscreenable):
    """
    A BoxLayout for the ManagerApp.
    """
    
    def __init__(self, puzzle_queue, red_q, ylw_q, blu_q, letters_q, **kwargs):
        """Create the layout."""
        super(ManagerLayout, self).__init__(**kwargs)
        
        self.puzzle_queue = puzzle_queue
        self.red_q = red_q
        self.ylw_q = ylw_q
        self.blu_q = blu_q
        self.letters_q = letters_q
        
        self.selected_player = 0
        self.unavailable_letters = []
        self.tossup_running = False
        self.tossup_players_done = []
        self.puzzle_string = ''
        self.puzzle_clue = ''
    
        self.load_settings()
        self.tossup_button(True)
        
        if self.puzzle_queue:
            Clock.schedule_once(self.check_queue, values.queue_start)
    
    def tossup_button(self, single_button_mode=True):
        """
        If `single_button_mode` is True,
        set `tossup_layout` to contain one button
        which starts a tossup.
        If `single_button_mode` is False,
        set `tossup_layout` to contain three buttons:
        one to ring in each player.
        """
        
        self.tossup_layout.clear_widgets()
        
        if single_button_mode:
            self.tossup_layout.add_widget(TossupOneButton(self))
        else:
            self.tossup_layout.add_widget(TossupThreeButtons(self))
    
    def check_queue(self, instance):
        """
        Check the queue for incoming commands.
        """
        try:
            command, args = self.puzzle_queue.b.get(block=False)
            if command == 'puzzle_loaded':
                self.puzzle_string = ' '.join(args['puzzle'].split())
                self.puzzle_clue = args['clue']
                self.show_puzzle()
            elif command == 'matches':
                self.correct_letter(args)
            elif command == 'tossup_timeout':
                self.tossup()
        except:
            pass
        Clock.schedule_once(self.check_queue, values.queue_interval)
    
    def show_puzzle(self, instance=None):
        """
        Show the current puzzle
        (and clue, if any)
        in the `puzzle_label`.
        """
        if self.puzzle_string:
            self.puzzle_label.text = self.puzzle_string
            if self.puzzle_clue:
                self.puzzle_label.text += ('\n'
                    + strings.mgr_label_clue + self.puzzle_clue)
        else:
            self.puzzle_label.text = ''
    
    def select_red(self):
        """
        Change the colors of TextInput boxes
        to indicate that the red player has been selected.
        """
        self.selected_player = 1
        self.selection_color(values.color_light_red)
        if self.btn_red.name:
            self.name_input.text = self.btn_red.name
        self.stop_all_flashing()
        self.red_q.put(('flash', None))
        self.letters_q.put(('flash', 'red', None))
    
    def select_yellow(self):
        """
        Change the colors of TextInput boxes
        to indicate that the yellow player has been selected.
        """
        self.selected_player = 2
        self.selection_color(values.color_light_yellow)
        if self.btn_ylw.name:
            self.name_input.text = self.btn_ylw.name
        self.stop_all_flashing()
        self.ylw_q.put(('flash', None))
        self.letters_q.put(('flash', 'yellow', None))
    
    def select_blue(self):
        """
        Change the colors of TextInput boxes
        to indicate that the blue player has been selected.
        """
        self.selected_player = 3
        self.selection_color(values.color_light_blue)
        if self.btn_blu.name:
            self.name_input.text = self.btn_blu.name
        self.stop_all_flashing()
        self.blu_q.put(('flash', None))
        self.letters_q.put(('flash', 'blue', None))
    
    def select_next_player(self):
        """
        Select the next player.
        """
        if self.selected_player == 1:
            # red selected, select yellow
            self.select_yellow()
        elif self.selected_player == 2:
            # yellow selected, select blue
            self.select_blue()
        else:
            # blue or no player selected, select red
            self.select_red()
    
    def selection_color(self, color):
        """
        Change the color of TextInput boxes to the specified `color`.
        """
        self.name_input.background_color = color
        self.score_edit.background_color = color
        self.custom_value.background_color = color
    
    def update_name(self, text):
        """
        Update the name of the selected player.
        """
        if self.selected_player == 1:
            self.btn_red.name = text
            self.red_q.put(('name', text))
            self.letters_q.put(('name', 'red', text))
        elif self.selected_player == 2:
            self.btn_ylw.name = text
            self.ylw_q.put(('name', text))
            self.letters_q.put(('name', 'yellow', text))
        elif self.selected_player == 3:
            self.btn_blu.name = text
            self.blu_q.put(('name', text))
            self.letters_q.put(('name', 'blue', text))
    
    def get_score(self):
        """
        Get the score of the selected player.
        """
        if self.selected_player == 1:
            return self.btn_red.score
        elif self.selected_player == 2:
            return self.btn_ylw.score
        elif self.selected_player == 3:
            return self.btn_blu.score
        return 0
    
    def set_score(self, score):
        """
        Set the score of the selected player.
        """
        if self.selected_player == 1:
            self.btn_red.score = score
            self.red_q.put(('score', score))
            self.letters_q.put(('score', 'red', score))
        elif self.selected_player == 2:
            self.btn_ylw.score = score
            self.ylw_q.put(('score', score))
            self.letters_q.put(('score', 'yellow', score))
        elif self.selected_player == 3:
            self.btn_blu.score = score
            self.blu_q.put(('score', score))
            self.letters_q.put(('score', 'blue', score))
    
    def add_score(self, score):
        """
        Add `score` to the selected player's score.
        """
        self.set_score(self.get_score() + score)
    
    def get_total(self):
        """
        Get the game total of the selected player.
        """
        if self.selected_player == 1:
            return self.btn_red.total
        elif self.selected_player == 2:
            return self.btn_ylw.total
        elif self.selected_player == 3:
            return self.btn_blu.total
        return 0
    
    def set_total(self, total):
        """
        Set the game total of the selected player.
        """
        if self.selected_player == 1:
            self.btn_red.total = total
            self.red_q.put(('total', total))
            self.letters_q.put(('total', 'red', total))
        elif self.selected_player == 2:
            self.btn_ylw.total = total
            self.ylw_q.put(('total', total))
            self.letters_q.put(('total', 'yellow', total))
        elif self.selected_player == 3:
            self.btn_blu.total = total
            self.blu_q.put(('total', total))
            self.letters_q.put(('total', 'blue', total))
    
    def add_total(self, total):
        """
        Add `total` to the selected player's game total.
        """
        self.set_total(self.get_total() + total)
    
    def choose_puzzle(self):
        """
        Prompt the user to select a puzzle.
        """
        prompts.LoadPuzzlePrompt(self.load_puzzle).open()
    
    def load_puzzle(self, puzzle):
        """
        Tell the layout to load `puzzle`.
        """
        if self.tossup_running:
            self.tossup()
        self.unavailable_letters = []
        self.puzzle_queue.a.put(('load', puzzle))
        self.letters_q.put(('reload', None, None))
        self.tossup_players_done = []
    
    def clear_puzzle(self):
        """
        Clear the puzzleboard.
        """
        self.load_puzzle({
            'category': '',
            'clue': '',
            'puzzle': ' ' * 52})
    
    def tossup(self, player=None):
        """
        If there is no tossup in progress, start one.
        If there is a tossup in progress, pause it.
        If `player` is 1, 2, or 3,
        select that player.
        """
        if player:
            if player in self.tossup_players_done:
                return  
            self.tossup_players_done.append(player)
        
        if self.tossup_running:
            self.puzzle_queue.a.put(('pause_tossup', None))
            self.tossup_button()
            
            if player == 1:
                self.select_red()
            elif player == 2:
                self.select_yellow()
            elif player == 3:
                self.select_blue()
        else:
            if set(self.tossup_players_done) == set([1, 2, 3]):
                return
            self.puzzle_queue.a.put(('tossup', None))
            self.tossup_button(single_button_mode=False)
            self.stop_all_flashing()
        
        self.tossup_running = not self.tossup_running
    
    def stop_all_flashing(self):
        """
        Tell all ScoreApps to stop flashing.
        """
        self.red_q.put(('stop_flash', None))
        self.ylw_q.put(('stop_flash', None))
        self.blu_q.put(('stop_flash', None))
        self.letters_q.put(('stop_flash', 'red', None))
        self.letters_q.put(('stop_flash', 'yellow', None))
        self.letters_q.put(('stop_flash', 'blue', None))
    
    def reveal_puzzle(self):
        """
        Tell the layout to reveal the puzzle.
        """
        self.puzzle_queue.a.put(('reveal', None))
        self.stop_all_flashing()
    
    def guess_letter(self):
        """
        Open a prompt to select a letter.
        """
        if (
                self.selected_player == 0
                or self.get_value() == 0):
            return
        popup = prompts.ChooseLetterPrompt(
            self.guessed_letter, self.unavailable_letters)
        popup.open()
        bind_keyboard(popup)
    
    def guessed_letter(self, letter):
        """
        Pass the `letter` to the PuzzleLayout to check for matches.
        This runs after `guess_letter()` is called
        and a letter is chosen.
        """
        if letter.lower() in 'aeiou':
            # do nothing if not enough money for a vowel
            if self.get_score() < self.vowel_price:
                return
            # subtract vowel price from score
            self.add_score(-self.vowel_price)
        self.unavailable_letters.append(letter.lower())
        self.puzzle_queue.a.put(('letter', letter))
        self.letters_q.put(('remove_letter', letter, None))
    
    def get_value(self):
        """
        Get the value indicated by the custom cash value input box.
        If the box is empty, get the value
        indicated by the cash value spinner.
        """
        
        custom_value = self.custom_value.text
        if custom_value:
            return data_caching.str_to_int(custom_value)
        else:
            return data_caching.str_to_int(self.dropdown.text)
    
    def correct_letter(self, match):
        """
        Adjust the selected player's score based on the number of matches.
        `match` is an tuple of the form (letter, number)
        indicating the letter and the number of matches.
        """
        letter, matches = match
        if letter.lower() not in 'aeiou':
            self.add_score(matches * self.get_value())
        self.custom_value.text = ''
        
        # show number of matches in puzzle_label
        self.puzzle_label.text = strings.label_matches.format(
            letter=letter.upper(), matches=matches)
        # schedule to show the puzzle again
        Clock.schedule_once(self.show_puzzle, values.time_show_matches)
    
    def lose_turn(self):
        """
        Player has lost a turn;
        move to next player.
        """
        self.select_next_player()
    
    def bankrupt(self):
        """
        Bankrupt the selected player.
        """
        self.set_score(0)
    
    def bank_score(self):
        """
        Add the selected player's score
        to their game total,
        then set each player's score to 0.
        """
        self.add_total(self.get_score())
        
        # set score = 0 for each player
        tmp = self.selected_player
        for i in range(1, 4):
            self.selected_player = i
            self.set_score(0)
        
        self.selected_player = tmp
    
    def cash_settings(self):
        """
        Open a Popup prompting the user
        to fill in some game settings.
        """
        popup = prompts.ManagerSettingsPrompt()
        popup.bind(on_dismiss=self.load_settings)
        popup.open()
    
    def load_settings(self, instance=None):
        """
        Load settings from file.
        """
        settings = data_caching.get_variables()
        try:
            self.vowel_price = int(settings.get('vowel_price', ''))
        except ValueError:
            self.vowel_price = values.default_vowel_price
        self.min_win = settings.get('min_win', values.default_min_win)
        self.dropdown.values = [strings.currency_format.format(value)
            for value in settings.get('cash_values', [])]
    
    def exit_app(self):
        """
        Tell all apps to stop, then stop this app.
        """
        self.exit_other_apps()
        App.get_running_app().stop()
    
    def exit_other_apps(self):
        """
        Tell all other apps to stop.
        """
        for q in [self.puzzle_queue.a, self.red_q, self.ylw_q, self.blu_q]:
            q.put(('exit', None))
        self.letters_q.put(('exit', None, None))

class ManagerApp(App):
    """
    An app to manage the PuzzleboardApp.
    """
    
    def __init__(self, *args, **kwargs):
        """Create the app."""
        super(ManagerApp, self).__init__(**kwargs)
        self.args = args
    
    def build(self):
        """Build the app."""
        return ManagerLayout(*self.args)
    
    def on_stop(self):
        self.root.exit_other_apps()

class ScoreApp(App):
    """
    An app showing a player's score.
    """
    
    def __init__(self, bg_color, queue, **kwargs):
        """Create the app."""
        super(ScoreApp, self).__init__(**kwargs)
        self.bg_color = bg_color
        self.queue = queue
    
    def build(self):
        """Build the app."""
        return score.ScoreLayout(self.bg_color, queue=self.queue)

class LetterboardApp(App):
    """
    An app showing the available letters
    and players' scores.
    """
    
    def __init__(self, queue, **kwargs):
        """Create the app."""
        super(LetterboardApp, self).__init__(**kwargs)
        self.queue = queue
    
    def build(self):
        """Build the app."""
        return used_letters.LettersWithScore(queue=self.queue)

def launchManager(*args):
    """
    Launch a ManagerApp.
    """
    ManagerApp(*args).run()

def launchScore(*args):
    """
    Launch a ScoreApp.
    """
    ScoreApp(*args).run()

def launchLetterboard(*args):
    """
    Launch a LetterboardApp.
    """
    LetterboardApp(*args).run()

if __name__ == '__main__':
    puzzle_q = CommQueue()
    red_q = multiprocessing.Queue()
    ylw_q = multiprocessing.Queue()
    blu_q = multiprocessing.Queue()
    letters_q = multiprocessing.Queue()
    
    manager_process = multiprocessing.Process(
        target=launchManager,
        args=(puzzle_q, red_q, ylw_q, blu_q, letters_q))
    red = multiprocessing.Process(
        target=launchScore,
        args=(values.color_red, red_q))
    ylw = multiprocessing.Process(
        target=launchScore,
        args=(values.color_yellow, ylw_q))
    blu = multiprocessing.Process(
        target=launchScore,
        args=((values.color_blue, blu_q)))
    letters = multiprocessing.Process(
        target=launchLetterboard,
        args=(letters_q,))
    
    manager_process.start()
    red.start()
    ylw.start()
    blu.start()
    letters.start()
    
    puzzleboard.PuzzleboardApp(puzzle_q).run()
