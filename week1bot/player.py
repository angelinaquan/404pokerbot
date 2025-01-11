'''
Simple example pokerbot, written in Python, with a basic preflop threshold
and a postflop pot-odds-based betting strategy.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random
import eval7


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.
        '''
        # Example: you could track your own cumulative bankroll or do other housekeeping
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.
        '''
        # You can examine how much you won or lost here, or log data for analysis
        previous_state = terminal_state.previous_state
        my_bounty_hit = terminal_state.bounty_hits[active]
        opponent_bounty_hit = terminal_state.bounty_hits[1-active]
        bounty_rank = previous_state.bounties[active]

        # Demonstration of trying to access illegal info (will fail in real engine):
        opponent_bounty_rank = previous_state.bounties[1-active]

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")

    def calculate_strength(self, my_cards, board_cards):
        '''
        Monte Carlo approximation of the probability of winning against a random hand.
        '''
        MC_ITER = 100  # Increase for greater accuracy (but slower)

        # Convert into eval7 objects
        my_cards_eval = [eval7.Card(card) for card in my_cards]
        board_cards_eval = [eval7.Card(card) for card in board_cards]

        deck = eval7.Deck()
        # Remove known cards from the deck
        for card in my_cards_eval + board_cards_eval:
            deck.cards.remove(card)

        score = 0
        for _ in range(MC_ITER):
            deck.shuffle()

            # How many extra cards we need:
            # 2 for opponent + whatever remains to fill 5 board cards
            remaining_board_cards = 5 - len(board_cards_eval)
            draw = deck.peek(2 + remaining_board_cards)

            opp_cards_eval = draw[:2]
            board_draw_eval = draw[2:]

            my_full_hand = my_cards_eval + board_cards_eval + board_draw_eval
            opp_full_hand = opp_cards_eval + board_cards_eval + board_draw_eval

            my_value = eval7.evaluate(my_full_hand)
            opp_value = eval7.evaluate(opp_full_hand)

            if my_value > opp_value:
                score += 1
            elif my_value == opp_value:
                score += 0.5
            else:
                score += 0

        win_rate = score / MC_ITER
        return win_rate

    def get_action(self, game_state, round_state, active):
        '''
        The main decision function, called any time we must act.
        '''
        legal_actions = round_state.legal_actions()  # the actions we can take
        street = round_state.street                 # 0=preflop, 3=flop, 4=turn, 5=river
        my_cards = round_state.hands[active]        # our 2 hole cards
        board_cards = round_state.deck[:street]     # community cards shown so far

        my_pip = round_state.pips[active]           # how many chips I have committed so far this street
        opp_pip = round_state.pips[1-active]        # how many chips opp has committed this street
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]

        continue_cost = opp_pip - my_pip
        pot_total = (STARTING_STACK - my_stack) + (STARTING_STACK - opp_stack)
        # A small "epsilon" to avoid dividing by zero
        pot_odds = float(continue_cost) / float(pot_total + 0.01)

        # Preflop: If street == 0, we can do a separate logic
        if street == 0:
            # approximate strength with no board cards
            preflop_strength = self.calculate_strength(my_cards, [])
            # If it's below 50%, we want to fold if there's a bet; check if free
            if preflop_strength < 0.50:
                # If we can check for free, do so
                if CheckAction in legal_actions:
                    return CheckAction()
                else:
                    # Otherwise, fold
                    return FoldAction()
            # If it's above 50, we proceed to a simple raise/call logic
            # just to put some chips in with a strong hand.
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                # We'll do a small raise if we haven't contributed yet
                raise_amount = min_raise
                return RaiseAction(raise_amount)
            elif CheckAction in legal_actions:
                return CheckAction()
            else:
                return CallAction()

        else:
            # Postflop (Flop/Turn/River)
            strength = self.calculate_strength(my_cards, board_cards)

            # If our approximate winning chance is well above the pot odds, we can be more aggressive
            # Simple rule: if strength > 1.3*pot_odds, raise (when possible); if > pot_odds, call/check; else fold
            if strength < pot_odds:
                # If we can check, do it; else fold
                if CheckAction in legal_actions:
                    return CheckAction()
                else:
                    return FoldAction()
            elif strength > 1.3 * pot_odds and RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()
                # We'll do a modest raise
                raise_amount = int(min_raise + 0.2 * (max_raise - min_raise))
                return RaiseAction(raise_amount)
            else:
                # Just call or check
                if CheckAction in legal_actions:
                    return CheckAction()
                else:
                    return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
