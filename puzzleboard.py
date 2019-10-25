import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.splitter import Splitter
from kivy.uix.widget import Widget

from prompts import save_puzzle_prompt, load_puzzle_prompt

panels_dir = os.path.join(os.path.dirname(__file__), r'assets')
panel_file = r'panel.png'
panel_file_blue = r'panel_blue.png'
panel_file_white = r'panel_white.png'
panel_file_corner = r'panel_corner.png'
category_background_file = r'category_background.png'

Builder.load_string(r"""
<Panel>:
    layout: ll
    LetterLayout:
        id: ll
        source_image: src_im
        text_label: txt
        anchor_x: 'center'
        anchor_y: 'center'
        pos: self.parent.pos
        size: self.parent.size
        Image:
            id: src_im
            source: r'{}'
        Label:
            id: txt
            color: 0, 0, 0, 0
            font_name: 'Helvetica_try_me'
            font_size: self.size[0]
            bold: True
            halign: 'center'
            valign: 'center'

<RotatedImage>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: 180
            axis: (root.axis_x, root.axis_y, root.axis_z)
            origin: root.center
    canvas.after:
        PopMatrix

<Category>:
    font_name: 'Gotham_Black_Regular'
    font_size: self.size[1] * .75
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: r'{}'
""".format(
    os.path.join(panels_dir, panel_file),
    os.path.join(panels_dir, category_background_file)))

def save_variable(key, value):
    """
    Save key-value pair in a JSON dict,
    stored in the file `vars.json`
    """
    vars = get_variables()
    vars[key] = value
    with open('vars.json', 'w') as f:
        json.dump(vars, f)

def get_variables():
    """
    Get the JSON dict stored in the file `vars.json`.
    Returns an empty dict if the file does not exist.
    """
    
    try:
        with open('vars.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def bind_keyboard(widget):
    """Provide keyboard focus to a widget"""
    # function must be overridden
    pass
    
class PuzzleWithCategory(BoxLayout):
    """BoxLayout containing the puzzleboard and category strip."""
    
    def __init__(self, queue=None, **kwargs):
        """Create the layout."""
        
        super(PuzzleWithCategory, self).__init__(
            orientation='vertical', **kwargs)
        
        category = Category()
        
        self.add_widget(SavableSplitter(
            'category_splitter',
            category,
            sizable_from='bottom'))
        
        self.add_widget(SplitterSurround(
            'puzzleboard',
            PuzzleLayout(category, queue=queue)))

class SplitterSurround(BoxLayout):
    """
    A Layout surrounding its contents with SavableSplitters
    on all four sides.
    """
    
    def __init__(self, name, widget, **kwargs):
        """
        Create the layout.
        `name` is a prefix appended to the Splitters' names.
        `widget` is a widget to be placed in the layout.
        """
        
        super(SplitterSurround, self).__init__(
            orientation='vertical', **kwargs)
        
        self.add_widget(SavableSplitter(
            name + '_top_splitter',
            Widget(),
            sizable_from='bottom'))
        
        middle = BoxLayout(orientation='horizontal')
        middle.add_widget(SavableSplitter(
            name + '_left_splitter',
            Widget(),
            sizable_from='right'))
        middle.add_widget(widget)
        middle.add_widget(SavableSplitter(
            name + '_right_splitter',
            Widget(),
            sizable_from='left'))
        self.add_widget(middle)
        
        self.add_widget(SavableSplitter(
            name + '_bottom_splitter',
            Widget(),
            sizable_from='top'))
        

class SavableSplitter(Splitter):
    """A Splitter that remembers its size hint."""
    
    def __init__(self, name, widget, **kwargs):
        """
        Create the Splitter.
        `name` is the string that will be used as a key
        by `save_variable()`.
        `widget` is the widget that will be assigned
        to this Splitter.
        """
        
        super(SavableSplitter, self).__init__(**kwargs)
        
        self.min_size = 0
        self.strip_size = '5pt'
        
        # get saved location
        if self.sizable_from in ['top', 'bottom']:
            self.size_hint_y = get_variables().get(name)
            axis = 1
        else:
            self.size_hint_x = get_variables().get(name)
            axis = 0
        
        # when the splitter is released, save its location
        self.bind(
            on_release=lambda i: save_variable(name,
                self.size[axis] / self.parent.size[axis]))
        
        self.add_widget(widget)

class Category(Label):
    """Strip displaying the category."""
    pass

class PuzzleLayout(GridLayout):
    """GridLayout containing all Panels."""
    panel_size = ListProperty([]) # [width, height] from an Image object
    category_label = ObjectProperty(None)
    queue = ObjectProperty(None)
    
    def __init__(self, category_label, rows=6, cols=16, queue=None, **kwargs):
        """Create the layout and bind the keyboard."""
        super(PuzzleLayout, self).__init__(rows=rows, cols=cols, **kwargs)
        self.category_label = category_label
        self.queue = queue
        
        for i in range(rows):
            for j in range(cols):
                top_left = (1, 1)
                top_right = (1, cols-2)
                bottom_left = (rows-2, 1)
                bottom_right = (rows-2, cols-2)
                corners = [top_left, top_right,
                           bottom_left, bottom_right]
                
                if (i, j) in corners:
                    source_image = os.path.join(panels_dir, panel_file_corner)
                    if (i, j) == top_left:
                        # rotate image 180 degrees
                        widget = RotatedImage(0, 0, 1, source=source_image)
                    elif (i, j) == top_right:
                        # flip image vertically
                        widget = RotatedImage(1, 0, 0, source=source_image)
                    elif (i, j) == bottom_left:
                        # flip image horizontally
                        widget = RotatedImage(0, 1, 0, source=source_image)
                    else:
                        widget = Image(source=source_image)
                    self.add_widget(widget)
                elif (
                        i in (0, rows-1)
                        or j in (0, cols-1)):
                    # create blank widgets for the borders.
                    # there are hidden widgets along the top, bottom,
                    # left, and right, that are resized to push the panels
                    # into the proper alignment
                    widget = Widget()
                    self.add_widget(widget)
                else:
                    # create panels
                    panel = Panel()
                    self.add_widget(panel)
                    self.panel_size = panel.layout.source_image.texture.size
        bind_keyboard(self)
        
        if self.queue:
            Clock.schedule_once(self.check_queue, 5)
    
    def check_queue(self, instance):
        """
        Check the queue for incoming commands to execute.
        """
        try:
            command, args = self.queue.a.get(block=False)
            if command == 'letter':
                # args is a guessed letter
                self.check_all(args)
            elif command == 'load':
                # args is a puzzle to be loaded
                self.load_puzzle(args)
            elif command == 'reveal':
                self.reveal_all()
            elif command == 'exit':
                App.get_running_app().stop()
        except:
            pass
        Clock.schedule_once(self.check_queue, 1)
    
    def do_layout(self, *args):
        super(PuzzleLayout, self).do_layout(*args)
        width = self.panel_size[0] * (self.cols - 2)
        height = self.panel_size[1] * (self.rows - 2)
        ratio = width / height
        
        w, h = self.size # current layout size
        if w / h > ratio:
            # too wide
            for i, x in enumerate(list(self.children)):
                # remove first and last row
                if i < self.cols or (len(self.children) - i) <= self.cols:
                    x.size_hint_y = None
                    x.height = 0
                # space out first and last column
                if (i % self.cols) in (0, self.cols-1):
                    x.size_hint_x = None
                    board_width = h * ratio
                    extra_width = w - board_width
                    x.width = extra_width / 2
                else:
                    x.size_hint_x = 1
        elif w / h < ratio:
            # too tall
            for i, x in enumerate(list(self.children)):
                # remove first and last column
                if (i % self.cols) in (0, self.cols-1):
                    x.size_hint_x = None
                    x.width = 0
                # space out first and last row
                if i < self.cols or (len(self.children) - i) <= self.cols:
                    x.size_hint_y = None
                    board_height = w / ratio
                    extra_height = h - board_height
                    x.height = extra_height / 2
                else:
                    x.size_hint_y = 1
    
    def check_all(self, letter):
        """Check all Panels for a given letter and reveal matches."""
        reveal_interval = 0.9 # seconds between panels being revealed
        blue_interval = 0.5 # seconds between panels turning blue
        
        if letter.lower() in 'abcdefghijklmnopqrstuvwxyz':
            # indices in order from top to bottom, right to left
            indices = [
                    i + (j*self.cols)
                    for i in range(self.cols-1, -1, -1)
                        for j in range(self.rows)
                ][::-1]
            # the number of matches found so far,
            # used to offset the scheduled time to change the panel
            matches = 0
            for i in indices:
                try:
                    layout = self.children[i].layout
                    if layout.hidden() and layout.check_letter(letter):
                        # match found
                        # schedule panel to turn blue
                        Clock.schedule_once(
                            layout.blue,
                            blue_interval * (matches + 1))
                        # schedule panel to be revealed
                        Clock.schedule_once(
                            layout.show_letter,
                            reveal_interval * (matches + 1))
                        matches += 1
                except AttributeError:
                    # empty widget
                    pass
            if self.queue:
                self.queue.b.put(('matches', matches))
    
    def reveal_all(self):
        """Reveal the entire puzzle."""
        reveal_interval = 0.05 # seconds between letters being revealed
        
        # indices in order from top to bottom, left to right
        indices = [
                i + (j*self.cols)
                for i in range(self.cols)
                    for j in range(self.rows)
            ][::-1]
        matches = 0
        for i in indices:
            try:
                layout = self.children[i].layout
                if layout.hidden() and layout.text_label.text:
                    # schedule panel reveal
                    Clock.schedule_once(
                        layout.show_letter,
                        reveal_interval * (matches + 1))
                    matches += 1
            except AttributeError:
                # empty widget
                pass
    
    def save_puzzle(self):
        """Prompt the user to save the puzzle."""
        puzzle = ''
        for widget in self.children[::-1]:
            try:
                letter = widget.layout.text_label.text
                puzzle += letter if letter else ' '
            except AttributeError:
                # empty widget
                pass
        prompt = save_puzzle_prompt(puzzle)
        prompt.bind(on_dismiss=lambda instance: bind_keyboard(self))
        prompt.open()
    
    def choose_puzzle(self):
        """
        Prompt the user to select a puzzle,
        then load that puzzle.
        """
        load_puzzle_prompt(self.load_puzzle).open()
    
    def load_puzzle(self, puzzle):
        """
        Load a puzzle into the puzzleboard.
        """
        interval = 0.05 # seconds between letters loading
        puzzle_string = list(puzzle['puzzle'])
        
        self.category_label.text = puzzle['category'].upper()
        
        if self.queue:
            self.queue.b.put(('puzzle_loaded', puzzle))
        
        # set letters
        for widget in self.children[::-1]:
            try:
                layout = widget.layout
                letter = puzzle_string.pop(0)
                layout.text_label.color = [0, 0, 0, 0]
                layout.text_label.text = '' if letter == ' ' else letter
                layout.green()
            except AttributeError:
                # empty widget
                pass
        
        # turn letter panels white
        # indices in order from top to bottom, left to right
        indices = [
                i + (j*self.cols)
                for i in range(self.cols)
                    for j in range(self.rows)
            ][::-1]
        # the number of non-space characters encountered,
        # used to offset the scheduled time to change the panel
        letters = 0
        for i in indices:
            try:
                layout = self.children[i].layout
                if layout.text_label.text:
                    # schedule panel to turn white
                    Clock.schedule_once(
                        layout.hide,
                        interval * (letters + 1))
                    letters += 1
            except AttributeError:
                # empty widget
                pass
        bind_keyboard(self)
    
    def _keyboard_closed(self):
        """Remove keyboard binding when the keyboard is closed."""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Reveal the puzzle when the Enter key is pressed."""
        letter = keycode[1]
        if 'ctrl' in modifiers:
            if letter == 's':
                self.save_puzzle()
            elif letter == 'o':
                self.choose_puzzle()
        elif keycode[1] == 'enter':
            self.reveal_all()
        else:
            self.check_all(letter)

class LetterLayout(AnchorLayout):
    """Defines the layout of a Panel object."""
    source_image = ObjectProperty(None) # an Image object
    text_label = ObjectProperty(None) # a Label object
    
    def blue(self, td=None):
        """Turn this panel blue."""
        self.source_image.source = os.path.join(panels_dir, panel_file_blue)
    
    def white(self):
        """Turn this panel white."""
        self.source_image.source = os.path.join(panels_dir, panel_file_white)
    
    def green(self):
        """Turn this panel to show the WOF logo."""
        self.source_image.source = os.path.join(panels_dir, panel_file)
    
    def show_letter(self, td=None):
        """Turn the panel white and reveal the letter."""
        self.white()
        self.text_label.color = [0, 0, 0, 1]
    
    def hide(self, td=None):
        """Hide the letter on this panel."""
        text = self.text_label.text.lower()
        if text:
            if not text in 'abcdefghijklmnopqrstuvwxyz':
                # don't hide punctuation
                self.show_letter()
                return
            self.white()
        else:
            # turn panel green if there's no letter
            self.green()
        self.text_label.color = [0, 0, 0, 0]
    
    def hidden(self):
        """Returns True if this panel's letter is currently hidden."""
        return self.text_label.color == [0, 0, 0, 0]

    def check_letter(self, letter):
        """
        Check whether this panel's letter is the same as the given letter.
        """
        
        if self.text_label.text.lower() == letter.lower():
            return True
        else:
            return False

class Panel(Button):
    """A single panel that may contain a letter."""
    
    layout = ObjectProperty(None) # a LetterLayout object
    
    def __init__(self, **kwargs):
        """Create the Panel and bind the click function."""
        super(Panel, self).__init__(**kwargs)
        self.bind(on_release=self.click)
    
    def click(self, instance):
        """
        Show this panel's letter and set keyboard focus to this Panel.
        Also turns all other panels green if they don't have letters.
        This function will be called when the Panel is clicked.
        """
        
        # turn widgets green if they don't have text
        for widget in self.parent.children:
            try:
                if not widget.layout.text_label.text:
                    widget.layout.hide()
            except AttributeError:
                # empty widget
                pass
        self.layout.show_letter()
        bind_keyboard(self)
    
    def _keyboard_closed(self):
        """Remove keyboard binding when the keyboard is closed."""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Receive a pressed key, and put the letter in the text label.
        Then, move focus to the next panel
        (or previous if backspace is pressed).
        """
        
        letter = keycode[1]
        # map non-alphabetic characters to their shift symbols
        # on a standard US keyboard
        shifts = {'1': '!', '2': '@', '3': '#',
                  '4': '$', '5': '%', '6': '^',
                  '7': '&', '8': '*', '9': '(',
                  '0': ')', '-': '_', '=': '+',
                  '[': '{', ']': '}', '\\': '|',
                  ';': ':', '\'': '"', ',': '<',
                  '.': '>', '/': '?'}
        if 'ctrl' in modifiers:
            if letter == 's':
                self.parent.save_puzzle()
            elif letter == 'o':
                self.parent.choose_puzzle()
        elif 'shift' in modifiers and letter in shifts.keys():
            # shift is held, get shift symbol
            self.layout.text_label.text = shifts[letter]
            self.select_next()
        elif letter in 'abcdefghijklmnopqrstuvwxyz1234567890-=[]\\;\',./':
            # set text and move to next panel
            self.layout.text_label.text = letter.upper()
            self.select_next()
        elif letter == 'backspace':
            # remove this panel's text, select previous panel
            self.layout.text_label.text = ''
            self.select_prev()
        elif letter == 'enter':
            # entry finished, hide all letters
            # and bind keyboard to main PuzzleLayout
            self.hide_all()
            bind_keyboard(self.parent)
        elif letter == 'spacebar':
            # move to next panel
            self.select_next()
    
    def select_next(self):
        """Select the next panel."""
        # hide panel if there's no text
        if not self.layout.text_label.text:
            self.layout.hide()
        children = list(self.parent.children)
        # list of panels is in reverse order
        i = children.index(self) - 1
        while i >= 0:
            try:
                children[i].click(None)
                break
            except AttributeError:
                # empty panel
                i -= 1
    
    def select_prev(self):
        """Select the previous panel and remove its text."""
        # hide panel if there's no text
        if not self.layout.text_label.text:
            self.layout.hide()
        children = list(self.parent.children)
        # list of panels is in reverse order
        i = children.index(self) + 1
        while i < len(children):
            try:
                children[i].click(None)
                children[i].layout.text_label.text = ''
                break
            except AttributeError:
                # empty panel
                i += 1
        # panel was hidden at the start of this function.
        # if this is the first panel, run click() to show it again:
        if i >= len(children):
            self.click(None)
    
    def hide_all(self):
        """
        Hide all panels in the parent PuzzleLayout.
        """
        
        children = list(self.parent.children)
        for c in children:
            try:
                c.layout.hide()
            except AttributeError:
                # empty widget
                pass

class RotatedImage(Image):
    axis_x = NumericProperty()
    axis_y = NumericProperty()
    axis_z = NumericProperty()
    
    def __init__(self, x, y, z, **kwargs):
        super(RotatedImage, self).__init__(**kwargs)
        self.axis_x = x
        self.axis_y = y
        self.axis_z = z

class PuzzleboardApp(App):
    """Puzzleboard Kivy App"""
    
    queue = None
    
    def __init__(self, queue=None, **kwargs):
        """
        Create the App.
        `queue` is a CommQueue instance from `manager`.
        """
        super(PuzzleboardApp, self).__init__(**kwargs)
        self.queue = queue
    
    def build(self):
        """Build the app."""
        
        return PuzzleWithCategory(self.queue)