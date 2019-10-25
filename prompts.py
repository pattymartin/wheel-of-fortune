import json
import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

import data_caching, strings, used_letters, values

class SavePuzzlePrompt(Popup):
    """
    A Popup prompting the user to save a puzzle.
    """
    
    def __init__(self, puzzle, **kwargs):
        """Create the Popup."""
        super(SavePuzzlePrompt, self).__init__(
            title=strings.title_save_puzzle, **kwargs)
        content = BoxLayout(orientation='vertical')
        
        name_layout, name_label, name_input = _input_layout(strings.label_name)
        cat_layout, cat_label, cat_input = _input_layout(strings.label_category)
        clue_layout, clue_label, clue_input = _input_layout(strings.label_clue)
        
        content.add_widget(name_layout)
        content.add_widget(cat_layout)
        content.add_widget(clue_layout)
        # create blank space with an empty widget
        content.add_widget(Widget())
        
        button_layout = BoxLayout(orientation='horizontal')
        button_close = Button(text=strings.button_close)
        button_save = Button(text=strings.button_save)
        button_layout.add_widget(button_close)
        button_layout.add_widget(button_save)
        content.add_widget(button_layout)
        
        def input_save(instance):
            """
            Get text from the input fields,
            and save the puzzle.
            """
            
            name = name_input.text
            category = cat_input.text
            clue = clue_input.text
            
            if name and category:
                puzzle_dict = {
                    'category': category,
                    'clue': clue,
                    'puzzle': puzzle}
                data_caching.add_puzzle(name, puzzle_dict)
                self.dismiss()
            else:
                if not name:
                    name_label.color = values.color_red
                if not category:
                    cat_label.color = values.color_red
        
        button_close.bind(on_release=self.dismiss)
        button_save.bind(on_release=input_save)
        
        self.content = content

class LoadPuzzlePrompt(Popup):
    """
    A Popup to prompt the user to select a puzzle by name.
    The selected puzzle will then be passed to `callback`.
    `callback` should be a function accepting a dict
    with the keys 'category', 'clue', and 'puzzle'.
    """
    def __init__(self, callback, **kwargs):
        """Create the Popup."""
        super(LoadPuzzlePrompt, self).__init__(
            title=strings.title_select_puzzle, **kwargs)
        
        self.callback = callback
        self.create_layout()
    
    def create_layout(self):
        content = BoxLayout(orientation='vertical')
        self.toggle_buttons = []
        
        puzzle_layout = BoxLayout(orientation='vertical', size_hint=(1, None))
        puzzle_layout.bind(minimum_height=puzzle_layout.setter('height'))
        puzzles = data_caching.read_puzzles()
        for name in puzzles.keys():
            puzzle_layout.add_widget(self._puzzle_button(name))
        puzzle_layout.add_widget(Widget())
        puzzle_scroll = ScrollView()
        puzzle_scroll.add_widget(puzzle_layout)
        content.add_widget(puzzle_scroll)
        
        content.add_widget(Widget(size_hint=(1, 0.02)))
        
        button_layout = BoxLayout(orientation='horizontal')
        button_layout.size_hint_y = button_layout.size_hint_min_y
        button_close = Button(text=strings.button_close)
        button_close.size_hint_y = button_close.size_hint_min_y
        button_confirm = Button(text=strings.button_confirm)
        button_confirm.size_hint_y = button_confirm.size_hint_min_y
        button_layout.add_widget(button_close)
        button_layout.add_widget(button_confirm)
        content.add_widget(button_layout)
        
        def input_save(instance):
            """
            Check which buttons are selected,
            then run `callback` on the first puzzle selected.
            """
            
            names = []
            for button in self.toggle_buttons:
                try:
                    if button.state == 'down':
                        names.append(button.text)
                except AttributeError:
                    # empty widget
                    pass
            selected_puzzles = [puzzles[name] for name in names]
            if selected_puzzles:
                self.callback(selected_puzzles[0])
            
            self.dismiss()
        
        button_close.bind(on_release=self.dismiss)
        button_confirm.bind(on_release=input_save)
        
        self.content = content
    
    def _puzzle_button(self, name):  
        """
        Create a ToggleButton with text `name`,
        and a button to delete the puzzle.
        """
        
        def prompt_delete_puzzle(instance):
            """
            Prompt the user to delete the puzzle
            with the name `name`.
            """
            YesNoPrompt(
                strings.label_delete_puzzle.format(
                    name),
                confirm_delete,
                None).open()
        
        def confirm_delete(instance):
            """
            Delete the puzzle with the name `name`.
            """
            data_caching.delete_puzzle(name)
            # reload layout to reflect deletion
            self.create_layout()
        
        layout = BoxLayout(orientation='horizontal')
        
        toggle_button = ToggleButton(text=name)
        self.toggle_buttons.append(toggle_button)
        layout.add_widget(toggle_button)
        
        delete_button = Button(text='X')
        delete_button.size_hint_x = 0.1
        delete_button.bind(
            on_release=prompt_delete_puzzle)
        layout.add_widget(delete_button)
        
        layout.size_hint_y = layout.size_hint_min_y
        
        return layout

class YesNoPrompt(Popup):
    """
    A Popup prompting the user with `text`,
    with yes and no buttons.
    Yes and no buttons are bound to `yes_callback` and `no_callback`
    respectively.
    """
    
    def __init__(self, text, yes_callback, no_callback, **kwargs):
        """Create the Popup."""
        super(YesNoPrompt, self).__init__(
            title=strings.title_name_exists, **kwargs)
        
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=text))
        
        button_layout = BoxLayout(orientation='horizontal')
        button_layout.size_hint_y = button_layout.size_hint_min_y
        button_no = Button(text=strings.button_no)
        button_no.size_hint_y = button_no.size_hint_min_y
        button_yes = Button(text=strings.button_yes)
        button_yes.size_hint_y = button_yes.size_hint_min_y
        button_layout.add_widget(button_no)
        button_layout.add_widget(button_yes)
        content.add_widget(button_layout)
        
        button_no.bind(on_release=_wrap_with_dismiss(no_callback, self))
        button_yes.bind(on_release=_wrap_with_dismiss(yes_callback, self))
        
        self.content = content

class ChooseLetterPrompt(Popup):
    """
    A Popup asking the user to choose a letter.
    """
    
    def __init__(self, callback, unavailable_letters=[], **kwargs):
        """Create the Popup."""
        super(ChooseLetterPrompt, self).__init__(
            title=strings.title_choose_letter, **kwargs)
        self.callback = _wrap_with_dismiss(callback, self)
        self.unavailable_letters = unavailable_letters
        letterboard = used_letters.LetterboardLayout(
            self.callback, unavailable=unavailable_letters)
        self.content = letterboard
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Reveal the puzzle when the Enter key is pressed."""
        letter = keycode[1]
        if letter.lower() in self.unavailable_letters:
            return
        self.callback(letter)
    
    def _keyboard_closed(self):
        """Remove keyboard binding when the keyboard is closed."""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

class ManagerSettingsPrompt(Popup):
    """
    A Popup with settings for the manager.
    """
    
    def __init__(self, **kwargs):
        """
        Create the Popup.
        """
        super(ManagerSettingsPrompt, self).__init__(
            title=strings.mgr_title_settings, **kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        vowel_layout, vowel_label, vowel_input = _input_layout(
            strings.label_vowel_price, strings.input_vowel_price)
        min_layout, min_label, min_input = _input_layout(
            strings.label_min_win, strings.input_min_win)
        wedges_layout, wedges_label, wedges_input = _input_layout(
            strings.label_wedges, strings.input_cash_values)
        
        wedges_label.size_hint_y = 1
        wedges_layout.size_hint_y = 1
        
        cash_values = data_caching.get_variables()
        vowel_input.text = str(cash_values.get('vowel_price', ''))
        min_input.text = str(cash_values.get('min_win', ''))
        wedges_input.text = '\r\n'.join([str(i)
            for i in cash_values.get('cash_values', [])])
        
        def input_save(instance):
            """
            Get the text from the input fields,
            and save them.
            """
            vowel_price = data_caching.str_to_int(vowel_input.text)
            min_win = data_caching.str_to_int(min_input.text)
            cash_values = [data_caching.str_to_int(line)
                for line in wedges_input.text.split()]
            
            data_caching.update_variables({
                'vowel_price': vowel_price if vowel_price else '',
                'min_win': min_win if min_win else '',
                'cash_values': sorted([v for v in cash_values if v])})
            
            self.dismiss()
        
        button_layout = BoxLayout(orientation='horizontal')
        button_close = Button(text=strings.button_close)
        button_confirm = Button(text=strings.button_confirm)
        button_close.bind(on_release=self.dismiss)
        button_confirm.bind(on_release=input_save)
        button_layout.add_widget(button_close)
        button_layout.add_widget(button_confirm)
        button_layout.size_hint_y = button_layout.size_hint_min_y
        
        layout.add_widget(vowel_layout)
        layout.add_widget(min_layout)
        layout.add_widget(wedges_layout)
        layout.add_widget(Widget(size_hint=(1, 0.02)))
        layout.add_widget(button_layout)
        
        self.content = layout

def _wrap_with_dismiss(callback, popup):
    """
    Wrap a function so that it calls popup.dismiss at the end.
    """
    
    def do_callback(*args, **kwargs):
        if callback:
            callback(*args, **kwargs)
        popup.dismiss()
    return do_callback

def _input_layout(title, hint_text=''):
    """
    Create a horizontal BoxLayout with text and an input box.
    Returns the BoxLayout, the text Label, and the TextInput
    """
    
    layout = BoxLayout(orientation='horizontal')
    
    layout_label = Label(text=title)
    layout_label.size_hint = layout_label.size_hint_min
    layout_label.valign = 'center'
    layout_label.halign = 'center'
    
    input = TextInput()
    input.hint_text = hint_text
    
    layout.add_widget(layout_label)
    layout.add_widget(input)
    
    layout.size_hint_y = layout.size_hint_min_y
    return layout, layout_label, input
