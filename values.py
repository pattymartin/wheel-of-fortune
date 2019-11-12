color_red = (1, 0, 0, 1)
color_yellow = (1, 1, 0, 1)
color_blue = (0, 0, 1, 1)
color_light_red = (1, 0.75, 0.75, 1)
color_light_yellow = (1, 1, 0.75, 1)
color_light_blue = (0.75, 0.75, 1, 1)
color_none = (0, 0, 0, 0)
color_white = (1, 1, 1, 1)

default_clue_solve_reward = 3000
default_final_spin_bonus = 1000
default_vowel_price = 250
default_min_win = 1000

edit_hotkey_timeout = 5

font_category = 'Gotham_Black_Regular'
font_category_size = 0.75
font_panel = 'Helvetica_try_me'
font_panel_size = 1
font_score = font_category
font_score_name_size = 0.5
font_score_size = 1
font_score_total_size = 0.5

hotkey_default_select_1 = '1'
hotkey_default_select_2 = '2'
hotkey_default_select_3 = '3'
hotkey_default_select_next = 'spacebar'
hotkey_default_increase_score = 'enter'
hotkey_default_select_puzzle = 'ctrl+o'
hotkey_default_clear_puzzle = 'backspace'
hotkey_default_solve = 'right'
hotkey_default_timer_start = '`'
hotkey_default_timer_reset = 'shift+`'
hotkey_default_start_tossup = '4'
hotkey_default_buzzer = '8'
hotkey_default_lose_turn = '9'
hotkey_default_bankrupt = '0'
hotkey_default_buy_vowel = '-'
hotkey_default_bank_score = '='
hotkey_names = [
    'select_1',
    'select_2',
    'select_3',
    'select_next',
    'increase_score',
    'select_puzzle',
    'clear_puzzle',
    'solve',
    'timer_start',
    'timer_reset',
    'start_tossup',
    'buzzer',
    'lose_turn',
    'bankrupt',
    'buy_vowel',
    'bank_score']
hotkey_defaults = [
    hotkey_default_select_1,
    hotkey_default_select_2,
    hotkey_default_select_3,
    hotkey_default_select_next,
    hotkey_default_increase_score,
    hotkey_default_select_puzzle,
    hotkey_default_clear_puzzle,
    hotkey_default_solve,
    hotkey_default_timer_start,
    hotkey_default_timer_reset,
    hotkey_default_start_tossup,
    hotkey_default_buzzer,
    hotkey_default_lose_turn,
    hotkey_default_bankrupt,
    hotkey_default_buy_vowel,
    hotkey_default_bank_score]

interval_blue = 0.5 # seconds between panels turning blue
interval_load = 0.05 # seconds between letters loading
interval_reveal = 0.9 # seconds between panels being revealed
interval_score_flash = 0.5 # seconds between player score flashes
interval_solve_reveal = 0.01 # seconds between letters being revealed on solve
interval_tossup = 0.924 # seconds between letters being revealed in a toss-up

opacity_adjustment = 0.25
opacity_interval = 0.001

queue_start = 5
queue_interval = 0

speedup_timeout = 4 # seconds the player has to solve the puzzle in speedup
splitter_size = '5pt'
time_show_matches = 5 # seconds correct letter matches will display in manager
timer_accuracy = 0.1 # seconds between final spin timer updates

used_letters_layout = [
    'BCDFGHJ',
    'KLMNPQR',
    'STVWXYZ',
    ' AEIOU ']

# circular import, can't import at top
import strings

round_types = [
    strings.round_type_standard,
    strings.round_type_mystery,
    strings.round_type_express,
    strings.round_type_tossup,
    strings.round_type_triple_tossup,
    strings.round_type_triple_tossup_final,
    strings.round_type_speedup,
    strings.round_type_bonus]
default_game_order = [
    strings.round_type_tossup,
    strings.round_type_tossup,
    strings.round_type_standard,
    strings.round_type_mystery,
    strings.round_type_express,
    strings.round_type_triple_tossup,
    strings.round_type_triple_tossup,
    strings.round_type_triple_tossup_final,
    strings.round_type_speedup,
    strings.round_type_speedup,
    strings.round_type_speedup,
    strings.round_type_bonus]
default_game_rewards = [
    1000,
    2000,
    0,
    0,
    0,
    2000,
    2000,
    2000,
    0,
    0,
    0,
    0]
