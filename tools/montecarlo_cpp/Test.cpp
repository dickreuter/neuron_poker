#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE HandEvaluationTests

#include <boost/test/included/unit_test.hpp>
#include "Montecarlo.h"

BOOST_AUTO_TEST_CASE(card_evaluation1)
{
	std::set<std::string> cards1 = { "3H", "3S", "4H", "4S", "8S", "8C", "QH" };
	std::set<std::string> cards2 = { "KH", "6C", "4H", "4S", "8S", "8C", "QH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation2)
{
	std::set<std::string> cards1 = { "8H", "8D", "QH", "7H", "9H", "JH", "TH" };
	std::set<std::string> cards2 = { "KH", "6C", "QH", "7H", "9H", "JH", "TH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation3)
{
	std::set<std::string> cards1 = { "AS", "KS", "TS", "9S", "7S", "2H", "2D" };
	std::set<std::string> cards2 = { "AS", "KS", "TS", "9S", "8S", "2H", "2D" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation4)
{
	std::set<std::string> cards1 = { "8S", "TS", "8H", "KS", "9S", "TH", "KH" };
	std::set<std::string> cards2 = { "TD", "7S", "8H", "KS", "9S", "TH", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = true;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation5)
{
	std::set<std::string> cards1 = { "2D", "2H", "AS", "AD", "AH", "8S", "7H" };
	std::set<std::string> cards2 = { "7C", "7S", "7H", "AD", "AS", "8S", "8H" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = true;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation6)
{
	std::set<std::string> cards1 = { "7C", "7S", "7H", "AD", "KS", "5S", "8H" };
	std::set<std::string> cards2 = { "2D", "3H", "AS", "4D", "5H", "8S", "7H" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation6b)
{
	std::set<std::string> cards1 = { "7C", "7C", "AC", "AC", "8C", "8S", "7H" };
	std::set<std::string> cards2 = { "2C", "3C", "4C", "5C", "6C", "8S", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation7)
{
	std::set<std::string> cards1 = { "AC", "JS", "AS", "2D", "5H", "3S", "3H" };
	std::set<std::string> cards2 = { "QD", "JD", "TS", "9D", "6H", "8S", "KH" };
	std::set<std::string> cards3 = { "2D", "3D", "4S", "5D", "6H", "8S", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2,cards3 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation8)
{
	std::set<std::string> cards1 = { "7C", "5S", "3S", "JD", "8H", "2S", "KH" };
	std::set<std::string> cards2 = { "AD", "3D", "4S", "5D", "9H", "8S", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation9)
{
	std::set<std::string> cards1 = { "2C", "2D", "4S", "4D", "4H", "8S", "KH" };
	std::set<std::string> cards2 = { "7C", "7S", "7D", "7H", "8H", "8S", "JH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation10)
{
	std::set<std::string> cards1 = { "7C", "5S", "3S", "JD", "8H", "2S", "KH" };
	std::set<std::string> cards2 = { "AD", "3D", "3S", "5D", "9H", "8S", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation11)
{
	std::set<std::string> cards1 = { "7H", "7S", "3S", "JD", "8H", "2S", "KH" };
	std::set<std::string> cards2 = { "7D", "3D", "3S", "7C", "9H", "8S", "KH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation12)
{
	std::set<std::string> cards1 = { "AS", "8H", "TS", "JH", "3H", "2H", "AH" };
	std::set<std::string> cards2 = { "QD", "QH", "TS", "JH", "3H", "2H", "AH" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = false;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(card_evaluation13)
{
	std::set<std::string> cards1 = { "9S", "7H", "KS", "KH", "AH", "AS", "AC" };
	std::set<std::string> cards2 = { "8D", "2H", "KS", "KH", "AH", "AS", "AC" };

	const std::vector<CardsWithTableCombined> all_cards{ cards1,cards2 };

	bool expected = true;
	bool won = eval_best_hand(all_cards);
	BOOST_TEST(won == expected);
}

BOOST_AUTO_TEST_CASE(montecarlo1)
{
	std::set<std::string> my_cards = { "3H", "3S" };
	std::set<std::string>    cards_on_table = { "8S", "4S", "QH", "8C", "4H" };
	const int number_of_players = 2;
	const int iterations = 50000;
	double equity = montecarlo(my_cards, cards_on_table, number_of_players, iterations);
	double expected = 40.2;
	int tolerance = 1;

	BOOST_CHECK_CLOSE(equity*100, expected, tolerance);
}


BOOST_AUTO_TEST_CASE(montecarlo3)
{
	std::set<std::string> my_cards = { "AS", "KS" };
	std::set<std::string> cards_on_table = { };
	const int number_of_players = 3;
	const int iterations = 50000;
	double equity = montecarlo(my_cards, cards_on_table, number_of_players, iterations);

	double expected = 51.8;
	int tolerance = 1;

	BOOST_CHECK_CLOSE(equity * 100, expected, tolerance);
}


BOOST_AUTO_TEST_CASE(montecarlo4)
{
	std::set<std::string> my_cards = { "AS", "KS" };
	std::set<std::string> cards_on_table = { };
	const int number_of_players = 2;
	const int iterations = 50000;
	double equity = montecarlo(my_cards, cards_on_table, number_of_players, iterations);

	double expected = 67.7;
	int tolerance = 1;

	BOOST_CHECK_CLOSE(equity * 100, expected, tolerance);
}