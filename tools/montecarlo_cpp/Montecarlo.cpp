#include "Montecarlo.h"

#include <array>
#include <vector>
#include <iostream>
#include <tuple>
#include <algorithm>

#include <iostream>
#include <algorithm>
#include <random>
#include <iterator>

bool eval_best_hand(const std::vector<CardsWithTableCombined>& all_cards_with_table_combined)
// returns true if first player has best hand
{
	std::vector<std::tuple< std::vector<int>, std::vector<int>, std::string>> all_players_score;
	std::vector<std::tuple< std::vector<int>, std::vector<int>, std::string>>  all_players_score_original;
	bool best_hand;

	for (const auto& cards_with_table : all_cards_with_table_combined)
	{
		auto result = calc_score(cards_with_table);
		all_players_score.emplace_back(result);
	}
	all_players_score_original = all_players_score;

	std::sort(all_players_score.begin(), all_players_score.end(), std::greater<>());
	if (all_players_score[0] == all_players_score_original[0])
		best_hand = true; // first player is best hand
	else
		best_hand = false; // different player is best hand

	return best_hand;
}

Score get_rcounts(const CardsWithTableCombined& all_cards_with_table_combined,
	std::vector<std::size_t> available_ranks,
	const std::string original_ranks) {
	Score rcounts;
	for (const auto& card : all_cards_with_table_combined) {
		available_ranks.emplace_back(original_ranks.find(card.substr(0, 1)));
	}
	for (int i = 0; i <= 12; i++) {
		int count = std::count(available_ranks.begin(), available_ranks.end(), i);
		if (count > 0) {
			rcounts.emplace_back(std::make_pair(count, i));
		}
	}
	return rcounts;
}

std::tuple< std::vector<int>, std::vector<int>, std::string> calc_score(const CardsWithTableCombined& all_cards_with_table_combined) {
	const std::string original_ranks = "23456789TJQKA";
	const std::vector<std::string> original_suits{ "C","D","H","S" };
	std::vector<std::size_t> available_ranks;
	std::vector<std::string> available_suits;
	std::vector<int> score;
	std::vector<int> card_ranks;
	std::vector<int> sorted_card_ranks;
	std::string hand_type;
	bool flush = false;
	bool straight = false;

	Score rcounts;
	std::vector<std::tuple<int, std::string>> rsuits;

	rcounts = get_rcounts(all_cards_with_table_combined, available_ranks, original_ranks);

	// sort tuple and split into score and card ranks
	std::sort(rcounts.begin(), rcounts.end(), std::greater<std::tuple<int, int>>());
	for (auto it = std::make_move_iterator(rcounts.begin()),
		end = std::make_move_iterator(rcounts.end()); it != end; ++it)
	{
		score.push_back(std::get<0>(*it));  // amount of occurrences
		card_ranks.push_back(std::get<1>(*it));  // ranks of individual cards
	}

	bool potential_threeofakind = score[0] == 3;
	bool potential_twopair = score == std::vector<int> {2, 2, 1, 1, 1};
	bool potential_pair = score == std::vector<int> {2, 1, 1, 1, 1, 1};

	auto sub_score2 = slice(score, 0, 2);
	auto sub_score4 = slice(score, 0, 5);
	auto sub_score0 = slice(score, 0, 0);
	// # fullhouse(three of a kind and pair, or two three of a kind)
	if (sub_score2 == std::vector<int> {3, 2} || sub_score2 == std::vector<int> {3, 3}) {
		// make adjustment
		card_ranks = slice(card_ranks, 0, 2);
		score = { 3,2 };
	}
	// edge case: convert three pair to two pair
	//const auto x = &score[3];
	else if (sub_score4 == std::vector<int>{2, 2, 2, 1}) {
		score = { 2,2,1 };
		int kicker = std::max(card_ranks[2], card_ranks[3]);
		card_ranks = { card_ranks[0], card_ranks[1], kicker };
	}
	else if (score[0] == 4) {  // four of a kind
		score = { 4, };
		// avoid for example 11, 8, 9
		sorted_card_ranks = card_ranks;
		std::sort(sorted_card_ranks.begin(), sorted_card_ranks.end(), std::greater <>());
		card_ranks = { sorted_card_ranks[0], sorted_card_ranks[1] };
	}
	else if (score.size() >= 5) {  // high card, flush, straight and straight flush
		// straight
		// adjust for 5 high straight
		if (std::find(card_ranks.begin(), card_ranks.end(), 12) != card_ranks.end())
			card_ranks.push_back(-1);
		sorted_card_ranks = card_ranks;
		std::sort(sorted_card_ranks.begin(), sorted_card_ranks.end(), std::greater <>());  // sort again

		for (int i = 0; i < sorted_card_ranks.size() - 4; ++i) {
			straight = sorted_card_ranks[i] - sorted_card_ranks[i + 4] == 4;
			if (straight == true) {
				card_ranks = {
					sorted_card_ranks[i], sorted_card_ranks[i + 1], sorted_card_ranks[i + 2], sorted_card_ranks[i + 3],
					sorted_card_ranks[i + 4] };
				break;
			}
		}

		//flush
		for (std::string card : all_cards_with_table_combined) {
			available_suits.emplace_back(card.substr(1, 1));
		}

		std::vector<int> suit_counts;
		std::vector<std::string> suit_cards;
		for (const auto& suit : original_suits) {  // why can original_suits not be a string and suit a char?
			int count = std::count(available_suits.begin(), available_suits.end(), suit);
			if (count > 0) {
				rsuits.emplace_back(std::make_pair(count, suit));
			}
		}
		std::sort(rsuits.begin(), rsuits.end(), std::greater<std::tuple<int, std::string>>());
		flush = std::get<0>(rsuits[0]) >= 5; // the most occurred suit appear at least 5 times

		if (flush == true)
		{
			auto flush_suit = std::get<1>(rsuits[0]);
			CardsWithTableCombined flush_hand;
			for (auto card : all_cards_with_table_combined) {
				if (card[1] == flush_suit[0]) {
					flush_hand.insert(card);
				}
			}

			Score rcounts_flush = get_rcounts(flush_hand, available_ranks, original_ranks);
			// sort tuple and split into score and card ranks
			std::sort(rcounts_flush.begin(), rcounts_flush.end(), std::greater<std::tuple<int, int>>());
			card_ranks.clear();
			score.clear();
			for (auto it = std::make_move_iterator(rcounts_flush.begin()),
				end = std::make_move_iterator(rcounts_flush.end()); it != end; ++it)
			{
				score.push_back(std::get<0>(*it));  // ranks of individual cards
				card_ranks.push_back(std::get<1>(*it));  // amount of occurrences
			}

			//	# check for straight in flush
			// if 12 in card_ranks and -1 not in card_ranks : # adjust if 5 high straight
			if (std::find(card_ranks.begin(), card_ranks.end(), 12) != card_ranks.end() &&
				!(std::find(card_ranks.begin(), card_ranks.end(), -1) != card_ranks.end())) {
				card_ranks.push_back(-1);
			}

			for (int i = 0; i < card_ranks.size() - 4; i++) {
				straight = card_ranks[i] - card_ranks[i + 4] == 4;
				if (straight == true)
				{
					break;
				}
			}
		}

		// no pair, straight, flush, or straight flush
		if (flush == false && straight == false)
			score = { 1 };
		else if (flush == false && straight == true)
			score = { 3, 1, 2 };
		else if (flush == true && straight == false)
			score = { 3, 1, 3 };
		else if (flush == true && straight == true)
			score = { 5 };
	}
	if (score[0] == 1 && potential_threeofakind == true)
		score = { 3,1 };
	else if (score[0] == 1 && potential_twopair == true)
		score = { 2, 2, 1 };
	else if (score[0] == 1 && potential_pair == true)
		score = { 2, 1, 1 };

	if (score[0] == 5)
		// # crdRanks=crdRanks[:5] # five card rule makes no difference {:5] would be incorrect
		hand_type = "StraightFlush";
	else if (score[0] == 4)
		hand_type = "FoufOfAKind"; // crdRanks = crdRanks[:2] # already implemented above
	else if (slice(score, 0, 2) == std::vector<int> {3, 2})
		hand_type = "FullHouse"; // # crdRanks = crdRanks[:2] # already implmeneted above
	else if (slice(score, 0, 3) == std::vector<int> {3, 1, 3}) {
		hand_type = "Flush";
		card_ranks = slice(card_ranks, 0, 5);
	}

	else if (slice(score, 0, 3) == std::vector<int> {3, 1, 2}) {
		hand_type = "Straight";
		card_ranks = slice(card_ranks, 0, 5);
	}

	else if (slice(score, 0, 2) == std::vector<int> {3, 1}) {
		hand_type = "ThreeOfAKind";
		card_ranks = slice(card_ranks, 0, 3);
	}
	else if (slice(score, 0, 2) == std::vector<int> {3, 1}) {
		hand_type = "ThreeOfAKind";
		card_ranks = slice(card_ranks, 0, 3);
	}
	else if (slice(score, 0, 2) == std::vector<int> {2, 2}) {
		hand_type = "TwoPair";
		card_ranks = slice(card_ranks, 0, 3);
	}
	else if (score[0] == 2) {
		hand_type = "Pair";
		card_ranks = slice(card_ranks, 0, 4);
	}
	else if (score[0] == 1) {
		hand_type = "HighCard";
		card_ranks = slice(card_ranks, 0, 5);
	}
	else
		throw std::runtime_error("Card Type error!");

	auto res = std::make_tuple(score, card_ranks, hand_type);
	return res;
}


double montecarlo(const std::set<std::string>& my_cards, std::set<std::string> cards_on_table, const int number_of_players, const int iterations) {

	if (cards_on_table.size() < 3)
		cards_on_table.clear();
	int wins = 0;

	for (int i = 0; i < iterations; i++)
	{
		Deck deck;
		deck.remove_visible_cards(my_cards, cards_on_table);
		deck.distribute_cards(number_of_players);
		std::vector<CardsWithTableCombined> cards_with_table_combined = deck.get_cards_combined();
		bool first_player_has_best_hand = eval_best_hand(cards_with_table_combined);
		if (first_player_has_best_hand == true)
			wins += 1;
	}
	double equity = (wins / (double)iterations);
	// std::cout << "Equity: " << equity << std::endl;
	return equity;
}



Deck::Deck() {
	std::string combined;
	//std::cout << "Constructing deck..." << std::endl;
	for (char& r : ranks) {
		for (char& s : suits) {
			combined = std::string() + r + s;
			full_deck.insert(combined);
		};
	};
	//std::cout << "Cards in deck: " << full_deck.size() << std::endl;
}

void Deck::remove_visible_cards(const Hand& my_cards_, const std::set<std::string>& cards_on_table_) {
	// remove my_cards and cards_on_table from full_deck
	set_difference(full_deck.begin(), full_deck.end(), my_cards_.begin(), my_cards_.end(),
		std::inserter(remaining_cards_tmp, remaining_cards_tmp.end()));

	// remove visible table cards from deck
	set_difference(remaining_cards_tmp.begin(), remaining_cards_tmp.end(), cards_on_table_.begin(),
		cards_on_table_.end(),
		std::inserter(remaining_cards, remaining_cards.end()));

	//std::cout << "Remaining cards: " << remaining_cards.size() << std::endl;

	this->my_cards = my_cards_.cards;
	this->cards_on_table = cards_on_table_;

	//std::cout << "Removed my cards from deck...\n";
}

void Deck::distribute_cards(int number_players) {
	constexpr size_t cards_in_hand = 2;

	std::vector<std::string> shuffled_deck(remaining_cards.begin(), remaining_cards.end());
	std::shuffle(shuffled_deck.begin(), shuffled_deck.end(), std::mt19937_64(std::random_device()()));
	std::vector<Hand> player_hands(number_players);  // empty container

	auto hand_it = player_hands.begin();
	*hand_it = Hand(my_cards);  // set my own cards
	hand_it++;

	auto card_it = shuffled_deck.begin();
	while (hand_it != player_hands.end()) {
		*hand_it = Hand(std::set<std::string>{*++card_it, * ++card_it});
		++hand_it;
	}

	while (cards_on_table.size() < 5) {
		cards_on_table.emplace(*++card_it);
	}

	// print out the hands
	//for (auto const& player_hand : player_hands) {
	//	std::cout << "Cards: ";
	//	for (const auto& card : player_hand.cards)
	//		std::cout << card << " ";
	//	std::cout << std::endl;
	//}
	this->player_hands = player_hands;

	//std::cout << "Cards on table: ";
	//print_set(cards_on_table);
}

std::vector<CardsWithTableCombined> Deck::get_cards_combined() {
	CardsWithTableCombined cards_with_table_combined;
	std::vector<CardsWithTableCombined> all_cards_with_table_combined;

	for (const auto& player_hand : player_hands) {
		cards_with_table_combined = player_hand.cards;
		cards_with_table_combined.insert(cards_on_table.begin(), cards_on_table.end());
		all_cards_with_table_combined.push_back(cards_with_table_combined);
	}

	return all_cards_with_table_combined;
}

void Deck::print_set(const std::set<std::string>& set) {
	for (const auto& card : set)
		std::cout << card << " ";
	std::cout << std::endl;
}